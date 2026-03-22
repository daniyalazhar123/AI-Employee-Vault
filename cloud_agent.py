#!/usr/bin/env python3
"""
☁️ CLOUD AGENT - Draft-Only Mode
Runs 24/7 on Oracle Cloud VM
Personal AI Employee Hackathon 0 - Platinum Tier

Responsibilities:
- Email triage and draft replies
- Social post drafts
- Odoo draft invoices
- NO final send permissions (security!)
"""

import os
import sys
import time
import shutil
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cloud_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('CloudAgent')


class CloudAgent:
    """
    Cloud Agent - Draft-Only Mode
    
    Runs on cloud VM 24/7, creating drafts that require
    Local Agent approval before execution.
    """
    
    def __init__(self, vault_path: str):
        self.vault = Path(vault_path)
        self.agent_id = 'cloud'
        self.agent_type = 'draft_only'
        
        # Platinum folder structure
        self.needs_action_cloud = self.vault / 'Needs_Action' / 'cloud'
        self.needs_action_local = self.vault / 'Needs_Action' / 'local'
        self.in_progress_cloud = self.vault / 'In_Progress' / 'cloud'
        self.in_progress_local = self.vault / 'In_Progress' / 'local'
        self.drafts = self.vault / 'Drafts'
        self.pending_approval = self.vault / 'Pending_Approval'
        self.approved = self.vault / 'Approved'
        self.done = self.vault / 'Done'
        self.updates = self.vault / 'Updates'
        self.signals = self.vault / 'Signals'
        self.logs = self.vault / 'Logs'
        self.dead_letter_queue = self.vault / 'Dead_Letter_Queue'
        
        # Ensure all folders exist
        self._ensure_folders()
        
        # Load environment
        self._load_env()
        
        # Statistics
        self.stats = {
            'items_processed': 0,
            'drafts_created': 0,
            'errors': 0,
            'start_time': datetime.now().isoformat()
        }
        
        logger.info("☁️  Cloud Agent initialized (Draft-Only Mode)")
        logger.info(f"📂 Vault path: {self.vault}")
        logger.info(f"📊 Stats: {self.stats}")
    
    def _ensure_folders(self):
        """Create all necessary folders for Platinum operation"""
        folders = [
            self.needs_action_cloud,
            self.needs_action_local,
            self.in_progress_cloud,
            self.in_progress_local,
            self.drafts / 'email',
            self.drafts / 'social',
            self.drafts / 'odoo',
            self.pending_approval,
            self.approved,
            self.done,
            self.updates,
            self.signals,
            self.logs,
            self.logs / 'Audit',
            self.dead_letter_queue
        ]
        for folder in folders:
            folder.mkdir(parents=True, exist_ok=True)
        logger.info("📁 All folders created/verified")
    
    def _load_env(self):
        """Load cloud environment variables from .env.cloud"""
        env_file = self.vault / '.env.cloud'
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
            logger.warning("⚠️ Cloud Agent will run with limited functionality")
    
    def claim_item(self, item_file: Path) -> bool:
        """
        Claim-by-move rule: First agent to move owns it
        
        Moves item from Needs_Action/cloud to In_Progress/cloud
        Returns True if successfully claimed
        """
        if item_file.suffix != '.md':
            return False
        
        try:
            dest = self.in_progress_cloud / item_file.name
            shutil.move(str(item_file), str(dest))
            
            # Log claim
            self._log_claim(item_file.name)
            logger.info(f"✅ Claimed: {item_file.name}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to claim {item_file.name}: {e}")
            return False
    
    def _log_claim(self, filename: str):
        """Log claim event to JSONL file"""
        log_file = self.logs / 'cloud_claims.jsonl'
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'claim',
            'file': filename,
            'agent': 'cloud',
            'mode': 'draft_only'
        }
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    def process_item(self, item_file: Path):
        """
        Process item based on type
        Routes to appropriate processor
        """
        filename = item_file.name.upper()
        
        try:
            if 'EMAIL' in filename:
                self.process_email(item_file)
            elif 'WHATSAPP' in filename:
                self.process_whatsapp(item_file)
            elif 'SOCIAL' in filename or 'POST' in filename or 'LINKEDIN' in filename:
                self.process_social_request(item_file)
            elif 'ODOO' in filename or 'INVOICE' in filename or 'PAYMENT' in filename:
                self.process_odoo_request(item_file)
            elif 'FILE' in filename:
                self.process_file_drop(item_file)
            else:
                logger.warning(f"⚠️ Unknown item type: {filename}")
                self.process_generic(item_file)
            
            self.stats['items_processed'] += 1
            
        except Exception as e:
            logger.error(f"❌ Error processing {item_file.name}: {e}", exc_info=True)
            self.stats['errors'] += 1
            self._move_to_dlq(item_file, str(e))
    
    def process_email(self, email_file: Path):
        """Process email and create draft reply"""
        logger.info(f"📧 Processing email: {email_file.name}")
        
        # Read email content
        content = email_file.read_text(encoding='utf-8')
        
        # Extract email details (simplified parsing)
        from_email = self._extract_field(content, 'from:')
        subject = self._extract_field(content, 'subject:')
        
        # Create draft reply
        draft_content = self._create_email_draft(from_email, subject, content)
        draft_file = self.drafts / 'email' / f"REPLY_{email_file.stem}.md"
        draft_file.write_text(draft_content, encoding='utf-8')
        
        # Create approval request
        self._create_approval_request('email', draft_file, email_file.name)
        
        self.stats['drafts_created'] += 1
        logger.info(f"✅ Email draft created: {draft_file.name}")
    
    def _extract_field(self, content: str, field: str) -> str:
        """Extract field from markdown frontmatter"""
        for line in content.split('\n'):
            if field.lower() in line.lower():
                return line.split(':', 1)[-1].strip()
        return 'Unknown'
    
    def _create_email_draft(self, to: str, subject: str, original_content: str) -> str:
        """Create professional email draft reply"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return f"""---
