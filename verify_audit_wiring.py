#!/usr/bin/env python3
"""
Verification harness for the comprehensive audit-logging wiring (Gold #9).

Proves that LocalAgent.execute_approved_item() feeds the comprehensive audit
trail at Logs/Audit/audit_YYYYMMDD.jsonl for BOTH:
  - a successful action  (status='success')
  - a failed action      (status='failed', with error)

SAFETY:
  - Forces DRY_RUN=true and, after building the agent, forces
    email_mcp.dry_run=True so NO real email can ever be sent.
  - Non-destructive: snapshots & restores Dashboard.md and
    Dead_Letter_Queue/errors.jsonl, and deletes the test approval /
    Done / DLQ / draft artifacts it creates.
  - Leaves ONLY the two audit rows it produced (clearly tagged with
    verify@example.com) so the proof is independently inspectable.

Run:  python verify_audit_wiring.py
Exit: 0 = PASS (both rows found), 1 = FAIL, 2 = could not run (MCP/audit missing)
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# --- Safety: dry-run ON before anything imports/reads it ---
os.environ['DRY_RUN'] = 'true'

VAULT = Path(__file__).parent.resolve()
sys.path.insert(0, str(VAULT))

AUDIT_DIR = VAULT / 'Logs' / 'Audit'
TODAY = datetime.now().strftime('%Y%m%d')
AUDIT_FILE = AUDIT_DIR / f'audit_{TODAY}.jsonl'

OK_NAME = 'APPROVAL_EMAIL_audit_verify_ok.md'
FAIL_NAME = 'APPROVAL_EMAIL_audit_verify_fail.md'


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
    print('AUDIT-LOGGING WIRING VERIFICATION')
    print(f'vault      : {VAULT}')
    print(f'audit file : {AUDIT_FILE}')
    print('=' * 72)

    # ---- Baseline snapshot of proof file ----
    before = read_jsonl(AUDIT_FILE)
    before_count = len(before)
    print(f'[baseline] existing audit rows today: {before_count}')

    # ---- Snapshot incidental side-effect files (to restore later) ----
    dashboard = VAULT / 'Dashboard.md'
    errors_jsonl = VAULT / 'Dead_Letter_Queue' / 'errors.jsonl'
    dashboard_before = dashboard.read_text(encoding='utf-8') if dashboard.exists() else None
    errors_before = errors_jsonl.read_text(encoding='utf-8') if errors_jsonl.exists() else None
    drafts_dir = VAULT / 'Drafts'
    drafts_before = set(drafts_dir.glob('email_*.md')) if drafts_dir.exists() else set()

    # ---- Build the agent ----
    from local_agent import LocalAgent
    agent = LocalAgent(str(VAULT))

    # ---- Hard safety guard: never a real send ----
    if agent.email_mcp is None:
        print('\n[ABORT] email_mcp is None (MCP servers not importable). Cannot prove success path.')
        return 2
    if not agent.email_mcp.dry_run:
        agent.email_mcp.dry_run = True
        print('[SAFETY] Forced email_mcp.dry_run=True for verification (secrets .env had it off).')
    assert agent.email_mcp.dry_run is True, 'dry_run guard failed'

    if agent.audit is None:
        print('\n[ABORT] agent.audit is None (AuditLogger failed to init). Wiring cannot work.')
        return 2
    print('[ok] agent.audit is a live AuditLogger; email_mcp.dry_run =', agent.email_mcp.dry_run)

    approved = VAULT / 'Approved'
    approved.mkdir(parents=True, exist_ok=True)

    # ---- Case 1: SUCCESS (valid recipient, dry-run email) ----
    ok_file = approved / OK_NAME
    ok_file.write_text(
        '---\n'
        'type: email\n'
        'to: verify@example.com\n'
        'subject: Audit Wiring Verification (dry run)\n'
        '---\n\n'
        'This is a dry-run verification body. No real email is sent.\n',
        encoding='utf-8',
    )
    print('\n[case 1] SUCCESS path -> execute_approved_item(', OK_NAME, ')')
    agent.execute_approved_item(ok_file)

    # ---- Case 2: FAILURE (no recipient -> raises -> failure audit) ----
    fail_file = approved / FAIL_NAME
    fail_file.write_text(
        '---\n'
        'type: email\n'
        'subject: Should Fail - No Recipient\n'
        '---\n\n'
        'No recipient field in this file, so recipient extraction must fail.\n',
        encoding='utf-8',
    )
    print('[case 2] FAILURE path -> execute_approved_item(', FAIL_NAME, ')')
    agent.execute_approved_item(fail_file)

    # ---- Read new audit rows ----
    after = read_jsonl(AUDIT_FILE)
    new = after[before_count:]

    print('\n' + '=' * 72)
    print(f'AUDIT DELTA: before={before_count}  after={len(after)}  new={len(new)}')
    print('-' * 72)
    for e in new:
        print(json.dumps(
            {k: e.get(k) for k in ('timestamp', 'action_type', 'actor', 'status', 'target', 'error')},
            ensure_ascii=False,
        ))
    print('=' * 72)

    # ---- Genuine assertions ----
    success_hit = [
        e for e in new
        if e.get('action_type') == 'email_send'
        and e.get('status') == 'success'
        and e.get('actor') == 'local_agent'
    ]
    fail_hit = [
        e for e in new
        if e.get('action_type') == 'email_send'
        and e.get('status') == 'failed'
        and e.get('actor') == 'local_agent'
        and e.get('error')
    ]
    print(f'success row present : {bool(success_hit)}')
    print(f'failed row present  : {bool(fail_hit)}  '
          + (f'(error="{fail_hit[0]["error"]}")' if fail_hit else ''))

    # ---- Cleanup incidental artifacts (keep the 2 proof rows) ----
    def _rm(p: Path):
        try:
            p.unlink()
        except OSError:
            pass

    _rm(VAULT / 'Done' / f'COMPLETED_{OK_NAME}')
    _rm(VAULT / 'Dead_Letter_Queue' / f'FAILED_{FAIL_NAME}')
    _rm(approved / OK_NAME)
    _rm(approved / FAIL_NAME)
    # delete the dry-run draft(s) created during this run
    if drafts_dir.exists():
        for p in set(drafts_dir.glob('email_*.md')) - drafts_before:
            _rm(p)
    # restore incidental appends
    if dashboard_before is not None:
        dashboard.write_text(dashboard_before, encoding='utf-8')
    if errors_before is not None:
        errors_jsonl.write_text(errors_before, encoding='utf-8')
    elif errors_jsonl.exists():
        _rm(errors_jsonl)
    print('[cleanup] removed test approval/Done/DLQ/draft files; restored Dashboard.md & errors.jsonl')
    print('[note] the 2 audit rows above remain in', AUDIT_FILE.name, 'as inspectable proof')

    ok = bool(success_hit) and bool(fail_hit)
    print('\nRESULT:', 'PASS - audit logging wired (success + failure both captured)'
          if ok else 'FAIL - wiring incomplete')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
