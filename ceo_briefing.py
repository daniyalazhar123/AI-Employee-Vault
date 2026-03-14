"""
CEO Weekly Briefing Generator for AI Employee Vault

Every Monday, reads Dashboard.md, Business_Goals.md, and Done/ folder to create
a professional CEO briefing with revenue, tasks, bottlenecks, and suggestions.
"""

import os
import re
from datetime import datetime, timedelta
from pathlib import Path


# Paths
VAULT_PATH = Path(__file__).parent
DASHBOARD_FILE = VAULT_PATH / "Dashboard.md"
BUSINESS_GOALS_FILE = VAULT_PATH / "Business_Goals.md"
DONE_FOLDER = VAULT_PATH / "Done"
BRIEFINGS_FOLDER = VAULT_PATH / "Briefings"


def ensure_folders():
    """Ensure Briefings folder exists."""
    BRIEFINGS_FOLDER.mkdir(exist_ok=True)


def read_dashboard():
    """Read and parse Dashboard.md for key metrics."""
    
    if not DASHBOARD_FILE.exists():
        return None
    
    content = DASHBOARD_FILE.read_text(encoding='utf-8')
    
    data = {
        'total_revenue': None,
        'months_tracked': None,
        'new_clients': None,
        'pending_invoices': None,
        'highlights': [],
        'recent_activity': [],
        'last_updated': None
    }
    
    # Extract total revenue
    revenue_match = re.search(r'Total[^\n]*\|\s*\*\*([\d,]+)\*\*', content)
    if revenue_match:
        data['total_revenue'] = revenue_match.group(1)
    
    # Extract months tracked
    months_match = re.search(r'(\d+)\s*months?\s*tracked', content, re.IGNORECASE)
    if months_match:
        data['months_tracked'] = months_match.group(1)
    
    # Extract new clients
    clients_match = re.search(r'(\d+)\s*new\s*clients', content, re.IGNORECASE)
    if clients_match:
        data['new_clients'] = clients_match.group(1)
    
    # Extract pending invoices
    invoices_match = re.search(r'(\d+)\s*pending\s*invoices', content, re.IGNORECASE)
    if invoices_match:
        data['pending_invoices'] = invoices_match.group(1)
    
    # Extract highlights
    highlights_section = re.search(r'###?\s*Key Highlights\s*\n(.*?)(?=###|##|\*\*Status|\Z)', content, re.DOTALL | re.IGNORECASE)
    if highlights_section:
        highlights = re.findall(r'^[-*•]\s*(.+)$', highlights_section.group(1), re.MULTILINE)
        data['highlights'] = [h.strip() for h in highlights[:5]]
    
    # Extract recent activity
    activity_section = re.search(r'###?\s*Recent Activity\s*\n(.*?)(?=###|##|\*\*Status|\Z)', content, re.DOTALL | re.IGNORECASE)
    if activity_section:
        activities = re.findall(r'^[-*•]\s*(.+)$', activity_section.group(1), re.MULTILINE)
        data['recent_activity'] = [a.strip() for a in activities[:10]]
    
    # Extract last updated date
    updated_match = re.search(r'Last updated:\s*(.+)$', content, re.MULTILINE)
    if updated_match:
        data['last_updated'] = updated_match.group(1).strip()
    
    return data


def read_business_goals():
    """Read Business_Goals.md if it exists."""
    
    if not BUSINESS_GOALS_FILE.exists():
        return None
    
    content = BUSINESS_GOALS_FILE.read_text(encoding='utf-8')
    
    goals = {
        'quarterly_goals': [],
        'annual_goals': [],
        'deadlines': []
    }
    
    # Extract quarterly goals
    quarterly = re.search(r'###?\s*Quarterly Goals?\s*\n(.*?)(?=###|##|\Z)', content, re.DOTALL | re.IGNORECASE)
    if quarterly:
        items = re.findall(r'^[-*•]\s*(.+)$', quarterly.group(1), re.MULTILINE)
        goals['quarterly_goals'] = [i.strip() for i in items]
    
    # Extract annual goals
    annual = re.search(r'###?\s*Annual Goals?\s*\n(.*?)(?=###|##|\Z)', content, re.DOTALL | re.IGNORECASE)
    if annual:
        items = re.findall(r'^[-*•]\s*(.+)$', annual.group(1), re.MULTILINE)
        goals['annual_goals'] = [i.strip() for i in items]
    
    # Extract deadlines
    deadlines = re.search(r'###?\s*Deadlines?\s*\n(.*?)(?=###|##|\Z)', content, re.DOTALL | re.IGNORECASE)
    if deadlines:
        items = re.findall(r'^[-*•]\s*(.+)$', deadlines.group(1), re.MULTILINE)
        goals['deadlines'] = [i.strip() for i in items]
    
    return goals


