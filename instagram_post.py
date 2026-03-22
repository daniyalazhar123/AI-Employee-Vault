#!/usr/bin/env python3
"""
📷 INSTAGRAM POST GENERATOR
Personal AI Employee Hackathon 0 - Gold Tier
Generates engaging Instagram posts with visual focus, emojis, and hashtags
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import json


class InstagramPostGenerator:
    """
    Instagram Post Generator
    
    Features:
    - Visual-first content
    - Emoji-rich captions
    - Instagram hashtag strategy (30 max)
    - Story and Reel support
    - Engagement optimization
    """
    
    def __init__(self, vault_path: str = None):
        self.vault = Path(vault_path) if vault_path else Path('.')
        self.drafts_folder = self.vault / 'Social_Drafts' / 'instagram'
        self.drafts_folder.mkdir(parents=True, exist_ok=True)
        
        # Instagram-specific settings
        self.max_caption_length = 2200  # Instagram limit
        self.optimal_length = 150  # Optimal engagement
        self.hashtag_limit = 30  # Instagram allows exactly 30
        self.hashtag_optimal = 15  # Best engagement at 15-20
        
        print("📷 Instagram Post Generator initialized")
    
    def generate_post(self, topic: str = None, image_description: str = None) -> str:
        """Generate Instagram post"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Default values
        if not topic:
            topic = "AI Business Solutions"
        
        if not image_description:
            image_description = "Professional workspace with AI technology"
        
        # Generate Instagram-specific content
        post_content = self._create_instagram_content(topic, image_description)
        
        # Create draft file
        draft_file = self.drafts_folder / f"INSTAGRAM_{timestamp}.md"
        draft_file.write_text(post_content, encoding='utf-8')
        
        print(f"✅ Instagram post created: {draft_file.name}")
        return str(draft_file)
    
    def _create_instagram_content(self, topic: str, image_description: str) -> str:
        """Create Instagram-specific content"""
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Instagram emojis (more liberal than Facebook)
        emojis = {
            'fire': '🔥',
            'rocket': '🚀',
            'lightning': '⚡',
            'target': '🎯',
            'chart': '📊',
            'computer': '💻',
            'phone': '📱',
            'camera': '📷',
            'star': '⭐',
            'sparkles': '✨',
            'bulb': '💡',
            'check': '✅',
            'arrow': '👇',
            'link': '🔗',
            'message': '💬',
            'heart': '❤️',
            'thumbsup': '👍',
            'party': '🎉',
            'gift': '🎁',
            'time': '⏰'
        }
        
        content = f"""---
type: instagram_post
platform: instagram
topic: {topic}
created_by: instagram_generator
created: {datetime.now().isoformat()}
status: draft
format: feed_post
image_required: true
---

# 📷 Instagram Post Draft

**Topic:** {topic}  
**Created:** {timestamp}  
**Platform:** Instagram  
**Format:** Feed Post  
**Caption Length:** ~150-200 characters  
**Hashtags:** 25-30 (max allowed)

---

## 📸 Visual Direction

**Image/Video:** {image_description}

**Style Notes:**
- High-quality, professional image
- Bright, engaging colors
- Clear focal point
- Instagram-worthy aesthetic
- Consider carousel format for multiple points

**Alt Text:** Professional AI technology setup for business automation

---

## 📝 Caption

{emojis['rocket']} Transform Your Business with AI {emojis['fire']}

{emojis['bulb']} Did you know AI can work 24/7 for your business?

✨ What our AI Employee does:
{emojis['check']} Instant customer responses
{emojis['check']} Automated workflows
{emojis['check']} Lead generation
{emojis['check']} 24/7 availability

{emojis['chart']} Results you'll see:
• 85% cost reduction
• 10x faster responses
• Zero missed opportunities
• Scalable growth

{emojis['sparkles']} Ready to future-proof your business?

{emojis['arrow']} Link in bio to learn more!
{emojis['message']} DM us for a free consultation

---

{self._generate_instagram_hashtags(topic)}

---

## 📊 Instagram Best Practices Applied

**✅ Hashtag Strategy:**
- 30 hashtags (maximum allowed)
- Mix of popular and niche
- Industry-specific tags
- Branded hashtag included

**✅ Engagement Optimization:**
- Strong hook in first line
- Clear value proposition
- Call-to-action included
- Question to encourage comments

**✅ Visual Guidelines:**
- Square format (1080x1080) recommended
- High contrast for mobile
- Text overlay minimal
- Brand colors consistent

**✅ Posting Tips:**
- Best times: 11 AM - 1 PM, 7-9 PM
- Use Instagram Stories for behind-the-scenes
- Engage with comments within 1 hour
- Share to Stories after posting

---

## 🎨 Story Version (Optional)

**Slide 1:** Hook - "AI can work 24/7 for you! 🚀"
**Slide 2:** Problem - "Missing customer messages?"
**Slide 3:** Solution - "AI Employee never sleeps!"
**Slide 4:** CTA - "Swipe up / Link in bio"

**Story Stickers:**
- Poll: "Need 24/7 support? Yes/No"
- Question: "What's your biggest challenge?"
- Link: Direct to landing page

---

**🔒 Security Note:** This is a DRAFT - requires approval before posting
"""
        return content
    
    def _generate_instagram_hashtags(self, topic: str) -> str:
        """Generate Instagram-specific hashtags (30 max)"""
        
        # Instagram hashtag strategy: Tiered approach
        hashtags = [
            # High popularity (1M+ posts)
            "#AI",
            "#Technology",
            "#Business",
            "#Innovation",
            "#Entrepreneur",
            
            # Medium popularity (100K-1M posts)
            "#Automation",
            "#DigitalTransformation",
            "#SmallBusiness",
            "#Startup",
            "#Productivity",
            "#TechTrends",
            "#BusinessOwner",
            "#OnlineBusiness",
            
            # Niche (10K-100K posts)
            "#AIEmployee",
            "#BusinessAutomation",
            "#AITools",
            "#SmartBusiness",
            "#FutureOfWork",
            "#BusinessGrowth",
            "#TechSolutions",
            "#DigitalBusiness",
            
            # Community tags
            "#EntrepreneurLife",
            "#BusinessTips",
            "#TechCommunity",
            "#StartupLife",
            
            # Branded/Campaign
            "#AI2026",
            "#AutomateToGrow",
            "#AIPowered"
        ]
        
        # Ensure we don't exceed 30
        return ' '.join(hashtags[:30])
    
    def generate_reel_script(self, topic: str = None) -> str:
        """Generate Instagram Reel script"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if not topic:
            topic = "AI Business Transformation"
        
        content = f"""---
