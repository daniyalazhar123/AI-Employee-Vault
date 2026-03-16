"""
Social Media Summary Generator for AI Employee Vault

Generates comprehensive summaries of social media posts and engagement.
Gold Tier Requirement #4 - Facebook & Instagram with summary
Gold Tier Requirement #5 - Twitter (X) with summary

Usage:
    python social_summary_generator.py [platform] [days]
    
Examples:
    python social_summary_generator.py linkedin 7
    python social_summary_generator.py all 30
"""

import os
import json
from pathlib import Path
from datetime import datetime, timedelta
import re


# Paths
VAULT_PATH = Path(__file__).parent
SOCIAL_DRAFTS = VAULT_PATH / "Social_Drafts"
POLISHED_FOLDER = SOCIAL_DRAFTS / "Polished"
LOGS_FOLDER = VAULT_PATH / "Logs"
SUMMARIES_FOLDER = VAULT_PATH / "Social_Summaries"


def ensure_folders():
    """Ensure required folders exist."""
    SUMMARIES_FOLDER.mkdir(exist_ok=True)
    LOGS_FOLDER.mkdir(exist_ok=True)


def get_platform_files(platform):
    """Get all post files for a platform."""
    if not POLISHED_FOLDER.exists():
        return []
    
    files = []
    for file in POLISHED_FOLDER.glob(f"*{platform}*.md"):
        files.append(file)
    
    # Also check main Social_Drafts folder
    for file in SOCIAL_DRAFTS.glob(f"*{platform}*.md"):
        if file not in files:
            files.append(file)
    
    return files


def parse_post_metadata(content):
    """Parse frontmatter from post content."""
    metadata = {}
    
    # Extract frontmatter
    frontmatter_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)
        
        # Parse key-value pairs
        for line in frontmatter.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip()
    
    return metadata


def analyze_post(content, metadata):
    """Analyze a single post."""
    analysis = {
        'platform': metadata.get('platform', 'Unknown'),
        'type': metadata.get('type', 'Unknown'),
        'status': metadata.get('status', 'Unknown'),
        'created': metadata.get('created', 'Unknown'),
        'approved': metadata.get('approved', None),
        'hashtags': [],
        'mentions': [],
        'word_count': 0,
        'character_count': 0,
        'engagement_score': 0
    }
    
    # Count hashtags
    hashtags = re.findall(r'#\w+', content)
    analysis['hashtags'] = list(set(hashtags))
    
    # Count mentions
    mentions = re.findall(r'@\w+', content)
    analysis['mentions'] = list(set(mentions))
    
    # Count words and characters
    analysis['word_count'] = len(content.split())
    analysis['character_count'] = len(content)
    
    # Calculate engagement score (mock - would need API data)
    analysis['engagement_score'] = len(hashtags) * 2 + len(mentions) * 5
    
    return analysis