def read_done_folder():
    """Read all files in Done/ folder from the past week."""
    
    if not DONE_FOLDER.exists():
        return []
    
    completed_tasks = []
    one_week_ago = datetime.now() - timedelta(days=7)
    
    for file in DONE_FOLDER.glob('*.md'):
        try:
            content = file.read_text(encoding='utf-8')
            
            # Extract task info from frontmatter
            type_match = re.search(r'type:\s*(.+)$', content, re.MULTILINE)
            status_match = re.search(r'status:\s*(.+)$', content, re.MULTILINE)
            processed_match = re.search(r'processed:\s*(.+)$', content, re.MULTILINE)
            
            task_type = type_match.group(1).strip() if type_match else 'Unknown'
            status = status_match.group(1).strip() if status_match else 'completed'
            
            # Check if processed this week
            if processed_match:
                try:
                    processed_date = datetime.strptime(processed_match.group(1).strip(), '%Y-%m-%d')
                    if processed_date >= one_week_ago:
                        completed_tasks.append({
                            'file': file.name,
                            'type': task_type,
                            'status': status,
                            'date': processed_match.group(1).strip()
                        })
                except:
                    # If date parsing fails, include anyway
                    completed_tasks.append({
                        'file': file.name,
                        'type': task_type,
                        'status': status,
                        'date': 'Unknown'
                    })
            else:
                completed_tasks.append({
                    'file': file.name,
                    'type': task_type,
                    'status': status,
                    'date': 'Unknown'
                })
        except Exception as e:
            continue
    
    return completed_tasks


def generate_bottlenecks(completed_tasks, dashboard_data):
    """Identify potential bottlenecks based on completed tasks."""
    
    bottlenecks = []
    
    # Check for pending approvals
    pending_approval_folder = VAULT_PATH / "Pending_Approval"
    if pending_approval_folder.exists():
        pending_count = len(list(pending_approval_folder.glob('*.md')))
        if pending_count > 0:
            bottlenecks.append(f"{pending_count} item(s) awaiting approval in Pending_Approval/")
    
    # Check for needs action items
    needs_action_folder = VAULT_PATH / "Needs_Action"
    if needs_action_folder.exists():
        needs_action_count = len(list(needs_action_folder.glob('*.md')))
        if needs_action_count > 0:
            bottlenecks.append(f"{needs_action_count} item(s) pending in Needs_Action/")
    
    # Check for pending invoices
    if dashboard_data and dashboard_data.get('pending_invoices'):
        count = int(dashboard_data['pending_invoices'].replace(',', ''))
        if count > 0:
            bottlenecks.append(f"{count} pending invoice(s) - follow up required for payment collection")
    
    # Check for low task completion
    if len(completed_tasks) < 5:
        bottlenecks.append("Low task completion rate this week - review workload and priorities")
    
    if not bottlenecks:
        bottlenecks.append("No significant bottlenecks identified - operations running smoothly")
    
    return bottlenecks


def generate_cost_optimization(dashboard_data, completed_tasks):
    """Generate cost optimization suggestions."""
    
    suggestions = []
    
    # Automation opportunities
    automation_tasks = [t for t in completed_tasks if 'email' in t['type'].lower() or 'whatsapp' in t['type'].lower()]
    if len(automation_tasks) > 10:
        suggestions.append("✅ High email/WhatsApp volume detected - consider automated response templates")
    
    # Social media efficiency
    social_drafts_folder = VAULT_PATH / "Social_Drafts"
    if social_drafts_folder.exists():
        social_count = len(list(social_drafts_folder.glob('*.md')))
        if social_count > 5:
            suggestions.append("📱 Multiple social media drafts pending - consider scheduling tool integration")
    
    # General suggestions
    suggestions.append("💡 Review recurring manual tasks for automation potential")
    suggestions.append("💡 Consider batch processing similar tasks to improve efficiency")
    
    if dashboard_data and dashboard_data.get('pending_invoices'):
        suggestions.append("💰 Implement automated invoice reminders to reduce pending payments")
    
    return suggestions


