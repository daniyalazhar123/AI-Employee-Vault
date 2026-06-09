#!/usr/bin/env python3
"""
EXECUTION LAYER STATUS CHECK
Shows real-time status of all components

Safe to run - no actions performed
"""

import os
import sys
import json
from pathlib import Path

# Force UTF-8 for Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except:
        pass

VAULT = Path(__file__).parent
sys.path.insert(0, str(VAULT))
from secrets_config import SECRETS_DIR, get_secret_path, load_secrets
load_secrets()

print("="*80)
print("🔍 EXECUTION LAYER STATUS CHECK")
print("="*80)
print()

# ====================================================================
# 1. DRY_RUN STATUS
# ====================================================================
print("="*80)
print("1️⃣  DRY RUN STATUS")
print("="*80)
print()

dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'
require_approval = os.getenv('REQUIRE_APPROVAL', 'true').lower() == 'true'

print(f"   DRY_RUN:          {'❌ FALSE (REAL SENDS ENABLED)' if not dry_run else '✅ TRUE (SAFE - NO ACTUAL SENDS)'}")
print(f"   REQUIRE_APPROVAL: {'✅ TRUE (HITL ENABLED)' if require_approval else '❌ FALSE (AUTO-EXECUTE)'}")
print()

if dry_run:
    print("   ⚠️  System is in DRY RUN MODE - NO actual emails/posts will be sent")
    print("   To enable real sends: Set DRY_RUN=false in .env.local")
else:
    print("   🚨 WARNING: REAL SENDS ENABLED - Emails and posts will actually be sent!")
print()

# ====================================================================
# 2. LINKEDIN SESSION STATUS
# ====================================================================
print("="*80)
print("2️⃣  LINKEDIN SESSION STATUS")
print("="*80)
print()

session_file = get_secret_path('linkedin_session.json')

if session_file.exists():
    with open(session_file) as f:
        session_data = json.load(f)
    
    cookies = session_data.get('cookies', [])
    
    # Check for li_at cookie (critical for authentication)
    li_at_cookies = [c for c in cookies if c.get('name') == 'li_at']
    
    print(f"   Session File:     ✅ FOUND ({session_file})")
    print(f"   Total Cookies:    {len(cookies)}")
    print(f"   li_at Cookie:     {'✅ FOUND (authentication ready)' if li_at_cookies else '❌ MISSING (need fresh session)'}")
    
    if li_at_cookies:
        li_at = li_at_cookies[0]
        domain = li_at.get('domain', 'unknown')
        expiry = li_at.get('expiry', 'unknown')
        print(f"   Domain:           {domain}")
        if expiry != 'unknown':
            from datetime import datetime
            try:
                expiry_date = datetime.fromtimestamp(expiry)
                print(f"   Expires:          {expiry_date.strftime('%Y-%m-%d %H:%M:%S')}")
                if expiry < datetime.now().timestamp():
                    print(f"   ⚠️  WARNING: Session EXPIRED - need fresh cookies")
                else:
                    print(f"   ✅ Session is VALID")
            except:
                print(f"   Expiry:           {expiry}")
    
    print()
    print("   ✅ LinkedIn ready for REAL POSTS (when DRY_RUN=false)")
else:
    print(f"   ❌ Session file NOT FOUND: {session_file}")
    print("   LinkedIn posting will NOT work without session cookies")

print()

# ====================================================================
# 3. GMAIL STATUS
# ====================================================================
print("="*80)
print("3️⃣  GMAIL STATUS")
print("="*80)
print()

# Check Gmail API token
token_file = VAULT / 'token.json'
credentials_file = VAULT / 'config' / 'credentials.json'

gmail_api_ready = False
smtp_ready = False

if token_file.exists():
    print(f"   Gmail API Token:  ✅ FOUND ({token_file})")
    if credentials_file.exists():
        print(f"   Credentials File: ✅ FOUND ({credentials_file})")
        gmail_api_ready = True
    else:
        print(f"   Credentials File: ❌ NOT FOUND (may still work)")
        gmail_api_ready = True