def generate_platform_summary(platform, days=7):
    """Generate summary for a specific platform."""
    print(f"\n{'='*70}")
    print(f"📊 {platform.upper()} SUMMARY (Last {days} days)")
    print(f"{'='*70}")
    
    files = get_platform_files(platform)
    
    if not files:
        print(f"ℹ️  No {platform} posts found")
        return None
    
    # Filter by date
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_posts = []
    
    for file in files:
        try:
            content = file.read_text(encoding='utf-8')
            metadata = parse_post_metadata(content)
            
            # Check if post is within date range
            created_str = metadata.get('created', '')
            if created_str:
                try:
                    created_date = datetime.strptime(created_str, '%Y-%m-%d %H:%M:%S')
                    if created_date >= cutoff_date:
                        analysis = analyze_post(content, metadata)
                        analysis['file'] = file.name
                        recent_posts.append(analysis)
                except:
                    # Include if date parsing fails
                    analysis = analyze_post(content, metadata)
                    analysis['file'] = file.name
                    recent_posts.append(analysis)
        except Exception as e:
            print(f"⚠️  Error reading {file.name}: {e}")
    
    if not recent_posts:
        print(f"ℹ️  No {platform} posts in last {days} days")
        return None
    
    # Generate statistics
    total_posts = len(recent_posts)
    total_hashtags = sum(len(p['hashtags']) for p in recent_posts)
    total_mentions = sum(len(p['mentions']) for p in recent_posts)
    avg_word_count = sum(p['word_count'] for p in recent_posts) / total_posts
    avg_engagement = sum(p['engagement_score'] for p in recent_posts) / total_posts
    
    # Status breakdown
    status_counts = {}
    for post in recent_posts:
        status = post['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Top hashtags
    all_hashtags = []
    for post in recent_posts:
        all_hashtags.extend(post['hashtags'])
    
    hashtag_counts = {}
    for tag in all_hashtags:
        hashtag_counts[tag] = hashtag_counts.get(tag, 0) + 1
    
    top_hashtags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Print summary
    print(f"\n📈 STATISTICS")
    print(f"   Total Posts: {total_posts}")
    print(f"   Total Hashtags: {total_hashtags}")
    print(f"   Total Mentions: {total_mentions}")
    print(f"   Avg Word Count: {avg_word_count:.1f}")
    print(f"   Avg Engagement Score: {avg_engagement:.1f}")
    
    print(f"\n📋 STATUS BREAKDOWN")
    for status, count in status_counts.items():
        print(f"   {status}: {count}")
    
    print(f"\n🔥 TOP HASHTAGS")
    for tag, count in top_hashtags:
        print(f"   {tag}: {count} times")
    
    print(f"\n📝 RECENT POSTS")
    for post in recent_posts[-5:]:  # Last 5 posts
        print(f"   • {post['file']} ({post['status']})")
        if post['hashtags']:
            print(f"     Hashtags: {', '.join(post['hashtags'][:3])}")
    
    # Create summary dict
    summary = {
        'platform': platform,
        'period_days': days,
        'generated_at': datetime.now().isoformat(),
        'statistics': {
            'total_posts': total_posts,
            'total_hashtags': total_hashtags,
            'total_mentions': total_mentions,
            'avg_word_count': avg_word_count,
            'avg_engagement_score': avg_engagement
        },
        'status_breakdown': status_counts,
        'top_hashtags': [{'tag': tag, 'count': count} for tag, count in top_hashtags],
        'recent_posts': [
            {
                'file': p['file'],
                'platform': p['platform'],
                'status': p['status'],
                'created': p['created'],
                'hashtags': p['hashtags']
            }
            for p in recent_posts[-10:]
        ]
    }
    
    return summary


def generate_all_platforms_summary(days=7):
    """Generate summary for all platforms."""
    print("="*70)
    print("📱 SOCIAL MEDIA COMPREHENSIVE SUMMARY")
    print(f"Period: Last {days} days")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    platforms = ['linkedin', 'facebook', 'instagram', 'twitter']
    all_summaries = {}
    
    for platform in platforms:
        summary = generate_platform_summary(platform, days)
        if summary:
            all_summaries[platform] = summary
    
    # Generate combined statistics
    if all_summaries:
        total_posts = sum(s['statistics']['total_posts'] for s in all_summaries.values())
        total_hashtags = sum(s['statistics']['total_hashtags'] for s in all_summaries.values())
        
        print("\n" + "="*70)
        print("🎯 COMBINED STATISTICS (All Platforms)")
        print("="*70)
        print(f"   Total Posts: {total_posts}")
        print(f"   Total Hashtags: {total_hashtags}")
        print(f"   Platforms Active: {len(all_summaries)}")
        
        print(f"\n📊 PLATFORM BREAKDOWN")
        for platform, summary in all_summaries.items():
            posts = summary['statistics']['total_posts']
            print(f"   {platform.title()}: {posts} posts")
    
    return all_summaries


def save_summary(summary, platform, days):
    """Save summary to file."""
    if not summary:
        return
    
    date_str = datetime.now().strftime('%Y-%m-%d')
    filename = f"social_summary_{platform}_{date_str}_{days}days.json"
    filepath = SUMMARIES_FOLDER / filename
    
    # Save as JSON
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Summary saved to: {filepath}")
    
    # Also create Markdown version
    md_filepath = SUMMARIES_FOLDER / f"social_summary_{platform}_{date_str}_{days}days.md"
    
    if isinstance(summary, dict):
        md_content = f"""# Social Media Summary - {platform.title()}

**Period:** Last {days} days
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Statistics

| Metric | Value |
|--------|-------|
| Total Posts | {summary['statistics'].get('total_posts', 0)} |
| Total Hashtags | {summary['statistics'].get('total_hashtags', 0)} |
| Total Mentions | {summary['statistics'].get('total_mentions', 0)} |
| Avg Word Count | {summary['statistics'].get('avg_word_count', 0):.1f} |
| Avg Engagement | {summary['statistics'].get('avg_engagement_score', 0):.1f} |

---

## Top Hashtags

"""
        
        for tag_info in summary.get('top_hashtags', []):
            md_content += f"- **{tag_info['tag']}**: {tag_info['count']} times\n"
        
        md_content += f"""
---

## Recent Posts

"""
        
        for post in summary.get('recent_posts', []):
            md_content += f"- {post['file']} ({post['status']})\n"
        
        md_filepath.write_text(md_content, encoding='utf-8')
        print(f"📄 Markdown version saved to: {md_filepath}")


def main():
    """Main function."""
    print("="*70)
    print("📱 SOCIAL MEDIA SUMMARY GENERATOR")
    print("="*70)
    
    ensure_folders()
    
    # Get command line arguments
    import sys
    
    if len(sys.argv) < 2:
        platform = 'all'
        days = 7
    else:
        platform = sys.argv[1].lower()
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    
    print(f"\n📊 Generating summary for: {platform}")
    print(f"📅 Period: Last {days} days")
    
    if platform == 'all':
        # Generate for all platforms
        summaries = generate_all_platforms_summary(days)
        
        # Save each platform summary
        for plat, summary in summaries.items():
            save_summary(summary, plat, days)
        
    else:
        # Generate for specific platform
        summary = generate_platform_summary(platform, days)
        save_summary(summary, platform, days)
    
    print("\n" + "="*70)
    print("✅ Summary generation complete!")
    print("="*70)


if __name__ == "__main__":
    main()
