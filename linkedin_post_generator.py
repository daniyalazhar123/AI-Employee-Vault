"""
LinkedIn Post Generator for AI Employee Vault

Reads Dashboard.md for latest business updates and generates professional LinkedIn posts.
Saves drafts to Social_Drafts/ folder for human approval before posting.
"""

import os
from datetime import datetime
from pathlib import Path
import re


# Paths
VAULT_PATH = Path(__file__).parent
DASHBOARD_FILE = VAULT_PATH / "Dashboard.md"
SOCIAL_DRAFTS = VAULT_PATH / "Social_Drafts"


def read_dashboard():
    """Read and parse Dashboard.md for key metrics and highlights."""
    
    if not DASHBOARD_FILE.exists():
        print("Error: Dashboard.md not found!")
        return None
    
    content = DASHBOARD_FILE.read_text(encoding='utf-8')
    
    # Extract key data
    data = {
        'total_revenue': None,
        'months_tracked': None,
        'new_clients': None,
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
    
    # Extract highlights
    highlights_section = re.search(r'###?\s*Key Highlights\s*\n(.*?)(?=###|##|\*\*Status|\Z)', content, re.DOTALL | re.IGNORECASE)
    if highlights_section:
        highlights = re.findall(r'^[-*•]\s*(.+)$', highlights_section.group(1), re.MULTILINE)
        data['highlights'] = [h.strip() for h in highlights[:3]]  # Top 3 highlights
    
    # Extract recent activity
    activity_section = re.search(r'###?\s*Recent Activity\s*\n(.*?)(?=###|##|\*\*Status|\Z)', content, re.DOTALL | re.IGNORECASE)
    if activity_section:
        activities = re.findall(r'^[-*•]\s*(.+)$', activity_section.group(1), re.MULTILINE)
        data['recent_activity'] = [a.strip() for a in activities[:5]]  # Top 5 activities
    
    # Extract last updated date
    updated_match = re.search(r'Last updated:\s*(.+)$', content, re.MULTILINE)
    if updated_match:
        data['last_updated'] = updated_match.group(1).strip()
    
    return data


def generate_linkedin_post(data):
    """Generate a professional LinkedIn post from dashboard data."""
    
    today = datetime.now().strftime("%B %d, %Y")
    
    # Build post content
    post_lines = []
    
    # Hook/Opening
    post_lines.append("🚀 Exciting Progress Update!")
    post_lines.append("")
    
    # Main achievement
    if data['total_revenue']:
        post_lines.append(f"Thrilled to share that we've achieved Rs. {data['total_revenue']} in total sales revenue!")
        post_lines.append("")
    
    # Time period
    if data['months_tracked']:
        post_lines.append(f"Over the past {data['months_tracked']} months, our team has been focused on consistent growth and delivering value to our clients.")
        post_lines.append("")
    
    # Client milestone
    if data['new_clients']:
        post_lines.append(f"🤝 Welcomed {data['new_clients']} new clients to our growing family")
    
    # Highlights
    if data['highlights']:
        post_lines.append("")
        post_lines.append("Key achievements this period:")
        for highlight in data['highlights']:
            # Clean up the highlight text
            clean_highlight = highlight.replace('Rs.', 'Rs.').replace('**', '')
            post_lines.append(f"  ✓ {clean_highlight}")
    
    # Recent activity (automation angle)
    if data['recent_activity']:
        post_lines.append("")
        post_lines.append("Behind the scenes:")
        for activity in data['recent_activity'][:3]:
            clean_activity = activity.replace('✅', '').replace('📋', '').strip()
            post_lines.append(f"  • {clean_activity}")
    
    # Closing
    post_lines.append("")
    post_lines.append("Grateful for the continued trust from our clients and partners. Here's to more growth ahead! 💼📈")
    post_lines.append("")
    
    # Hashtags
    post_lines.append("#BusinessGrowth #Sales #Entrepreneurship #ClientSuccess #Progress #Milestone")
    post_lines.append("")
    post_lines.append(f"— Posted from AI Employee Vault | {today}")
    
    return '\n'.join(post_lines)


def save_draft(post_content):
    """Save the LinkedIn post draft to Social_Drafts folder."""
    
    # Ensure folder exists
    SOCIAL_DRAFTS.mkdir(exist_ok=True)
    
    # Generate filename with date
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"linkedin_post_{date_str}.md"
    filepath = SOCIAL_DRAFTS / filename
    
    # Create markdown content with frontmatter
    markdown_content = f"""---
type: linkedin_post
status: draft
created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
requires_approval: true
---

{post_content}
"""
    
    # Save file
    filepath.write_text(markdown_content, encoding='utf-8')
    
    return filepath


def ask_for_approval(filepath):
    """Display draft and ask for human approval."""
    
    print("\n" + "=" * 60)
    print("📝 LINKEDIN POST DRAFT CREATED")
    print("=" * 60)
    
    # Read and display the draft
    content = filepath.read_text(encoding='utf-8')
    
    # Extract just the post content (skip frontmatter for display)
    post_content = re.sub(r'^---\n.*?\n---\n\n', '', content, flags=re.DOTALL)
    
    print("\n📄 Preview:\n")
    print("-" * 60)
    print(post_content)
    print("-" * 60)
    
    print("\n" + "=" * 60)
    print("APPROVAL OPTIONS")
    print("=" * 60)
    print(f"\nDraft saved to: {filepath}")
    print("\nChoose an option:")
    print("  1. Approve - Ready to post (copy manually to LinkedIn)")
    print("  2. Edit - Modify the draft in Social_Drafts folder")
    print("  3. Regenerate - Create a new version with different tone")
    print("  4. Discard - Delete this draft")
    print("\n⚠️  Note: Auto-posting to LinkedIn requires API access.")
    print("   For now, please copy the approved post to LinkedIn manually.")
    
    while True:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            print("\n✅ Draft approved!")
            print("   Next step: Copy the post content and paste to LinkedIn")
            print(f"   Draft location: {filepath}")
            
            # Update status to approved
            updated_content = content.replace('status: draft', 'status: approved')
            updated_content = updated_content.replace('requires_approval: true', 'requires_approval: false')
            updated_content = updated_content.replace(f'created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 
                                                      f'created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\napproved: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            filepath.write_text(updated_content, encoding='utf-8')
            return 'approved'
            
        elif choice == '2':
            print(f"\n✏️  Edit the file at: {filepath}")
            print("   After editing, run the script again to regenerate or approve.")
            return 'edit'
            
        elif choice == '3':
            print("\n🔄 Regenerating with different tone...")
            return 'regenerate'
            
        elif choice == '4':
            confirm = input("   Are you sure you want to discard this draft? (y/n): ").strip().lower()
            if confirm == 'y':
                filepath.unlink()
                print("\n🗑️  Draft discarded.")
                return 'discarded'
            else:
                print("   Draft kept. Please choose another option.")
        else:
            print("   Invalid choice. Please enter 1-4.")


def main():
    """Main function to generate LinkedIn post."""
    
    print("=" * 60)
    print("🔗 LinkedIn Post Generator - AI Employee Vault")
    print("=" * 60)
    print(f"\nReading Dashboard.md...")
    
    # Read dashboard data
    data = read_dashboard()
    
    if not data:
        print("Failed to read dashboard. Exiting.")
        return
    
    print(f"✅ Dashboard loaded successfully!")
    print(f"   Last updated: {data['last_updated'] or 'Unknown'}")
    
    # Generate post
    print("\nGenerating LinkedIn post...")
    post_content = generate_linkedin_post(data)
    
    # Save draft
    filepath = save_draft(post_content)
    print(f"✅ Draft saved to: {filepath}")
    
    # Ask for approval
    result = ask_for_approval(filepath)
    
    print("\n" + "=" * 60)
    print(f"Action completed: {result.upper()}")
    print("=" * 60)


if __name__ == "__main__":
    main()
