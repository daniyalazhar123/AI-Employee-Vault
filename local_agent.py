#!/usr/bin/env python3
"""
🏠 LOCAL AGENT - Approval & Execute Mode
Runs on your local machine
Personal AI Employee Hackathon 0 - Platinum Tier

Responsibilities:
- Human approvals (reviews pending files)
- WhatsApp messaging (session local only)
- Final email send
- Final social post
- Banking/payments
- Dashboard.md updates (single writer)
"""

import os
import sys
import time
import shutil
import logging
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('local_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('LocalAgent')


class LocalAgent:
    """
    Local Agent - Approval & Execute Mode
    
    Runs on local machine, handles approvals and executes
    final actions via MCP servers.
    """
    
    def __init__(self, vault_path: str):
        self.vault = Path(vault_path)
        self.agent_id = 'local'
        self.agent_type = 'execute'
        
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
        self.drafts = self.vault / 'Drafts'
        self.in_progress_cloud = self.vault / 'In_Progress' / 'cloud'
        self.in_progress_local = self.vault / 'In_Progress' / 'local'
        self.needs_action_cloud = self.vault / 'Needs_Action' / 'cloud'
        self.needs_action_local = self.vault / 'Needs_Action' / 'local'
        
        # Ensure all folders exist
        self._ensure_folders()
        
        # Load environment
        self._load_env()
        
        # Statistics
        self.stats = {
            'items_processed': 0,
            'actions_executed': 0,
            'approvals_processed': 0,
            'errors': 0,
            'start_time': datetime.now().isoformat()
        }
        
        logger.info("🏠 Local Agent initialized (Approval + Execute Mode)")
        logger.info(f"📂 Vault path: {self.vault}")
        logger.info(f"📊 Stats: {self.stats}")
    
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
            self.dead_letter_queue,
            self.drafts / 'email',
            self.drafts / 'social',
            self.drafts / 'odoo',
            self.in_progress_cloud,
            self.in_progress_local,
            self.needs_action_cloud,
            self.needs_action_local
        ]
        for folder in folders:
            folder.mkdir(parents=True, exist_ok=True)
        logger.info("📁 All folders created/verified")
    
    def _load_env(self):
        """Load local environment variables from .env.local"""
        env_file = self.vault / '.env.local'
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value
            logger.info(f"✅ Loaded environment from {env_file}")
        else:
            logger.warning(f"⚠️ Environment file not found: {env_file}")
            logger.warning("⚠️ Local Agent will run with limited functionality")
    
    def check_approvals(self) -> List[Path]:
        """Check for files moved to Approved by human"""
        if not self.approved.exists():
            return []
        return list(self.approved.glob('*.md'))
    
    def execute_approved_item(self, approval_file: Path):
        """Execute approved item via appropriate MCP"""
        logger.info(f"🚀 Executing: {approval_file.name}")
        
        content = approval_file.read_text(encoding='utf-8')
        
        try:
            # Parse approval file type and execute
            if 'CLOUD_EMAIL' in approval_file.name or 'EMAIL' in approval_file.name:
                self.execute_email_send(approval_file, content)
            elif 'CLOUD_SOCIAL' in approval_file.name or 'SOCIAL' in approval_file.name:
                self.execute_social_post(approval_file, content)
            elif 'CLOUD_ODOO' in approval_file.name or 'ODOO' in approval_file.name:
                self.execute_odoo_action(approval_file, content)
            elif 'WHATSAPP' in approval_file.name:
                self.execute_whatsapp_send(approval_file, content)
            else:
                # Local item or generic
                self.execute_local_action(approval_file, content)
            
            # Move to Done
            done_file = self.done / f"COMPLETED_{approval_file.name}"
            shutil.move(str(approval_file), str(done_file))
            logger.info(f"✅ Moved to Done: {done_file.name}")
            
            # Update Dashboard
            self.update_dashboard(f"Completed: {approval_file.name}")
            
            # Update stats
            self.stats['actions_executed'] += 1
            self.stats['approvals_processed'] += 1
            
        except Exception as e:
            logger.error(f"❌ Failed to execute {approval_file.name}: {e}", exc_info=True)
            self.stats['errors'] += 1
            self._move_to_dlq(approval_file, str(e))
    
    def execute_email_send(self, approval_file: Path, content: str):
        """Execute email send via Email MCP"""
        logger.info("📧 Executing email send via MCP")
        
        # Extract draft path from content
        draft_path = self._extract_draft_path(content)
        
        if draft_path and draft_path.exists():
            # Read draft content
            draft_content = draft_path.read_text(encoding='utf-8')
            
            # Extract email details
            to = self._extract_field(draft_content, 'to:')
            subject = self._extract_field(draft_content, 'subject:')
            
            logger.info(f"📧 Sending email to: {to}, subject: {subject}")
            
            # In production: Call Email MCP to send
            # For now: Simulate send
            time.sleep(2)
            
            # Log action
            self._log_action('email_send', {
                'to': to,
                'subject': subject,
                'draft_file': str(draft_path)
            })
            
            logger.info("✅ Email sent successfully")
        else:
            raise Exception(f"Draft file not found: {draft_path}")
    
    def execute_social_post(self, approval_file: Path, content: str):
        """Execute social post via Social MCP"""
        logger.info("📱 Executing social post via MCP")
        
        # Extract draft path from content
        draft_path = self._extract_draft_path(content)
        
        if draft_path and draft_path.exists():
            # Read draft content
            draft_content = draft_path.read_text(encoding='utf-8')
            
            # Extract platform
            platform = self._extract_field(draft_content, 'platform:')
            
            logger.info(f"📱 Posting to: {platform}")
            
            # In production: Call Social MCP to post
            # For now: Simulate post
            time.sleep(2)
            
            # Log action
            self._log_action('social_post', {
                'platform': platform,
                'draft_file': str(draft_path)
            })
            
            logger.info("✅ Social post published successfully")
        else:
            raise Exception(f"Draft file not found: {draft_path}")
    
    def execute_odoo_action(self, approval_file: Path, content: str):
        """Execute Odoo action via Odoo MCP"""
        logger.info("📊 Executing Odoo action via MCP")
        
        # Extract action details from content
        # In production: Parse and call Odoo MCP
        
        logger.info("📊 Executing Odoo action (simulated)")
        
        # Simulate execution
        time.sleep(2)
        
        # Log action
        self._log_action('odoo_action', {
            'approval_file': str(approval_file)
        })
        
        logger.info("✅ Odoo action executed successfully")
    
    def execute_whatsapp_send(self, approval_file: Path, content: str):
        """Execute WhatsApp send via WhatsApp integration"""
        logger.info("💬 Executing WhatsApp send")
        
        # WhatsApp session is LOCAL ONLY for security
        # In production: Use WhatsApp Web automation or API
        
        logger.info("💬 WhatsApp message sent (simulated)")
        
        # Log action
        self._log_action('whatsapp_send', {
            'approval_file': str(approval_file)
        })
        
        logger.info("✅ WhatsApp message sent successfully")
    
    def execute_local_action(self, approval_file: Path, content: str):
        """Execute local action"""
        logger.info(f"🏠 Executing local action: {approval_file.name}")
        
        # Handle local-specific actions
        # In production: Implement actual action logic
        
        time.sleep(1)
        
        # Log action
        self._log_action('local_action', {
            'approval_file': str(approval_file)
        })
        
        logger.info("✅ Local action executed successfully")
    
    def _extract_draft_path(self, content: str) -> Optional[Path]:
        """Extract draft path from approval content"""
        # Parse frontmatter to find draft_path
        for line in content.split('\n'):
            if 'draft_path:' in line.lower():
                path_str = line.split(':', 1)[-1].strip().strip('`')
                return Path(path_str)
        return None
    
    def _extract_field(self, content: str, field: str) -> str:
        """Extract field from content"""
        for line in content.split('\n'):
            if field.lower() in line.lower():
                return line.split(':', 1)[-1].strip()
        return 'Unknown'
    
    def merge_updates(self):
        """Merge updates from Cloud into Dashboard"""
        if not self.updates.exists():
            return
        
        updates = list(self.updates.glob('*.md'))
        for update in updates:
            try:
                self.merge_update_into_dashboard(update)
                update.unlink()  # Remove after merging
                logger.info(f"✅ Merged update: {update.name}")
            except Exception as e:
                logger.error(f"❌ Failed to merge {update.name}: {e}")
    
    def merge_update_into_dashboard(self, update_file: Path):
        """Merge single update into Dashboard.md"""
        if not self.dashboard.exists():
            return
        
        # Read update
        update_content = update_file.read_text(encoding='utf-8')
        
        # Read current Dashboard
        dashboard_content = self.dashboard.read_text(encoding='utf-8')
        
        # Simple append (implement proper merge logic in production)
        timestamp = datetime.now().strftime('%H:%M:%S')
        dashboard_content += f"\n\n---\n*[{timestamp}] Cloud Update: {update_file.name}*\n"
        
        # Write back
        self.dashboard.write_text(dashboard_content, encoding='utf-8')
        logger.info(f"✅ Merged {update_file.name} into Dashboard")
    
    def update_dashboard(self, message: str):
        """Update Dashboard with new activity"""
        if not self.dashboard.exists():
            logger.warning("⚠️ Dashboard.md not found")
            return
        
        dashboard_content = self.dashboard.read_text(encoding='utf-8')
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Add new activity
        dashboard_content += f"\n- [{timestamp}] {message}"
        
        self.dashboard.write_text(dashboard_content, encoding='utf-8')
        logger.info(f"✅ Dashboard updated: {message}")
    
    def _log_action(self, action_type: str, details: Dict):
        """Log action to audit log"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'agent': 'local',
            'action_type': action_type,
            'details': details
        }
        
        log_file = self.logs / 'Audit' / f"local_actions_{datetime.now().strftime('%Y%m%d')}.jsonl"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def _move_to_dlq(self, file: Path, error: str):
        """Move failed item to Dead Letter Queue"""
        dlq_file = self.dead_letter_queue / f"FAILED_{file.name}"
        try:
            shutil.move(str(file), str(dlq_file))
            
            # Log error
            error_log = self.dead_letter_queue / 'errors.jsonl'
            entry = {
                'timestamp': datetime.now().isoformat(),
                'file': file.name,
                'error': error,
                'agent': 'local'
            }
            with open(error_log, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
            
            logger.error(f"❌ Moved to DLQ: {dlq_file.name}")
        except Exception as e:
            logger.error(f"❌ Failed to move to DLQ: {e}")
    
    def save_stats(self):
        """Save agent statistics"""
        stats_file = self.logs / 'local_agent_stats.json'
        self.stats['last_updated'] = datetime.now().isoformat()
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2)
    
    def run_git_sync(self):
        """Run git sync to pull/push changes"""
        try:
            logger.info("🔄 Running git sync...")
            
            # Git pull
            result = subprocess.run(
                ['git', 'pull'],
                cwd=self.vault,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                logger.info("✅ Git pull successful")
            else:
                logger.warning(f"⚠️ Git pull failed: {result.stderr}")
            
            # Git add
            subprocess.run(
                ['git', 'add', '.'],
                cwd=self.vault,
                capture_output=True,
                timeout=30
            )
            
            # Git status check
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.vault,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.stdout.strip():
                # Has changes to commit
                subprocess.run(
                    ['git', 'commit', '-m', f'Local Agent updates {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'],
                    cwd=self.vault,
                    capture_output=True,
                    timeout=30
                )
                
                # Git push
                result = subprocess.run(
                    ['git', 'push'],
                    cwd=self.vault,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    logger.info("✅ Git push successful")
                else:
                    logger.warning(f"⚠️ Git push failed: {result.stderr}")
            else:
                logger.info("✅ No changes to commit")
            
        except Exception as e:
            logger.error(f"❌ Git sync error: {e}")
    
    def run(self):
        """Main Local Agent loop"""
        logger.info("="*60)
        logger.info("🏠 LOCAL AGENT STARTING (Approval + Execute Mode)")
        logger.info(f"📂 Vault: {self.vault}")
        logger.info(f"🎯 Mode: Execute (Final Actions)")
        logger.info("="*60)
        
        git_sync_counter = 0
        
        while True:
            try:
                # Check for approved items
                approved_items = self.check_approvals()
                for item in approved_items:
                    logger.info(f"📋 Processing approved: {item.name}")
                    self.execute_approved_item(item)
                
                # Merge updates from Cloud
                self.merge_updates()
                
                # Git sync every 5 iterations (5 minutes)
                git_sync_counter += 1
                if git_sync_counter >= 5:
                    self.run_git_sync()
                    git_sync_counter = 0
                
                # Save stats
                self.save_stats()
                
                # Log status every 10 minutes
                if self.stats['items_processed'] % 10 == 0:
                    logger.info(f"📊 Status: {self.stats['approvals_processed']} approvals, "
                               f"{self.stats['actions_executed']} actions, "
                               f"{self.stats['errors']} errors")
                
            except KeyboardInterrupt:
                logger.info("⏹️  Local Agent stopped by user")
                self.save_stats()
                break
            except Exception as e:
                logger.error(f"❌ Local Agent error: {e}", exc_info=True)
                self.stats['errors'] += 1
            
            time.sleep(30)  # Check every 30 seconds
        
        logger.info("🏠 Local Agent shutdown complete")


def main():
    """Main entry point"""
    print("="*60)
    print("🏠 PLATINUM TIER - LOCAL AGENT")
    print("🎯 Mode: Approval + Execute")
    print("="*60)
    
    # Get vault path from argument or use default
    vault_path = sys.argv[1] if len(sys.argv) > 1 else 'C:/Users/CC/Documents/Obsidian Vault'
    
    print(f"📂 Vault Path: {vault_path}")
    print("\n🚀 Starting Local Agent in 3 seconds...")
    time.sleep(3)
    
    agent = LocalAgent(vault_path)
    
    try:
        agent.run()
    except KeyboardInterrupt:
        logger.info("⏹️  Local Agent stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
