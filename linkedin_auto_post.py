#!/usr/bin/env python3
"""
LinkedIn Auto-Poster - AI Employee Vault

Posts content to LinkedIn using browser automation (Playwright)
No API credentials needed!

Usage:
    python linkedin_auto_post.py "Your post content here"
    python linkedin_auto_post.py --file "Social_Drafts/linkedin_post.md"
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    print("❌ Playwright not installed!")
    print("Install with: playwright install chromium")
    PLAYWRIGHT_AVAILABLE = False
    sys.exit(1)


class LinkedInAutoPoster:
    """Automated LinkedIn poster using Playwright"""

    def __init__(self):
        self.email = os.getenv('LINKEDIN_EMAIL', '')
        self.password = os.getenv('LINKEDIN_PASSWORD', '')
        self.dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'
        
        self.vault_path = Path(__file__).parent
        self.logs_folder = self.vault_path / 'Logs'
        self.logs_folder.mkdir(exist_ok=True)
        
        print("="*60)
        print("  LinkedIn Auto-Poster - AI Employee Vault")
        print("="*60)
        print()

    def login(self, page):
        """Login to LinkedIn"""
        print("🔐 Logging in to LinkedIn...")
        
        # Go to LinkedIn login
        page.goto('https://www.linkedin.com/login')
        time.sleep(2)
        
        # Find and fill email
        email_field = page.locator('#username')
        if email_field.is_visible():
            email_field.fill(self.email)
            print(f"   ✅ Email entered: {self.email}")
        
        # Find and fill password
        password_field = page.locator('#password')
        if password_field.is_visible():
            password_field.fill(self.password)
            print("   ✅ Password entered")
        
        # Click sign in
        sign_in_button = page.locator('button[type="submit"]')
        if sign_in_button.is_visible():
            sign_in_button.click()
            print("   ✅ Sign in button clicked")
            time.sleep(3)  # Wait for login
        
        # Check if login successful
        if 'feed' in page.url or 'mynetwork' in page.url:
            print("   ✅ Login successful!")
            return True
        else:
            print("   ❌ Login failed. Check credentials.")
            return False

    def post(self, content: str) -> bool:
        """Post content to LinkedIn"""
        if self.dry_run:
            print("⚠️  DRY RUN MODE - Not actually posting")
            print(f"📝 Content would be posted:\n{content}")
            return True
        
        try:
            with sync_playwright() as p:
                # Launch browser
                print("🌐 Launching browser...")
                browser = p.chromium.launch(headless=False)  # Visible browser for debugging
                context = browser.new_context()
                page = context.new_page()
                
                # Login
                if not self.login(page):
                    browser.close()
                    return False
                
                # Go to create post page
                print("📝 Navigating to post creation...")
                page.goto('https://www.linkedin.com/feed/')
                time.sleep(2)
                
                # Find the post creation textbox
                print("   Finding post input...")
                textbox = page.locator('div[role="textbox"]').first
                if not textbox.is_visible():
                    print("   ❌ Post input not found")
                    browser.close()
                    return False
                
                # Fill content
                print("   Entering content...")
                textbox.fill(content)
                time.sleep(1)
                
                # Click post button
                print("   Clicking Post button...")
                post_button = page.locator('button:has-text("Post")').first
                if post_button.is_visible():
                    post_button.click()
                    time.sleep(2)
                    print("   ✅ Post button clicked!")
                else:
                    print("   ❌ Post button not found")
                    browser.close()
                    return False
                
                # Wait for post to be published
                print("   Waiting for post to publish...")
                time.sleep(3)
                
                # Verify post was published
                if 'feed' in page.url:
                    print("   ✅ Post published successfully!")
                    
                    # Save to logs
                    self.save_post_log(content)
                    
                    browser.close()
                    return True
                else:
                    print("   ⚠️  Post may not have published")
                    browser.close()
                    return False
                    
        except Exception as e:
            print(f"❌ Error posting: {e}")
            return False

    def save_post_log(self, content: str):
        """Save post to logs"""
        log_file = self.logs_folder / f'linkedin_post_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        
        log_content = f"""---
type: linkedin_post
platform: LinkedIn
posted: {datetime.now().isoformat()}
status: published
---

# LinkedIn Post

{content}

---
*Posted via AI Employee Vault*
"""
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(log_content)
        
        print(f"   📁 Post log saved: {log_file.name}")

    def post_from_file(self, file_path: str) -> bool:
        """Read content from file and post"""
        file = Path(file_path)
        if not file.exists():
            print(f"❌ File not found: {file_path}")
            return False
        
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract content from markdown (remove frontmatter)
        if '---' in content:
            parts = content.split('---', 2)
            if len(parts) > 2:
                content = parts[2].strip()
        
        print(f"📄 Reading content from: {file_path}")
        print(f"   Content length: {len(content)} characters")
        
        return self.post(content)


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python linkedin_auto_post.py \"Your post content here\"")
        print("  python linkedin_auto_post.py --file \"Social_Drafts/post.md\"")
        print()
        print("Environment Variables:")
        print("  LINKEDIN_EMAIL - Your LinkedIn email")
        print("  LINKEDIN_PASSWORD - Your LinkedIn password")
        print("  DRY_RUN=true - Test without posting (default)")
        print("  DRY_RUN=false - Actually post to LinkedIn")
        sys.exit(1)
    
    poster = LinkedInAutoPoster()
    
    # Check credentials
    if not poster.email or not poster.password:
        print("⚠️  LinkedIn credentials not set!")
        print()
        print("Please set in .env file:")
        print("  LINKEDIN_EMAIL=your.email@example.com")
        print("  LINKEDIN_PASSWORD=your_password")
        print()
        print("Or set DRY_RUN=true to test without credentials")
        sys.exit(1)
    
    # Get content
    if sys.argv[1] == '--file':
        if len(sys.argv) < 3:
            print("❌ Please specify file path")
            sys.exit(1)
        success = poster.post_from_file(sys.argv[2])
    else:
        content = ' '.join(sys.argv[1:])
        success = poster.post(content)
    
    # Exit with status
    if success:
        print()
        print("="*60)
        print("  ✅ LINKEDIN POST SUCCESSFUL!")
        print("="*60)
        sys.exit(0)
    else:
        print()
        print("="*60)
        print("  ❌ LINKEDIN POST FAILED")
        print("="*60)
        sys.exit(1)


if __name__ == '__main__':
    main()
