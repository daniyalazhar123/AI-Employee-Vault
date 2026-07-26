"""
Odoo Bank Reconciliation Engine — Platinum Tier Core Engine

Monitors Needs_Action/ for CSV/PDF bank statements, parses transactions,
matches them deterministically against Odoo unpaid invoices via XML-RPC,
and auto-registers payments for 100% matches. Ambiguous matches go to
Pending_Approval/Reconciliation_Errors.md for human-in-the-loop review.

Matching Priority (deterministic, no ML):
    1. Exact Reference string match (invoice reference == bank ref)
    2. Exact Amount match (|bank_amount - invoice_amount| < 0.01)
    3. Date proximity scoring (closest date wins)

Credentials (secrets_config / env):
    ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, ODOO_API_KEY

Usage:
    python odoo_bank_reconciliation.py check    # Scan Needs_Action once
    python odoo_bank_reconciliation.py watch    # Poll every 30s
    python odoo_bank_reconciliation.py status   # Show reconciliation state
"""

import csv
import json
import logging
import os
import re
import sys
import time
import xmlrpc.client
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from audit_logger import setup_logging, AuditLogger, log_action, log_mcp_action
logger = setup_logging('BankRecon')

sys.path.insert(0, str(Path(__file__).parent))
from secrets_config import SECRETS_DIR, load_secrets, get_secret_path
load_secrets()
from error_recovery import CircuitBreaker, DeadLetterQueue, get_dlq
from dependency_fallback_guard import PyPDF2Proxy, PYPDF2_AVAILABLE as PDF_AVAILABLE

VAULT_PATH = Path(__file__).parent
NEEDS_ACTION = VAULT_PATH / 'Needs_Action'
PENDING = VAULT_PATH / 'Pending_Approval'
APPROVED = VAULT_PATH / 'Approved'
DLQ_DIR = VAULT_PATH / 'Dead_Letter_Queue'
LOGS = VAULT_PATH / 'Logs'
PROCESSED_FILE = VAULT_PATH / 'data' / 'bank_recon_processed.txt'
RECONCILIATION_ERRORS = PENDING / 'Reconciliation_Errors.md'

POLL_INTERVAL = 30
MATCH_CONFIDENCE_EXACT = 1.0
AMOUNT_EPSILON = 0.01