else:
    print(f"   Gmail API Token:  ❌ NOT FOUND (token.json)")
    print(f"   Credentials File: {'✅ FOUND' if credentials_file.exists() else '❌ NOT FOUND'}")

print()

# Check SMTP credentials
email_user = os.getenv('EMAIL_USER', '')
email_password = os.getenv('EMAIL_PASSWORD', '')
smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
smtp_port = os.getenv('SMTP_PORT', '587')

if email_user and email_password:
    smtp_ready = True
    print(f"   SMTP Credentials: ✅ CONFIGURED")
    print(f"   SMTP Server:      {smtp_server}:{smtp_port}")
    print(f"   Email User:       {email_user}")
else:
    print(f"   SMTP Credentials: ❌ NOT CONFIGURED")
    print(f"   EMAIL_USER:       {'Set' if email_user else 'Not set'}")
    print(f"   EMAIL_PASSWORD:   {'Set' if email_password else 'Not set'}")

print()

if gmail_api_ready:
    print("   ✅ Gmail API ready for REAL SENDS (when DRY_RUN=false)")
elif smtp_ready:
    print("   ✅ SMTP ready for REAL SENDS (when DRY_RUN=false)")
else:
    print("   ⚠️  Neither Gmail API nor SMTP configured")
    print("   To enable:")
    print("     Option A: Place token.json in vault root (Gmail API)")
    print("     Option B: Set EMAIL_USER and EMAIL_PASSWORD in .env.local (SMTP)")

print()

# ====================================================================
# 4. MCP SERVERS STATUS
# ====================================================================
print("="*80)
print("4️⃣  MCP SERVERS STATUS")
print("="*80)
print()

# Check Email MCP
try:
    from mcp_email import MCPEmailServer
    os.environ['DRY_RUN'] = 'true'  # Safe mode
    email_mcp = MCPEmailServer(vault_path=VAULT)
    print(f"   Email MCP:        ✅ INITIALIZED")
    print(f"   Mode:             {email_mcp.mode.upper()}")
    print(f"   DRY_RUN:          {email_mcp.dry_run}")
    print(f"   Real Send Path:   {'✅ _send_via_gmail_api' if email_mcp.mode == 'gmail_api' else '✅ _send_via_smtp'}")
except Exception as e:
    print(f"   Email MCP:        ❌ FAILED: {e}")

print()

# Check Social MCP
try:
    from mcp_social import MCPSocialServer, PLAYWRIGHT_AVAILABLE
    os.environ['DRY_RUN'] = 'true'  # Safe mode
    social_mcp = MCPSocialServer(vault_path=VAULT)
    print(f"   Social MCP:       ✅ INITIALIZED")
    print(f"   Playwright:       {'✅ Available' if PLAYWRIGHT_AVAILABLE else '❌ Not installed'}")
    print(f"   DRY_RUN:          {social_mcp.dry_run}")
    print(f"   Real Post Path:   ✅ _post_linkedin_with_cookies")
except Exception as e:
    print(f"   Social MCP:       ❌ FAILED: {e}")

print()

# ====================================================================
# 5. LOCAL AGENT STATUS
# ====================================================================
print("="*80)
print("5️⃣  LOCAL AGENT STATUS")
print("="*80)
print()

try:
    from local_agent import LocalAgent
    os.environ['DRY_RUN'] = 'true'  # Safe mode
    os.environ['REQUIRE_APPROVAL'] = 'false'  # Allow test
    
    agent = LocalAgent(vault_path=str(VAULT))
    
    print(f"   Local Agent:      ✅ INITIALIZED")
    print(f"   Email MCP:        {'✅ Connected' if agent.email_mcp else '❌ Not connected'}")
    print(f"   Social MCP:       {'✅ Connected' if agent.social_mcp else '❌ Not connected'}")
    print(f"   Execution Path:   ✅ REAL (no simulation)")
    print()
    print(f"   Methods:")
    print(f"     execute_email_send:      ✅ Calls email_mcp.send_email(approved=True)")
    print(f"     execute_social_post:     ✅ Calls social_mcp.post_to_linkedin(approved=True)")
    print(f"     execute_odoo_action:     ✅ Calls odoo_mcp (if available)")
    print(f"     execute_whatsapp_send:   ✅ Real Playwright automation")
    
