#!/usr/bin/env python3
"""
MCP Odoo Server - Pure Python Implementation
Odoo ERP integration using xmlrpc.client

Personal AI Employee Hackathon 0
Platinum Tier: Pure Python Implementation
"""

import os
import sys
import json
import xmlrpc.client
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import logging

# --- MCP stdio mode detection (must precede logging-configuring imports) ---
# MCP-over-stdio uses stdout for the JSON-RPC channel; any log line written to
# stdout corrupts the protocol. When this file is launched as an MCP server
# (no CLI args, or an explicit --mcp flag), route ALL logging to stderr BEFORE
# importing secrets_config / audit_logger, both of which emit log lines at
# import time. When imported as a module (local_agent), __name__ != '__main__'
# so nothing changes.
_MCP_MODE = __name__ == '__main__' and (len(sys.argv) == 1 or '--mcp' in sys.argv)
if _MCP_MODE:
    os.environ['AI_EMPLOYEE_LOG_STREAM'] = 'stderr'

# Load secrets from outside vault
sys.path.insert(0, str(Path(__file__).parent))
from secrets_config import SECRETS_DIR, load_secrets, get_secret_path
load_secrets()

from audit_logger import setup_logging, log_mcp_action
logger = setup_logging('MCPOdoo')

# Security matrix gate for the payment path (>$100 or new payee => approval).
try:
    from security_guard import SecurityGuard
except Exception as _sg_err:  # pragma: no cover - guard import must never break Odoo ops
    SecurityGuard = None
    logger.warning(f"⚠️ SecurityGuard unavailable ({_sg_err}); payments will fail-safe to requiring approval")


class MCPOdooServer:
    """Pure Python MCP Odoo Server"""
    
    def __init__(self, vault_path: Optional[Path] = None):
        self.vault_path = vault_path or Path(__file__).parent
        self.logs_folder = self.vault_path / 'Logs'
        self.logs_folder.mkdir(exist_ok=True)
        
        # Load Odoo credentials from environment
        self.odoo_url = os.getenv('ODOO_URL', 'http://localhost:8069')
        self.odoo_db = os.getenv('ODOO_DB', 'odoo')
        self.odoo_username = os.getenv('ODOO_USERNAME', 'admin')
        self.odoo_password = os.getenv('ODOO_PASSWORD', 'admin')
        self.odoo_api_key = os.getenv('ODOO_API_KEY')
        
        # Odoo client
        self.uid = None
        self.common = None
        self.models = None
        
        # Dry run mode
        # Fail-safe: dry-run is ON unless DRY_RUN is explicitly set to "false".
        # A missing var or a typo keeps Odoo writes simulated, never real.
        self.dry_run = os.getenv('DRY_RUN', 'true').strip().lower() != 'false'
        
        logger.info(f"💼 MCP Odoo Server initialized (URL: {self.odoo_url}, Dry Run: {self.dry_run})")

        # Security matrix gate for payments (local agent enforces >threshold / new-payee approval)
        self.security = None
        if SecurityGuard is not None:
            try:
                self.security = SecurityGuard('local', str(self.vault_path))
            except Exception as e:
                logger.warning(f"⚠️ Could not initialize SecurityGuard: {e}; payments will require approval")

        # Try to authenticate
        if not self.dry_run:
            self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Odoo"""
        try:
            self.common = xmlrpc.client.ServerProxy(f'{self.odoo_url}/xmlrpc/2/common')
            self.models = xmlrpc.client.ServerProxy(f'{self.odoo_url}/xmlrpc/2/object')
            
            self.uid = self.common.authenticate(
                self.odoo_db, 
                self.odoo_username, 
                self.odoo_password,
                {}
            )
            
            if self.uid:
                logger.info(f"✅ Odoo authenticated as UID: {self.uid}")
            else:
                logger.error("❌ Odoo authentication failed")
                
        except Exception as e:
            logger.error(f"❌ Odoo connection error: {e}")
    
    def create_invoice(self, partner_id: int, amount: float, 
                       description: str = 'Service') -> Dict:
        """Create customer invoice"""
        try:
            logger.info(f"💰 Creating invoice for partner {partner_id}, amount: {amount}")
            
            if self.dry_run:
                logger.info(f"📝 [DRY RUN] Invoice would be created")
                
                # Save draft
                draft_file = self.vault_path / 'Drafts' / f'invoice_{partner_id}_{datetime.now().strftime("%Y%m%d")}.md'
                draft_file.parent.mkdir(exist_ok=True)
                draft_content = f"""---
