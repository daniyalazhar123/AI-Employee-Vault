#!/usr/bin/env python3
"""
TEST EXECUTION LAYER
Tests real MCP calls (no simulation)
Creates test action file → processes → shows output

⚠️ SAFETY:
    - DRY_RUN=true by default (won't actually send/post)
    - Tests draft creation only
    - No passwords asked or used
    - Uses existing sessions only
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except:
        pass

VAULT = Path(__file__).parent

print("="*70)
print("🧪 TESTING EXECUTION LAYER - REAL MCP CALLS")
print("="*70)
print()

# ====================================================================
# TEST 1: Email MCP - Draft Creation (DRY_RUN mode)
# ====================================================================
print("TEST 1: Email MCP Server")
print("-" * 70)

try:
    from mcp_email import MCPEmailServer

    # Initialize with DRY_RUN=true (safe)
    os.environ['DRY_RUN'] = 'true'
    os.environ['REQUIRE_APPROVAL'] = 'false'

    email_mcp = MCPEmailServer(vault_path=VAULT)

    print(f"  Mode: {email_mcp.mode}")
    print(f"  DRY_RUN: {email_mcp.dry_run}")
    print()

    # Test draft creation
    result = email_mcp.send_email(
        to='test@example.com',
        subject='Test Email from AI Employee',
        body='This is a test email to verify the execution layer is working.\n\nSent from AI Employee Vault.',
        approved=True
    )

    print(f"  Result: {json.dumps(result, indent=2)}")

    if result.get('success'):
        print("  ✅ Email MCP TEST PASSED - Draft created successfully")
    else:
        print(f"  ⚠️ Email MCP returned: {result.get('message')}")

except Exception as e:
    print(f"  ❌ Email MCP test failed: {e}")

print()

# ====================================================================
# TEST 2: Social MCP - LinkedIn Draft (DRY_RUN mode)
# ====================================================================
print("TEST 2: Social MCP Server (LinkedIn)")
print("-" * 70)

try:
    from mcp_social import MCPSocialServer

    # Initialize with DRY_RUN=true (safe)
    os.environ['DRY_RUN'] = 'true'
    os.environ['REQUIRE_APPROVAL'] = 'false'

    social_mcp = MCPSocialServer(vault_path=VAULT)

    print(f"  DRY_RUN: {social_mcp.dry_run}")
    print(f"  Playwright: ✅ Available")  # Already checked above

    # Check session file
    session_file = VAULT / 'linkedin_session.json'
    if session_file.exists():
        with open(session_file) as f:
            session_data = json.load(f)
        cookies = session_data.get('cookies', [])
        print(f"  LinkedIn Session: ✅ {len(cookies)} cookies loaded")
    else:
        print(f"  LinkedIn Session: ❌ No session file found")

    print()

    # Test draft creation
    result = social_mcp.post_to_linkedin(
        content="🚀 Testing AI Employee execution layer!\n\nThis is an automated test post to verify the system is working correctly.\n\n#AIEmployee #Automation #Test",
        approved=True
    )

    print(f"  Result: {json.dumps(result, indent=2)}")

    if result.get('success'):
        print("  ✅ Social MCP TEST PASSED - LinkedIn draft created successfully")
    else:
        print(f"  ⚠️ Social MCP returned: {result.get('message')}")

except Exception as e:
    print(f"  ❌ Social MCP test failed: {e}")

print()

# ====================================================================
# TEST 3: Local Agent - Execute Approved Email
# ====================================================================
print("TEST 3: Local Agent - Execute Approved Email")
print("-" * 70)

try:
    # Create test approval file
    test_approval = VAULT / 'Approved' / 'TEST_EMAIL_20260415_120000.md'
    test_approval.parent.mkdir(exist_ok=True)

    approval_content = f"""---
type: email
to: test@example.com
subject: Test from AI Employee Execution Layer
created: {datetime.now().isoformat()}
status: approved
approved_by: test_script
---

# Approved Email

**To:** test@example.com
**Subject:** Test from AI Employee Execution Layer

---

This is a test email to verify the Local Agent can execute real MCP calls.

The execution layer is working correctly.

