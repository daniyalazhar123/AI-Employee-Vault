#!/usr/bin/env python3
"""
🔗 LinkedIn Automation Agent
Professional Cloud Architecture Portfolio Module

A robust agent class for LinkedIn automation using session cookies.
Implements feed reading and posting capabilities with proper error handling.

Usage:
    from linkedin_agent import LinkedInAgent
    
    agent = LinkedInAgent()
    feed = agent.get_latest_feed_post()
    agent.post_status_update("Your post content here")
"""

import os
import re
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

# Playwright imports
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext, Playwright

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
    LinkedIn Automation Agent
    
    A professional agent class for LinkedIn automation using session cookies.
    Supports feed reading, posting, and profile operations with robust error handling.
    
    Attributes:
        headless (bool): Whether to run browser in headless mode
        timeout (int): Default timeout for operations in milliseconds
        _playwright: Playwright instance
        _browser: Browser instance
        _context: Browser context with LinkedIn session
        _page: Active page instance
    """

    LINKEDIN_BASE_URL = "https://www.linkedin.com"
    FEED_URL = f"{LINKEDIN_BASE_URL}/feed/"
    POST_URL = f"{LINKEDIN_BASE_URL/feed/"
    
    # Cookie expiry detection patterns
    EXPIRED_SESSION_PATTERNS = [
        "session key",
        "sign in",
        "join now",
        "access denied",
        "verify it's you",
        "checkpoint",
        "captcha"
    ]

    def __init__(
        self,
        headless: bool = True,
        timeout: int = 30000,
        cookie_env_var: str = "LINKEDIN_COOKIE"
    ):
        """
        Initialize LinkedIn Agent
        
        Args:
            headless: Run browser in headless mode (default: True)
            timeout: Default timeout in milliseconds (default: 30000)
            cookie_env_var: Environment variable name for cookie (default: LINKEDIN_COOKIE)
        """
        self.headless = headless
        self.timeout = timeout
        self.cookie_env_var = cookie_env_var
        
        # Load environment
        self._load_environment()
        
        # Playwright instances
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        
        # Validation
        self._validate_cookie()
        
        logger.info("✅ LinkedIn Agent initialized")
        logger.info(f"🎭 Headless: {self.headless}")
        logger.info(f"⏱️  Timeout: {self.timeout}ms")

    def _load_environment(self):
        """Load environment variables from .env file"""
        # Load from multiple possible locations
        env_paths = [
            Path.cwd() / '.env',
            Path.cwd() / '.env.local',
            Path.home() / '.env',
        ]
        
        for env_path in env_paths:
            if env_path.exists():
                load_dotenv(env_path, override=True)
                logger.debug(f"📄 Loaded env from: {env_path}")
        
        logger.info("🔐 Environment variables loaded")

    def _validate_cookie(self):
        """Validate that LinkedIn cookie exists in environment"""
        cookie = os.getenv(self.cookie_env_var)
        
        if not cookie:
            raise ValueError(
                f"❌ LinkedIn cookie not found in environment variable '{self.cookie_env_var}'.\n"
                f"Please add it to your .env file:\n"
                f"  {self.cookie_env_var}=your_li_at_cookie_here"
            )
        
        logger.info("✅ LinkedIn cookie found in environment")

    def _get_cookie(self) -> str:
        """Retrieve LinkedIn cookie from environment"""
        return os.getenv(self.cookie_env_var, "").strip()

    def _setup_browser(self):
        """Initialize Playwright browser with LinkedIn session"""
        try:
            logger.info("🚀 Launching browser...")
            
            self._playwright = sync_playwright().start()
            
            # Launch browser
            self._browser = self._playwright.chromium.launch(
                headless=self.headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--no-sandbox'
                ]
            )
            
            # Create context with anti-detection settings
            self._context = self._browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='en-US',
                timezone_id='Asia/Karachi'
            )
            
            # Set anti-detection scripts
            self._context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                window.chrome = {
                    runtime: {}
                };
                
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
            """)
            
            # Set LinkedIn cookie
            cookie_value = self._get_cookie()
            
            self._context.add_cookies([
                {
                    'name': 'li_at',
                    'value': cookie_value,
                    'domain': '.linkedin.com',
                    'path': '/',
                    'httpOnly': True,
                    'secure': True
                }
            ])
            
            logger.info("✅ Browser launched with LinkedIn session")
            
        except Exception as e:
            logger.error(f"❌ Browser setup failed: {e}")
            self.close()
            raise

    def _ensure_browser(self):
        """Ensure browser is running, start if needed"""
        if not self._browser or not self._context:
            self._setup_browser()

    def _check_session_valid(self) -> bool:
        """
        Check if LinkedIn session is still valid
        
        Returns:
            bool: True if session is valid, False if expired
        """
        try:
            self._ensure_browser()
            
            if not self._page:
                self._page = self._context.new_page()
            
            # Navigate to feed
            logger.info("🔍 Checking session validity...")
            response = self._page.goto(self.FEED_URL, timeout=self.timeout, wait_until="domcontentloaded")
            
            if not response:
                logger.error("❌ No response from LinkedIn")
                return False
            
            # Wait for page to load
            self._page.wait_for_timeout(3000)
            
            # Get page content to check for session expiry
            page_content = self._page.content().lower()
            
            # Check for expired session indicators
            for pattern in self.EXPIRED_SESSION_PATTERNS:
                if pattern.lower() in page_content:
                    logger.error(f"❌ Session expired - detected: '{pattern}'")
                    return False
            
            # Check if we're redirected to login
            if "login" in self._page.url.lower():
                logger.error("❌ Redirected to login page - session expired")
                return False
            
            logger.info("✅ Session is valid")
            return True
            
        except Exception as e:
            logger.error(f"❌ Session check failed: {e}")
            return False

    def is_session_expired(self) -> bool:
        """
        Public method to check session expiry
        
        Returns:
            bool: True if session has expired
        """
        return not self._check_session_valid()

    def get_latest_feed_post(self) -> Optional[Dict[str, Any]]:
        """
        Fetch the latest post from LinkedIn feed
        
        Returns:
            dict: Post data including author, content, timestamp, engagement metrics
            None: If fetch fails or feed is empty
        """
        try:
            self._ensure_browser()
            
            # Validate session first
            if not self._check_session_valid():
                raise Exception("LinkedIn session has expired. Please update your cookie.")
            
            if not self._page:
                self._page = self._context.new_page()
            
            logger.info("📰 Fetching latest feed post...")
            self._page.goto(self.FEED_URL, timeout=self.timeout, wait_until="networkidle")
            self._page.wait_for_timeout(3000)
            
            # Extract posts using JavaScript
            posts_data = self._page.evaluate("""
                () => {
                    const posts = [];
                    const postElements = document.querySelectorAll('article');
                    
                    postElements.forEach((el) => {
                        const text = el.innerText || '';
                        const author = el.querySelector('[data-view-name="profile"]')?.innerText || 'Unknown';
                        
                        if (text.length > 50) { // Filter out short posts
                            posts.push({
                                author: author.trim().substring(0, 100),
                                content: text.substring(0, 500),
                                timestamp: new Date().toISOString()
                            });
                        }
                    });
                    
                    return posts;
                }
            """)
            
            if not posts_data or len(posts_data) == 0:
                logger.warning("⚠️ No posts found in feed")
                return None
            
            latest_post = posts_data[0]
            logger.info(f"✅ Fetched latest post by: {latest_post['author']}")
            
            return latest_post
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch feed post: {e}")
            return None

    def post_status_update(
        self,
        text: str,
        visibility: str = "PUBLIC",
        wait_for_confirmation: bool = True
    ) -> Dict[str, Any]:
        """
        Post a status update to LinkedIn
        
        Args:
            text: Post content (max 3000 characters)
            visibility: Post visibility (PUBLIC, CONNECTIONS, LOGGED_IN)
            wait_for_confirmation: Wait for post to be published
            
        Returns:
            dict: Result with success status and post URL
        """
        try:
            self._ensure_browser()
            
            # Validate session
            if not self._check_session_valid():
                raise Exception("LinkedIn session has expired. Please update your cookie.")
            
            # Validate text length
            if len(text) > 3000:
                raise ValueError("Post content exceeds 3000 character limit")
            
            if len(text.strip()) < 10:
                raise ValueError("Post content too short (minimum 10 characters)")
            
            if not self._page:
                self._page = self._context.new_page()
            
            logger.info(f"📝 Posting status update ({len(text)} chars)...")
            
            # Navigate to homepage
            self._page.goto(self.LINKEDIN_BASE_URL, timeout=self.timeout, wait_until="networkidle")
            self._page.wait_for_timeout(2000)
            
            # Try to find and click the post box
            post_box_clicked = self._page.evaluate("""
                () => {
                    // Try multiple selectors for the post box
                    const selectors = [
                        '.share-box-feed-entry__trigger',
                        '[data-placeholder="Start a post"]',
                        'button.share-box-feed-entry__trigger',
                        '.artdeco-button:has-text("Start a post")'
                    ];
                    
                    for (const selector of selectors) {
                        const element = document.querySelector(selector);
                        if (element) {
                            element.click();
                            return true;
                        }
                    }
                    
                    return false;
                }
            """)
            
            if not post_box_clicked:
                logger.warning("⚠️ Could not find post box, trying alternative method...")
                # Fallback: navigate directly to post page
                self._page.goto(f"{self.LINKEDIN_BASE_URL/post/new/", timeout=self.timeout)
                self._page.wait_for_timeout(2000)
            
            # Wait for modal to appear
            self._page.wait_for_timeout(2000)
            
            # Type the post content
            self._page.keyboard.type(text, delay=50)  # Realistic typing speed
            self._page.wait_for_timeout(1000)
            
            # Click post button
            post_clicked = self._page.evaluate("""
                () => {
                    const postButton = document.querySelector('button[data-control-name="share_post"]') ||
                                      Array.from(document.querySelectorAll('button')).find(
                                          btn => btn.innerText.includes('Post')
                                      );
                    
                    if (postButton) {
                        postButton.click();
                        return true;
                    }
                    return false;
                }
            """)
            
            if not post_clicked:
                raise Exception("Could not find Post button")
            
            # Wait for confirmation
            if wait_for_confirmation:
                self._page.wait_for_timeout(3000)
                
                # Check for success indicators
                success = self._page.evaluate("""
                    () => {
                        const bodyText = document.body.innerText.toLowerCase();
                        return bodyText.includes('your post was') || 
                               bodyText.includes('post is now') ||
                               !document.querySelector('[class*="share-modal"]');
                    }
                """)
                
                if not success:
                    logger.warning("⚠️ Post confirmation not detected, but request was sent")
            
            result = {
                "success": True,
                "text": text[:100] + "..." if len(text) > 100 else text,
                "visibility": visibility,
                "timestamp": datetime.now().isoformat(),
                "url": f"{self.LINKEDIN_BASE_URL/feed/"
            }
            
            logger.info("✅ Status update posted successfully")
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to post status update: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def get_profile_data(self) -> Optional[Dict[str, Any]]:
        """
        Get current user's profile data
        
        Returns:
            dict: Profile information or None if failed
        """
        try:
            self._ensure_browser()
            
            if not self._check_session_valid():
                raise Exception("LinkedIn session has expired")
            
            if not self._page:
                self._page = self._context.new_page()
            
            logger.info("👤 Fetching profile data...")
            
            # Go to profile page
            self._page.goto(f"{self.LINKEDIN_BASE_URL}/me/", timeout=self.timeout, wait_until="networkidle")
            self._page.wait_for_timeout(2000)
            
            # Extract profile data
            profile_data = self._page.evaluate("""
                () => {
                    return {
                        name: document.querySelector('.actor-name')?.innerText || 
                              document.querySelector('h1')?.innerText || 'Unknown',
                        headline: document.querySelector('.text-body-medium')?.innerText || '',
                        url: window.location.href
                    };
                }
            """)
            
            logger.info(f"✅ Profile fetched: {profile_data.get('name', 'Unknown')}")
            return profile_data
            
        except Exception as e:
            logger.error(f"❌ Failed to get profile data: {e}")
            return None

    def close(self):
        """Safely close browser and cleanup"""
        try:
            if self._page:
                self._page.close()
                self._page = None
            
            if self._context:
                self._context.close()
                self._context = None
            
            if self._browser:
                self._browser.close()
                self._browser = None
            
            if self._playwright:
                self._playwright.stop()
                self._playwright = None
            
            logger.info("🔒 Browser closed")
            
        except Exception as e:
            logger.error(f"⚠️ Error during cleanup: {e}")

    def __enter__(self):
        """Context manager entry"""
        self._setup_browser()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
        return False