type: email_draft
to: {to}
subject: Re: {subject}
created_by: cloud_agent
created: {datetime.now().isoformat()}
status: draft
priority: normal
---

# ☁️ Email Draft (Cloud Agent)

**To:** {to}  
**Subject:** Re: {subject}  
**Created:** {timestamp}  
**Agent:** Cloud Agent (Draft-Only)

---

Dear Valued Client,

Thank you for your email. We have received your message and appreciate you reaching out to us.

Our team is currently reviewing your inquiry and will respond with a detailed answer within 24 hours.

If you have any urgent matters that require immediate attention, please don't hesitate to contact us directly.

## Original Message

```
{self._extract_email_body(original_content)}
```

---

Best regards,

**AI Employee Team**  
*Working 24/7 to serve you*

---
**⚠️ SECURITY NOTE:** This is a CLOUD DRAFT - requires Local Agent approval before sending  
**Draft Path:** `{self.drafts / 'email'}`  
**Approval Required:** Move to /Approved/ folder to send
"""
    
    def _extract_email_body(self, content: str) -> str:
        """Extract email body from content"""
        # Simple extraction - in production use proper parsing
        lines = content.split('\n')
        body_start = False
        body = []
        for line in lines:
            if '### Email Content' in line or '## Email Content' in line:
                body_start = True
                continue
            if body_start:
                body.append(line)
        return '\n'.join(body) if body else content[:500]
    
    def process_whatsapp(self, whatsapp_file: Path):
        """Process WhatsApp message and create draft response"""
        logger.info(f"💬 Processing WhatsApp: {whatsapp_file.name}")
        
        content = whatsapp_file.read_text(encoding='utf-8')
        
        # Create draft response
        draft_content = self._create_whatsapp_draft(content)
        draft_file = self.drafts / 'social' / f"WHATSAPP_REPLY_{whatsapp_file.stem}.md"
        draft_file.write_text(draft_content, encoding='utf-8')
        
        # Create approval request
        self._create_approval_request('whatsapp', draft_file, whatsapp_file.name)
        
        self.stats['drafts_created'] += 1
        logger.info(f"✅ WhatsApp draft created: {draft_file.name}")
    
    def _create_whatsapp_draft(self, content: str) -> str:
        """Create WhatsApp response draft"""
        return f"""---
type: whatsapp_draft
created_by: cloud_agent
created: {datetime.now().isoformat()}
status: draft
---

# 💬 WhatsApp Response Draft

**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Agent:** Cloud Agent (Draft-Only)

---

Hi! 👋

Thank you for your message. We've received it and will get back to you shortly.

If this is urgent, please let us know!

Best regards,  
AI Employee Team

