"""
Odoo Lead Watcher - AI Employee Vault

Monitors Odoo CRM for new leads and creates action files for processing.
Assumes Odoo is connected via XML-RPC API.

Usage:
    python odoo_lead_watcher.py
"""

import os
import time
import subprocess
from pathlib import Path
from datetime import datetime

# Try to import Odoo library (optional - will use placeholder if not available)
try:
    import xmlrpc.client
    ODOO_AVAILABLE = True
except ImportError:
    ODOO_AVAILABLE = False

# Paths
VAULT_PATH = Path(__file__).parent
NEEDS_ACTION = VAULT_PATH / "Needs_Action"
PENDING_APPROVAL = VAULT_PATH / "Pending_Approval"

# Odoo Configuration (update with your actual Odoo instance details)
ODOO_CONFIG = {
    'url': 'http://localhost:8069',  # Your Odoo instance URL
    'db': 'odoo',                     # Database name
    'username': 'admin',              # Odoo username
    'password': 'admin',              # Odoo password or API key
    'api_key': None                   # Optional API key for newer Odoo versions
}


def ensure_folders():
    """Ensure Needs_Action and Pending_Approval folders exist."""
    NEEDS_ACTION.mkdir(exist_ok=True)
    PENDING_APPROVAL.mkdir(exist_ok=True)


def connect_to_odoo():
    """
    Connect to Odoo via XML-RPC.
    Returns (common, models, uid) if successful, None otherwise.
    """
    if not ODOO_AVAILABLE:
        print("⚠️  Odoo library not available - using placeholder mode")
        return None

    try:
        url = ODOO_CONFIG['url']
        db = ODOO_CONFIG['db']
        username = ODOO_CONFIG['username']
        password = ODOO_CONFIG['password']

        # Common authentication
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})

        if not uid:
            print("❌ Odoo authentication failed - check credentials")
            return None

        # Models endpoint
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        print(f"✅ Odoo connected successfully! (User ID: {uid})")

        return (common, models, uid)

    except Exception as e:
        print(f"❌ Odoo connection error: {e}")
        return None


def get_new_leads(models, uid, processed_ids):
    """
    Fetch new leads from Odoo CRM that haven't been processed yet.
    Returns list of lead dictionaries.
    """
    try:
        # Search for leads (crm.lead model in Odoo)
        # Filter: not in processed_ids and create_date within last 24 hours
        domain = [
            ('id', 'not in', list(processed_ids)),
        ]

        leads = models.execute_kw(
            'odoo',  # database
            uid,     # user id
            ODOO_CONFIG['password'],  # password
            'crm.lead',  # model
            'search_read',  # method
            [domain],  # domain filter
            {
                'fields': [
                    'id', 'name', 'partner_name', 'email_from',
                    'phone', 'company_name', 'description',
                    'priority', 'stage_id', 'create_date'
                ],
                'limit': 10  # Max leads to fetch per run
            }
        )

        return leads

    except Exception as e:
        print(f"❌ Error fetching leads: {e}")
        return []


def create_lead_action_file(lead: dict) -> Path:
    """
    Create an action file for a new Odoo lead in Needs_Action folder.
    Filename: ODOO_LEAD_[lead_id].md
    """
    lead_id = lead.get('id', 'UNKNOWN')
    lead_name = lead.get('name', 'New Lead')
    partner_name = lead.get('partner_name', 'N/A')
    email = lead.get('email_from', 'N/A')
    phone = lead.get('phone', 'N/A')
    company = lead.get('company_name', 'N/A')
    description = lead.get('description', '')
    priority = lead.get('priority', '0')
    stage = lead.get('stage_id', ['N/A'])[1] if isinstance(lead.get('stage_id'), list) else 'N/A'
    create_date = lead.get('create_date', '')

    # Safe filename
    filename = f"ODOO_LEAD_{lead_id}.md"
    filepath = NEEDS_ACTION / filename

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
    print(f"📝 Odoo lead action file created: {filename}")

    return filepath


def create_follow_up_draft(lead: dict, action_file: Path) -> Path:
    """
    Create a follow-up reply draft in Pending_Approval folder.
    """
    lead_id = lead.get('id', 'UNKNOWN')
    lead_name = lead.get('name', 'New Lead')
    partner_name = lead.get('partner_name', 'Contact')
    email = lead.get('email_from', '')
    company = lead.get('company_name', '')

    filename = f"REPLY_ODOO_LEAD_{lead_id}.md"
    filepath = PENDING_APPROVAL / filename

    content = f"""---
type: reply_draft
related_to: ODOO_LEAD_{lead_id}
lead_name: {lead_name}
recipient: {partner_name}
email_to: {email}
status: pending_approval
created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
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
If you have any immediate questions or would like to provide additional details about your requirements, please don't hesitate to reach out.

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
    print(f"📧 Follow-up draft created: {filename}")

    return filepath


def trigger_qwen_processing(action_file: Path):
    """
    Trigger Qwen to process the lead and create additional tasks if needed.
    """
    try:
        qwen_prompt = f"""Read the Odoo lead file: {action_file.name} in Needs_Action folder.

Tasks:
1. Summarize the lead details and qualification status
2. Draft a personalized follow-up task or reply
3. Save any additional drafts in Pending_Approval folder
4. Update Dashboard.md with this lead summary

