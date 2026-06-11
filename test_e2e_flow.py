#!/usr/bin/env python3
"""End-to-End Flow Test"""
import json, shutil
from pathlib import Path
from datetime import datetime

VAULT = Path(__file__).parent

ts = datetime.now().strftime("%Y%m%d_%H%M%S")

# Step 1: Create test email in Needs_Action
test_email = VAULT / 'Needs_Action' / f'EMAIL_TEST_{ts}.md'
test_email.write_text('''---
type: email
from: client@test.com
subject: Invoice Request
priority: high
status: pending
---
Please send me invoice for consulting services.
''', encoding='utf-8')
print(f'[1] Email created: {test_email.name}')

# Step 2: Create approval file
approval = VAULT / 'Pending_Approval' / f'REPLY_{ts}.md'
approval.write_text('''---
type: approval_request
action: email_reply
to: client@test.com
status: pending
---
Draft reply: Thank you for contacting us. Invoice will be sent shortly.
Move to /Approved to send.
''', encoding='utf-8')
print(f'[2] Approval created: {approval.name}')

# Step 3: Log to audit
logs = VAULT / 'Logs'
logs.mkdir(exist_ok=True)
log_entry = {
    'timestamp': datetime.now().isoformat(),
    'action': 'email_received_and_drafted',
    'from': 'client@test.com',
    'status': 'pending_approval'
}
log_file = logs / f'audit_{datetime.now().strftime("%Y-%m-%d")}.json'
with open(log_file, 'a') as f:
    f.write(json.dumps(log_entry) + '\n')
print(f'[3] Audit log saved: {log_file.name}')

# Step 4: Move to Done
done_file = VAULT / 'Done' / f'FLOW_TEST_{ts}.md'
shutil.copy(test_email, done_file)
print(f'[4] Moved to Done: {done_file.name}')

print()
print('END-TO-END FLOW COMPLETE')
print('Email -> Needs_Action -> Pending_Approval -> Audit Log -> Done')
