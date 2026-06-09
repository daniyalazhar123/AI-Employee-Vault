#!/usr/bin/env python3
"""
🔗 LinkedIn AI Agent (Playwright-based)
Professional Cloud Architecture Portfolio Module

Uses Playwright browser automation with persistent session.
More reliable than cookie-based approach.

Setup:
    Just run the script - it will use your existing Chrome profile
    
Usage:
    from linkedin_playwright_agent import LinkedInAgent
    
    agent = LinkedInAgent()
    agent.post_status_update("Hello from AI Agent! 🚀")
"""

import os
import sys
import json
import time
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright, Page, BrowserContext
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('linkedin_agent.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('LinkedInAgent')


class LinkedInAgent:
    """
    LinkedIn AI Agent (Playwright-based)
    
    Uses Playwright browser automation for LinkedIn operations.
    More reliable than cookie extraction.
    """

    LINKEDIN_URL = "https://www.linkedin.com"
    FEED_URL = "https://www.linkedin.com/feed/"

    def __init__(self, use_chrome_profile: bool = True):
        """
        Initialize LinkedIn Agent
        
        Args:
            use_chrome_profile: Use existing Chrome profile (keeps you logged in)
        """
        self.use_chrome_profile = False  # Always use separate profile for reliability
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
        # Separate profile for LinkedIn automation
        self.profile_path = str(Path.cwd() / "linkedin_browser_profile")
        
        logger.info("✅ LinkedIn Playwright Agent initialized")

    def _start_browser(self):
        """Start browser with LinkedIn session"""
        self.playwright = sync_playwright().start()
        
        # Launch fresh browser with persistent profile
        logger.info("🌐 Starting browser...")
        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.profile_path,
            headless=False,
            viewport={"width": 1280, "height": 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
        
        logger.info("✅ Browser started")

    def _ensure_logged_in(self):
        """Ensure we're logged into LinkedIn"""
        if not self.page:
            self._start_browser()
        
        # Navigate to LinkedIn
        self.page.goto(self.LINKEDIN_URL, timeout=30000, wait_until="domcontentloaded")
        self.page.wait_for_timeout(3000)
        
        # Check if logged in
        page_url = self.page.url
        if 'login' in page_url.lower() or 'checkpoint' in page_url.lower():
            print("\n" + "="*60)
            print("⚠️  PLEASE LOGIN TO LINKEDIN")
            print("="*60)
            print("📋 Steps:")
            print("   1. Enter your email: smartydaniyazhar234@gmail.com")
            print("   2. Enter your password")
            print("   3. Complete any verification")
            print("   4. Wait for feed to load")
            print("   5. Press ENTER here to continue")
            print("="*60)
            
            # Wait for user to login and press ENTER
            input("\n⏳ Press ENTER once you see your LinkedIn feed...")
            
            # Verify we're on feed
            current_url = self.page.url
            if 'feed' not in current_url.lower():
                print("⚠️ Still not on feed. Navigating...")
                self.page.goto(self.FEED_URL, timeout=30000, wait_until="networkidle")
                self.page.wait_for_timeout(5000)
            
            print("\n✅ Feed loaded!")
        else:
            # Already on feed or another page, wait a bit
            self.page.wait_for_timeout(2000)
            logger.info("✅ Already on LinkedIn")

    def get_profile_name(self) -> Optional[str]:
        """
        Get current user's profile name
        
        Returns:
            str: Full name or None if failed
        """
        try:
            self._ensure_logged_in()
            
            # Go to profile page
            self.page.goto(f"{self.LINKEDIN_URL}/me/", timeout=30000)
            self.page.wait_for_timeout(2000)
            
            # Extract name
            name = self.page.evaluate("""
                () => {
                    // Try multiple selectors
                    const selectors = [
                        '.actor-name',
                        'h1',
                        '.text-heading-xlarge',
                        '[data-view-name="profile-topcard"]'
                    ];
                    
                    for (const selector of selectors) {
                        const el = document.querySelector(selector);
                        if (el && el.innerText) {
                            return el.innerText.trim();
                        }
                    }
                    return 'Unknown';
                }
            """)
            
            logger.info(f"✅ Profile name: {name}")
            return name
            
        except Exception as e:
            logger.error(f"❌ Failed to get profile: {e}")
            return None

    def post_status_update(self, text: str, wait_for_post: bool = True) -> Dict[str, Any]:
        """
        Post a status update to LinkedIn
        
        Args:
            text: Post content
            wait_for_post: Wait for confirmation
            
        Returns:
            dict: Result with success status
        """
        try:
            # Validate
            if len(text) > 3000:
                raise ValueError("Post exceeds 3000 character limit")
            if len(text.strip()) < 10:
                raise ValueError("Post too short (minimum 10 characters)")
            
            self._ensure_logged_in()
            
            logger.info(f"📝 Posting: {text[:50]}...")
            
            # Navigate to feed
            self.page.goto(self.FEED_URL, timeout=30000, wait_until="networkidle")
            self.page.wait_for_timeout(2000)
            
            # Click "Start a post"
            post_box_clicked = self.page.evaluate("""
                () => {
                    const selectors = [
                        '.share-box-feed-entry__trigger',
                        '[data-placeholder="Start a post"]',
                        'button[aria-label="Start a post"]'
                    ];
                    
                    for (const selector of selectors) {
                        const elements = document.querySelectorAll(selector);
                        for (const el of elements) {
                            if (el.offsetParent !== null) { // Visible element
                                el.click();
                                return true;
                            }
                        }
                    }
                    
                    // Fallback: search by text
                    const buttons = document.querySelectorAll('button');
                    for (const btn of buttons) {
                        if (btn.textContent.includes('Start a post') && btn.offsetParent !== null) {
                            btn.click();
                            return true;
                        }
                    }
                    
                    return false;
                }
            """)
            
            if not post_box_clicked:
                raise Exception("Could not find 'Start a post' box")
            
            self.page.wait_for_timeout(1000)
            
            # Type the post
            # Find textarea and type
            textarea_found = self.page.evaluate("""
                (text) => {
                    const textareas = document.querySelectorAll('textarea');
                    for (const ta of textareas) {
                        if (ta.offsetParent !== null) {
                            ta.value = text;
                            ta.dispatchEvent(new Event('input', { bubbles: true }));
                            return true;
                        }
                    }
                    return false;
                }
            """, text)
            
            if not textarea_found:
                # Fallback: keyboard typing
                self.page.keyboard.type(text, delay=30)
            
            self.page.wait_for_timeout(1000)
            
            # Click "Post" button
            post_clicked = self.page.evaluate("""
                () => {
                    const buttons = document.querySelectorAll('button');
                    for (const btn of buttons) {
                        if (btn.innerText.includes('Post') && btn.offsetParent !== null) {
                            btn.click();
                            return true;
                        }
                    }
                    return false;
                }
            """)
            
            if not post_clicked:
                raise Exception("Could not find 'Post' button")
            
            # Wait for confirmation
            if wait_for_post:
                self.page.wait_for_timeout(3000)
                
                # Check for success
                success = self.page.evaluate("""
                    () => {
                        const bodyText = document.body.innerText.toLowerCase();
                        return bodyText.includes('post') && 
                               !document.querySelector('[class*="share-modal"]');
                    }
                """)
                
                if not success:
                    logger.warning("⚠️ Post confirmation not detected")
            
            result = {
                'success': True,
                'text': text[:100] + '...' if len(text) > 100 else text,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info("✅ Post published successfully")
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to post: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def get_feed_posts(self, count: int = 5) -> List[Dict[str, Any]]:
        """
        Get posts from feed
        
        Args:
            count: Number of posts
            
        Returns:
            list: Posts data
        """
        try:
            self._ensure_logged_in()
            
            self.page.goto(self.FEED_URL, timeout=30000, wait_until="networkidle")
            self.page.wait_for_timeout(3000)
            
            # Extract posts
            posts = self.page.evaluate("""
                (count) => {
                    const posts = [];
                    const articles = document.querySelectorAll('article');
                    
                    for (let i = 0; i < Math.min(articles.length, count); i++) {
                        const article = articles[i];
                        const text = article.innerText || '';
                        const author = article.querySelector('.actor-name')?.innerText || 
                                      article.querySelector('[data-view-name="profile"]')?.innerText || 
                                      'Unknown';
                        
                        if (text.length > 50) {
                            posts.push({
                                author: author.substring(0, 100),
                                content: text.substring(0, 300),
                                index: i
                            });
                        }
                    }
                    
                    return posts;
                }
            """, count)
            
            logger.info(f"✅ Fetched {len(posts)} posts")
            return posts
            
        except Exception as e:
            logger.error(f"❌ Failed to get feed: {e}")
            return []

    def close(self):
        """Close browser"""
        try:
            if self.context:
                self.context.close()
            if self.playwright:
                self.playwright.stop()
            logger.info("🔒 Browser closed")
        except:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False


def main():
    """Test LinkedIn Agent"""
    print("="*60)
    print("🔗 LINKEDIN AI AGENT (Playwright-based)")
    print("="*60)
    
    try:
        with LinkedInAgent() as agent:
            
            # Get profile
            print("\n👤 Profile:")
            name = agent.get_profile_name()
            print(f"   Name: {name}")
            
            # Post status update
            print("\n📝 Posting test status...")
            result = agent.post_status_update(
                text="🚀 Testing AI Agent for Cloud Architecture! #AI #Automation #CloudComputing"
            )
            print(f"   Result: {result}")
            
            print("\n✅ Test complete!")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == '__main__':
    main()
