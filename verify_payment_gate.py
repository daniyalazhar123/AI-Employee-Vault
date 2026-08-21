#!/usr/bin/env python3
"""
Verification harness for the payment approval gate (Safety Gap #1).

Proves that MCPOdooServer.record_payment() enforces security_guard's matrix on
the ACTUAL payment path:

  A. small ($50) + known payee            -> auto-allowed  (dry-run simulated)
  B. large ($5000) + known payee          -> BLOCKED       (requires_approval)
  C. small ($50) + NEW/unknown payee      -> BLOCKED       (requires_approval)
  D. large ($5000) + known payee + APPROVED-> allowed      (human override)

It drives the real record_payment() method (not evaluate_payment in isolation),
so it proves the gate is wired into the payment path, and it reads the real
on-disk proof rows written to:
  - Logs/Audit/audit_YYYYMMDD.jsonl     (mcp_odoo_record_payment via log_mcp_action)
  - Logs/Audit/security_YYYYMMDD.jsonl  (payment_gate via SecurityGuard._audit_action)

SAFETY:
  - Forces DRY_RUN=true before import AND asserts server.dry_run is True, so no
    real Odoo write / authentication ever happens. No live payment is executed.
  - Only side effect is appended log lines (Logs/ is gitignored, regenerable).

Run:  python verify_payment_gate.py
Exit: 0 = PASS (all four cases behaved correctly), 1 = FAIL, 2 = could not run.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# --- Safety: dry-run ON before anything imports/reads it ---
os.environ['DRY_RUN'] = 'true'
# Pin threshold so the test is deterministic regardless of local .env.
os.environ['PAYMENT_APPROVAL_THRESHOLD'] = '100'

VAULT = Path(__file__).parent.resolve()
sys.path.insert(0, str(VAULT))

AUDIT_DIR = VAULT / 'Logs' / 'Audit'
TODAY = datetime.now().strftime('%Y%m%d')
AUDIT_FILE = AUDIT_DIR / f'audit_{TODAY}.jsonl'
SEC_FILE = AUDIT_DIR / f'security_{TODAY}.jsonl'


def read_jsonl(path: Path):
    if not path.exists():
        return []
    out = []
    for ln in path.read_text(encoding='utf-8').splitlines():
        ln = ln.strip()
        if not ln:
            continue
        try:
            out.append(json.loads(ln))
        except json.JSONDecodeError:
            pass
    return out


def main():
    print('=' * 72)
    print('PAYMENT APPROVAL GATE VERIFICATION')
    print(f'vault      : {VAULT}')
    print(f'threshold  : $%s  (PAYMENT_APPROVAL_THRESHOLD)' % os.environ['PAYMENT_APPROVAL_THRESHOLD'])
    print(f'audit file : {AUDIT_FILE.name}')
    print(f'sec file   : {SEC_FILE.name}')
    print('=' * 72)

    audit_before = len(read_jsonl(AUDIT_FILE))
    sec_before = len(read_jsonl(SEC_FILE))

    from mcp_odoo import MCPOdooServer
    server = MCPOdooServer(VAULT)

    # ---- Hard safety guards ----
    if not server.dry_run:
        print('\n[ABORT] server.dry_run is False - refusing to run (would risk a real payment).')
        return 2
    if server.security is None:
        print('\n[ABORT] server.security is None - SecurityGuard failed to init; gate cannot work.')
        return 2
    print('[ok] server.dry_run =', server.dry_run, '| server.security =', type(server.security).__name__)

    INV = 999  # fake invoice id; never written in dry-run

    print('\n' + '-' * 72)
    cases = []

    # A: small, known payee -> allowed
    a = server.record_payment(INV, 50.0, partner_id=1, payee_known=True, approved=False)
    print('[A] $50   known payee            ->',
          'success=%s requires_approval=%s' % (a.get('success'), a.get('requires_approval')))
    cases.append(('A allowed (small+known)',
                  a.get('success') is True and a.get('dry_run') is True
                  and not a.get('requires_approval')))

    # B: large, known payee -> blocked
    b = server.record_payment(INV, 5000.0, partner_id=1, payee_known=True, approved=False)
    print('[B] $5000 known payee            ->',
          'success=%s requires_approval=%s reasons=%s'
          % (b.get('success'), b.get('requires_approval'), b.get('reasons')))
    cases.append(('B blocked (large+known)',
                  b.get('success') is False and b.get('requires_approval') is True
                  and any('threshold' in r for r in b.get('reasons', []))))

    # C: small, NEW payee -> blocked
    c = server.record_payment(INV, 50.0, partner_id=2, payee_known=False, approved=False)
    print('[C] $50   NEW/unknown payee      ->',
          'success=%s requires_approval=%s reasons=%s'
          % (c.get('success'), c.get('requires_approval'), c.get('reasons')))
    cases.append(('C blocked (small+new payee)',
                  c.get('success') is False and c.get('requires_approval') is True
                  and any('payee' in r for r in c.get('reasons', []))))

    # D: large, known payee, HUMAN APPROVED -> allowed (override)
    d = server.record_payment(INV, 5000.0, partner_id=1, payee_known=True, approved=True)
    print('[D] $5000 known payee + APPROVED ->',
          'success=%s requires_approval=%s' % (d.get('success'), d.get('requires_approval')))
    cases.append(('D allowed (large but approved)',
                  d.get('success') is True and d.get('dry_run') is True
                  and not d.get('requires_approval')))

    # ---- Real on-disk proof rows ----
    audit_new = read_jsonl(AUDIT_FILE)[audit_before:]
    sec_new = read_jsonl(SEC_FILE)[sec_before:]

    print('\n' + '=' * 72)
    print('PROOF — new rows in %s (actor=mcp, target=odoo):' % AUDIT_FILE.name)
    print('-' * 72)
    for e in audit_new:
        if e.get('action_type') == 'mcp_odoo_record_payment':
            print(json.dumps({k: e.get(k) for k in
                              ('action_type', 'actor', 'status', 'target', 'parameters')},
                             ensure_ascii=False))

    print('\nPROOF — new rows in %s (payment_gate decisions):' % SEC_FILE.name)
    print('-' * 72)
    for e in sec_new:
        if e.get('action_type') == 'payment_gate':
            print(json.dumps({k: e.get(k) for k in
                              ('action_type', 'success', 'details')}, ensure_ascii=False))
    print('=' * 72)

    # ---- Verdict ----
    print('\nCASE RESULTS:')
    all_ok = True
    for name, ok in cases:
        print(f'  {"PASS" if ok else "FAIL"}  {name}')
        all_ok = all_ok and ok

    # Also require that the gate actually wrote proof rows.
    blocked_rows = [e for e in audit_new
                    if e.get('action_type') == 'mcp_odoo_record_payment'
                    and e.get('status') == 'requires_approval']
    allowed_rows = [e for e in audit_new
                    if e.get('action_type') == 'mcp_odoo_record_payment'
                    and e.get('status') == 'success']
    gate_rows = [e for e in sec_new if e.get('action_type') == 'payment_gate']
    print(f'\n  proof: {len(blocked_rows)} blocked + {len(allowed_rows)} allowed audit rows, '
          f'{len(gate_rows)} payment_gate rows')
    proof_ok = len(blocked_rows) >= 2 and len(allowed_rows) >= 2 and len(gate_rows) >= 4
    print(f'  {"PASS" if proof_ok else "FAIL"}  proof rows present on disk')
    all_ok = all_ok and proof_ok

    print('\nRESULT:', 'PASS - payment gate enforced on the real record_payment path'
          if all_ok else 'FAIL - gate did not behave as specified')
    return 0 if all_ok else 1


if __name__ == '__main__':
    sys.exit(main())