Process this lead completely.
"""
        result = subprocess.run(
            ["qwen", "-y", qwen_prompt],
            check=False,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd=str(VAULT_PATH),
            shell=True,
            timeout=180
        )
        print("✅ Qwen processing triggered for lead")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()[:200]}")

    except subprocess.TimeoutExpired:
        print("⚠️  Qwen timeout")
    except FileNotFoundError:
        print("⚠️  Qwen CLI not found")
    except Exception as e:
        print(f"⚠️  Error triggering Qwen: {e}")


def update_dashboard_lead_summary(lead_count: int = 0):
    """
    Update Dashboard.md with Odoo lead summary section.
    """
    dashboard_path = VAULT_PATH / "Dashboard.md"

    if not dashboard_path.exists():
        print("⚠️  Dashboard.md not found")
        return

    try:
        content = dashboard_path.read_text(encoding='utf-8')

        # Check if Odoo Lead Summary section exists
        if "### Odoo Leads" not in content:
            # Add new section after "Recent Activity" or before "Email Summary"
            odoo_section = """
### Odoo Leads
**No new leads processed yet.** Pipeline monitoring active.

"""
            # Insert before "### Email Summary"
            if "### Email Summary" in content:
                content = content.replace(
                    "### Email Summary",
                    odoo_section + "### Email Summary"
                )
            else:
                # Add after "Recent Activity" section
                content += "\n" + odoo_section

            dashboard_path.write_text(content, encoding='utf-8')
            print("📊 Dashboard.md updated with Odoo Leads section")
        else:
            print("ℹ️  Odoo Leads section already exists in Dashboard")

    except Exception as e:
        print(f"⚠️  Error updating Dashboard: {e}")


def load_processed_leads() -> set:
    """Load set of already processed lead IDs from file."""
    processed_file = VAULT_PATH / "processed_odoo_leads.txt"

    if processed_file.exists():
        try:
            content = processed_file.read_text(encoding='utf-8')
            return set(line.strip() for line in content.splitlines() if line.strip())
        except:
            pass

    return set()


def save_processed_lead(lead_id: str):
    """Save a processed lead ID to file."""
    processed_file = VAULT_PATH / "processed_odoo_leads.txt"

    with open(processed_file, 'a', encoding='utf-8') as f:
        f.write(f"{lead_id}\n")


def main():
    """Main function to run Odoo Lead Watcher."""
    print("=" * 70)
    print("🔍 ODOO LEAD WATCHER - CRM Monitor")
    print("=" * 70)

    ensure_folders()

    # Check if Odoo is connected
    odoo_connection = connect_to_odoo()

    if odoo_connection is None:
        print("\n" + "=" * 70)
        print("⚠️  ODOO NOT CONNECTED - Running in Placeholder Mode")
        print("=" * 70)
        print("\nThis script is ready for Odoo integration.")
        print("To enable full functionality:")
        print("  1. Install Odoo library: pip install odoo")
        print("  2. Update ODOO_CONFIG with your Odoo instance details")
        print("  3. Ensure network connectivity to Odoo server")
        print("\nCreating placeholder script and test lead for demonstration...")
        print("=" * 70)

        # Create a test lead action file for demonstration
        test_lead = {
            'id': 'TEST001',
            'name': 'Test Lead - Demo',
            'partner_name': 'Demo Customer',
            'email_from': 'demo.customer@example.com',
            'phone': '+1-555-0123',
            'company_name': 'Demo Company Ltd.',
            'description': 'This is a test lead created to demonstrate the Odoo Lead Watcher functionality. Interested in Product A and Product B.',
            'priority': '3',
            'stage_id': ['1', 'New'],
            'create_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        action_file = create_lead_action_file(test_lead)
        create_follow_up_draft(test_lead, action_file)
        update_dashboard_lead_summary(1)

        print("\n✅ Placeholder test lead created successfully!")
        print(f"   Action file: {action_file.name}")
        print(f"   Draft: REPLY_ODOO_LEAD_TEST001.md")

        return

    # Odoo is connected - proceed with real lead monitoring
    common, models, uid = odoo_connection

    processed_ids = load_processed_leads()
    print(f"📂 Loaded {len(processed_ids)} previously processed lead IDs")

    print("\n🔍 Checking for new leads...")

    try:
        leads = get_new_leads(models, uid, processed_ids)

        if leads:
            print(f"✅ Found {len(leads)} new lead(s)!")

            for lead in leads:
                lead_id = lead.get('id')
                print(f"\n--- Processing Lead #{lead_id} ---")

                # Create action file
                action_file = create_lead_action_file(lead)

                # Create follow-up draft
                create_follow_up_draft(lead, action_file)

                # Trigger Qwen for additional processing
                trigger_qwen_processing(action_file)

                # Mark as processed
                save_processed_lead(str(lead_id))
                processed_ids.add(str(lead_id))

            # Update dashboard
            update_dashboard_lead_summary(len(leads))

            print(f"\n🎉 Successfully processed {len(leads)} lead(s)!")

        else:
            print("ℹ️  No new leads found")
            update_dashboard_lead_summary(0)

    except Exception as e:
        print(f"❌ Error processing leads: {e}")

    print("\n" + "=" * 70)
    print("✅ Odoo Lead Watcher run complete")
    print("=" * 70)


if __name__ == "__main__":
    main()
