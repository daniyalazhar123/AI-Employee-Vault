#!/usr/bin/env python3
"""
☁️ CLOUD ORCHESTRATOR - Platinum Tier
Runs on Cloud VM 24/7 in Draft-Only Mode

Personal AI Employee Hackathon 0
Platinum Tier: Always-On Cloud + Local Executive

Responsibilities:
- Monitor Needs_Action/ folder every 30 seconds
- Create drafts in Updates/ folder (DRAFT-ONLY MODE)
- Move tasks to In_Progress/cloud/ when processing
- CANNOT send emails or post directly (security!)
- Log all activities to Logs/cloud_agent.log

Security Restrictions:
- NO direct email sending
- NO direct social media posting
- NO payment execution
- NO WhatsApp access (session local only)
- All actions require Local Agent approval
"""

import os
import sys
import time
import shutil
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import signal

# Configuration
VAULT_PATH = Path(os.getenv('VAULT_PATH', '.'))
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '30'))
AGENT_ID = 'cloud'
AGENT_TYPE = 'draft_only'

# Setup logging
LOG_FILE = VAULT_PATH / 'Logs' / 'cloud_agent.log'
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('CloudOrchestrator')


class CloudOrchestrator:
    """
    Cloud Orchestrator - Draft-Only Mode
    
    Runs on cloud VM 24/7, creating drafts that require
    Local Agent approval before execution.
    """
    
    def __init__(self, vault_path: Path):
        self.vault = vault_path
        self.agent_id = AGENT_ID
        self.agent_type = AGENT_TYPE
        
        # Platinum folder structure
        self.needs_action_cloud = self.vault / 'Needs_Action' / 'cloud'
        self.needs_action_local = self.vault / 'Needs_Action' / 'local'
        self.in_progress_cloud = self.vault / 'In_Progress' / 'cloud'
        self.in_progress_local = self.vault / 'In_Progress' / 'local'
        self.updates = self.vault / 'Updates'
        self.signals = self.vault / 'Signals'
        self.logs = self.vault / 'Logs'
        self.dead_letter_queue = self.vault / 'Dead_Letter_Queue'
        
        # Ensure all folders exist
        self._ensure_folders()
        
        # Statistics
        self.stats = {
            'items_processed': 0,
            'drafts_created': 0,
            'errors': 0,
            'start_time': datetime.now().isoformat(),
            'last_check': None
        }
        
        # Running flag
        self.running = True
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("☁️  Cloud Orchestrator initialized (Draft-Only Mode)")
        logger.info(f"📂 Vault path: {self.vault}")
        logger.info(f"📊 Initial stats: {self.stats}")
    
    def _ensure_folders(self):
        """Create all necessary folders for Platinum operation"""
        folders = [
            self.needs_action_cloud,
            self.needs_action_local,
            self.in_progress_cloud,
            self.in_progress_local,
            self.updates,
            self.signals,
            self.logs,
            self.logs / 'Audit',
            self.dead_letter_queue
        ]
        for folder in folders:
            folder.mkdir(parents=True, exist_ok=True)
        logger.debug("✅ All folders created/verified")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"🛑 Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    def claim_item(self, item_file: Path) -> bool:
        """
        Claim an item from Needs_Action/cloud
        Claim-by-move rule: First agent to move owns it
        
        Moves item from Needs_Action/cloud to In_Progress/cloud
        """
        try:
            # Check if already claimed
            if item_file.parent.name == 'cloud':
                # Check if file is in In_Progress/cloud
                in_progress_file = self.in_progress_cloud / item_file.name
                if in_progress_file.exists():
                    logger.warning(f"⚠️ Item already claimed: {item_file.name}")
                    return False
            
            # Move to In_Progress/cloud
            dest = self.in_progress_cloud / item_file.name
            shutil.move(str(item_file), str(dest))
            
            logger.info(f"✅ Cloud claimed: {item_file.name}")
            
            # Log claim for audit
            self._log_claim(item_file.name)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to claim item: {e}")
            self.stats['errors'] += 1
            return False
    
    def _log_claim(self, item_name: str):
        """Log claim for audit trail"""
        claim_log = {
            'item': item_name,
            'claimed_by': self.agent_id,
            'timestamp': datetime.now().isoformat(),
            'action': 'claim'
        }
        
        audit_file = self.logs / 'Audit' / f'claims_{datetime.now().strftime("%Y%m%d")}.jsonl'
        with open(audit_file, 'a') as f:
            f.write(json.dumps(claim_log) + '\n')
    
    def create_draft(self, item_file: Path) -> Optional[Path]:
        """
        Create draft response for item
        DRAFT-ONLY MODE: Cannot execute, only create drafts
        """
        try:
            # Read item content
            content = item_file.read_text(encoding='utf-8')
            
            # Parse metadata
            metadata = self._parse_metadata(content)
            
            # Create draft based on type
            draft_type = metadata.get('type', 'unknown')
            
            if draft_type == 'email':
                draft_content = self._create_email_draft(metadata, content)
            elif draft_type == 'social':
                draft_content = self._create_social_draft(metadata, content)
            elif draft_type == 'invoice':
                draft_content = self._create_invoice_draft(metadata, content)
            else:
                draft_content = self._create_general_draft(metadata, content)
            
            # Save draft to Updates/
            draft_file = self.updates / f'DRAFT_{item_file.stem}.md'
            draft_file.write_text(draft_content, encoding='utf-8')
            
            logger.info(f"✅ Draft created: {draft_file.name}")
            self.stats['drafts_created'] += 1
            
            return draft_file
            
        except Exception as e:
            logger.error(f"❌ Failed to create draft: {e}")
            self.stats['errors'] += 1
            return None
    
    def _parse_metadata(self, content: str) -> Dict:
        """Parse YAML frontmatter from markdown"""
        metadata = {}
        
        # Simple YAML parsing (frontmatter between ---)
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                yaml_content = parts[1]
                for line in yaml_content.strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip()] = value.strip()
        
        return metadata
    
    def _create_email_draft(self, metadata: Dict, original_content: str) -> str:
        """Create email reply draft"""
        from_email = metadata.get('from', 'Unknown')
        subject = metadata.get('subject', 'No Subject')
        
        draft = f"""---
type: email_reply
original_email: {from_email}
subject: RE: {subject}
created_by: cloud
created: {datetime.now().isoformat()}
status: draft
requires_approval: true
agent_type: draft_only
---

# Draft Email Reply

**To:** {from_email}
**Subject:** RE: {subject}

---

Dear Valued Client,

Thank you for your email.

[AI-generated response based on email content]

This is a DRAFT created by Cloud Agent.
Requires Local Agent approval before sending.

---

Best regards,
AI Employee

---
*Draft created by Cloud Agent (Draft-Only Mode)*
*Local Agent must approve before sending*
"""
        return draft
    
    def _create_social_draft(self, metadata: Dict, original_content: str) -> str:
        """Create social media post draft"""
        platform = metadata.get('platform', 'LinkedIn')
        
        draft = f"""---
type: social_post
platform: {platform}
created_by: cloud
created: {datetime.now().isoformat()}
status: draft
requires_approval: true
agent_type: draft_only
---

# Draft Social Media Post

**Platform:** {platform}

---

[AI-generated social media post content]

This is a DRAFT created by Cloud Agent.
Requires Local Agent approval before posting.

---

#Hashtag1 #Hashtag2 #Hashtag3

---
*Draft created by Cloud Agent (Draft-Only Mode)*
*Local Agent must approve before posting*
"""
        return draft
    
    def _create_invoice_draft(self, metadata: Dict, original_content: str) -> str:
        """Create invoice draft"""
        customer = metadata.get('customer', 'Unknown')
        amount = metadata.get('amount', '0')
        
        draft = f"""---
type: invoice_draft
customer: {customer}
amount: {amount}
created_by: cloud
created: {datetime.now().isoformat()}
status: draft
requires_approval: true
agent_type: draft_only
---

# Draft Invoice

**Customer:** {customer}
**Amount:** {amount}

---

This is a DRAFT invoice created by Cloud Agent.
Requires Local Agent approval before creating in Odoo.

---
*Draft created by Cloud Agent (Draft-Only Mode)*
*Local Agent must approve before execution*
"""
        return draft
    
    def _create_general_draft(self, metadata: Dict, original_content: str) -> str:
        """Create general purpose draft"""
        draft = f"""---
type: general_draft
created_by: cloud
created: {datetime.now().isoformat()}
status: draft
requires_approval: true
agent_type: draft_only
---

# Draft Response

---

[AI-generated response]

This is a DRAFT created by Cloud Agent.
Requires Local Agent approval before execution.

---
*Draft created by Cloud Agent (Draft-Only Mode)*
*Local Agent must approve before execution*
"""
        return draft
    
    def create_approval_request(self, draft_file: Path) -> Optional[Path]:
        """Create approval request for Local Agent"""
        try:
            approval_file = self.vault / 'Pending_Approval' / f'APPROVAL_{draft_file.stem}.md'
            
            content = f"""---
type: approval_request
draft_file: {draft_file.name}
created_by: cloud
created: {datetime.now().isoformat()}
status: pending
agent_type: draft_only
---

# Approval Required

**Draft:** {draft_file.name}
**Created by:** Cloud Agent (Draft-Only)
**Action Required:** Review and approve/reject

## To Approve
Move this file to `/Approved` folder

## To Reject
Move this file to `/Rejected` folder

---
*Cloud Agent cannot execute - requires Local approval*
"""
            approval_file.write_text(content, encoding='utf-8')
            logger.info(f"✅ Approval request created: {approval_file.name}")
            
            return approval_file
            
        except Exception as e:
            logger.error(f"❌ Failed to create approval request: {e}")
            self.stats['errors'] += 1
            return None
    
    def monitor_needs_action(self):
        """Monitor Needs_Action/cloud folder for new items"""
        try:
            if not self.needs_action_cloud.exists():
                return
            
            # Find all .md files
            items = list(self.needs_action_cloud.glob('*.md'))
            
            for item_file in items:
                if not self.running:
                    break
                
                logger.info(f"📧 Found new item: {item_file.name}")
                
                # Claim item (claim-by-move rule)
                if not self.claim_item(item_file):
                    continue
                
                self.stats['items_processed'] += 1
                
                # Create draft
                draft_file = self.create_draft(item_file)
                
                if draft_file:
                    # Create approval request
                    self.create_approval_request(draft_file)
                
                # Update stats
                self.stats['last_check'] = datetime.now().isoformat()
                
        except Exception as e:
            logger.error(f"❌ Error monitoring Needs_Action: {e}")
            self.stats['errors'] += 1
    
    def save_stats(self):
        """Save statistics to file"""
        stats_file = self.logs / 'cloud_stats.json'
        with open(stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def run(self):
        """Main run loop"""
        logger.info("🚀 Starting Cloud Orchestrator...")
        logger.info(f"⏱️ Check interval: {CHECK_INTERVAL} seconds")
        logger.info(f"🔒 Mode: Draft-Only (CANNOT execute)")
        
        try:
            while self.running:
                self.monitor_needs_action()
                self.save_stats()
                time.sleep(CHECK_INTERVAL)
            
            logger.info("🛑 Cloud Orchestrator stopped")
            self.save_stats()
            
        except Exception as e:
            logger.error(f"❌ Fatal error: {e}")
            self.save_stats()
            sys.exit(1)


def main():
    """Main entry point"""
    print("╔════════════════════════════════════════════════════════╗")
    print("║  ☁️  CLOUD ORCHESTRATOR - Platinum Tier               ║")
    print("║     Draft-Only Mode - 24/7 Operation                  ║")
    print("╚════════════════════════════════════════════════════════╝")
    print()
    
    orchestrator = CloudOrchestrator(VAULT_PATH)
    orchestrator.run()


if __name__ == '__main__':
    main()
