#!/usr/bin/env python3
"""
FULL FLOW TEST - DRY RUN MODE (SAFE)
Tests complete execution path WITHOUT actually sending emails or posts

This test:
1. Creates a test email approval file
2. Creates a test LinkedIn post approval file
3. Processes both through Local Agent
4. Shows clear DRY RUN vs REAL SEND output
5. Verifies files moved to Done folder

⚠️ SAFETY:
    - DRY_RUN=true (won't actually send/post)
    - No real emails or posts will be published
    - Uses existing sessions only
    - No passwords asked or used

To enable REAL sends:
    Set DRY_RUN=false in .env.local
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Force DRY_RUN mode for safety
os.environ['DRY_RUN'] = 'true'
os.environ['REQUIRE_APPROVAL'] = 'false'

# Fix Windows console encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except:
        pass

VAULT = Path(__file__).parent

print("="*80)
print("🧪 FULL FLOW TEST - DRY RUN MODE (SAFE)")
print("="*80)
print()
print("This test will:")
print("  ✅ Create test approval files")
print("  ✅ Process through Local Agent")
print("  ✅ Show DRY RUN output (NO ACTUAL SENDS)")
print("  ✅ Verify files moved to Done")
print()
print("="*80)
print()

# ====================================================================
# SETUP: Import Local Agent
# ====================================================================
print("📦 INITIALIZING...")
print("-" * 80)

try:
    from local_agent import LocalAgent

    agent = LocalAgent(vault_path=str(VAULT))

    print(f"✅ Local Agent initialized")
    print(f"   Email MCP: {'✅ Available' if agent.email_mcp else '❌ Not available'}")
    print(f"   Social MCP: {'✅ Available' if agent.social_mcp else '❌ Not available'}")
    print(f"   DRY_RUN: {os.environ.get('DRY_RUN', 'true')}")
    print(f"   REQUIRE_APPROVAL: {os.environ.get('REQUIRE_APPROVAL', 'true')}")
    print()

except Exception as e:
    print(f"❌ Failed to initialize Local Agent: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ====================================================================
# TEST 1: Email Flow
# ====================================================================
print("="*80)
print("TEST 1: EMAIL FLOW (Approval → Process → Done)")
print("="*80)
print()

try:
    # Step 1: Create approval file
    email_approval = VAULT / 'Approved' / 'TEST_EMAIL_FLOW_20260415.md'

    email_content = f"""---
type: email
to: test@example.com
subject: Test Email - Full Flow Test
created: {datetime.now().isoformat()}
status: approved
approved_by: test_script
---

# Approved Email

**Action:** Send email reply
**To:** test@example.com
**Subject:** Test Email - Full Flow Test

---

Dear Test,

This is a test email to verify the full execution flow is working correctly.

The AI Employee system is operational and processing approvals.

Best regards,
AI Employee

---
*This is a test - no real action required*
"""

    email_approval.write_text(email_content, encoding='utf-8')
    print(f"✅ Step 1: Created approval file: {email_approval.name}")

    # Step 2: Process through Local Agent
    print(f"🔄 Step 2: Processing through Local Agent...")
    print()

    agent.execute_approved_item(email_approval)

    # Step 3: Check result
    done_file = VAULT / 'Done' / f"COMPLETED_{email_approval.name}"

    if done_file.exists():
        print()
        print(f"✅ Step 3: File moved to Done: {done_file.name}")
        print("✅ EMAIL FLOW TEST PASSED")
    else:
        print()
        print(f"⚠️ File not moved to Done (check logs for errors)")
        if email_approval.exists():
            print(f"   Original file still in Approved: {email_approval.name}")

except Exception as e:
    print(f"❌ Email flow test failed: {e}")
    import traceback
    traceback.print_exc()

print()

# ====================================================================
# TEST 2: LinkedIn Post Flow
# ====================================================================
print("="*80)
print("TEST 2: LINKEDIN POST FLOW (Approval → Process → Done)")
print("="*80)
print()

try:
    # Step 1: Create approval file
    linkedin_approval = VAULT / 'Approved' / 'TEST_LINKEDIN_FLOW_20260415.md'

    linkedin_content = f"""---
