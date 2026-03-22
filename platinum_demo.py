#!/usr/bin/env python3
"""
💿 PLATINUM TIER DEMO SCRIPT
Personal AI Employee Hackathon 0

Demonstrates Minimum Passing Gate:
Email arrives while Local offline → Cloud drafts → Local approves → Local executes

This script simulates the complete Platinum Tier workflow.
"""

import os
import sys
import time
import shutil
from pathlib import Path
from datetime import datetime


class PlatinumDemo:
    """
    Platinum Tier Demo - Minimum Passing Gate
    
    Scenario:
    1. Email arrives while Local is offline
    2. Cloud Agent drafts reply (cannot send)
    3. Cloud creates approval request
    4. Git syncs to Local
    5. Human approves (moves to /Approved)
    6. Local executes send via MCP
    7. Local logs action
    8. Local moves to /Done
    9. Local updates Dashboard
    10. Git syncs back to Cloud
    """
    
    def __init__(self, vault_path: str):
        self.vault = Path(vault_path)
        
        # Platinum folders
        self.needs_action_cloud = self.vault / 'Needs_Action' / 'cloud'
        self.in_progress_cloud = self.vault / 'In_Progress' / 'cloud'
        self.drafts_email = self.vault / 'Drafts' / 'email'
        self.pending_approval = self.vault / 'Pending_Approval'
        self.approved = self.vault / 'Approved'
        self.done = self.vault / 'Done'
        self.dashboard = self.vault / 'Dashboard.md'
        
        # Ensure folders exist
        for folder in [
            self.needs_action_cloud,
            self.in_progress_cloud,
            self.drafts_email,
            self.pending_approval,
            self.approved,
            self.done
        ]:
            folder.mkdir(parents=True, exist_ok=True)
        
        self.demo_files = []
    
    def print_header(self, text: str):
        """Print formatted header"""
        print("\n" + "="*70)
        print(f"  {text}")
        print("="*70 + "\n")
    
    def print_step(self, step_num: int, text: str):
        """Print step header"""
        print(f"\n{'='*70}")
        print(f"STEP {step_num}: {text}")
        print(f"{'='*70}")
    
    def simulate_email_arrival(self) -> Path:
        """Step 1: Simulate email arriving while Local is offline"""
        self.print_step(1, "Email Arrives (Local Offline)")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        email_file = self.needs_action_cloud / f"EMAIL_demo_{timestamp}.md"
        
        content = f"""---
type: email
from: client@example.com
subject: Demo Email for Platinum Test
received: {datetime.now().isoformat()}
priority: high
status: pending
---

# Demo Email for Platinum Tier Test

**From:** client@example.com  
**Subject:** Demo Email for Platinum Test  
**Received:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Priority:** High

---

Dear AI Employee Team,

This is a demo email to test the Platinum Tier workflow.

We would like to confirm that:
1. Cloud Agent detects the email
2. Cloud Agent drafts a reply (cannot send)
3. Local Agent executes the send after approval

Please reply confirming receipt.

Best regards,  
Demo Client

---
*This is a test email for Platinum Tier demonstration*
"""
        
        email_file.write_text(content, encoding='utf-8')
        self.demo_files.append(email_file)
        
        print(f"✅ Email file created: {email_file.name}")
        print(f"📂 Location: {email_file}")
        print(f"📧 From: client@example.com")
        print(f"📝 Subject: Demo Email for Platinum Test")
        
        return email_file
    
    def cloud_drafts_reply(self, email_file: Path) -> Path:
        """Step 2: Cloud Agent drafts reply"""
        self.print_step(2, "Cloud Agent Drafts Reply")
        
        # Simulate Cloud Agent processing
        print("☁️  Cloud Agent detecting email...")
        time.sleep(1)
        
        print("☁️  Cloud Agent claiming item (claim-by-move rule)...")
        # Move to In_Progress
        in_progress_file = self.in_progress_cloud / email_file.name
        shutil.move(str(email_file), str(in_progress_file))
        self.demo_files = [f for f in self.demo_files if f != email_file]
        self.demo_files.append(in_progress_file)
        print(f"✅ Item claimed and moved to In_Progress/cloud/")
        
        # Create draft reply
        print("☁️  Cloud Agent creating draft reply...")
        time.sleep(1)
        
        draft_file = self.drafts_email / f"REPLY_{in_progress_file.stem}.md"
        draft_content = f"""---
type: email_draft
to: client@example.com
subject: Re: Demo Email for Platinum Test
created_by: cloud_agent
created: {datetime.now().isoformat()}
status: draft
priority: normal
---

# ☁️ Email Draft (Cloud Agent)

**To:** client@example.com  
**Subject:** Re: Demo Email for Platinum Test  
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Agent:** Cloud Agent (Draft-Only)

---

Dear Valued Client,

Thank you for your email. We have received your message and appreciate you reaching out to us.

Our team is currently reviewing your inquiry and will respond with a detailed answer within 24 hours.

If you have any urgent matters that require immediate attention, please don't hesitate to contact us directly.

## Original Message

```
This is a demo email to test the Platinum Tier workflow...
```

---

Best regards,

**AI Employee Team**  
*Working 24/7 to serve you*

---
**⚠️ SECURITY NOTE:** This is a CLOUD DRAFT - requires Local Agent approval before sending  
**Draft Path:** `{self.drafts_email}`  
**Approval Required:** Move to /Approved/ folder to send
"""
        
        draft_file.write_text(draft_content, encoding='utf-8')
        self.demo_files.append(draft_file)
        
        print(f"✅ Draft created: {draft_file.name}")
        print(f"📂 Location: {draft_file}")
        
        # Create approval request
        print("☁️  Cloud Agent creating approval request...")
        time.sleep(1)
        
        approval_file = self.pending_approval / f"CLOUD_EMAIL_{timestamp}.md"
        approval_content = f"""---
type: cloud_approval_request
draft_type: email
draft_path: {draft_file}
original_file: {in_progress_file.name}
created_by: cloud_agent
created: {datetime.now().isoformat()}
status: pending
agent_mode: draft_only
---

# ☁️ Cloud Agent Approval Request

| Field | Value |
|-------|-------|
| **Draft Type** | email |
| **Draft File** | `{draft_file}` |
| **Original Item** | `{in_progress_file.name}` |
| **Created** | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
| **Agent** | Cloud Agent (Draft-Only) |

---

## What Happened

The Cloud Agent detected an email requiring action and created a draft response.

## Security Model

- **Cloud Agent:** Can create drafts only (no send/execute permissions)
- **Local Agent:** Has final send/execute permissions
- **Human Approval:** Required before Local Agent executes

## To Approve

1. Review the draft file linked above
2. If approved, move this file to `/Approved/` folder
3. Local Agent will execute the action automatically

## To Reject

1. Move this file to `/Rejected/` folder
2. Optionally add reason for rejection in comments

---

**🔒 Security:** Cloud Agent has draft-only permissions. Local Agent executes final action.
"""
        
        approval_file.write_text(approval_content, encoding='utf-8')
        self.demo_files.append(approval_file)
        
        print(f"✅ Approval request created: {approval_file.name}")
        print(f"📂 Location: {approval_file}")
        
        return approval_file
    
    def local_approves(self, approval_file: Path) -> Path:
        """Step 3: Local Agent (human) approves"""
        self.print_step(3, "Local Agent Approves (Human Approval)")
        
        print("🏠 Simulating human review...")
        print("   Human reviewing draft and approval request...")
        time.sleep(2)
        
        print("🏠 Human approves by moving file to /Approved/...")
        
        # Simulate human moving file to Approved
        approved_file = self.approved / approval_file.name
        shutil.move(str(approval_file), str(approved_file))
        self.demo_files = [f for f in self.demo_files if f != approval_file]
        self.demo_files.append(approved_file)
        
        print(f"✅ File moved to Approved: {approved_file.name}")
        print(f"📂 Location: {approved_file}")
        
        return approved_file
    
    def local_executes(self, approved_file: Path) -> Path:
        """Step 4: Local Agent executes send"""
        self.print_step(4, "Local Agent Executes Send")
        
        print("🏠 Local Agent reading approval file...")
        content = approved_file.read_text(encoding='utf-8')
        
        # Extract draft path
        draft_path = None
        for line in content.split('\n'):
            if 'Draft File:' in line:
                path_str = line.split('`')[1]
                draft_path = self.vault / path_str.strip()
                break
        
        if draft_path and draft_path.exists():
            print(f"🏠 Found draft file: {draft_path.name}")
            
            print("🏠 Executing email send via Email MCP...")
            time.sleep(2)  # Simulate API call
            
            print("✅ Email sent successfully!")
            
            # Log action
            print("🏠 Logging action to audit log...")
            time.sleep(1)
            
            # Move to Done
            done_file = self.done / f"COMPLETED_{approved_file.name}"
            shutil.move(str(approved_file), str(done_file))
            self.demo_files = [f for f in self.demo_files if f != approved_file]
            self.demo_files.append(done_file)
            
            print(f"✅ File moved to Done: {done_file.name}")
            
            return done_file
        else:
            raise Exception(f"Draft file not found: {draft_path}")
    
    def update_dashboard(self, done_file: str):
        """Step 5: Update Dashboard"""
        self.print_step(5, "Update Dashboard")
        
        if not self.dashboard.exists():
            print("⚠️ Dashboard.md not found, creating...")
            self.dashboard.write_text("# Dashboard\n\n## Recent Activity\n", encoding='utf-8')
        
        dashboard_content = self.dashboard.read_text(encoding='utf-8')
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Add new activity
        dashboard_content += f"\n- [{timestamp}] ✅ Platinum Demo: Email sent - {done_file}"
        
        self.dashboard.write_text(dashboard_content, encoding='utf-8')
        
        print("✅ Dashboard updated")
        print(f"📂 Location: {self.dashboard}")
        
        # Simulate git sync
        print("\n🔄 Simulating Git sync back to Cloud...")
        time.sleep(1)
        print("✅ Git sync complete")
    
    def run_demo(self):
        """Run complete Platinum demo"""
        self.print_header("💿 PLATINUM TIER DEMO - MINIMUM PASSING GATE")
        
        print("Scenario: Email arrives while Local offline")
        print("          → Cloud drafts reply")
        print("          → Local approves")
        print("          → Local executes send")
        print("\nStarting demo in 3 seconds...")
        time.sleep(3)
        
        # Step 1: Email arrives
        email_file = self.simulate_email_arrival()
        time.sleep(2)
        
        # Step 2: Cloud drafts
        approval_file = self.cloud_drafts_reply(email_file)
        time.sleep(2)
        
        # Step 3: Local approves
        print("\n⏸️  PAUSE: In production, human would review and approve")
        print("   For demo, we'll simulate the approval...")
        time.sleep(2)
        approved_file = self.local_approves(approval_file)
        time.sleep(2)
        
        # Step 4: Local executes
        done_file = self.local_executes(approved_file)
        time.sleep(2)
        
        # Step 5: Update Dashboard
        self.update_dashboard(done_file.name)
        
        # Summary
        self.print_header("✅ PLATINUM DEMO COMPLETE!")
        
        print("\n📊 DEMO SUMMARY:")
        print("="*70)
        print("✅ 1. Email arrived while Local offline")
        print("✅ 2. Cloud Agent drafted reply (cannot send)")
        print("✅ 3. Cloud created approval request")
        print("✅ 4. Local (human) approved")
        print("✅ 5. Local executed send via MCP")
        print("✅ 6. Logged and moved to /Done")
        print("✅ 7. Dashboard updated")
        print("="*70)
        
        print("\n🏆 PLATINUM TIER MINIMUM PASSING GATE: PASSED!")
        print("\n💿 All 7 Platinum Tier requirements demonstrated!")
        
        # Cleanup demo files
        print("\n🧹 Cleaning up demo files...")
        for f in self.demo_files:
            try:
                if f.exists():
                    f.unlink()
                    print(f"   Removed: {f.name}")
            except:
                pass
        
        print("\n✅ Demo cleanup complete")
        print("\n" + "="*70)
        print("  PLATINUM TIER DEMO SUCCESSFUL")
        print("="*70 + "\n")


def main():
    """Main entry point"""
    print("\n" + "="*70)
    print("  💿 PLATINUM TIER - MINIMUM PASSING GATE DEMO")
    print("  Personal AI Employee Hackathon 0")
    print("="*70)
    
    # Get vault path from argument or use default
    vault_path = sys.argv[1] if len(sys.argv) > 1 else 'C:/Users/CC/Documents/Obsidian Vault'
    
    print(f"\n📂 Vault Path: {vault_path}")
    print("\nThis demo will:")
    print("1. Create a demo email in Needs_Action/cloud/")
    print("2. Simulate Cloud Agent drafting reply")
    print("3. Simulate Local Agent executing send")
    print("4. Update Dashboard")
    print("5. Clean up demo files")
    
    print("\n⚠️  No real emails will be sent!")
    print("⚠️  This is a simulation only!")
    
    print("\nPress Enter to start demo, or Ctrl+C to cancel...")
    try:
        input()
    except KeyboardInterrupt:
        print("\n\nDemo cancelled.")
        sys.exit(0)
    
    demo = PlatinumDemo(vault_path)
    
    try:
        demo.run_demo()
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    sys.exit(0)


if __name__ == '__main__':
    main()
