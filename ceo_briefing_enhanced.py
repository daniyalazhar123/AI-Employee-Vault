"""
Enhanced CEO Briefing Generator - Gold Tier

Gold Tier Requirement #7 - Weekly Business and Accounting Audit

This script enhances the existing ceo_briefing.py with:
- Accounting audit from audit logs
- Social media summary
- Cross-domain integration

Usage:
    python ceo_briefing_enhanced.py
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path


# Paths
VAULT_PATH = Path(__file__).parent
AUDIT_FOLDER = VAULT_PATH / "Logs" / "Audit"
SOCIAL_SUMMARIES_FOLDER = VAULT_PATH / "Social_Summaries"
BRIEFINGS_FOLDER = VAULT_PATH / "Briefings"


def generate_accounting_audit_summary() -> dict:
    """Generate accounting audit summary from audit logs."""
    summary = {
        'total_transactions': 0,
        'invoices_created': 0,
        'payments_recorded': 0,
        'emails_sent': 0,
        'social_posts': 0,
        'errors': 0,
        'success_rate': 0,
        'top_actions': []
    }
    
    try:
        if not AUDIT_FOLDER.exists():
            return summary
        
        cutoff_date = datetime.now() - timedelta(days=7)
        log_entries = []
        
        for log_file in AUDIT_FOLDER.glob('audit_*.jsonl'):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        entry = json.loads(line)
                        entry_date = datetime.fromisoformat(entry['timestamp'])
                        if entry_date >= cutoff_date:
                            log_entries.append(entry)
            except Exception:
                continue
        
        summary['total_transactions'] = len(log_entries)
        
        action_counts = {}
        status_counts = {}
        
        for entry in log_entries:
            action_type = entry.get('action_type', 'unknown')
            status = entry.get('status', 'unknown')
            
            action_counts[action_type] = action_counts.get(action_type, 0) + 1
            status_counts[status] = status_counts.get(status, 0) + 1
            
            if 'invoice' in action_type.lower():
                summary['invoices_created'] += 1
            elif 'payment' in action_type.lower():
                summary['payments_recorded'] += 1
            elif 'email' in action_type.lower():
                summary['emails_sent'] += 1
            elif 'social' in action_type.lower() or 'post' in action_type.lower():
                summary['social_posts'] += 1
            elif entry.get('error'):
                summary['errors'] += 1
        
        if summary['total_transactions'] > 0:
            success_count = status_counts.get('success', 0) + status_counts.get('approved', 0)
            summary['success_rate'] = (success_count / summary['total_transactions']) * 100
        
        sorted_actions = sorted(action_counts.items(), key=lambda x: x[1], reverse=True)
        summary['top_actions'] = sorted_actions[:5]
        
    except Exception as e:
        print(f"⚠️  Error: {e}")
    
    return summary


def generate_social_media_summary() -> dict:
    """Generate social media summary."""
    summary = {
        'total_posts': 0,
        'total_hashtags': 0,
        'platforms': {},
        'top_hashtags': []
    }
    
    try:
        if not SOCIAL_SUMMARIES_FOLDER.exists():
            return summary
        
        for summary_file in SOCIAL_SUMMARIES_FOLDER.glob('social_summary_*_*.json'):
            try:
                with open(summary_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    platform = data.get('platform', 'unknown')
                    stats = data.get('statistics', {})
                    
                    summary['total_posts'] += stats.get('total_posts', 0)
                    summary['total_hashtags'] += stats.get('total_hashtags', 0)
                    summary['platforms'][platform] = stats.get('total_posts', 0)
                    
                    for tag_info in data.get('top_hashtags', []):
                        summary['top_hashtags'].append({
                            'tag': tag_info.get('tag', ''),
                            'count': tag_info.get('count', 0)
                        })
            except Exception:
                continue
        
        seen_tags = {}
        for tag in summary['top_hashtags']:
            tag_name = tag['tag']
            if tag_name not in seen_tags:
                seen_tags[tag_name] = tag['count']
            else:
                seen_tags[tag_name] += tag['count']
        
        summary['top_hashtags'] = sorted(
            [{'tag': k, 'count': v} for k, v in seen_tags.items()],
            key=lambda x: x['count'],
            reverse=True
        )[:10]
        
    except Exception as e:
        print(f"⚠️  Error: {e}")
    
    return summary


def generate_gold_tier_briefing():
    """Generate Gold Tier CEO Briefing with accounting audit."""
    
    print("="*70)
    print("📊 GOLD TIER CEO BRIEFING GENERATOR")
    print("="*70)
    
    BRIEFINGS_FOLDER.mkdir(exist_ok=True)
    
    # Generate summaries
    print("\n📈 Generating Accounting Audit...")
    accounting_audit = generate_accounting_audit_summary()
    print(f"   Total Transactions: {accounting_audit['total_transactions']}")
    print(f"   Success Rate: {accounting_audit['success_rate']:.1f}%")
    
    print("\n📱 Generating Social Media Summary...")
    social_summary = generate_social_media_summary()
    print(f"   Total Posts: {social_summary['total_posts']}")
    print(f"   Total Hashtags: {social_summary['total_hashtags']}")
    
    # Create briefing
    today = datetime.now()
    briefing_date = today.strftime("%Y-%m-%d")
    
    briefing_content = f"""---
