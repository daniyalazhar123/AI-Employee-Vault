#!/usr/bin/env python3
"""
GMAIL OAUTH AUTHENTICATION
Generates token.json for Gmail API access

This script:
1. Opens browser for Google login
2. Gets authorization code
3. Saves token.json for MCP Email Server

Safe - credentials stored locally, never shared.
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
print("🔐 GMAIL OAUTH AUTHENTICATION")
print("="*80)
print()

# Check credentials
if not CREDENTIALS_FILE.exists():
    print(f"❌ Credentials file not found: {CREDENTIALS_FILE}")
    print("Please run setup first.")
    sys.exit(1)

with open(CREDENTIALS_FILE) as f:
    creds_data = json.load(f)

client_id = creds_data['installed']['client_id']
print(f"✅ Client ID: {client_id[:50]}...")
print()

# Check if Google libraries are installed
try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    GOOGLE_LIBS_AVAILABLE = True
except ImportError:
    GOOGLE_LIBS_AVAILABLE = False
    print("⚠️  Google OAuth libraries not installed.")
    print()
    print("Install them with:")
    print("  pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    print()
    response = input("Install now? (y/n): ")
    if response.lower() == 'y':
        import subprocess
        subprocess.run([sys.executable, '-m', 'pip', 'install', 
                       'google-auth-oauthlib', 'google-auth-httplib2', 'google-api-python-client'])
        # Try importing again
        try:
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            GOOGLE_LIBS_AVAILABLE = True
        except:
            print("❌ Installation failed. Please install manually.")
            sys.exit(1)
    else:
        sys.exit(0)

# Scopes needed for Gmail
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]

print("📋 Required permissions:")
print("   - Send emails")
print("   - Compose drafts")
print("   - Read emails")
print("   - Modify emails")
print()

# Check if token already exists
if TOKEN_FILE.exists():
    print(f"⚠️  Token already exists: {TOKEN_FILE}")
    print("This will overwrite it.")
    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print("Aborted.")
        sys.exit(0)
    print()

print("="*80)
print("🌐 STEP 1: Browser will open for Google login")
print("="*80)
print()
print("After login:")
print("  1. Google will show permissions screen")
print("  2. Click 'Allow' or 'Continue'")
print("  3. Browser will redirect to localhost (may show error - that's OK)")
print("  4. Token will be saved automatically")
print()

response = input("Ready to authenticate? (y/n): ")
if response.lower() != 'y':
    print("Aborted.")
    sys.exit(0)

print()
print("🔑 Authenticating with Google...")
print()

try:
    # Start OAuth flow
    flow = InstalledAppFlow.from_client_secrets_file(
        str(CREDENTIALS_FILE),
        SCOPES,
        redirect_uri='http://localhost:8080/'
    )

    # This opens browser
    creds = flow.run_local_server(
        port=8080,
        open_browser=True,
        authorization_prompt_message="Opening browser... Please wait.\n"
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
    print()
    print(f"Token saved to: {TOKEN_FILE}")
    print()
    print("Next steps:")
    print("  1. Set DRY_RUN=false in .env.local (when ready for real sends)")
    print("  2. Email MCP will use Gmail API automatically")
    print("  3. Run: python check_execution_status.py to verify")
    print()

except Exception as e:
    print()
    print("="*80)
    print("❌ AUTHENTICATION FAILED")
    print("="*80)
    print()
    print(f"Error: {e}")
    print()
    print("Troubleshooting:")
    print("  1. Make sure Google account is logged in")
    print("  2. Check if pop-up blocker is enabled")
    print("  3. Try running in incognito window")
    print("  4. Ensure credentials.json is correct")
    print()