def generate_ceo_briefing(dashboard_data, business_goals, completed_tasks):
    """Generate the complete CEO briefing document."""
    
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    briefing_date = today.strftime("%B %d, %Y")
    week_range = f"{week_start.strftime('%B %d')} - {week_end.strftime('%d, %Y')}"
    
    # Generate bottlenecks and suggestions
    bottlenecks = generate_bottlenecks(completed_tasks, dashboard_data)
    cost_suggestions = generate_cost_optimization(dashboard_data, completed_tasks)
    
    # Build briefing content
    briefing = f"""---
type: ceo_briefing
period: {week_range}
created: {today.strftime("%Y-%m-%d %H:%M:%S")}
status: draft
---

# CEO Weekly Briefing

**Period:** {week_range}  
**Generated:** {briefing_date}  
**Status:** Ready for Review

---

## 📊 Executive Summary

### Weekly Revenue Performance
| Metric | Value |
|--------|-------|
| Total Revenue (Tracked Period) | Rs. {dashboard_data['total_revenue'] if dashboard_data and dashboard_data.get('total_revenue') else 'N/A'} |
| Months Tracked | {dashboard_data['months_tracked'] if dashboard_data and dashboard_data.get('months_tracked') else 'N/A'} |
| New Clients Acquired | {dashboard_data['new_clients'] if dashboard_data and dashboard_data.get('new_clients') else 'N/A'} |
| Pending Invoices | {dashboard_data['pending_invoices'] if dashboard_data and dashboard_data.get('pending_invoices') else '0'} |

### Week at a Glance
- **Tasks Completed:** {len(completed_tasks)}
- **Pending Approvals:** {len(list((VAULT_PATH / 'Pending_Approval').glob('*.md'))) if (VAULT_PATH / 'Pending_Approval').exists() else 0}
- **Operational Status:** {'✅ Smooth' if len(bottlenecks) <= 1 else '⚠️ Attention Needed'}

---

## ✅ Completed Tasks This Week

**Total:** {len(completed_tasks)} tasks completed

"""
    
    # Group tasks by type
    task_types = {}
    for task in completed_tasks:
        task_type = task['type']
        if task_type not in task_types:
            task_types[task_type] = []
        task_types[task_type].append(task)
    
    for task_type, tasks in task_types.items():
        briefing += f"\n### {task_type.replace('_', ' ').title()}\n"
        for task in tasks[:5]:  # Show top 5 per category
            briefing += f"- [x] {task['file']} ({task['date']})\n"
        if len(tasks) > 5:
            briefing += f"- _...and {len(tasks) - 5} more_\n"
    
    briefing += """
---

## 🎯 Business Goals Progress

"""
    
    if business_goals:
        if business_goals.get('quarterly_goals'):
            briefing += "### Quarterly Goals\n"
            for goal in business_goals['quarterly_goals'][:5]:
                briefing += f"- {goal}\n"
            briefing += "\n"
        
        if business_goals.get('annual_goals'):
            briefing += "### Annual Goals\n"
            for goal in business_goals['annual_goals'][:5]:
                briefing += f"- {goal}\n"
            briefing += "\n"
        
        if business_goals.get('deadlines'):
            briefing += "### Upcoming Deadlines\n"
            for deadline in business_goals['deadlines'][:5]:
                briefing += f"- ⏰ {deadline}\n"
    else:
        briefing += "*Business_Goals.md not found. Consider creating this file for goal tracking.*\n"
    
    briefing += """
---

## ⚠️ Bottlenecks & Issues

"""
    
    for bottleneck in bottlenecks:
        briefing += f"- {bottleneck}\n"
    
    briefing += """
---

## 💡 Cost Optimization Suggestions

"""
    
    for suggestion in cost_suggestions:
        briefing += f"{suggestion}\n"
    
    briefing += f"""
---

## 📈 Key Highlights

"""
    
    if dashboard_data and dashboard_data.get('highlights'):
        for highlight in dashboard_data['highlights']:
            briefing += f"- {highlight}\n"
    else:
        briefing += "- Consistent operations maintained\n"
        briefing += "- All critical tasks completed\n"
    
    briefing += f"""
---

## 📋 Action Items for CEO Review

- [ ] Review pending approvals in Pending_Approval/ folder
- [ ] Address identified bottlenecks
- [ ] Approve cost optimization initiatives
- [ ] Review upcoming deadlines and prioritize
- [ ] Provide feedback on weekly briefing format

---

## 📝 Notes

This briefing was automatically generated by AI Employee Vault.
For questions or modifications, contact your system administrator.

---
*Generated: {briefing_date} | AI Employee Vault v1.0*
"""
    
    return briefing