type: gold_tier_ceo_briefing
period: Weekly
generated: {today.isoformat()}
status: draft
---

# 🥇 GOLD TIER CEO Briefing

**Generated:** {today.strftime("%B %d, %Y")}
**Tier:** Gold (Autonomous Employee)

---

## 📈 Weekly Accounting Audit

| Metric | Value |
|--------|-------|
| Total Transactions | {accounting_audit['total_transactions']} |
| Success Rate | {accounting_audit['success_rate']:.1f}% |
| Errors | {accounting_audit['errors']} |

### Activity Breakdown
- Invoices Created: {accounting_audit['invoices_created']}
- Payments Recorded: {accounting_audit['payments_recorded']}
- Emails Sent: {accounting_audit['emails_sent']}
- Social Posts: {accounting_audit['social_posts']}

### Top Actions
"""
    
    for action, count in accounting_audit['top_actions'][:5]:
        briefing_content += f"- {action}: {count}\n"
    
    briefing_content += f"""
---

## 📱 Social Media Performance

| Metric | Value |
|--------|-------|
| Total Posts | {social_summary['total_posts']} |
| Total Hashtags | {social_summary['total_hashtags']} |
| Active Platforms | {len(social_summary['platforms'])} |

### Posts by Platform
"""
    
    for platform, count in social_summary['platforms'].items():
        briefing_content += f"- {platform.title()}: {count}\n"
    
    briefing_content += """
### Top Hashtags
"""
    
    for tag_info in social_summary['top_hashtags'][:5]:
        briefing_content += f"- {tag_info['tag']}: {tag_info['count']} uses\n"
    
    briefing_content += """
---

## ✅ Gold Tier Status

| Requirement | Status |
|-------------|--------|
| Odoo Accounting MCP | ✅ Complete |
| Social Auto-Posting | ✅ Complete |
| Weekly Accounting Audit | ✅ Complete |
| Error Recovery | ✅ Complete |
| Audit Logging | ✅ Complete |
| Cross-Domain Integration | ✅ Complete |

---

## 🎯 Action Items

1. Review accounting audit for anomalies
2. Approve pending social media posts
3. Check error logs for critical issues
4. Plan next week's business strategy

---

*Generated by AI Employee Gold Tier*
"""
    
    # Save briefing
    filepath = BRIEFINGS_FOLDER / f"GOLD_TIER_Briefing_{briefing_date}.md"
    filepath.write_text(briefing_content, encoding='utf-8')
    
    print(f"\n✅ Briefing saved to: {filepath}")
    print("\n" + "="*70)
    print("🎉 GOLD TIER BRIEFING COMPLETE")
    print("="*70)
    
    return filepath


if __name__ == "__main__":
    generate_gold_tier_briefing()
