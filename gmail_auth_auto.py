#!/usr/bin/env python3
"""
GMAIL OAUTH - NON-INTERACTIVE (automatic)
Opens browser, saves token.json, no prompts
"""

import os
import sys
import json
from pathlib import Path

VAULT = Path(__file__).parent
sys.path.insert(0, str(VAULT))
from secrets_config import SECRETS_DIR, get_secret_path
CREDENTIALS_FILE = get_secret_path('credentials.json')
TOKEN_FILE = get_secret_path('token.json')

print("="*70)
print("🔐 GMAIL OAUTH - AUTOMATIC (no prompts)")
print("="*70)
print()

# Check credentials
if not CREDENTIALS_FILE.exists():
    print(f"❌ Credentials file NOT found: {CREDENTIALS_FILE}")
    sys.exit(1)

with open(CREDENTIALS_FILE) as f:
    creds_data = json.load(f)

client_id = creds_data['installed']['client_id'][:50]
print(f"✅ Credentials loaded: {client_id}...")
print()

# Import Google libraries
try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.oauth2.credentials import Credentials
except ImportError:
    print("❌ Google libraries not installed")
    print("Run: pip install google-auth-oauthlib google-api-python-client")
    sys.exit(1)

SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.readonly'
]

print("🌐 Opening browser for Gmail login...")
print("   → Login with your Gmail account")
print("   → Click 'Allow' when asked for permissions")
print("   → Token will save automatically")
print()

try:
    flow = InstalledAppFlow.from_client_secrets_file(
        str(CREDENTIALS_FILE),
        SCOPES,
        redirect_uri='http://localhost:8080/'
    )

    creds = flow.run_local_server(
        port=8080,
        open_browser=True,
        authorization_prompt_message="Browser opened. Please authorize in your browser...\n"
    )

    # Save token
    token_data = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes,
        'expiry': creds.expiry.isoformat() if creds.expiry else None
    }

    with open(TOKEN_FILE, 'w') as f:
        json.dump(token_data, f, indent=2)

    print()
    print("="*70)
    print("✅ SUCCESS! Token saved to:")
    print(f"   {TOKEN_FILE}")
    print("="*70)

except KeyboardInterrupt:
    print("\n❌ Cancelled by user")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ OAuth failed: {e}")
    print("\nALTERNATIVE: Use SMTP mode instead:")
    print("  1. Go to: https://myaccount.google.com/apppasswords")
    print("  2. Create App Password for 'Mail'")
    print("  3. Add to .env.local:")
    print("     EMAIL_USER=your-email@gmail.com")
    print("     EMAIL_PASSWORD=your-16-char-password")
    sys.exit(1)