---
**⚠️ SECURITY NOTE:** This is a CLOUD DRAFT - requires Local Agent approval before sending  
**WhatsApp session is LOCAL ONLY** for security
"""
    
    def process_social_request(self, social_file: Path):
        """Process social media request and create draft post"""
        logger.info(f"📱 Processing social request: {social_file.name}")
        
        content = social_file.read_text(encoding='utf-8')
        platform = self._detect_platform(content)
        
        # Create draft post
        draft_content = self._create_social_draft(content, platform)
        draft_file = self.drafts / 'social' / f"POST_{platform}_{social_file.stem}.md"
        draft_file.write_text(draft_content, encoding='utf-8')
        
        # Create approval request
        self._create_approval_request('social', draft_file, social_file.name)
        
        self.stats['drafts_created'] += 1
        logger.info(f"✅ {platform} draft created: {draft_file.name}")
    
    def _detect_platform(self, content: str) -> str:
        """Detect target platform from request"""
        content_lower = content.lower()
        if 'linkedin' in content_lower:
            return 'linkedin'
        elif 'facebook' in content_lower:
            return 'facebook'
        elif 'twitter' in content_lower or 'x.com' in content_lower:
            return 'twitter'
        elif 'instagram' in content_lower:
            return 'instagram'
        return 'multi'
    
    def _create_social_draft(self, content: str, platform: str) -> str:
        """Create social media post draft"""
        return f"""---
type: social_draft
platform: {platform}
created_by: cloud_agent
created: {datetime.now().isoformat()}
status: draft
---

# 📱 Social Media Post Draft ({platform})

**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Agent:** Cloud Agent (Draft-Only)

---

🚀 Exciting Update!

We're continuously improving our services to serve you better. Our AI Employee system now works 24/7 to ensure you never miss an opportunity!

✨ What we offer:
• Instant response to inquiries
• Professional communication
• Round-the-clock availability
• Secure and reliable service

Ready to experience the future? Get in touch!

#AI #Automation #Business #Innovation #DigitalTransformation #24x7

---
**⚠️ SECURITY NOTE:** This is a CLOUD DRAFT - requires Local Agent approval before posting
"""
    
    def process_odoo_request(self, odoo_file: Path):
        """Process Odoo request and create draft action"""
        logger.info(f"📊 Processing Odoo request: {odoo_file.name}")
        
        content = odoo_file.read_text(encoding='utf-8')
        
        # Create draft action
        draft_content = self._create_odoo_draft(content)
        draft_file = self.drafts / 'odoo' / f"ODOO_DRAFT_{odoo_file.stem}.md"
        draft_file.write_text(draft_content, encoding='utf-8')
        
        # Create approval request
        self._create_approval_request('odoo', draft_file, odoo_file.name)
        
        self.stats['drafts_created'] += 1
        logger.info(f"✅ Odoo draft created: {draft_file.name}")
    
    def _create_odoo_draft(self, content: str) -> str:
        """Create Odoo action draft"""
        return f"""---
type: odoo_draft
action: invoice_or_payment
created_by: cloud_agent
created: {datetime.now().isoformat()}
status: draft
---

# 📊 Odoo Action Draft

**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Agent:** Cloud Agent (Draft-Only)

---

## Draft Action Details

This Odoo action has been prepared and requires Local Agent approval for execution.

**Security:** Cloud Agent has DRAFT-ONLY permissions for Odoo.  
**Execution:** Local Agent will execute after human approval.