type: invoice_draft
partner_id: {partner_id}
amount: {amount}
description: {description}
created: {datetime.now().isoformat()}
status: draft (dry run)
---

# Invoice Draft

**Partner ID:** {partner_id}
**Amount:** Rs. {amount}
**Description:** {description}

---

*Draft created (dry run mode)*
"""
                draft_file.write_text(draft_content, encoding='utf-8')
                
                return {
                    'success': True,
                    'message': 'Invoice draft created (dry run)',
                    'draft_file': str(draft_file)
                }
            
            # Actual invoice creation
            invoice_data = {
                'move_type': 'out_invoice',
                'partner_id': partner_id,
                'invoice_line_ids': [(0, 0, {
                    'name': description,
                    'quantity': 1,
                    'price_unit': amount,
                })]
            }
            
            invoice_id = self.models.execute_kw(
                self.odoo_db, self.uid, self.odoo_password,
                'account.move', 'create', [invoice_data]
            )
            
            logger.info(f"✅ Invoice created: {invoice_id}")
            
            return {
                'success': True,
                'invoice_id': invoice_id,
                'message': f'Invoice {invoice_id} created'
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to create invoice: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def get_leads(self, limit: int = 10) -> Dict:
        """Get CRM leads"""
        try:
            logger.info(f"Getting leads (limit: {limit})")
            
            if not self.uid:
                return {
                    'success': False,
                    'message': 'Not authenticated to Odoo. Check ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD',
                    'leads': []
                }
            
            if self.dry_run:
                logger.info("DRY RUN: Would fetch leads from Odoo CRM")
                return {
                    'success': True,
                    'message': 'Dry run - no leads fetched',
                    'leads': [],
                    'count': 0
                }
            
            # Actual Odoo query
            leads = self.models.execute_kw(
                self.odoo_db, self.uid, self.odoo_password,
                'crm.lead', 'search_read',
                [[]],
                {'limit': limit, 'fields': ['name', 'partner_name', 'email_from', 'phone', 'priority', 'stage_id']}
            )
            
            logger.info(f"✅ Retrieved {len(leads)} leads")
            
            return {
                'success': True,
                'leads': leads,
                'count': len(leads)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get leads: {e}")
            return {
                'success': False,
                'message': str(e),
                'leads': []
            }
    
    def update_lead(self, lead_id: int, values: Dict) -> Dict:
        """Update CRM lead"""
        try:
            logger.info(f"✏️ Updating lead {lead_id}")
            
            if self.dry_run:
                logger.info(f"📝 [DRY RUN] Lead {lead_id} would be updated with: {values}")
                return {
                    'success': True,
                    'message': f'Lead {lead_id} would be updated (dry run)',
                    'lead_id': lead_id,
                    'values': values
                }
            
            # Actual update
            result = self.models.execute_kw(
                self.odoo_db, self.uid, self.odoo_password,
                'crm.lead', 'write', [lead_id, values]
            )
            
            logger.info(f"✅ Lead {lead_id} updated")
            
            return {
                'success': True,
                'message': f'Lead {lead_id} updated',
                'lead_id': lead_id
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to update lead: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def _payee_has_history(self, partner_id) -> bool:
        """Best-effort 'known payee' check.

        True only if the partner already has a posted payment in Odoo. Without
        a partner_id, without a live connection, or in dry-run, returns False
        so an unknown payee fails safe (new payee => approval required).
        """
        if not partner_id or self.dry_run or not self.uid:
            return False
        try:
            count = self.models.execute_kw(
                self.odoo_db, self.uid, self.odoo_password,
                'account.payment', 'search_count',
                [[['partner_id', '=', int(partner_id)], ['state', '=', 'posted']]]
            )
            return bool(count and count > 0)
        except Exception as e:
            logger.warning(f"⚠️ Could not check payee history: {e}; treating as new payee")
            return False

    def record_payment(self, invoice_id: int, amount: float,
                       payment_date: str = None, partner_id: Optional[int] = None,
                       payee_known: Optional[bool] = None, approved: bool = False,
                       ref: str = '') -> Dict:
        """Register a customer payment against an invoice via the
        account.payment.register wizard, gated by the security matrix.

        Gate: a payment > PAYMENT_APPROVAL_THRESHOLD (default $100) OR to a
        new/unknown payee maps to 'large_payment' (HUMAN_APPROVAL) and is
        refused unless approved=True. Ordinary payments to a known payee map to
        'odoo_payment' (LOCAL_EXECUTE) and proceed. The gate runs BEFORE the
        dry-run branch so it is enforced in every mode.
        """
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            return {'success': False, 'message': f'Invalid amount: {amount!r}'}

        logger.info(f"💰 Recording payment for invoice {invoice_id}, amount: {amount}")

        # --- Resolve payee_known (best-effort) if the caller didn't assert it ---
        if payee_known is None:
            payee_known = self._payee_has_history(partner_id)

        # --- Security gate (matrix): >threshold OR new payee => human approval ---
        if self.security is not None:
            decision = self.security.evaluate_payment(amount, payee_known, approved=approved)
        else:
            # Fail-safe: no guard available => treat as needing approval.
            decision = {
                'action_type': 'large_payment', 'amount': amount, 'threshold': None,
                'payee_known': bool(payee_known), 'reasons': ['security guard unavailable'],
                'requires_approval': True, 'approved': bool(approved),
                'allowed': bool(approved),
            }

        if decision['requires_approval'] and not approved:
            logger.warning(f"🔒 [BLOCKED] Payment requires human approval: {decision['reasons']}")
            log_mcp_action(
                'odoo', 'record_payment',
                {'invoice_id': invoice_id, 'amount': amount, 'partner_id': partner_id,
                 'payee_known': bool(payee_known), 'reasons': decision['reasons']},
                'requires_approval'
            )
            return {
                'success': False,
                'requires_approval': True,
                'reasons': decision['reasons'],
                'message': ('Payment of %.2f requires human approval: %s'
                            % (amount, ', '.join(decision['reasons']))),
                'invoice_id': invoice_id,
                'amount': amount,
            }

        # --- Dry run: gate passed, but no real write ---
        if self.dry_run:
            logger.info("📝 [DRY RUN] Payment would be registered (gate passed, no real Odoo write)")
            log_file = self.logs_folder / 'payments.log'
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"{datetime.now().isoformat()} - [DRY RUN] Invoice {invoice_id}, "
                        f"Amount {amount}, approved={approved}, payee_known={payee_known}\n")
            log_mcp_action(
                'odoo', 'record_payment',
                {'invoice_id': invoice_id, 'amount': amount, 'dry_run': True,
                 'approved': approved, 'payee_known': bool(payee_known)},
                'success'
            )
            return {
                'success': True,
                'dry_run': True,
                'message': 'Payment simulated (dry run) - approval gate passed',
                'invoice_id': invoice_id,
                'amount': amount,
                'approved': approved,
            }

        # --- REAL payment via account.payment.register wizard ---
        if not self.uid:
            self._authenticate()
        if not self.uid:
            return {'success': False, 'message': 'Not authenticated to Odoo'}

        try:
            payment_date = payment_date or datetime.now().strftime('%Y-%m-%d')
            payment_ctx = {
                'active_model': 'account.move',
                'active_ids': [invoice_id],
                'active_id': invoice_id,
            }
            wizard_data = {
                'amount': amount,
                'payment_date': payment_date,
                'communication': ref or f'AI Employee payment {datetime.now():%Y%m%d}',
                'payment_type': 'inbound',
                'partner_type': 'customer',
                'journal_id': int(os.getenv('ODOO_PAYMENT_JOURNAL_ID', '1')),
            }
            wizard_id = self.models.execute_kw(
                self.odoo_db, self.uid, self.odoo_password,
                'account.payment.register', 'create', [wizard_data],
                {'context': payment_ctx}
            )
            result = self.models.execute_kw(
                self.odoo_db, self.uid, self.odoo_password,
                'account.payment.register', 'action_create_payments',
                [[wizard_id]], {'context': payment_ctx}
            )
            logger.info(f"✅ REAL PAYMENT registered for invoice {invoice_id}: {amount}")
            log_mcp_action(
                'odoo', 'record_payment',
                {'invoice_id': invoice_id, 'amount': amount, 'wizard_id': wizard_id},
                'success', result={'wizard_id': wizard_id}
            )
            return {
                'success': True,
                'message': f'Payment of {amount} registered for invoice {invoice_id}',
                'invoice_id': invoice_id,
                'amount': amount,
                'wizard_id': wizard_id,
                'result': result,
            }

        except Exception as e:
            logger.error(f"❌ Failed to register payment: {e}")
            log_mcp_action(
                'odoo', 'record_payment',
                {'invoice_id': invoice_id, 'amount': amount},
                'failed', error=str(e)
            )
            return {
                'success': False,
                'message': str(e)
            }


# CLI Interface
if __name__ == '__main__':
    if _MCP_MODE:
        # ---- Real MCP protocol server over stdio (Silver #5 / Gold #3, #6) ----
        # Speaks JSON-RPC over stdin/stdout via the official `mcp` SDK. The
        # MCPOdooServer logic class (incl. the security-gated record_payment) is
        # reused unchanged; mcp_server_base wraps each method as a tool.
        from mcp_server_base import ToolSpec, run_mcp_server

        server = MCPOdooServer()

        tools = [
            ToolSpec(
                name='create_invoice',
                description='Create a customer invoice in Odoo for a partner and amount.',
                input_schema={
                    'type': 'object',
                    'properties': {
                        'partner_id': {'type': 'integer'},
                        'amount': {'type': 'number'},
                        'description': {'type': 'string', 'default': 'Service'},
                    },
                    'required': ['partner_id', 'amount'],
                },
                handler=lambda a: server.create_invoice(
                    int(a['partner_id']), float(a['amount']),
                    description=a.get('description', 'Service'),
                ),
            ),
            ToolSpec(
                name='get_leads',
                description='Fetch recent CRM leads from Odoo (read-only).',
                input_schema={
                    'type': 'object',
                    'properties': {'limit': {'type': 'integer', 'default': 10}},
                },
                handler=lambda a: server.get_leads(limit=int(a.get('limit', 10))),
            ),
            ToolSpec(
                name='update_lead',
                description='Update fields on an Odoo CRM lead by id.',
                input_schema={
                    'type': 'object',
                    'properties': {
                        'lead_id': {'type': 'integer'},
                        'values': {'type': 'object', 'description': 'Field/value map to write'},
                    },
                    'required': ['lead_id', 'values'],
                },
                handler=lambda a: server.update_lead(int(a['lead_id']), dict(a.get('values') or {})),
            ),
            ToolSpec(
                name='record_payment',
                description=('Register a payment against an invoice. Security-gated: a '
                             'payment over PAYMENT_APPROVAL_THRESHOLD (default $100) OR to '
                             'a new/unknown payee is refused unless approved=true. Honors '
                             'DRY_RUN.'),
                input_schema={
                    'type': 'object',
                    'properties': {
                        'invoice_id': {'type': 'integer'},
                        'amount': {'type': 'number'},
                        'payment_date': {'type': 'string', 'description': 'YYYY-MM-DD; defaults to today'},
                        'partner_id': {'type': 'integer'},
                        'payee_known': {'type': 'boolean', 'description': 'Assert payee is known/trusted'},
                        'approved': {'type': 'boolean', 'default': False},
                        'ref': {'type': 'string', 'default': ''},
                    },
                    'required': ['invoice_id', 'amount'],
                },
                handler=lambda a: server.record_payment(
                    int(a['invoice_id']), float(a['amount']),
                    payment_date=a.get('payment_date'),
                    partner_id=(int(a['partner_id']) if a.get('partner_id') is not None else None),
                    payee_known=a.get('payee_known'),
                    approved=bool(a.get('approved', False)),
                    ref=a.get('ref', ''),
                ),
            ),
        ]

        run_mcp_server('ai-employee-odoo', tools)
    else:
        import argparse

        parser = argparse.ArgumentParser(description='MCP Odoo Server')
        parser.add_argument('--action', choices=['create_invoice', 'get_leads', 'update_lead', 'record_payment'], required=True)
        parser.add_argument('--partner-id', type=int, help='Partner ID')
        parser.add_argument('--amount', type=float, help='Amount')
        parser.add_argument('--lead-id', type=int, help='Lead ID')
        parser.add_argument('--invoice-id', type=int, help='Invoice ID')
        parser.add_argument('--approved', action='store_true',
                            help='Mark a flagged payment as human-approved (bypasses the approval gate)')
        parser.add_argument('--payee-known', action='store_true',
                            help='Assert the payee is known/trusted (skips new-payee detection)')
        parser.add_argument('--vault', help='Vault path')

        args = parser.parse_args()

        server = MCPOdooServer(Path(args.vault) if args.vault else None)

        if args.action == 'create_invoice' and args.partner_id and args.amount:
            result = server.create_invoice(args.partner_id, args.amount)
        elif args.action == 'get_leads':
            result = server.get_leads()
        elif args.action == 'update_lead' and args.lead_id:
            result = server.update_lead(args.lead_id, {'priority': '4'})
        elif args.action == 'record_payment' and args.invoice_id and args.amount:
            result = server.record_payment(
                args.invoice_id, args.amount,
                partner_id=args.partner_id,
                payee_known=(True if args.payee_known else None),
                approved=args.approved,
            )
        else:
            parser.print_help()
            sys.exit(1)

        print(json.dumps(result, indent=2))