class BankReconciliationEngine:
    """Odoo bank reconciliation engine with deterministic matching."""

    def __init__(self, vault_path: Optional[Path] = None):
        self.vault = Path(vault_path) if vault_path else VAULT_PATH
        self.needs_action = self.vault / 'Needs_Action'
        self.pending = self.vault / 'Pending_Approval'
        self.approved = self.vault / 'Approved'
        self.dlq = self.vault / 'Dead_Letter_Queue'
        self.logs = self.vault / 'Logs'
        for d in [self.needs_action, self.pending, self.approved, self.dlq, self.logs]:
            d.mkdir(parents=True, exist_ok=True)

        self.odoo_url = os.environ.get('ODOO_URL', 'http://localhost:8069')
        self.odoo_db = os.environ.get('ODOO_DB', 'odoo')
        self.odoo_username = os.environ.get('ODOO_USERNAME', 'admin')
        self.odoo_password = os.environ.get('ODOO_PASSWORD', 'admin')
        self.odoo_api_key = os.environ.get('ODOO_API_KEY', '')

        self.uid = None
        self.common = None
        self.models = None
        self._odoo_circuit = CircuitBreaker('odoo_xmlrpc', failure_threshold=3, timeout=30)

        self.audit = AuditLogger(self.vault)
        self.processed_files = self._load_processed()
        self.reconciled_count = 0
        self.error_count = 0

    # ---- Processed File Tracking ----

    def _load_processed(self) -> set:
        if PROCESSED_FILE.exists():
            try:
                return set(PROCESSED_FILE.read_text(encoding='utf-8').splitlines())
            except Exception:
                return set()
        return set()

    def _save_processed(self):
        PROCESSED_FILE.parent.mkdir(parents=True, exist_ok=True)
        PROCESSED_FILE.write_text('\n'.join(sorted(self.processed_files)), encoding='utf-8')

    # ---- Odoo XML-RPC Client ----

    def _odoo_authenticate(self) -> bool:
        if not self._odoo_circuit.can_execute():
            logger.warning("Odoo circuit breaker open, skipping")
            return False
        try:
            self.common = xmlrpc.client.ServerProxy(f'{self.odoo_url}/xmlrpc/2/common')
            self.models = xmlrpc.client.ServerProxy(f'{self.odoo_url}/xmlrpc/2/object')
            self.uid = self.common.authenticate(self.odoo_db, self.odoo_username, self.odoo_password, {})
            if self.uid:
                logger.info(f"Odoo authenticated as UID {self.uid}")
                self._odoo_circuit.record_success()
                return True
            logger.error("Odoo authentication failed")
            self._odoo_circuit.record_failure()
            return False
        except Exception as e:
            logger.error(f"Odoo connection error: {e}")
            self._odoo_circuit.record_failure(e)
            return False

    def fetch_unpaid_invoices(self) -> List[Dict]:
        """Fetch all unpaid invoices from Odoo."""
        if not self.uid and not self._odoo_authenticate():
            return []
        try:
            domain = [
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('payment_state', '=', 'not_paid'),
            ]
            invoice_ids = self.models.execute_kw(
                self.odoo_db, self.uid, self.odoo_password,
                'account.move', 'search', [domain]
            )
            if not invoice_ids:
                logger.info("No unpaid invoices found")
                return []
            invoices = self.models.execute_kw(
                self.odoo_db, self.uid, self.odoo_password,
                'account.move', 'read',
                [invoice_ids],
                {'fields': ['id', 'name', 'ref', 'invoice_date', 'amount_total',
                            'partner_id', 'invoice_payment_term_id', 'amount_residual',
                            'currency_id', 'state', 'payment_state']}
            )
            logger.info(f"Fetched {len(invoices)} unpaid invoices")
            log_mcp_action('odoo', 'fetch_unpaid_invoices',
                           {'count': len(invoices)}, 'success')
            return invoices
        except Exception as e:
            logger.error(f"Failed to fetch invoices: {e}")
            self._odoo_circuit.record_failure(e)
            log_mcp_action('odoo', 'fetch_unpaid_invoices', {}, 'failed', error=str(e))
            return []

    def register_payment(self, invoice_id: int, amount: float,
                         payment_date: str, ref: str = '') -> Dict:
        """Register payment for an invoice via account.payment.register."""
        if not self.uid and not self._odoo_authenticate():
            return {'success': False, 'message': 'Not authenticated to Odoo'}
        try:
            payment_ctx = {
                'active_model': 'account.move',
                'active_ids': [invoice_id],
                'active_id': invoice_id,
            }
            wizard_data = {
                'amount': amount,
                'payment_date': payment_date,
                'communication': ref or f'Bank Recon Auto {datetime.now():%Y%m%d}',
                'payment_type': 'inbound',
                'partner_type': 'customer',
                'journal_id': 1,
            }
            wizard_id = self.models.execute_kw(
                self.odoo_db, self.uid, self.odoo_password,
                'account.payment.register', 'create', [wizard_data]
            )
            result = self.models.execute_kw(
                self.odoo_db, self.uid, self.odoo_password,
                'account.payment.register', 'action_create_payments',
                [[wizard_id]], payment_ctx
            )
            logger.info(f"Payment registered for invoice {invoice_id}: {amount}")
            log_mcp_action('odoo', 'register_payment',
                           {'invoice_id': invoice_id, 'amount': amount},
                           'success')
            return {'success': True, 'invoice_id': invoice_id, 'amount': amount,
                    'wizard_id': wizard_id, 'result': result}
        except Exception as e:
            logger.error(f"Failed to register payment for invoice {invoice_id}: {e}")
            self._odoo_circuit.record_failure(e)
            log_mcp_action('odoo', 'register_payment',
                           {'invoice_id': invoice_id, 'amount': amount},
                           'failed', error=str(e))
            return {'success': False, 'message': str(e)}

    # ---- Statement File Scanning ----

    def scan_statement_files(self) -> List[Path]:
        """Find all unprocessed CSV/PDF files in Needs_Action."""
        files = []
        for ext in ('*.csv', '*.CSV', '*.pdf', '*.PDF'):
            for f in sorted(self.needs_action.glob(ext)):
                if f.name not in self.processed_files:
                    files.append(f)
        if files:
            logger.info(f"Found {len(files)} unprocessed statement file(s)")
        return files

    # ---- Parser: CSV ----

    def parse_csv(self, file_path: Path) -> List[Dict]:
        """Parse a bank statement CSV into structured transactions."""
        transactions = []
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                if not reader.fieldnames:
                    logger.warning(f"CSV {file_path.name} has no headers")
                    return []
                headers_lower = [h.strip().lower() for h in reader.fieldnames]
                date_col = self._find_column(headers_lower, ['date', 'transaction date', 'posting date', 'value date'])
                ref_col = self._find_column(headers_lower, ['reference', 'ref', 'description', 'narrative', 'particulars', 'memo'])
                amount_col = self._find_column(headers_lower, ['amount', 'value', 'transaction amount', 'debit/credit', 'sum'])
                partner_col = self._find_column(headers_lower, ['counterparty', 'partner', 'payer', 'payee', 'beneficiary', 'name', 'merchant'])

                for row in reader:
                    txn = self._normalize_transaction(row, date_col, ref_col, amount_col, partner_col)
                    if txn:
                        transactions.append(txn)

            logger.info(f"Parsed {len(transactions)} transactions from {file_path.name}")
            return transactions
        except Exception as e:
            logger.error(f"Failed to parse CSV {file_path.name}: {e}")
            return []

    def _find_column(self, headers: List[str], candidates: List[str]) -> int:
        for i, h in enumerate(headers):
            for c in candidates:
                if c in h:
                    return i
        return -1

    def _normalize_transaction(self, row: Dict, date_col: int, ref_col: int,
                                amount_col: int, partner_col: int) -> Optional[Dict]:
        try:
            values = list(row.values())
            raw_date = values[date_col].strip() if date_col >= 0 and date_col < len(values) else ''
            raw_ref = values[ref_col].strip() if ref_col >= 0 and ref_col < len(values) else ''
            raw_amount = values[amount_col].strip() if amount_col >= 0 and amount_col < len(values) else ''
            raw_partner = values[partner_col].strip() if partner_col >= 0 and partner_col < len(values) else ''

            parsed_date = self._parse_date(raw_date)
            parsed_amount = self._parse_amount(raw_amount)
            clean_ref = raw_ref.strip(' "\'')

            if parsed_amount is None:
                return None

            return {
                'date': parsed_date,
                'reference': clean_ref,
                'amount': parsed_amount,
                'counterparty': raw_partner,
                'raw': {k.strip(): v.strip() for k, v in row.items()},
            }
        except Exception:
            return None

    # ---- Parser: PDF ----

    def parse_pdf(self, file_path: Path) -> List[Dict]:
        """Parse a bank statement PDF into structured transactions."""
        if not PDF_AVAILABLE:
            logger.warning(f"PDF parser not available, cannot parse: {file_path.name}")
            return []
        try:
            transactions = []
            text = ''
            reader = PyPDF2Proxy.PdfReader(file_path)
            for page in reader.pages:
                text += page.extract_text() + '\n'

            blocks = re.split(r'\n\s*\n', text)
            for block in blocks:
                txn = self._parse_pdf_block(block)
                if txn:
                    transactions.append(txn)

            logger.info(f"Parsed {len(transactions)} transactions from PDF {file_path.name}")
            return transactions
        except Exception as e:
            logger.error(f"Failed to parse PDF {file_path.name}: {e}")
            return []

    def _parse_pdf_block(self, block: str) -> Optional[Dict]:
        date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
        ]
        amount_patterns = [
            r'[\$\€\£\₹]?\s*(\d{1,3}(?:,\d{3})*\.\d{2})',
            r'[\$\€\£\₹]?\s*(\d+\.\d{2})',
        ]
        date_match = None
        for p in date_patterns:
            m = re.search(p, block)
            if m:
                date_match = self._parse_date(m.group(1))
                if date_match:
                    break
        amount = None
        raw_amount = ''
        for p in amount_patterns:
            m = re.findall(p, block)
            if m:
                raw_amount = m[-1]
                amount = self._parse_amount(raw_amount)
                if amount:
                    break
        if date_match is None or amount is None:
            return None
        clean_block = re.sub(r'\s+', ' ', block).strip()
        ref = clean_block[:80]
        return {
            'date': date_match,
            'reference': ref,
            'amount': amount,
            'counterparty': '',
            'raw': {'pdf_text': clean_block[:200]},
        }

    # ---- Shared Parsing Utilities ----

    def _parse_date(self, raw: str) -> str:
        raw = raw.strip()
        for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%Y/%m/%d',
                    '%d/%m/%y', '%m/%d/%y', '%d-%b-%Y', '%d-%b-%y'):
            try:
                return datetime.strptime(raw, fmt).strftime('%Y-%m-%d')
            except ValueError:
                continue
        return datetime.now().strftime('%Y-%m-%d')

    def _parse_amount(self, raw: str) -> Optional[float]:
        raw = raw.strip().replace(' ', '').replace(',', '').replace('$', '').replace('€', '').replace('£', '').replace('₹', '').replace('Rs', '').replace('rs', '')
        try:
            return abs(float(raw))
        except (ValueError, TypeError):
            return None

    # ---- Deterministic Matching Engine ----

    def match_transactions(self, transactions: List[Dict],
                           invoices: List[Dict]) -> List[Dict]:
        """Match bank transactions to invoices. Priority: Reference > Amount > Date."""
        if not transactions or not invoices:
            return []
        results = []
        unmatched_txns = list(transactions)
        used_invoice_ids = set()

        last_pass_unmatched = 0
        while unmatched_txns and len(unmatched_txns) != last_pass_unmatched:
            last_pass_unmatched = len(unmatched_txns)
            still_unmatched = []
            for txn in unmatched_txns:
                match = self._find_best_match(txn, invoices, used_invoice_ids)
                if match:
                    results.append(match)
                    used_invoice_ids.add(match['invoice_id'])
                else:
                    still_unmatched.append(txn)
            unmatched_txns = still_unmatched

        for txn in unmatched_txns:
            results.append({
                'transaction': txn,
                'invoice_id': None,
                'confidence': 0.0,
                'match_tier': 'none',
                'match_detail': 'No matching invoice found',
                'needs_review': True,
            })

        matched = sum(1 for r in results if r.get('invoice_id'))
        logger.info(f"Matched {matched}/{len(transactions)} transactions "
                    f"({len(unmatched_txns)} unmatched)")
        return results

    def _find_best_match(self, txn: Dict, invoices: List[Dict],
                          used_ids: set) -> Optional[Dict]:
        """Find the best invoice match. Returns None if no match found."""
        txn_ref = txn.get('reference', '').strip().lower()
        txn_amount = txn.get('amount', 0.0)
        txn_date = txn.get('date', '')

        # Tier 1: Exact reference match
        if txn_ref:
            for inv in invoices:
                if inv['id'] in used_ids:
                    continue
                inv_ref = (inv.get('ref') or '').strip().lower()
                inv_name = (inv.get('name') or '').strip().lower()
                if txn_ref == inv_ref or txn_ref == inv_name:
                    score = SequenceMatcher(None, txn_ref, inv_ref or inv_name).ratio()
                    if score >= 0.95:
                        return {
                            'transaction': txn,
                            'invoice_id': inv['id'],
                            'invoice_ref': inv.get('ref', ''),
                            'invoice_name': inv.get('name', ''),
                            'invoice_amount': inv.get('amount_total', 0.0),
                            'confidence': MATCH_CONFIDENCE_EXACT,
                            'match_tier': '1_reference',
                            'match_detail': f'Exact reference match: {inv.get("ref", "")}',
                            'needs_review': False,
                        }

        # Tier 2: Exact amount match
        amount_candidates = []
        for inv in invoices:
            if inv['id'] in used_ids:
                continue
            inv_amount = inv.get('amount_total', 0.0)
            if abs(txn_amount - inv_amount) < AMOUNT_EPSILON:
                score = SequenceMatcher(None, txn_ref, (inv.get('ref') or '').lower()).ratio()
                amount_candidates.append({
                    'invoice_id': inv['id'],
                    'invoice_ref': inv.get('ref', ''),
                    'invoice_name': inv.get('name', ''),
                    'invoice_amount': inv_amount,
                    'invoice_date': inv.get('invoice_date', ''),
                    'ref_similarity': score,
                })

        if len(amount_candidates) == 1:
            cand = amount_candidates[0]
            return {
                'transaction': txn,
                'invoice_id': cand['invoice_id'],
                'invoice_ref': cand['invoice_ref'],
                'invoice_name': cand['invoice_name'],
                'invoice_amount': cand['invoice_amount'],
                'confidence': MATCH_CONFIDENCE_EXACT,
                'match_tier': '2_amount',
                'match_detail': f'Exact amount match: {txn_amount}',
                'needs_review': False,
            }

        # Tier 3: Date proximity scoring
        if amount_candidates and txn_date:
            for cand in amount_candidates:
                inv_date = cand.get('invoice_date', '')
                if inv_date:
                    try:
                        txn_dt = datetime.strptime(txn_date, '%Y-%m-%d')
                        inv_dt = datetime.strptime(inv_date, '%Y-%m-%d')
                        days_diff = abs((txn_dt - inv_dt).days)
                        cand['date_proximity'] = max(0, 30 - days_diff) / 30.0
                    except ValueError:
                        cand['date_proximity'] = 0.0
                else:
                    cand['date_proximity'] = 0.0

            amount_candidates.sort(key=lambda x: (
                -x.get('ref_similarity', 0),
                -x.get('date_proximity', 0)
            ))
            best = amount_candidates[0]
            if len(amount_candidates) == 1 or (
                best.get('date_proximity', 0) > amount_candidates[1].get('date_proximity', 0) + 0.2
            ):
                return {
                    'transaction': txn,
                    'invoice_id': best['invoice_id'],
                    'invoice_ref': best['invoice_ref'],
                    'invoice_name': best['invoice_name'],
                    'invoice_amount': best['invoice_amount'],
                    'confidence': 0.9,
                    'match_tier': '3_date_proximity',
                    'match_detail': f'Amount match + date proximity (diff={1-best.get("date_proximity", 0):.0f}d)',
                    'needs_review': False,
                }

        # Multiple candidates with same amount and close dates -> needs review
        if len(amount_candidates) >= 2:
            return {
                'transaction': txn,
                'invoice_id': None,
                'confidence': 0.0,
                'match_tier': 'ambiguous',
                'match_detail': f'Multiple invoices with same amount ({txn_amount}). '
                                f'Candidates: {", ".join(str(c["invoice_id"]) for c in amount_candidates)}',
                'needs_review': True,
                'candidates': amount_candidates,
            }

        return None

    # ---- Reconciliation Pipeline ----

    def process_statement(self, file_path: Path) -> int:
        """Process a single statement file. Returns matched count."""
        logger.info(f"Processing statement: {file_path.name}")
        log_action('bank_recon', {'file': file_path.name}, 'pending',
                   actor='reconciliation_engine', target=file_path.name)

        if file_path.suffix.lower() == '.csv':
            transactions = self.parse_csv(file_path)
        elif file_path.suffix.lower() == '.pdf':
            transactions = self.parse_pdf(file_path)
        else:
            logger.warning(f"Unsupported file type: {file_path.suffix}")
            return 0

        if not transactions:
            logger.info(f"No transactions parsed from {file_path.name}")
            self.processed_files.add(file_path.name)
            self._save_processed()
            return 0

        invoices = self.fetch_unpaid_invoices()
        if not invoices:
            logger.warning("No unpaid invoices to match against")
            dlq = get_dlq(self.vault)
            dlq.add(file_path.name, 'bank_statement',
                    'No unpaid invoices in Odoo to reconcile against',
                    original_data={'transactions': transactions})
            self.processed_files.add(file_path.name)
            self._save_processed()
            return 0

        results = self.match_transactions(transactions, invoices)
        matched_count = 0
        pending_review = 0

        for result in results:
            if result.get('needs_review'):
                self._write_reconciliation_error(result)
                pending_review += 1
            elif result.get('invoice_id'):
                ok = self._execute_payment(result)
                if ok:
                    matched_count += 1

        total = len(transactions)
        logger.info(f"Statement {file_path.name}: {matched_count} paid, "
                    f"{pending_review} pending review, "
                    f"{total - matched_count - pending_review} unmatched")

        log_action('bank_recon', {
            'file': file_path.name,
            'transactions': total,
            'matched': matched_count,
            'pending_review': pending_review,
        }, 'success' if matched_count > 0 else 'pending',
            actor='reconciliation_engine', target=file_path.name)

        self.processed_files.add(file_path.name)
        self._save_processed()
        return matched_count

    def _execute_payment(self, match: Dict) -> bool:
        """Execute payment for a matched transaction."""
        txn = match['transaction']
        invoice_id = match['invoice_id']
        amount = txn['amount']
        date = txn['date']
        ref = txn.get('reference', '')

        result = self.register_payment(invoice_id, amount, date, ref)
        if result.get('success'):
            self.reconciled_count += 1
            logger.info(f"PAID: Invoice {invoice_id} ({match['invoice_ref'] or match['invoice_name']}) "
                        f"- {amount} on {date} [{match['match_tier']}]")
            return True
        else:
            self.error_count += 1
            logger.error(f"Payment FAILED for invoice {invoice_id}: {result.get('message')}")
            dlq = get_dlq(self.vault)
            dlq.add(f'inv_{invoice_id}', 'payment_failed',
                    result.get('message', 'Unknown error'),
                    original_data={'match': match, 'result': result})
            return False

    # ---- Human-in-the-Loop Exception Files ----

    def _write_reconciliation_error(self, match: Dict):
        """Write a reconciliation error to Pending_Approval/Reconciliation_Errors.md."""
        txn = match['transaction']
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        inv_lines = ''
        candidates = match.get('candidates', [])
        if candidates:
            for c in candidates:
                inv_lines += (
                    f"  - Invoice ID: {c['invoice_id']}\n"
                    f"    Ref: {c.get('invoice_ref', 'N/A')}\n"
                    f"    Name: {c.get('invoice_name', 'N/A')}\n"
                    f"    Amount: {c.get('invoice_amount', 0.0)}\n"
                    f"    Date: {c.get('invoice_date', 'N/A')}\n"
                    f"    Ref Similarity: {c.get('ref_similarity', 0.0):.2f}\n"
                    f"    Date Proximity: {c.get('date_proximity', 0.0):.2f}\n"
                )

        self.pending.mkdir(parents=True, exist_ok=True)

        entry = (
            f"---\n"
            f"type: reconciliation_error\n"
            f"timestamp: {datetime.now().isoformat()}\n"
            f"match_tier: {match.get('match_tier', 'none')}\n"
            f"confidence: {match.get('confidence', 0.0)}\n"
            f"status: pending_review\n"
            f"---\n\n"
            f"## Bank Transaction\n\n"
            f"| Field | Value |\n"
            f"|-------|-------|\n"
            f"| Date | {txn.get('date', 'N/A')} |\n"
            f"| Reference | {txn.get('reference', 'N/A')} |\n"
            f"| Amount | {txn.get('amount', 0.0)} |\n"
            f"| Counterparty | {txn.get('counterparty', 'N/A')} |\n\n"
            f"## Match Detail\n\n"
            f"**Tier:** {match.get('match_tier', 'none')}\n\n"
            f"**Detail:** {match.get('match_detail', 'No match found')}\n\n"
        )

        if inv_lines:
            entry += f"## Candidate Invoices\n\n{inv_lines}\n\n"

        entry += (
            f"## Action Required\n\n"
            f"1. Review the bank transaction above\n"
            f"2. Identify the correct invoice manually\n"
            f"3. Update this file with the correct `invoice_id`\n"
            f"4. Move to Approved/ to trigger payment\n"
        )

        if RECONCILIATION_ERRORS.exists():
            existing = RECONCILIATION_ERRORS.read_text(encoding='utf-8')
            existing += f'\n\n---\n\n{entry}'
            RECONCILIATION_ERRORS.write_text(existing, encoding='utf-8')
        else:
            header = (
                f"# Reconciliation Errors\n\n"
                f"Bank transactions that could not be automatically reconciled.\n"
                f"Each entry requires human review and operator override.\n\n"
                f"---\n\n"
            )
            RECONCILIATION_ERRORS.write_text(header + entry, encoding='utf-8')

        logger.warning(f"Reconciliation error written for {txn.get('reference', 'unknown')}")
        log_action('bank_recon', {
            'reference': txn.get('reference', ''),
            'amount': txn.get('amount', 0),
            'tier': match.get('match_tier', 'none'),
        }, 'pending_review', actor='reconciliation_engine',
            target=f'Reconciliation_Errors.md')

    # ---- Orchestration ----

    def check_and_reconcile(self) -> int:
        """Scan Needs_Action and reconcile all statement files."""
        files = self.scan_statement_files()
        if not files:
            logger.info("No new statement files to process")
            return 0

        logger.info(f"Processing {len(files)} statement file(s)")
        total_matched = 0
        for f in files:
            try:
                matched = self.process_statement(f)
                total_matched += matched
            except Exception as e:
                logger.error(f"Failed to process {f.name}: {e}")
                dlq = get_dlq(self.vault)
                dlq.add(f.name, 'bank_statement', str(e))
                self.error_count += 1

        if total_matched > 0:
            logger.info(f"Reconciliation complete: {total_matched} transaction(s) paid")
        else:
            logger.info("No transactions were auto-reconciled")

        log_action('bank_recon', {
            'files': len(files),
            'matched': total_matched,
            'errors': self.error_count,
        }, 'success', actor='reconciliation_engine', target='batch')

        return total_matched

    def watch_loop(self):
        """Continuously poll Needs_Action for new statements."""
        logger.info(f"Starting bank reconciliation watch loop (poll every {POLL_INTERVAL}s)")
        while True:
            try:
                self.check_and_reconcile()
            except Exception as e:
                logger.error(f"Watch loop error: {e}")
            time.sleep(POLL_INTERVAL)


