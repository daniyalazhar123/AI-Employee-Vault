#!/usr/bin/env python3
"""
GMAIL OAUTH AUTHENTICATION
Generates token.json for Gmail API access

Supports:
  --noauth_local_webserver : OOB flow (print URL, user pastes code)
  --yes                    : Auto-answer yes to prompts
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
USE_OOB = '--noauth_local_webserver' in sys.argv
AUTO_YES = '--yes' in sys.argv

os.environ['PYTHONIOENCODING'] = 'utf-8'

_prompt_idx = 0
def prompt(msg):
    global _prompt_idx
    _prompt_idx += 1
    if AUTO_YES and _prompt_idx <= 3 and 'code' not in msg.lower():
        print(msg + " [auto-yes]")
        return 'y'
    return input(msg)

print("=" * 80)
print("GMAIL OAUTH AUTHENTICATION")
print("=" * 80)

if not CREDENTIALS_FILE.exists():
    print(f"ERROR: Credentials file not found: {CREDENTIALS_FILE}")
    sys.exit(1)

with open(CREDENTIALS_FILE) as f:
    creds_data = json.load(f)

client_id = creds_data['installed']['client_id']
print(f"Client ID: {client_id[:50]}...")

# Check Google libraries
try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
except ImportError:
    print("Google OAuth libraries not installed.")
    resp = prompt("Install now? (y/n): ")
    if resp.lower() == 'y':
        import subprocess
        subprocess.run([sys.executable, '-m', 'pip', 'install',
                        'google-auth-oauthlib', 'google-auth-httplib2', 'google-api-python-client'])
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
    else:
        sys.exit(0)

SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]

print("Scopes: send, compose, read, modify")

if TOKEN_FILE.exists():
    resp = prompt(f"Overwrite existing token? (y/n): ")
    if resp.lower() != 'y':
        print("Aborted.")
        sys.exit(0)

print()
print("=" * 80)
print("Starting OAuth flow...")
print("=" * 80)

try:
    flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)

    if USE_OOB:
        flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
        auth_url, _ = flow.authorization_url(prompt='consent')
        print()
        print("=" * 80)
        print("OPEN THIS URL IN YOUR BROWSER:")
        print("=" * 80)
        print(auth_url)
        print("=" * 80)
        print("After authorizing, Google shows a code.")
        code = prompt("Paste authorization code: ")
        flow.fetch_token(code=code.strip())
        creds = flow.credentials
    else:
        creds = flow.run_local_server(port=8080, open_browser=True)

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
    print("=" * 80)
    print("SUCCESS! Token saved to:")
    print(f"  {TOKEN_FILE}")
    print("=" * 80)

except Exception as e:
    print()
    print("=" * 80)
    print(f"ERROR: {e}")
    print("=" * 80)
    print()
    print("If 'deleted_client': recreate OAuth client in Google Cloud Console")
    print("If 'access_denied':   try again and click Allow")
    print("If 'redirect_uri':    use --noauth_local_webserver flag")
    sys.exit(1)