---
**⚠️ SECURITY NOTE:** This is a CLOUD DRAFT - requires Local Agent approval before execution
"""
    
    def process_file_drop(self, file_file: Path):
        """Process file drop and create acknowledgment"""
        logger.info(f"📁 Processing file drop: {file_file.name}")
        
        # Create acknowledgment
        self._create_approval_request('file', file_file, file_file.name)
        self.stats['drafts_created'] += 1
    
    def process_generic(self, item_file: Path):
        """Process generic item"""
        logger.info(f"📄 Processing generic item: {item_file.name}")
        
        # Create generic approval request
        self._create_approval_request('generic', item_file, item_file.name)
        self.stats['drafts_created'] += 1
    
    def _create_approval_request(self, draft_type: str, draft_path: Path, original: str):
        """Create approval request for Local Agent"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        approval_file = self.pending_approval / f"CLOUD_{draft_type.upper()}_{timestamp}.md"
        
        content = f"""---
type: cloud_approval_request
draft_type: {draft_type}
draft_path: {draft_path}
original_file: {original}
created_by: cloud_agent
created: {datetime.now().isoformat()}
status: pending
agent_mode: draft_only
---

# ☁️ Cloud Agent Approval Request

| Field | Value |
|-------|-------|
| **Draft Type** | {draft_type} |
| **Draft File** | `{draft_path}` |
| **Original Item** | `{original}` |
| **Created** | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
| **Agent** | Cloud Agent (Draft-Only) |

---

## What Happened

The Cloud Agent detected an item requiring action and created a draft response.

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
**📊 Stats:** Items processed: {self.stats['items_processed']}, Drafts created: {self.stats['drafts_created']}
"""
        approval_file.write_text(content, encoding='utf-8')
        logger.info(f"✅ Approval request created: {approval_file.name}")
    
    def write_update(self, update_type: str, data: Dict):
        """Write update to /Updates/ for Local to merge into Dashboard"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        update_file = self.updates / f"{update_type}_{timestamp}.md"
        
        content = f"""---
type: cloud_update
update_type: {update_type}
timestamp: {datetime.now().isoformat()}
agent: cloud
---

# ☁️ Cloud Update

**Type:** {update_type}  
**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Agent:** Cloud Agent

---

**Data:**
```json
{json.dumps(data, indent=2)}
```

---
Local Agent: Please merge this update into Dashboard.md
"""
        update_file.write_text(content, encoding='utf-8')
        logger.info(f"📝 Update written: {update_file.name}")
    
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
                'agent': 'cloud'
            }
            with open(error_log, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
            
            logger.error(f"❌ Moved to DLQ: {dlq_file.name}")
        except Exception as e:
            logger.error(f"❌ Failed to move to DLQ: {e}")
    
    def save_stats(self):
        """Save agent statistics"""
        stats_file = self.logs / 'cloud_agent_stats.json'
        self.stats['last_updated'] = datetime.now().isoformat()
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2)
    
    def run(self):
        """Main Cloud Agent loop - runs 24/7"""
        logger.info("="*60)
        logger.info("☁️  CLOUD AGENT STARTING (24/7 MODE)")
        logger.info(f"📂 Vault: {self.vault}")
        logger.info(f"🎯 Mode: Draft-Only (No Send/Execute)")
        logger.info("="*60)
        
        while True:
            try:
                # Check for new items in Needs_Action/cloud
                if self.needs_action_cloud.exists():
                    items = list(self.needs_action_cloud.glob('*.md'))
                    
                    for item in items:
                        if self.claim_item(item):
                            logger.info(f"🔄 Processing: {item.name}")
                            self.process_item(item)
                
                # Write periodic health update
                self.write_update('health', {
                    'status': 'healthy',
                    'timestamp': datetime.now().isoformat(),
                    'items_processed': self.stats['items_processed'],
                    'drafts_created': self.stats['drafts_created'],
                    'errors': self.stats['errors']
                })
                
                # Save stats every 5 minutes
                self.save_stats()
                
                # Log status every 10 minutes
                if self.stats['items_processed'] % 10 == 0:
                    logger.info(f"📊 Status: {self.stats['items_processed']} items, "
                               f"{self.stats['drafts_created']} drafts, "
                               f"{self.stats['errors']} errors")
                
            except KeyboardInterrupt:
                logger.info("⏹️  Cloud Agent stopped by user")
                self.save_stats()
                break
            except Exception as e:
                logger.error(f"❌ Cloud Agent error: {e}", exc_info=True)
                self.stats['errors'] += 1
            
            time.sleep(60)  # Check every minute
        
        logger.info("☁️  Cloud Agent shutdown complete")


def main():
    """Main entry point"""
    print("="*60)
    print("☁️  PLATINUM TIER - CLOUD AGENT")
    print("🎯 Mode: Draft-Only (No Send/Execute)")
    print("="*60)
    
    # Get vault path from argument or use default
    vault_path = sys.argv[1] if len(sys.argv) > 1 else '/home/ubuntu/ai-employee-vault'
    
    print(f"📂 Vault Path: {vault_path}")
    print("\n🚀 Starting Cloud Agent in 3 seconds...")
    time.sleep(3)
    
    agent = CloudAgent(vault_path)
    
    try:
        agent.run()
    except KeyboardInterrupt:
        logger.info("⏹️  Cloud Agent stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
