"""
Twitter Post Generator for AI Employee Vault

Reads Dashboard.md and generates 3 tweet options (under 280 chars each).
Saves drafts and asks for human approval.
"""

import os
import re
from datetime import datetime
from pathlib import Path


# Paths
VAULT_PATH = Path(__file__).parent
DASHBOARD_FILE = VAULT_PATH / "Dashboard.md"
SOCIAL_DRAFTS = VAULT_PATH / "Social_Drafts"

# Twitter character limit
MAX_CHARS = 280


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
        data['highlights'] = [h.strip() for h in highlights[:2]]
    
    # Extract status
    status_match = re.search(r'\*\*Status:\*\*\s*(.+)$', content, re.MULTILINE)
    if status_match:
        data['status'] = status_match.group(1).strip()
    
    return data


def generate_tweet_options(data):
    """Generate 3 different tweet options."""
    
    tweets = []
    
    # Tweet Option 1: Revenue focused
    tweet1 = f"🚀 Business Update: Achieved Rs. {data.get('total_revenue', 'N/A')} in revenue! "
    
    if data and data.get('new_clients'):
        tweet1 += f"Welcomed {data['new_clients']} new clients. "
    
    tweet1 += "Grateful for the trust and continued support. Here's to more growth! 📈 "
    tweet1 += "#BusinessGrowth #Success #Entrepreneurship"
    
    # Ensure under 280 chars
    if len(tweet1) > MAX_CHARS:
        tweet1 = tweet1[:MAX_CHARS-3] + "..."
    
    tweets.append(tweet1[:MAX_CHARS])
    
    # Tweet Option 2: Client focused
    tweet2 = f"🤝 {data.get('new_clients', 'New')} new clients joined us this period! "
    
    if data and data.get('total_revenue'):
        tweet2 += f"Revenue: Rs. {data['total_revenue']}. "
    
    tweet2 += "Your success is our success. Let's build something amazing together! 💼 "
    tweet2 += "#ClientSuccess #Business #Growth"
    
    if len(tweet2) > MAX_CHARS:
        tweet2 = tweet2[:MAX_CHARS-3] + "..."
    
    tweets.append(tweet2[:MAX_CHARS])
    
    # Tweet Option 3: Motivational/Progress focused
    tweet3 = "📊 Consistent progress, one milestone at a time. "
    
    if data and data.get('months_tracked'):
        tweet3 += f"{data['months_tracked']} months of tracking growth. "
    
    if data and data.get('highlights'):
        highlight = data['highlights'][0].replace('**', '')[:50]
        tweet3 += f"Highlight: {highlight}. "
    
    tweet3 += "Keep pushing forward! 💪 #Motivation #Progress #Goals"
    
    if len(tweet3) > MAX_CHARS:
        tweet3 = tweet3[:MAX_CHARS-3] + "..."
    
    tweets.append(tweet3[:MAX_CHARS])
    
    return tweets


def save_tweets(tweets):
    """Save tweets to Social_Drafts folder."""
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"twitter_post_{date_str}.md"
    filepath = SOCIAL_DRAFTS / filename
    
    content = f"""---
type: twitter_posts
platform: Twitter/X
status: draft
created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
requires_approval: true
options: 3
---

# Twitter Post Options

**Generated:** {datetime.now().strftime("%B %d, %Y")}  
**Character Limit:** {MAX_CHARS} characters  
**Status:** Awaiting Approval

---

## Tweet Option 1 🚀

```
{tweets[0]}
```

**Character Count:** {len(tweets[0])}/{MAX_CHARS}

---

## Tweet Option 2 🤝

```
{tweets[1]}
```

**Character Count:** {len(tweets[1])}/{MAX_CHARS}

---

## Tweet Option 3 💪

```
{tweets[2]}
```

**Character Count:** {len(tweets[2])}/{MAX_CHARS}

---

## Posting Instructions

1. Choose your preferred tweet option (1, 2, or 3)
2. Copy the text from the code block above
3. Go to twitter.com or open Twitter app
4. Paste and post!

### Best Practices:
- Add relevant image/media for better engagement
- Post during peak hours (9-11 AM or 7-9 PM)
- Engage with replies promptly
- Consider threading for longer updates

---
*Generated by AI Employee Vault*
"""
    
    filepath.write_text(content, encoding='utf-8')
    
    return filepath


def ask_for_approval(filepath, tweets):
    """Display tweet options and ask for approval."""
    
    print("\n" + "=" * 70)
    print("🐦 TWITTER POST OPTIONS CREATED")
    print("=" * 70)
    
    for i, tweet in enumerate(tweets, 1):
        emoji = ['🚀', '🤝', '💪'][i-1]
        print(f"\n{emoji} TWEET OPTION {i}:")
        print("-" * 70)
        print(tweet)
        print("-" * 70)
        print(f"Characters: {len(tweet)}/{MAX_CHARS}")
    
    print("\n" + "=" * 70)
    print("APPROVAL OPTIONS")
    print("=" * 70)
    print(f"\nDraft saved to: {filepath}")
    print("\nChoose an option:")
    print("  1. Approve - Ready to post (select option 1, 2, or 3)")
    print("  2. Edit - Modify draft in Social_Drafts folder")
    print("  3. Regenerate - Create new tweet options")
    print("  4. Discard - Delete this draft")
    print("\n⚠️  Note: Copy and paste manually to Twitter/X")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == '1':
                # Ask which tweet option
                while True:
                    try:
                        tweet_num = input("\nWhich tweet option to post? (1/2/3): ").strip()
                        if tweet_num in ['1', '2', '3']:
                            print(f"\n✅ Tweet Option {tweet_num} approved!")
                            print(f"   Next step: Copy and paste to twitter.com")
                            print(f"   Draft location: {filepath}")
                            
                            # Update status to approved
                            content = filepath.read_text(encoding='utf-8')
                            content = content.replace('status: draft', 'status: approved')
                            content = content.replace('requires_approval: true', 'requires_approval: false')
                            content = content.replace(
                                f'created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                                f'created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\napproved: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\nselected_option: {tweet_num}'
                            )
                            filepath.write_text(content, encoding='utf-8')
                            
                            return 'approved'
                        else:
                            print("   Please enter 1, 2, or 3")
                    except EOFError:
                        break
                break
                
            elif choice == '2':
                print(f"\n✏️  Edit the file at: {filepath}")
                print("   After editing, you can manually update the status to 'approved'")
                return 'edit'
                
            elif choice == '3':
                print("\n🔄 Regenerating tweet options...")
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
        except EOFError:
            print("\n\n⚠️  No input detected. Draft saved for manual review.")
            return 'manual'


def main():
    """Main function to generate Twitter posts."""
    
    print("=" * 70)
    print("🐦 Twitter Post Generator - AI Employee Vault")
    print("=" * 70)
    print(f"\n📅 Generating tweets for: {datetime.now().strftime('%B %d, %Y')}")
    
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
    
    # Generate tweets
    print("\n✨ Generating 3 tweet options...")
    tweets = generate_tweet_options(data)
    
    # Validate character counts
    for i, tweet in enumerate(tweets, 1):
        status = "✅" if len(tweet) <= MAX_CHARS else "⚠️"
        print(f"   {status} Tweet {i}: {len(tweet)}/{MAX_CHARS} characters")
    
    # Save drafts
    filepath = save_tweets(tweets)
    print(f"\n✅ Draft saved to: {filepath}")
    
    # Ask for approval
    result = ask_for_approval(filepath, tweets)
    
    print("\n" + "=" * 70)
    print(f"Action completed: {result.upper()}")
    print("=" * 70)


if __name__ == "__main__":
    main()
