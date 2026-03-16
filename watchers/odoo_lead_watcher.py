"""
Odoo Lead Watcher for AI Employee Vault

Monitors Odoo CRM for new leads and creates action items.
Features:
- XML-RPC integration with Odoo
- Robust error handling with retry logic
- JSON logging to /Logs/ folder
- Graceful fallback to placeholder mode
"""

import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

try:
    import xmlrpc.client
    ODOO_AVAILABLE = True
except ImportError:
    ODOO_AVAILABLE = False
    xmlrpc = None

from base_watcher import BaseWatcher, ConfigurationError, ConnectionError


# Configuration
ODOO_CONFIG = {
    'url': 'http://localhost:8069',
    'db': 'odoo',
    'username': 'admin',
    'password': 'admin',
}
MAX_LEADS_PER_RUN = 10
MAX_RETRIES = 3


class OdooLeadWatcher(BaseWatcher):
    """Odoo CRM lead monitoring watcher."""
    
    def __init__(self, vault_path: Optional[Path] = None):
        super().__init__('odoo', vault_path)
        
        self.needs_action_folder = self.vault_path / 'Needs_Action'
        self.pending_approval_folder = self.vault_path / 'Pending_Approval'
        self.dashboard_file = self.vault_path / 'docs' / 'Dashboard.md'
        self.processed_file = self.vault_path / 'data' / 'processed_odoo_leads.txt'
        
        self.processed_ids: Set[str] = set()
        self.odoo_connected = False
        self.common = None
        self.models = None
        self.uid = None
        
        # Ensure folders exist
        self.needs_action_folder.mkdir(exist_ok=True)
        self.pending_approval_folder.mkdir(exist_ok=True)
    
    def connect(self) -> bool:
        """
        Connect to Odoo via XML-RPC.
        
        Returns:
            True if connection successful
        """
        if not ODOO_AVAILABLE:
            self.log_warning("Odoo library not available - using placeholder mode")
            self.log_info("Install with: pip install odoo")
            return False
        
        try:
            url = ODOO_CONFIG['url']
            db = ODOO_CONFIG['db']
            username = ODOO_CONFIG['username']
            password = ODOO_CONFIG['password']
            
            self.log_info(f"Connecting to Odoo at {url}...")
            
            # Authenticate
            self.common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
            self.uid = self.common.authenticate(db, username, password, {})
            
            if not self.uid:
                raise ConnectionError("Odoo authentication failed - check credentials")
            
            # Get models endpoint
            self.models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
            
            self.log_info(f"✅ Odoo connected successfully (User ID: {self.uid})")
            self.odoo_connected = True
            return True
            
        except ConfigurationError as e:
            self.log_error(str(e), exc=e)
            return False
        except ConnectionError as e:
            self.log_error(str(e), exc=e)
            return False
        except Exception as e:
            self.log_error(f"Odoo connection failed: {e}", exc=e)
            return False
    
    def fetch_leads(self) -> List[Dict]:
        """
        Fetch new leads from Odoo CRM.
        
        Returns:
            List of lead dictionaries
        """
        if not self.odoo_connected or not self.models:
            return []
        
        def _fetch():
            domain = [('id', 'not in', list(self.processed_ids))]
            
            leads = self.models.execute_kw(
                ODOO_CONFIG['db'],
                self.uid,
                ODOO_CONFIG['password'],
                'crm.lead',
                'search_read',
                [domain],
                {
                    'fields': [
                        'id', 'name', 'partner_name', 'email_from',
                        'phone', 'company_name', 'description',
                        'priority', 'stage_id', 'create_date'
                    ],
                    'limit': MAX_LEADS_PER_RUN
                }
            )
            
            return leads
        
        try:
            leads = self.with_retry(
                _fetch,
                max_retries=MAX_RETRIES,
                retryable_exceptions=(Exception,)  # XML-RPC errors
            )
            
            if leads:
                self.log_info(f"Found {len(leads)} new lead(s)")
            else:
                self.log_info("No new leads found")
            
            return leads
            
        except Exception as e:
            self.log_error(f"Failed to fetch leads: {e}", exc=e)
            return []
    
    def create_lead_action_file(self, lead: Dict) -> Optional[Path]:
        """
        Create action file for Odoo lead.
        
        Args:
            lead: Lead dictionary from Odoo
        
        Returns:
            Path to action file or None if failed
        """
        try:
            lead_id = lead.get('id', 'UNKNOWN')
            lead_name = lead.get('name', 'New Lead')
            partner_name = lead.get('partner_name', 'N/A')
            email = lead.get('email_from', 'N/A')
            phone = lead.get('phone', 'N/A')
            company = lead.get('company_name', 'N/A')
            description = lead.get('description', '')
            priority = lead.get('priority', '0')
            
            # Handle stage_id (can be list or string)
            stage_id = lead.get('stage_id')
            stage = stage_id[1] if isinstance(stage_id, list) and len(stage_id) > 1 else str(stage_id or 'N/A')
            
            create_date = lead.get('create_date', '')
            
            filename = f"ODOO_LEAD_{lead_id}.md"
            filepath = self.needs_action_folder / filename
            
            content = f"""---
type: odoo_lead
lead_id: {lead_id}
lead_name: {lead_name}
partner_name: {partner_name}
email: {email}
phone: {phone}
company: {company}
priority: {priority}
stage: {stage}
create_date: {create_date}
status: pending
created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
---

# Odoo Lead: {lead_name}

## Lead Details
| Field | Value |
|-------|-------|
| **Lead ID** | {lead_id} |
| **Partner Name** | {partner_name} |
| **Company** | {company} |
| **Email** | {email} |
| **Phone** | {phone} |
| **Priority** | {priority}/5 |
| **Stage** | {stage} |
| **Created** | {create_date} |

## Description
{description if description else '*No description provided*'}

## Suggested Actions
- [ ] Review lead details and qualify
- [ ] Draft follow-up email
- [ ] Assign to sales representative
- [ ] Schedule call/meeting
- [ ] Update Odoo lead stage

## Notes
*Add notes here after processing*
"""
            
            filepath.write_text(content, encoding='utf-8')
            self.log_info(f"Lead action file created: {filename}")
            return filepath
            
        except IOError as e:
            self.log_error(f"Failed to create action file: {e}", exc=e)
            return None
        except Exception as e:
            self.log_error(f"Unexpected error: {e}", exc=e)
            return None
    
    def create_follow_up_draft(self, lead: Dict, action_file: Path) -> Optional[Path]:
        """
        Create follow-up email draft.
        
        Args:
            lead: Lead dictionary
            action_file: Path to action file
        
        Returns:
            Path to draft file or None if failed
        """
        try:
            lead_id = lead.get('id', 'UNKNOWN')
            lead_name = lead.get('name', 'New Lead')
            partner_name = lead.get('partner_name', 'Contact')
            email = lead.get('email_from', '')
            company = lead.get('company_name', '')
            
            filename = f"REPLY_ODOO_LEAD_{lead_id}.md"
            filepath = self.pending_approval_folder / filename
            
            content = f"""---
type: reply_draft
related_to: ODOO_LEAD_{lead_id}
lead_name: {lead_name}
recipient: {partner_name}
email_to: {email}
status: pending_approval
created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
---

# Follow-Up Email Draft

## Recipient
**To:** {email}
**Name:** {partner_name}
**Company:** {company}

## Subject
Thank You for Your Interest - Next Steps

## Email Body

Dear {partner_name},

Thank you for reaching out to us and expressing interest in our products/services.

We have received your inquiry (Lead Reference: #{lead_id}) and are excited about the opportunity to work with you.

### Next Steps:
1. Our sales team will review your requirements
2. We will schedule a call/meeting within 24-48 hours
3. You will receive a customized proposal based on your needs

### In the Meantime:
If you have any immediate questions, please don't hesitate to reach out.

We look forward to partnering with you!

Best regards,
Sales Team
[Your Company Name]
[Contact Information]

---

## Internal Notes
- Lead ID: {lead_id}
- Source: Odoo CRM
- Action file: {action_file.name}
- Requires: Sales team assignment and follow-up scheduling

## Approval Status
- [ ] Ready to send
- [ ] Needs revision
- [ ] Approved and sent
"""
            
            filepath.write_text(content, encoding='utf-8')
            self.log_info(f"Follow-up draft created: {filename}")
            return filepath
            
        except IOError as e:
            self.log_error(f"Failed to create draft: {e}", exc=e)
            return None
        except Exception as e:
            self.log_error(f"Unexpected error: {e}", exc=e)
            return None
    
    def trigger_qwen(self, action_file: Path) -> bool:
        """Trigger Qwen CLI to process lead."""
        try:
            prompt = (
                f"Read the Odoo lead file: {action_file.name} in Needs_Action folder.\n\n"
                f"Tasks:\n"
                f"1. Summarize the lead details and qualification status\n"
                f"2. Draft a personalized follow-up task or reply\n"
                f"3. Save any additional drafts in Pending_Approval folder\n"
                f"4. Update Dashboard.md with this lead summary\n\n"
                f"Process this lead completely."
            )
            
            result = subprocess.run(
                ['qwen', '-y', prompt],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                cwd=str(self.vault_path),
                timeout=180
            )
            
            self.log_info("Qwen processing triggered for lead")
            
            if result.stdout:
                self.log_info(f"Output: {result.stdout.strip()[:200]}")
            if result.stderr:
                self.log_warning(f"Errors: {result.stderr.strip()[:200]}")
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            self.log_warning("Qwen timeout")
            return False
        except FileNotFoundError:
            self.log_error("Qwen CLI not found")
            return False
        except Exception as e:
            self.log_error(f"Qwen error: {e}", exc=e)
            return False
    
    def update_dashboard(self, lead_count: int):
        """Update Dashboard.md with lead summary."""
        if not self.dashboard_file.exists():
            self.log_warning("Dashboard.md not found")
            return
        
        try:
            content = self.dashboard_file.read_text(encoding='utf-8')
            
            if "### Odoo Leads" not in content:
                odoo_section = f"\n### Odoo Leads\n**{lead_count} lead(s) processed.** Pipeline monitoring active.\n"
                
                if "### Email Summary" in content:
                    content = content.replace(
                        "### Email Summary",
                        odoo_section + "\n### Email Summary"
                    )
                else:
                    content += "\n" + odoo_section
                
                self.dashboard_file.write_text(content, encoding='utf-8')
                self.log_info("Dashboard.md updated with Odoo Leads section")
            else:
                self.log_info("Odoo Leads section already exists in Dashboard")
            
        except IOError as e:
            self.log_error(f"Failed to update Dashboard: {e}", exc=e)
        except Exception as e:
            self.log_error(f"Unexpected error updating Dashboard: {e}", exc=e)
    
    def create_placeholder_lead(self):
        """Create a test lead for demonstration when Odoo is not connected."""
        self.log_info("Creating placeholder test lead for demonstration...")
        
        test_lead = {
            'id': 'TEST001',
            'name': 'Test Lead - Demo',
            'partner_name': 'Demo Customer',
            'email_from': 'demo.customer@example.com',
            'phone': '+1-555-0123',
            'company_name': 'Demo Company Ltd.',
            'description': 'This is a test lead created to demonstrate the Odoo Lead Watcher functionality.',
            'priority': '3',
            'stage_id': ['1', 'New'],
            'create_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        action_file = self.create_lead_action_file(test_lead)
        
        if action_file:
            self.create_follow_up_draft(test_lead, action_file)
            self.trigger_qwen(action_file)
            self.processed_ids.add(str(test_lead['id']))
            self.save_processed_ids('processed_odoo_leads.txt', self.processed_ids)
            self.update_dashboard(1)
            
            self.log_info("✅ Placeholder test lead created successfully")
    
    def run(self):
        """Main watcher loop."""
        self.print_status_header("🎯 ODOO LEAD WATCHER STARTED")
        
        # Load processed IDs
        self.processed_ids = self.load_processed_ids('processed_odoo_leads.txt')
        self.log_info(f"Loaded {len(self.processed_ids)} previously processed lead IDs")
        
        # Try to connect to Odoo
        self.connect()
        
        if not self.odoo_connected:
            self.log_warning("=" * 60)
            self.log_warning("ODOO NOT CONNECTED - Running in Placeholder Mode")
            self.log_warning("=" * 60)
            self.log_info("\nTo enable full functionality:")
            self.log_info("  1. Install Odoo library: pip install odoo")
            self.log_info("  2. Update ODOO_CONFIG with your Odoo instance details")
            self.log_info("  3. Ensure network connectivity to Odoo server\n")
            
            self.create_placeholder_lead()
            return
        
        # Fetch and process leads
        leads = self.fetch_leads()
        
        if leads:
            self.log_info(f"Processing {len(leads)} lead(s)...")
            
            for lead in leads:
                lead_id = lead.get('id')
                self.log_info(f"\n--- Processing Lead #{lead_id} ---")
                
                # Create action file
                action_file = self.create_lead_action_file(lead)
                
                if action_file:
                    # Create follow-up draft
                    self.create_follow_up_draft(lead, action_file)
                    
                    # Trigger Qwen
                    self.trigger_qwen(action_file)
                    
                    # Mark as processed
                    self.processed_ids.add(str(lead_id))
            
            # Save processed IDs
            self.save_processed_ids('processed_odoo_leads.txt', self.processed_ids)
            
            # Update dashboard
            self.update_dashboard(len(leads))
            
            self.log_info(f"\n✅ Successfully processed {len(leads)} lead(s)!")
        else:
            self.log_info("ℹ️ No new leads found")
            self.update_dashboard(0)
        
        self.log_info("\n" + "=" * 60)
        self.log_info("✅ Odoo Lead Watcher run complete")
        self.log_info("=" * 60)


def main():
    """Entry point."""
    watcher = OdooLeadWatcher()
    watcher.run()


if __name__ == '__main__':
    main()