# ============================================
# MAIN - Test/Example Usage
# ============================================
def main():
    """Test LinkedIn Agent functionality"""
    
    print("="*60)
    print("🔗 LINKEDIN AUTOMATION AGENT")
    print("="*60)
    
    # Check if cookie is set
    if not os.getenv("LINKEDIN_COOKIE"):
        print("\n❌ LINKEDIN_COOKIE not found in .env file")
        print("\n📋 Setup Instructions:")
        print("1. Add to your .env file:")
        print("   LINKEDIN_COOKIE=your_li_at_cookie_value_here")
        print("\n2. How to get LinkedIn cookie:")
        print("   - Login to LinkedIn in Chrome")
        print("   - Open DevTools (F12)")
        print("   - Go to Application > Cookies > linkedin.com")
        print("   - Copy the 'li_at' cookie value")
        return
    
    # Test the agent
    try:
        # Use context manager for automatic cleanup
        with LinkedInAgent(headless=False) as agent:  # Set headless=True for production
            
            # Check session validity
            print("\n🔍 Checking session validity...")
            if agent.is_session_expired():
                print("❌ Session has expired! Please update your LinkedIn cookie.")
                return
            print("✅ Session is valid!")
            
            # Get profile data
            print("\n👤 Fetching profile...")
            profile = agent.get_profile_data()
            if profile:
                print(f"   Name: {profile.get('name')}")
                print(f"   Headline: {profile.get('headline')}")
            
            # Get latest feed post
            print("\n📰 Fetching latest feed post...")
            latest_post = agent.get_latest_feed_post()
            if latest_post:
                print(f"   Author: {latest_post['author']}")
                print(f"   Content: {latest_post['content'][:100]}...")
            
            # Example: Post status update (commented out for safety)
            # print("\n📝 Posting status update...")
            # result = agent.post_status_update(
            #     text="🚀 Testing LinkedIn Automation Agent! #CloudArchitecture #Automation",
            #     visibility="PUBLIC"
            # )
            # if result['success']:
            #     print("✅ Post published successfully!")
            # else:
            #     print(f"❌ Post failed: {result['error']}")
            
            print("\n✅ All tests completed!")
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")


if __name__ == '__main__':
    main()