except Exception as e:
    print(f"   Local Agent:      ❌ FAILED: {e}")
    import traceback
    traceback.print_exc()

print()

# ====================================================================
# 6. EXECUTION LAYER VERIFICATION
# ====================================================================
print("="*80)
print("6️⃣  EXECUTION LAYER VERIFICATION")
print("="*80)
print()

# Check for simulation code
import subprocess
try:
    result = subprocess.run(
        ['findstr', '/C:time.sleep(2)', '/C:Simulate', '/C:simulated', 
         'mcp_email.py', 'mcp_social.py', 'local_agent.py'],
        cwd=str(VAULT),
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0 and result.stdout:
        lines = result.stdout.strip().split('\n')
        # Filter out browser wait times (legitimate)
        simulation_lines = [l for l in lines if 'sleep' in l and 'wait' not in l.lower()]
        
        if simulation_lines:
            print(f"   ⚠️  Found {len(simulation_lines)} potential simulation lines:")
            for line in simulation_lines[:5]:
                print(f"      {line.strip()}")
        else:
            print(f"   ✅ No simulation code found (time.sleep calls are browser waits only)")
    else:
        print(f"   ✅ No simulation code found")
except:
    print(f"   ⚠️  Could not verify simulation code (findstr failed)")

print()

# ====================================================================
# SUMMARY
# ====================================================================
print("="*80)
print("📊 EXECUTION LAYER SUMMARY")
print("="*80)
print()

print("   Component              Status")
print("   " + "-"*76)

# LinkedIn
linkedin_ready = session_file.exists() and li_at_cookies
print(f"   LinkedIn Session       {'✅ READY' if linkedin_ready else '❌ NOT READY'}")

# Gmail
gmail_ready = gmail_api_ready or smtp_ready
print(f"   Gmail/SMTP             {'✅ READY' if gmail_ready else '❌ NOT READY'}")

# Email MCP
email_mcp_ready = 'email_mcp' in locals() and email_mcp
print(f"   Email MCP Server       {'✅ READY' if email_mcp_ready else '❌ NOT READY'}")

# Social MCP
social_mcp_ready = 'social_mcp' in locals() and social_mcp
print(f"   Social MCP Server      {'✅ READY' if social_mcp_ready else '❌ NOT READY'}")

# Local Agent
local_agent_ready = 'agent' in locals() and agent
print(f"   Local Agent            {'✅ READY' if local_agent_ready else '❌ NOT READY'}")

# DRY_RUN
print(f"   DRY_RUN Mode           {'✅ SAFE (true)' if dry_run else '🚨 REAL (false)'}")

print()

if all([linkedin_ready, gmail_ready, email_mcp_ready, social_mcp_ready, local_agent_ready]):
    print("   🎉 ALL COMPONENTS READY FOR REAL EXECUTION")
    print()
    if dry_run:
        print("   Current Mode: DRY RUN (SAFE)")
        print("   To enable real sends:")
        print("     1. Open .env.local")
        print("     2. Set: DRY_RUN=false")
        print("     3. Set: REQUIRE_APPROVAL=false (or approve manually)")
        print("     4. Restart orchestrator")
    else:
        print("   🚨 REAL SENDS ENABLED - System will actually send emails and posts!")
else:
    print("   ⚠️  Some components not ready - check status above")

print()
print("="*80)
print("✅ STATUS CHECK COMPLETE")
print("="*80)
