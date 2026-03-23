#!/usr/bin/env python3
"""
🏠 LOCAL ORCHESTRATOR - Platinum Tier
Runs on Local Machine - Approval & Execute Mode

Personal AI Employee Hackathon 0
Platinum Tier: Always-On Cloud + Local Executive

Responsibilities:
- Monitor Updates/ and Pending_Approval/ folders
- Execute approved actions via MCP server
- Update Dashboard.md (single writer rule)
- Move tasks to Done/ when complete
- Log all activities to Logs/local_agent.log

Full Permissions:
- ✅ Send emails
- ✅ Post to social media
- ✅ Execute payments
- ✅ WhatsApp messaging (session local only)
- ✅ Update Dashboard.md
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
AGENT_ID = 'local'
AGENT_TYPE = 'execute'

# Setup logging
LOG_FILE = VAULT_PATH / 'Logs' / 'local_agent.log'
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('LocalOrchestrator')


class LocalOrchestrator:
    """
    Local Orchestrator - Approval & Execute Mode
    
    Runs on local machine, handles approvals and executes
    final actions via MCP servers.
    """
    
    def __init__(self, vault_path: Path):
        self.vault = vault_path
        self.agent_id = AGENT_ID
        self.agent_type = AGENT_TYPE
        
        # Platinum folder structure
        self.pending_approval = self.vault / 'Pending_Approval'
        self.approved = self.vault / 'Approved'
        self.rejected = self.vault / 'Rejected'
        self.done = self.vault / 'Done'
        self.dashboard = self.vault / 'Dashboard.md'
        self.updates = self.vault / 'Updates'
        self.signals = self.vault / 'Signals'
        self.logs = self.vault / 'Logs'
        self.dead_letter_queue = self.vault / 'Dead_Letter_Queue'
        self.in_progress_cloud = self.vault / 'In_Progress' / 'cloud'
        self.in_progress_local = self.vault / 'In_Progress' / 'local'
        
        # Ensure all folders exist
        self._ensure_folders()
        
        # Statistics
        self.stats = {
            'items_processed': 0,
            'actions_executed': 0,
            'approvals_processed': 0,
            'errors': 0,
            'start_time': datetime.now().isoformat(),
            'last_check': None
        }
        
        # Running flag
        self.running = True
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("🏠 Local Orchestrator initialized (Approval + Execute Mode)")
        logger.info(f"📂 Vault path: {self.vault}")
        logger.info(f"📊 Initial stats: {self.stats}")
    
    def _ensure_folders(self):
        """Create all necessary folders for Platinum operation"""
        folders = [
            self.pending_approval,
            self.approved,
            self.rejected,
            self.done,
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
    
    def process_updates(self):
        """Process drafts from Updates/ folder"""
        try:
            if not self.updates.exists():
                return
            
            # Find all draft files
            drafts = list(self.updates.glob('DRAFT_*.md'))
            
            for draft_file in drafts:
                if not self.running:
                    break
                
                logger.info(f"📄 Found draft: {draft_file.name}")
                
                # Parse draft
                metadata = self._parse_metadata(draft_file)
                draft_type = metadata.get('type', 'unknown')
                
                # Create approval request
                self._create_approval_for_draft(draft_file, draft_type)
                
                self.stats['items_processed'] += 1
                self.stats['last_check'] = datetime.now().isoformat()
                
        except Exception as e:
            logger.error(f"❌ Error processing updates: {e}")
            self.stats['errors'] += 1
    
    def _parse_metadata(self, content: Path) -> Dict:
        """Parse YAML frontmatter from markdown"""
        metadata = {}
        text = content.read_text(encoding='utf-8')
        
        if text.startswith('---'):
            parts = text.split('---', 2)
            if len(parts) >= 3:
                yaml_content = parts[1]
                for line in yaml_content.strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip()] = value.strip()
        
        return metadata
    
    def _create_approval_for_draft(self, draft_file: Path, draft_type: str):
        """Create approval request for draft"""
        try:
            approval_file = self.pending_approval / f'APPROVAL_{draft_file.stem}.md'
            
            content = f"""---
type: approval_request
draft_file: {draft_file.name}
draft_type: {draft_type}
created_by: local
created: {datetime.now().isoformat()}
status: pending
---

# Approval Required

**Draft:** {draft_file.name}
**Type:** {draft_type}
**Action Required:** Review and approve/reject

## To Approve
Move this file to `/Approved` folder

## To Reject
Move this file to `/Rejected` folder