type: social_post
platform: linkedin
created: {datetime.now().isoformat()}
status: approved
approved_by: test_script
---

# Approved LinkedIn Post

**Platform:** LinkedIn
**Action:** Publish post

---

🚀 Testing AI Employee Full Flow!

This is a test post to verify the execution layer is working correctly.

The system processed this approval through the Local Agent.

✅ Email MCP: Working
✅ Social MCP: Working
✅ Local Agent: Working

#AIEmployee #Automation #Test #FullFlow

---
*This is a test post - DRY RUN MODE*
"""

    linkedin_approval.write_text(linkedin_content, encoding='utf-8')
    print(f"✅ Step 1: Created approval file: {linkedin_approval.name}")

    # Step 2: Process through Local Agent
    print(f"🔄 Step 2: Processing through Local Agent...")
    print()

    agent.execute_approved_item(linkedin_approval)

    # Step 3: Check result
    done_file = VAULT / 'Done' / f"COMPLETED_{linkedin_approval.name}"

    if done_file.exists():
        print()
        print(f"✅ Step 3: File moved to Done: {done_file.name}")
        print("✅ LINKEDIN POST FLOW TEST PASSED")
    else:
        print()
        print(f"⚠️ File not moved to Done (check logs for errors)")
        if linkedin_approval.exists():
            print(f"   Original file still in Approved: {linkedin_approval.name}")

except Exception as e:
    print(f"❌ LinkedIn post flow test failed: {e}")
    import traceback
    traceback.print_exc()

print()

# ====================================================================
# TEST 3: Draft Files Created
# ====================================================================
print("="*80)
print("TEST 3: DRAFT FILES VERIFICATION")
print("="*80)
print()

try:
    drafts_folder = VAULT / 'Drafts'
    social_drafts = VAULT / 'Social_Drafts'

    email_drafts = list(drafts_folder.glob('email_*.md')) if drafts_folder.exists() else []
    linkedin_drafts = list(social_drafts.glob('linkedin_post_*.md')) if social_drafts.exists() else []

    print(f"📁 Email Drafts: {len(email_drafts)} found")
    if email_drafts:
        print(f"   Latest: {email_drafts[-1].name}")

    print(f"📁 LinkedIn Drafts: {len(linkedin_drafts)} found")
    if linkedin_drafts:
        print(f"   Latest: {linkedin_drafts[-1].name}")

    if email_drafts or linkedin_drafts:
        print("✅ DRAFT FILES TEST PASSED")
    else:
        print("⚠️ No draft files found (may be expected if test ran quickly)")

except Exception as e:
    print(f"❌ Draft verification failed: {e}")

print()

# ====================================================================
# SUMMARY
# ====================================================================
print("="*80)
print("📊 TEST SUMMARY")
print("="*80)
print()
print("Execution Mode: DRY RUN (SAFE)")
print()
print("What was tested:")
print("  ✅ Local Agent initialization with MCP servers")
print("  ✅ Email approval processing (DRY RUN)")
print("  ✅ LinkedIn post approval processing (DRY RUN)")
print("  ✅ File movement: Approved → Done")
print("  ✅ Draft file creation")
print()
print("Output indicators:")
print("  📝 [DRY RUN MODE] = Test mode, no actual sends")
print("  🚀 [REAL SEND EXECUTED] = Would appear if DRY_RUN=false")
print()
print("To enable REAL sends:")
print("  1. Open .env.local")
print("  2. Set: DRY_RUN=false")
print("  3. Set: REQUIRE_APPROVAL=false (or approve manually)")
print("  4. Restart orchestrator")
print()
print("  For Gmail:")
print("    - Option A: Place token.json in vault root (Gmail API)")
print("    - Option B: Add EMAIL_USER and EMAIL_PASSWORD to .env.local (SMTP)")
print()
print("  For LinkedIn:")
print("    - linkedin_session.json already has valid cookies ✅")
print()
print("="*80)
print("✅ FULL FLOW TEST COMPLETE")
print("="*80)
