#!/usr/bin/env python3
"""
GMAIL OAUTH - AUTOMATED (no prompts)
Generates token.json for Gmail API access
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

print("="*80)
print("🔐 GMAIL OAUTH AUTHENTICATION - AUTOMATED")
print("="*80)
print()

# Import Google libraries
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]

print("📋 Opening browser for Google login...")
print("   Please click 'Allow' when prompted.")
print()

try:
    # Start OAuth flow (auto-opens browser)
    flow = InstalledAppFlow.from_client_secrets_file(
        str(CREDENTIALS_FILE),
        SCOPES,
        redirect_uri='http://localhost:8080/'
    )

    print("🌐 Browser opening...")
    creds = flow.run_local_server(
        port=8080,
        open_browser=True,
        authorization_prompt_message="Browser opened. Please authorize in browser...\n"
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
    print("="*80)
    print("✅ GMAIL AUTHENTICATION SUCCESSFUL!")
    print("="*80)
    print(f"\nToken saved to: {TOKEN_FILE}")
    print("\nGmail API is now ready for REAL SENDS.")

except Exception as e:
    print(f"\n❌ AUTHENTICATION FAILED: {e}")
    sys.exit(1)