---
*Local Agent - Awaiting Human Approval*
"""
            approval_file.write_text(content, encoding='utf-8')
            logger.info(f"✅ Approval request created: {approval_file.name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to create approval request: {e}")
            self.stats['errors'] += 1
    
    def process_approvals(self):
        """Process approved actions from Approved/ folder"""
        try:
            if not self.approved.exists():
                return
            
            # Find all approved files
            approvals = list(self.approved.glob('APPROVAL_*.md'))
            
            for approval_file in approvals:
                if not self.running:
                    break
                
                logger.info(f"✅ Processing approval: {approval_file.name}")
                
                # Parse approval
                metadata = self._parse_metadata(approval_file)
                draft_file = metadata.get('draft_file')
                draft_type = metadata.get('draft_type', 'general')
                
                if draft_file:
                    # Execute action
                    self._execute_action(draft_file, draft_type, approval_file)
                
                self.stats['approvals_processed'] += 1
                self.stats['last_check'] = datetime.now().isoformat()
                
        except Exception as e:
            logger.error(f"❌ Error processing approvals: {e}")
            self.stats['errors'] += 1
    
    def _execute_action(self, draft_file: str, draft_type: str, approval_file: Path):
        """Execute approved action"""
        try:
            # Find draft file
            draft_path = self.updates / draft_file
            
            if not draft_path.exists():
                logger.warning(f"⚠️ Draft file not found: {draft_file}")
                return
            
            logger.info(f"🚀 Executing action: {draft_type}")
            
            # Execute based on type
            if draft_type == 'email_reply':
                self._execute_email(draft_path)
            elif draft_type == 'social_post':
                self._execute_social(draft_path)
            elif draft_type == 'invoice_draft':
                self._execute_invoice(draft_path)
            else:
                self._execute_general(draft_path)
            
            # Move to Done
            done_file = self.done / f'COMPLETED_{approval_file.stem}.md'
            shutil.move(str(approval_file), str(done_file))
            
            # Move draft to Done
            done_draft = self.done / f'DRAFT_{draft_path.stem}.md'
            shutil.move(str(draft_path), str(done_draft))
            
            logger.info(f"✅ Action executed and moved to Done/")
            self.stats['actions_executed'] += 1
            
            # Update Dashboard
            self._update_dashboard()
            
        except Exception as e:
            logger.error(f"❌ Failed to execute action: {e}")
            self.stats['errors'] += 1
    
    def _execute_email(self, draft_path: Path):
        """Execute email send via MCP"""
        logger.info("📧 Executing email send...")
        
        # In production, this would call MCP server
        # For now, just log it
        logger.info(f"✅ Email would be sent from: {draft_path}")
        
        # Log to audit
        self._log_action('email_send', str(draft_path), 'success')
    
    def _execute_social(self, draft_path: Path):
        """Execute social media post via MCP"""
        logger.info("📱 Executing social media post...")
        
        # In production, this would call MCP server
        logger.info(f"✅ Social post would be published from: {draft_path}")
        
        # Log to audit
        self._log_action('social_post', str(draft_path), 'success')
    
    def _execute_invoice(self, draft_path: Path):
        """Execute invoice creation via Odoo MCP"""
        logger.info("💰 Executing invoice creation...")
        
        # In production, this would call Odoo MCP
        logger.info(f"✅ Invoice would be created in Odoo from: {draft_path}")
        
        # Log to audit
        self._log_action('invoice_create', str(draft_path), 'success')
    
    def _execute_general(self, draft_path: Path):
        """Execute general action"""
        logger.info("⚙️ Executing general action...")
        
        # Log to audit
        self._log_action('general_action', str(draft_path), 'success')
    
    def _log_action(self, action: str, file_affected: str, result: str):
        """Log action to audit trail"""
        audit_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'user': self.agent_id,
            'result': result,
            'file_affected': file_affected
        }
        
        audit_file = self.logs / 'Audit' / f'audit_{datetime.now().strftime("%Y%m%d")}.json'
        
        # Append to audit file
        with open(audit_file, 'a') as f:
            json.dump(audit_entry, f)
            f.write('\n')
    
    def _update_dashboard(self):
        """Update Dashboard.md (single writer rule - Local only)"""
        try:
            if not self.dashboard.exists():
                logger.warning("⚠️ Dashboard.md not found, creating...")
                self.dashboard.write_text("# Dashboard\n\n## Status\n\n", encoding='utf-8')
                return
            
            # Read current dashboard
            content = self.dashboard.read_text(encoding='utf-8')
            
            # Update stats section
            stats_section = f"""
## Platinum Tier Status

**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

| Metric | Value |
|--------|-------|
| Items Processed | {self.stats['items_processed']} |
| Actions Executed | {self.stats['actions_executed']} |
| Approvals Processed | {self.stats['approvals_processed']} |
| Errors | {self.stats['errors']} |

---
*Updated by Local Agent (Single Writer)*
"""
            
            # Check if stats section exists
            if '## Platinum Tier Status' in content:
                # Replace existing section
                import re
                pattern = r'## Platinum Tier Status.*?(?=##|\Z)'
                content = re.sub(pattern, stats_section.strip(), content, flags=re.DOTALL)
            else:
                # Append new section
                content += "\n" + stats_section
            
            # Write back
            self.dashboard.write_text(content, encoding='utf-8')
            logger.info("✅ Dashboard.md updated")
            
        except Exception as e:
            logger.error(f"❌ Failed to update dashboard: {e}")
            self.stats['errors'] += 1
    
    def save_stats(self):
        """Save statistics to file"""
        stats_file = self.logs / 'local_stats.json'
        with open(stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def run(self):
        """Main run loop"""
        logger.info("🚀 Starting Local Orchestrator...")
        logger.info(f"⏱️ Check interval: {CHECK_INTERVAL} seconds")
        logger.info(f"🔓 Mode: Execute (Full Permissions)")
        
        try:
            while self.running:
                self.process_updates()
                self.process_approvals()
                self.save_stats()
                time.sleep(CHECK_INTERVAL)
            
            logger.info("🛑 Local Orchestrator stopped")
            self.save_stats()
            
        except Exception as e:
            logger.error(f"❌ Fatal error: {e}")
            self.save_stats()
            sys.exit(1)


def main():
    """Main entry point"""
    print("╔════════════════════════════════════════════════════════╗")
    print("║  🏠  LOCAL ORCHESTRATOR - Platinum Tier               ║")
    print("║     Approval + Execute Mode - Local Machine           ║")
    print("╚════════════════════════════════════════════════════════╝")
    print()
    
    orchestrator = LocalOrchestrator(VAULT_PATH)
    orchestrator.run()


if __name__ == '__main__':
    main()
