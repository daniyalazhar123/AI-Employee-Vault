#!/usr/bin/env python3
"""
🔗 LinkedIn Cookie Extractor
Automatically extracts li_at cookie from Chrome browser.
"""

import os
import sys
import json
import base64
import sqlite3
import shutil
import logging
from pathlib import Path

from playwright.sync_api import sync_playwright
from dotenv import load_dotenv, set_key

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('CookieExtractor')


def extract_linkedin_cookie():
    """Extract li_at cookie from LinkedIn using Playwright"""
    
    print("="*60)
    print("🔗 LINKEDIN COOKIE EXTRACTOR")
    print("="*60)
    
    li_at_cookie = None
    
    with sync_playwright() as p:
        # Launch Chrome with persistent profile
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(Path.home() / ".linkedin_browser_data"),
            headless=False,  # Show browser so user can login
            viewport={"width": 1280, "height": 720}
        )
        
        print("\n🌐 Browser opened!")
        print("📋 Steps:")
        print("   1. Login to LinkedIn if not already logged in")
        print("   2. Wait for feed to load")
        print("   3. Press ENTER here once you're logged in")
        
        # Navigate to LinkedIn
        page = browser.new_page()
        page.goto("https://www.linkedin.com", timeout=60000)
        
        # Wait for user to login
        input("\n⏳ Press ENTER once you're logged into LinkedIn...")
        
        # Extract cookies
        cookies = page.context.cookies()
        
        for cookie in cookies:
            if cookie['name'] == 'li_at':
                li_at_cookie = cookie['value']
                logger.info("✅ li_at cookie found!")
                break
        
        # Also try to get JSESSIONID
        jsessionid = None
        for cookie in cookies:
            if cookie['name'] == 'JSESSIONID':
                jsessionid = cookie['value']
                logger.info("✅ JSESSIONID cookie found!")
                break
        
        browser.close()
    
    if not li_at_cookie:
        print("\n❌ li_at cookie not found!")
        print("   Make sure you're logged into LinkedIn.")
        return False
    
    # Save to .env.local
    env_file = Path.cwd() / '.env.local'
    if not env_file.exists():
        env_file = Path(__file__).parent / '.env.local'
    
    if env_file.exists():
        set_key(str(env_file), 'LINKEDIN_COOKIE', li_at_cookie)
        print(f"\n✅ Cookie saved to: {env_file}")
        print(f"📝 Cookie length: {len(li_at_cookie)} characters")
        print(f"🔑 Starts with: {li_at_cookie[:20]}...")
        return True
    else:
        print(f"\n❌ .env.local not found at: {env_file}")
        print("   Manual save:")
        print(f"   LINKEDIN_COOKIE={li_at_cookie}")
        return False


if __name__ == '__main__':
    try:
        extract_linkedin_cookie()
    except KeyboardInterrupt:
        print("\n\n⏹️  Extraction cancelled")
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
