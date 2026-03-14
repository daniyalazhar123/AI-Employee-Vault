"""
Facebook & Instagram Post Generator for AI Employee Vault

Reads Dashboard.md and generates engaging Facebook and Instagram posts
with hashtags and emojis. Saves drafts and asks for human approval.
"""

import os
import re
from datetime import datetime
from pathlib import Path


# Paths
VAULT_PATH = Path(__file__).parent
DASHBOARD_FILE = VAULT_PATH / "Dashboard.md"
SOCIAL_DRAFTS = VAULT_PATH / "Social_Drafts"


def ensure_folders():
    """Ensure Social_Drafts folder exists."""
    SOCIAL_DRAFTS.mkdir(exist_ok=True)


def read_dashboard():
    """Read and parse Dashboard.md for key metrics."""
    
    if not DASHBOARD_FILE.exists():
        return None
    
    content = DASHBOARD_FILE.read_text(encoding='utf-8')
    
    data = {
        'total_revenue': None,
        'months_tracked': None,
        'new_clients': None,
        'highlights': [],
        'recent_activity': [],
        'status': None
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
        data['highlights'] = [h.strip() for h in highlights[:3]]
    
    # Extract status
    status_match = re.search(r'\*\*Status:\*\*\s*(.+)$', content, re.MULTILINE)
    if status_match:
        data['status'] = status_match.group(1).strip()
    
    return data


def generate_facebook_post(data):
    """Generate an engaging Facebook post."""
    
    today = datetime.now().strftime("%B %d, %Y")
    
    post = f"""🚀 EXCITING BUSINESS UPDATE! 🚀

We're thrilled to share our latest progress with our amazing community!

📊 ACHIEVEMENT HIGHLIGHTS:
"""
    
    if data and data.get('total_revenue'):
        post += f"""💰 Total Revenue: Rs. {data['total_revenue']}
"""
    
    if data and data.get('new_clients'):
        post += f"""🤝 New Clients Welcomed: {data['new_clients']}
"""
    
    if data and data.get('months_tracked'):
        post += f"""📈 Tracking Period: {data['months_tracked']} months of consistent growth
"""
    
    post += """
✨ WHAT MAKES THIS SPECIAL:
"""
    
    if data and data.get('highlights'):
        for highlight in data['highlights']:
            clean_highlight = highlight.replace('**', '').replace('Rs.', 'Rs. ')
            post += f"✅ {clean_highlight}\n"
    else:
        post += """✅ Consistent performance across all metrics
✅ Strong client relationships
✅ Commitment to excellence
"""
    
    post += f"""
🙏 To our incredible clients and partners - THANK YOU for trusting us with your business. Your success is our success!

💬 We'd love to hear from you! Drop a comment below or send us a message to discuss how we can help your business grow.

📩 Let's connect and create something amazing together!

---
📍 Posted from AI Employee Vault | {today}

#BusinessGrowth #Success #Entrepreneurship #ClientSuccess #BusinessUpdate #Growth #Milestone #Professional #Achievement #Grateful
"""
    
    return post


def generate_instagram_post(data):
    """Generate an engaging Instagram post with more emojis and visual language."""
    
    today = datetime.now().strftime("%B %d, %Y")
    
    post = f"""✨ GROWTH MINDSET IN ACTION ✨

📈 Another week, another milestone! Here's what we've been up to:

💫 THE NUMBERS:
━━━━━━━━━━━━━━━━
💰 Revenue: Rs. {data.get('total_revenue', 'N/A') if data else 'N/A'}
🤝 New Clients: {data.get('new_clients', 'N/A') if data else 'N/A'}
📊 Months Tracked: {data.get('months_tracked', 'N/A') if data else 'N/A'}
━━━━━━━━━━━━━━━━

🌟 HIGHLIGHTS OF THE WEEK:
"""
    
    if data and data.get('highlights'):
        for i, highlight in enumerate(data['highlights'], 1):
            clean_highlight = highlight.replace('**', '').replace('Rs.', 'Rs. ')
            emojis = ['🎯', '⭐', '🔥', '💪', '✨']
            emoji = emojis[i % len(emojis)]
            post += f"{emoji} {clean_highlight}\n"
    else:
        post += """🎯 Consistent daily progress
⭐ Amazing team collaboration
🔥 Client satisfaction at 100%
"""
    
    post += f"""
💭 BEHIND THE SCENES:
Every number tells a story of dedication, late nights, and unwavering commitment to excellence. This isn't just about growth - it's about building something meaningful. 🏗️

🙏 GRATEFUL FOR:
✨ Our incredible clients who trust us
✨ Our team's hard work and dedication
✨ Every challenge that made us stronger
✨ Every win, big or small

🚀 WHAT'S NEXT:
We're just getting started! More exciting updates coming your way soon. Stay tuned! 👀

━━━━━━━━━━━━━━━━

💬 DOUBLE TAP if you're working towards your goals this week!
📌 SAVE this post for motivation
🔄 SHARE with someone who needs this energy

👇 Drop a 🔥 in the comments if you're crushing your goals!

---
📸 AI Employee Vault | {today}

#BusinessGrowth #Entrepreneur #Success #Motivation #BusinessOwner #Growth #Milestone #Hustle #Goals #BusinessLife #Entrepreneurship #SuccessStory #Grateful #Inspiration #BusinessTips #Leadership #Mindset #Achievement #Winning #Progress
"""
    
    return post


def save_drafts(facebook_post, instagram_post):
    """Save both posts to Social_Drafts folder."""
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # Save Facebook post
    fb_filename = f"facebook_post_{date_str}.md"
    fb_filepath = SOCIAL_DRAFTS / fb_filename
    
    fb_content = f"""---
type: facebook_post
platform: Facebook
status: draft
created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
requires_approval: true
---

{facebook_post}
"""
    
    fb_filepath.write_text(fb_content, encoding='utf-8')
    
    # Save Instagram post
    ig_filename = f"instagram_post_{date_str}.md"
    ig_filepath = SOCIAL_DRAFTS / ig_filename
    
    ig_content = f"""---
type: instagram_post
platform: Instagram
status: draft
created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
requires_approval: true
---

{instagram_post}
"""
    
    ig_filepath.write_text(ig_content, encoding='utf-8')
    
    return fb_filepath, ig_filepath


def ask_for_approval(fb_filepath, ig_filepath):
    """Display drafts and ask for approval."""
    
    print("\n" + "=" * 70)
    print("📱 FACEBOOK & INSTAGRAM POSTS CREATED")
    print("=" * 70)
    
    # Read Facebook post
    fb_content = fb_filepath.read_text(encoding='utf-8')
    fb_post = re.sub(r'^---\n.*?\n---\n\n', '', fb_content, flags=re.DOTALL)
    
    # Read Instagram post
    ig_content = ig_filepath.read_text(encoding='utf-8')
    ig_post = re.sub(r'^---\n.*?\n---\n\n', '', ig_content, flags=re.DOTALL)
    
    print("\n📘 FACEBOOK POST PREVIEW:\n")
    print("-" * 70)
    print(fb_post[:800])
    print("...")
    print("-" * 70)
    
    print("\n📷 INSTAGRAM POST PREVIEW:\n")
    print("-" * 70)
    print(ig_post[:800])
    print("...")
    print("-" * 70)
    
    print("\n" + "=" * 70)
    print("APPROVAL OPTIONS")
    print("=" * 70)
    print(f"\nDrafts saved to:")
    print(f"  📘 Facebook: {fb_filepath}")
    print(f"  📷 Instagram: {ig_filepath}")
    print("\nChoose an option:")
    print("  1. Approve Both - Ready to post")
    print("  2. Edit - Modify drafts in Social_Drafts folder")
    print("  3. Regenerate - Create new versions")
    print("  4. Discard - Delete both drafts")
    print("\n⚠️  Note: Copy and paste manually to each platform")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == '1':
                print("\n✅ Both drafts approved!")
                print("   Next steps:")
                print("   1. Copy Facebook post → facebook.com")
                print("   2. Copy Instagram post → instagram.com")
                print(f"   Draft locations:")
                print(f"      📘 {fb_filepath}")
                print(f"      📷 {ig_filepath}")
                
                # Update status to approved
                for filepath in [fb_filepath, ig_filepath]:
                    content = filepath.read_text(encoding='utf-8')
                    content = content.replace('status: draft', 'status: approved')
                    content = content.replace('requires_approval: true', 'requires_approval: false')
                    filepath.write_text(content, encoding='utf-8')
                
                return 'approved'
                
            elif choice == '2':
                print(f"\n✏️  Edit the files:")
                print(f"   📘 {fb_filepath}")
                print(f"   📷 {ig_filepath}")
                print("   After editing, run the script again or update status manually")
                return 'edit'
                
            elif choice == '3':
                print("\n🔄 Regenerating posts...")
                return 'regenerate'
                
            elif choice == '4':
                confirm = input("   Are you sure you want to discard both drafts? (y/n): ").strip().lower()
                if confirm == 'y':
                    fb_filepath.unlink()
                    ig_filepath.unlink()
                    print("\n🗑️  Both drafts discarded.")
                    return 'discarded'
                else:
                    print("   Drafts kept. Please choose another option.")
            else:
                print("   Invalid choice. Please enter 1-4.")
        except EOFError:
            print("\n\n⚠️  No input detected. Drafts saved for manual review.")
            return 'manual'


def main():
    """Main function to generate Facebook and Instagram posts."""
    
    print("=" * 70)
    print("📱 Facebook & Instagram Post Generator - AI Employee Vault")
    print("=" * 70)
    print(f"\n📅 Generating posts for: {datetime.now().strftime('%B %d, %Y')}")
    
    ensure_folders()
    
    # Read dashboard
    print("\n📊 Reading Dashboard.md...")
    data = read_dashboard()
    
    if data:
        print(f"   ✅ Dashboard loaded")
        if data.get('total_revenue'):
            print(f"   💰 Revenue: Rs. {data['total_revenue']}")
        if data.get('new_clients'):
            print(f"   🤝 New Clients: {data['new_clients']}")
    else:
        print("   ⚠️  Dashboard not found or empty")
    
    # Generate posts
    print("\n✨ Generating Facebook post...")
    facebook_post = generate_facebook_post(data)
    
    print("\n✨ Generating Instagram post...")
    instagram_post = generate_instagram_post(data)
    
    # Save drafts
    fb_filepath, ig_filepath = save_drafts(facebook_post, instagram_post)
    
    print(f"\n✅ Facebook draft saved to: {fb_filepath}")
    print(f"✅ Instagram draft saved to: {ig_filepath}")
    
    # Ask for approval
    result = ask_for_approval(fb_filepath, ig_filepath)
    
    print("\n" + "=" * 70)
    print(f"Action completed: {result.upper()}")
    print("=" * 70)


if __name__ == "__main__":
    main()