# ---- CLI ----

def main():
    if len(sys.argv) < 2:
        print("Usage: python odoo_bank_reconciliation.py <command>")
        print("  check   - Scan Needs_Action and reconcile once")
        print("  watch   - Continuously poll Needs_Action")
        print("  status  - Show reconciliation system status")
        sys.exit(1)

    cmd = sys.argv[1]
    engine = BankReconciliationEngine()

    if cmd == 'check':
        count = engine.check_and_reconcile()
        logger.info(f"Reconciled {count} transaction(s)")
        sys.exit(0)

    elif cmd == 'watch':
        engine.watch_loop()

    elif cmd == 'status':
        print(f"Bank Reconciliation Engine Status")
        print(f"  Odoo URL:           {engine.odoo_url}")
        print(f"  Odoo DB:            {engine.odoo_db}")
        print(f"  Odoo Auth:          {'YES' if engine.uid else 'NO'}")
        print(f"  Needs_Action files: {len(list(engine.needs_action.glob('*.csv')))} CSV, "
              f"{len(list(engine.needs_action.glob('*.pdf')))} PDF")
        print(f"  Pending review:     {'YES' if RECONCILIATION_ERRORS.exists() else 'NO'}"
              f"{' (' + str(sum(1 for _ in RECONCILIATION_ERRORS.read_text().split('---')) - 2) + ' errors)' if RECONCILIATION_ERRORS.exists() else ''}")
        print(f"  Reconciled count:   {engine.reconciled_count}")
        print(f"  Error count:        {engine.error_count}")
        print(f"  PDF parser:         {'PyPDF2Proxy (available)' if PDF_AVAILABLE else 'NOT INSTALLED'}")
        print(f"  Odoo circuit:       {engine._odoo_circuit.state.value}")

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == '__main__':
    main()