def save_briefing(briefing_content):
    """Save the briefing to Briefings/ folder."""
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"CEO_Briefing_{date_str}.md"
    filepath = BRIEFINGS_FOLDER / filename
    
    filepath.write_text(briefing_content, encoding='utf-8')
    
    return filepath


def ask_for_approval(filepath):
    """Display briefing and ask for approval."""
    
    print("\n" + "=" * 70)
    print("📋 CEO WEEKLY BRIEFING CREATED")
    print("=" * 70)
    
    content = filepath.read_text(encoding='utf-8')
    
    # Extract just the content (skip frontmatter for display)
    main_content = re.sub(r'^---\n.*?\n---\n\n', '', content, flags=re.DOTALL)
    
    print("\n📄 Preview (first 2000 chars):\n")
    print("-" * 70)
    print(main_content[:2000])
    print("...")
    print("-" * 70)
    
    print("\n" + "=" * 70)
    print("APPROVAL OPTIONS")
    print("=" * 70)
    print(f"\nBriefing saved to: {filepath}")
    print("\nChoose an option:")
    print("  1. Approve - Ready to send to CEO")
    print("  2. Edit - Modify the briefing in Briefings/ folder")
    print("  3. Regenerate - Create a new version")
    print("  4. Discard - Delete this briefing")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == '1':
                print("\n✅ Briefing approved!")
                print(f"   Location: {filepath}")
                print("   Next step: Send to CEO via email or presentation")
                
                # Update status to approved
                updated_content = content.replace('status: draft', 'status: approved')
                updated_content = updated_content.replace(
                    f'created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                    f'created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\napproved: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
                )
                filepath.write_text(updated_content, encoding='utf-8')
                return 'approved'
                
            elif choice == '2':
                print(f"\n✏️  Edit the file at: {filepath}")
                print("   After editing, you can manually update the status to 'approved'")
                return 'edit'
                
            elif choice == '3':
                print("\n🔄 Regenerating briefing...")
                return 'regenerate'
                
            elif choice == '4':
                confirm = input("   Are you sure you want to discard this briefing? (y/n): ").strip().lower()
                if confirm == 'y':
                    filepath.unlink()
                    print("\n🗑️  Briefing discarded.")
                    return 'discarded'
                else:
                    print("   Briefing kept. Please choose another option.")
            else:
                print("   Invalid choice. Please enter 1-4.")
        except EOFError:
            print("\n\n⚠️  No input detected. Briefing saved for manual review.")
            return 'manual'


def main():
    """Main function to generate CEO briefing."""
    
    print("=" * 70)
    print("📊 CEO Weekly Briefing Generator - AI Employee Vault")
    print("=" * 70)
    print(f"\n📅 Generating briefing for: {datetime.now().strftime('%B %d, %Y')}")
    
    ensure_folders()
    
    # Read dashboard
    print("\n📈 Reading Dashboard.md...")
    dashboard_data = read_dashboard()
    
    if dashboard_data:
        print(f"   ✅ Dashboard loaded")
        print(f"   💰 Total Revenue: Rs. {dashboard_data.get('total_revenue', 'N/A')}")
    else:
        print("   ⚠️  Dashboard not found or empty")
    
    # Read business goals
    print("\n🎯 Reading Business_Goals.md...")
    business_goals = read_business_goals()
    
    if business_goals:
        print(f"   ✅ Business goals loaded")
        if business_goals.get('quarterly_goals'):
            print(f"   📋 Quarterly Goals: {len(business_goals['quarterly_goals'])}")
    else:
        print("   ℹ️  Business_Goals.md not found (optional)")
    
    # Read completed tasks
    print("\n✅ Reading Done/ folder...")
    completed_tasks = read_done_folder()
    print(f"   ✅ Found {len(completed_tasks)} completed tasks this week")
    
    # Generate briefing
    print("\n📝 Generating CEO briefing...")
    briefing_content = generate_ceo_briefing(dashboard_data, business_goals, completed_tasks)
    
    # Save briefing
    filepath = save_briefing(briefing_content)
    print(f"✅ Briefing saved to: {filepath}")
    
    # Ask for approval
    result = ask_for_approval(filepath)
    
    print("\n" + "=" * 70)
    print(f"Action completed: {result.upper()}")
    print("=" * 70)


if __name__ == "__main__":
    main()
