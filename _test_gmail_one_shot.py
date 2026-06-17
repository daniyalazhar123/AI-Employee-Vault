#!/usr/bin/env python3
"""
One-shot Gmail Watcher Test Script
Imports GmailWatcher, authenticates, fetches unread emails,
processes each one, and prints EVERYTHING.
If no unread emails found, sends a test email first then re-checks.
"""

import sys
import os
import time
import base64
import pickle
from datetime import datetime
from pathlib import Path
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# ── Add vault path to sys.path so imports resolve ──
VAULT_PATH = Path(r"D:\Desktop4\Obsidian Vault")
sys.path.insert(0, str(VAULT_PATH))
sys.path.insert(0, str(VAULT_PATH / 'watchers'))

# ── Ensure DRY_RUN is false ──
os.environ['DRY_RUN'] = 'false'
os.environ['REQUIRE_APPROVAL'] = 'true'
os.environ['SECRETS_DIR'] = str(Path.home() / '.ai_employee' / 'secrets')

# ── Import the real GmailWatcher ──
from watchers.gmail_watcher import GmailWatcher


def send_test_email(gmail_service):
    """Send a test email to self via the Gmail API."""
    profile = gmail_service.users().getProfile(userId='me').execute()
    email_addr = profile.get('emailAddress', 'unknown')

    print(f"\n{'=' * 70}")
    print(f"  SENDING TEST EMAIL TO: {email_addr}")
    print(f"{'=' * 70}")

    subject = f"AI Employee Gmail Watcher Test - {datetime.now().strftime('%H:%M:%S')}"
    body = (
        f"This is an automated test email from the AI Employee Gmail Watcher.\n\n"
        f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Purpose: Verify email processing pipeline.\n\n"
        f"If you receive this, the pipeline is working correctly."
    )

    message = MIMEText(body, 'plain', 'utf-8')
    message['To'] = email_addr
    message['From'] = email_addr
    message['Subject'] = subject

    raw_bytes = base64.urlsafe_b64encode(message.as_bytes())
    raw_str = raw_bytes.decode('utf-8')

    sent = gmail_service.users().messages().send(
        userId='me',
        body={'raw': raw_str}
    ).execute()

    print(f"  \u2705 Test email sent!")
    print(f"     ID:      {sent['id']}")
    print(f"     Subject: {subject}")
    print(f"     To:      {email_addr}")
    print(f"{'=' * 70}\n")
    return sent['id']


# ═══════════════════════════════════════════════════════
#  MAIN TEST
# ═══════════════════════════════════════════════════════

print(f"\n{'=' * 70}")
print(f"  GMAIL WATCHER — ONE-SHOT TEST")
print(f"  Started:  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"  Vault:    {VAULT_PATH}")
print(f"  DRY_RUN:  {os.environ.get('DRY_RUN', 'NOT SET')}")
print(f"  Sys.path: {VAULT_PATH}")
print(f"{'=' * 70}\n")

# ── Create watcher instance ──
watcher = GmailWatcher(vault_path=VAULT_PATH)

# ── STEP 1: Authenticate ──
print(f"{'─' * 70}")
print(f"  [STEP 1] AUTHENTICATE")
print(f"{'─' * 70}")
auth_ok = watcher.authenticate()
if not auth_ok:
    print("  \u274c AUTHENTICATION FAILED — cannot continue")
    sys.exit(1)
print(f"  \u2705 Authenticated successfully\n")

# ── STEP 2: Fetch unread emails ──
print(f"{'─' * 70}")
print(f"  [STEP 2] FETCH UNREAD EMAILS")
print(f"{'─' * 70}")
new_emails = watcher.fetch_unread_emails()

if not new_emails:
    print(f"\n  \u26a0\ufe0f  No new unread emails found.")
    print(f"  \u2709\ufe0f  Sending a test email, then re-checking...\n")

    send_test_email(watcher.gmail_service)

    print("  \u23f3  Waiting 18 seconds for delivery...")
    time.sleep(18)

    print(f"\n  \U0001f504  Re-checking for unread emails...")
    new_emails = watcher.fetch_unread_emails()

    if not new_emails:
        print(f"  \u274c  Still no emails after sending test. Aborting.")
        sys.exit(1)

print(f"\n  \u2705 Found {len(new_emails)} new unread email(s)\n")

# ── STEP 3 & 4: Process each email ──
for i, msg in enumerate(new_emails, 1):
    email_id = msg['id']

    print(f"{'=' * 70}")
    print(f"  EMAIL #{i}")
    print(f"  Message ID: {email_id}")
    print(f"{'=' * 70}")

    # ── Get details ──
    print(f"\n{'─' * 70}")
    print(f"  [STEP 3] GET EMAIL DETAILS")
    print(f"{'─' * 70}")

    email_data = watcher.get_email_details(email_id)

    if not email_data:
        print(f"  \u274c Failed to get details for {email_id}\n")
        continue

    print(f"\n  \U0001f4e8  REAL EMAIL DATA:")
    print(f"     From:    {email_data['from']}")
    print(f"     Subject: {email_data['subject']}")
    print(f"     Date:    {email_data['date']}")
    print(f"     To:      {email_data['to']}")
    print(f"     Snippet: {email_data['snippet']}")
    print(f"     Gmail:   https://mail.google.com/mail/u/0/#inbox/{email_id}")

    # ── Create action file ──
    print(f"\n{'─' * 70}")
    print(f"  [STEP 4] CREATE ACTION FILE")
    print(f"{'─' * 70}")

    action_file = watcher.create_action_file(email_data)

    if action_file:
        print(f"\n  \u2705 Action file created:")
        print(f"     Path:   {action_file}")
        print(f"     Folder: {action_file.parent}")
        print(f"     Name:   {action_file.name}")
        print(f"\n  \U0001f4c4  File contents:")
        print(f"  {'─' * 56}")
        content = action_file.read_text(encoding='utf-8')
        for line in content.splitlines():
            print(f"     {line}")
        print(f"  {'─' * 56}")
    else:
        print(f"  \u274c Failed to create action file!")

    print()

# ── Done ──
print(f"{'=' * 70}")
print(f"  TEST COMPLETE")
print(f"  Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"  Processed: {len(new_emails)} email(s)")
print(f"{'=' * 70}")
