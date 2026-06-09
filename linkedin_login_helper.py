#!/usr/bin/env python3
"""
🔗 LinkedIn Login Helper
Opens LinkedIn and waits for you to login manually.
Saves the session for future use.
"""

from playwright.sync_api import sync_playwright
from pathlib import Path

PROFILE_PATH = Path(__file__).parent / "linkedin_browser_profile"

def login_to_linkedin():
    print("="*60)
    print("🔗 LINKEDIN LOGIN HELPER")
    print("="*60)
    print("\n📋 Steps:")
    print("   1. Browser will open")
    print("   2. Login with: smartydaniyazhar234@gmail.com")
    print("   3. Wait for feed to load")
    print("   4. Press ENTER here to save session and test posting")
    print("="*60)
    
    input("\n⏳ Press ENTER to open browser...")
    
    with sync_playwright() as p:
        # Launch browser
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_PATH),
            headless=False,
            viewport={"width": 1280, "height": 720}
        )
        
        page = context.pages[0] if context.pages else context.new_page()
        
        # Go to LinkedIn
        print("\n🌐 Opening LinkedIn...")
        page.goto("https://www.linkedin.com", timeout=30000)
        
        input("\n⏳ Login to LinkedIn and wait for feed, then press ENTER...")
        
        # Check current page
        print(f"\n📍 Current URL: {page.url}")
        
        # Try to post
        print("\n📝 Testing post...")
        page.goto("https://www.linkedin.com/feed/", timeout=30000, wait_until="networkidle")
        page.wait_for_timeout(3000)
        
        # Find and click post box
        post_clicked = page.evaluate("""
            () => {
                const triggers = document.querySelectorAll('.share-box-feed-entry__trigger');
                for (const trigger of triggers) {
                    if (trigger.offsetParent !== null) {
                        trigger.click();
                        return true;
                    }
                }
                return false;
            }
        """)
        
        if post_clicked:
            page.wait_for_timeout(1000)
            
            # Type message
            page.keyboard.type("Testing LinkedIn Agent! 🚀 #AI #Automation", delay=50)
            page.wait_for_timeout(1000)
            
            # Click Post button
            posted = page.evaluate("""
                () => {
                    const buttons = document.querySelectorAll('button');
                    for (const btn of buttons) {
                        if (btn.textContent.includes('Post') && btn.offsetParent !== null) {
                            btn.click();
                            return true;
                        }
                    }
                    return false;
                }
            """)
            
            if posted:
                page.wait_for_timeout(3000)
                print("✅ Post test complete!")
            else:
                print("❌ Could not find Post button")
        else:
            print("❌ Could not find post box")
        
        context.close()
    
    print("\n✅ Session saved! You can now use linkedin_playwright_agent.py")

if __name__ == '__main__':
    login_to_linkedin()