type: instagram_reel
platform: instagram
topic: {topic}
created: {datetime.now().isoformat()}
duration: 30-60 seconds
format: vertical_video
---

# 📷 Instagram Reel Script

**Topic:** {topic}  
**Duration:** 30-60 seconds  
**Format:** 9:16 Vertical Video  
**Audio:** Trending business/tech sound

---

## 🎬 Script

**[0-3 seconds]** - HOOK
📸 Visual: Eye-catching AI animation
📝 Text Overlay: "Your business needs THIS! 🚀"
🎵 Audio: Trending sound starts

**[3-10 seconds]** - PROBLEM
📸 Visual: Stressed business owner
📝 Text: "Working 24/7 yourself?"
🎵 Audio: Relatable sound

**[10-20 seconds]** - SOLUTION
📸 Visual: AI dashboard, automation demo
📝 Text: "AI Employee works while you sleep! 💤"
🎵 Audio: Upbeat transition

**[20-25 seconds]** - RESULTS
📸 Visual: Growth charts, happy client
📝 Text: "85% cost reduction 📊"
🎵 Audio: Success sound

**[25-30 seconds]** - CTA
📸 Visual: Your logo + contact
📝 Text: "Link in bio! 🔗"
🎵 Audio: Call-to-action sound

---

## 📝 Caption

Transform your business with AI! 🚀

Our AI Employee:
✅ Works 24/7
✅ Never misses messages
✅ Cuts costs by 85%
✅ Scales instantly

Ready to grow? Link in bio! 🔗

#AI #Business #Automation #Reels #Entrepreneur #TechTrends #BusinessGrowth #AI2026