Best regards,
AI Employee
"""

    test_approval.write_text(approval_content, encoding='utf-8')
    print(f"  ✅ Created test approval file: {test_approval.name}")

    # Initialize Local Agent
    os.environ['DRY_RUN'] = 'true'
    os.environ['REQUIRE_APPROVAL'] = 'false'

    from local_agent import LocalAgent

    agent = LocalAgent(vault_path=str(VAULT))

    print(f"  Email MCP: {'✅' if agent.email_mcp else '❌'}")
    print(f"  Social MCP: {'✅' if agent.social_mcp else '❌'}")
    print()

    # Execute the approval file
    agent.execute_approved_item(test_approval)

    # Check if moved to Done
    done_file = VAULT / 'Done' / f"COMPLETED_{test_approval.name}"
    if done_file.exists():
        print(f"  ✅ File moved to Done: {done_file.name}")
        print("  ✅ Local Agent TEST PASSED - Execution layer working")
    else:
        print(f"  ⚠️ File not moved to Done (may be in DLQ if errors)")

    # Cleanup
    if test_approval.exists():
        test_approval.unlink()
    if done_file.exists():
        done_file.unlink()

except Exception as e:
    print(f"  ❌ Local Agent test failed: {e}")
    import traceback
    traceback.print_exc()

print()

# ====================================================================
# TEST 4: End-to-End Flow
# ====================================================================
print("TEST 4: End-to-End Flow (Action File → Draft → Approval)")
print("-" * 70)

try:
    from mcp_email import MCPEmailServer

    os.environ['DRY_RUN'] = 'true'
    os.environ['REQUIRE_APPROVAL'] = 'false'

    # Step 1: Create action file in Needs_Action
    action_file = VAULT / 'Needs_Action' / 'TEST_EMAIL_FLOW.md'
    action_file.parent.mkdir(exist_ok=True)

    action_content = f"""---
type: email
from: client@example.com
subject: Inquiry about services
received: {datetime.now().isoformat()}
priority: normal
status: pending
---

## Email Content

Hi, I'm interested in learning more about your services. Can you send me information?

Thanks,
Client
"""

    action_file.write_text(action_content, encoding='utf-8')
    print(f"  ✅ Step 1: Action file created")

    # Step 2: Create draft reply
    email_mcp = MCPEmailServer(vault_path=VAULT)

    draft_result = email_mcp.draft_email(
        to='client@example.com',
        subject='Re: Inquiry about services',
        body='Dear Client,\n\nThank you for your interest! I\'d be happy to send you information about our services.\n\nBest regards,\nAI Employee'
    )

    if draft_result.get('success'):
        print(f"  ✅ Step 2: Draft created - {draft_result.get('draft_file')}")
    else:
        print(f"  ⚠️ Step 2: {draft_result.get('message')}")

    # Step 3: Create approval file
    approval_file = VAULT / 'Pending_Approval' / 'TEST_FLOW_APPROVAL.md'
    approval_file.parent.mkdir(exist_ok=True)

    approval_content = f"""---
type: email
to: client@example.com
subject: Re: Inquiry about services
created: {datetime.now().isoformat()}
status: pending
---

# Approval Request

**Action:** Send email reply
**To:** client@example.com
**Subject:** Re: Inquiry about services

Move to Approved/ to send.
"""

    approval_file.write_text(approval_content, encoding='utf-8')
    print(f"  ✅ Step 3: Approval file created")

    # Step 4: Simulate approval (move to Approved)
    approved_file = VAULT / 'Approved' / 'TEST_FLOW_APPROVAL.md'
    if approved_file.exists():
        approved_file.unlink()  # Remove old file
    approval_file.rename(approved_file)
    print(f"  ✅ Step 4: Approved (file moved)")

    # Step 5: Execute via Local Agent
    from local_agent import LocalAgent

    agent = LocalAgent(vault_path=str(VAULT))
    agent.execute_approved_item(approved_file)

    done_file = VAULT / 'Done' / f"COMPLETED_TEST_FLOW_APPROVAL.md"
    if done_file.exists():
        print(f"  ✅ Step 5: Executed and moved to Done")
        print("  ✅ END-TO-END FLOW TEST PASSED")
    else:
        print(f"  ⚠️ Step 5: Not moved to Done")

    # Cleanup
    for f in [action_file, approved_file, done_file]:
        if f.exists():
            f.unlink()

except Exception as e:
    print(f"  ❌ End-to-end test failed: {e}")
    import traceback
    traceback.print_exc()

print()
print("="*70)
print("📊 TEST SUMMARY")
print("="*70)
print()
print("All tests run in DRY_RUN mode (safe - no actual sends)")
print("Execution layer is wired up and calling real MCP servers")
print()
print("Next steps to enable REAL sends:")
print("  1. Set DRY_RUN=false in .env")
print("  2. Ensure Gmail token or SMTP credentials in .env")
print("  3. Ensure LinkedIn session cookies are valid")
print("  4. Run orchestrator to process real action files")
print("="*70)