---

**🔒 Security Note:** This is a DRAFT - requires approval before posting
"""
        
        draft_file = self.drafts_folder / f"INSTAGRAM_REEL_{timestamp}.md"
        draft_file.write_text(content, encoding='utf-8')
        print(f"✅ Instagram Reel script created: {draft_file.name}")
        return str(draft_file)
    
    def generate_carousel_post(self, topic: str = None) -> str:
        """Generate Instagram Carousel post (multiple slides)"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        content = f"""---
type: instagram_carousel
platform: instagram
topic: Business Automation
created: {datetime.now().isoformat()}
slides: 5-7
format: square_images
---

# 📷 Instagram Carousel Post

**Topic:** Business Automation  
**Slides:** 5-7  
**Format:** Square (1080x1080)

---

## 📊 Slide Breakdown

**Slide 1/7** - HOOK
📸 Visual: Bold headline
📝 Text: "7 Ways AI Transforms Business 🚀"
🎨 Style: Eye-catching gradient background

**Slide 2/7** - Point 1
📸 Visual: Clock/24-7 icon
📝 Text: "1️⃣ 24/7 Customer Service"
💡 Detail: "Never miss a message"

**Slide 3/7** - Point 2
📸 Visual: Money/cost icon
📝 Text: "2️⃣ 85% Cost Reduction"
💡 Detail: "Save on staffing costs"

**Slide 4/7** - Point 3
📸 Visual: Speed/rocket icon
📝 Text: "3️⃣ 10x Faster Responses"
💡 Detail: "Instant customer replies"

**Slide 5/7** - Point 4
📸 Visual: Growth chart
📝 Text: "4️⃣ Scalable Growth"
💡 Detail: "Grow without hiring"

**Slide 6/7** - Point 5
📸 Visual: Analytics dashboard
📝 Text: "5️⃣ Data-Driven Decisions"
💡 Detail: "Real-time insights"

**Slide 7/7** - CTA
📸 Visual: Your logo + contact
📝 Text: "Ready to Start? 🎯"
💡 Detail: "Link in bio!"

---

## 📝 Caption

Swipe to see how AI transforms business! 👉

Which benefit matters most to you?
Comment below! 👇

#AI #Business #Automation #Carousel #Entrepreneur #BusinessTips #TechTrends #Growth #AI2026

---

**🔒 Security Note:** This is a DRAFT - requires approval before posting
"""
        
        draft_file = self.drafts_folder / f"INSTAGRAM_CAROUSEL_{timestamp}.md"
        draft_file.write_text(content, encoding='utf-8')
        print(f"✅ Instagram Carousel post created: {draft_file.name}")
        return str(draft_file)


def main():
    """Main entry point"""
    print("="*60)
    print("📷 INSTAGRAM POST GENERATOR")
    print("Personal AI Employee Hackathon 0 - Gold Tier")
    print("="*60)
    
    # Initialize generator
    vault_path = sys.argv[1] if len(sys.argv) > 1 else 'C:/Users/CC/Documents/Obsidian Vault'
    generator = InstagramPostGenerator(vault_path)
    
    # Generate posts
    print("\n📝 Generating Instagram posts...")
    
    # Generate general post
    draft1 = generator.generate_post("AI Business Solutions", "Modern office with AI technology")
    print(f"✅ General post: {draft1}")
    
    # Generate Reel script
    draft2 = generator.generate_reel_script("AI Transformation")
    print(f"✅ Reel script: {draft2}")
    
    # Generate Carousel post
    draft3 = generator.generate_carousel_post("Business Automation")
    print(f"✅ Carousel post: {draft3}")
    
    print("\n" + "="*60)
    print("✅ INSTAGRAM POST GENERATION COMPLETE!")
    print("="*60)
    print(f"\n📂 Drafts saved to: {generator.drafts_folder}")
    print("\n📊 Posts created:")
    print("  - 1 Feed post")
    print("  - 1 Reel script")
    print("  - 1 Carousel post (7 slides)")
    print("\n🔒 All posts require approval before posting")
    print("="*60)


if __name__ == '__main__':
    main()
