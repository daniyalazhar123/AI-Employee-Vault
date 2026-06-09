#!/usr/bin/env python3
"""
Simple LinkedIn Test Script
Step by step testing with clear prompts
"""

import time
from pathlib import Path
from playwright.sync_api import sync_playwright

PROFILE_DIR = Path(__file__).parent / "linkedin_profile"

def main():
    print("="*60)
    print("🔗 LINKEDIN SIMPLE TEST")
    print("="*60)
    print()
    print("Step 1: Browser will open")
    print("Step 2: Login to LinkedIn")
    print("Step 3: Wait for feed")
    print()
    input("Press ENTER to start...")
    
    try:
        with sync_playwright() as p:
            # Launch browser
            print("\n🌐 Opening browser...")
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(PROFILE_DIR),
                headless=False,
                viewport={"width": 1280, "height": 720}
            )
            page = context.pages[0] if context.pages else context.new_page()
            
            # Go to LinkedIn
            print("📍 Going to LinkedIn...")
            page.goto("https://www.linkedin.com", timeout=30000)
            page.wait_for_timeout(2000)
            
            print("\n⚠️  BROWSER IS OPEN NOW")
            print("   Please login to LinkedIn if not already")
            print("   Wait for your feed to load")
            print()
            input("   Press ENTER when you see your LinkedIn feed...")
            
            # Navigate to feed
            print("\n📰 Loading feed...")
            page.goto("https://www.linkedin.com/feed/", timeout=30000, wait_until="networkidle")
            page.wait_for_timeout(3000)
            
            # Get profile name
            print("\n👤 Getting profile name...")
            name = page.evaluate("""
                () => {
                    const nameEl = document.querySelector('.actor-name') || 
                                  document.querySelector('h1') ||
                                  document.querySelector('.text-heading-xlarge');
                    return nameEl ? nameEl.innerText.trim() : 'Not found';
                }
            """)
            print(f"   Name: {name}")
            
            # Test posting
            print("\n📝 Testing post...")
            print("   Looking for post box...")
            
            # Find post trigger
            clicked = page.evaluate("""
                () => {
                    const triggers = document.querySelectorAll('button');
                    for (const btn of triggers) {
                        if (btn.textContent.includes('Start a post') && btn.offsetParent) {
                            btn.click();
                            return true;
                        }
                    }
                    return false;
                }
            """)
            
            if clicked:
                print("   ✅ Post box found")
                page.wait_for_timeout(1000)
                
                # Type in textarea
                print("   Typing message...")
                page.keyboard.type("Testing LinkedIn AI Agent! 🚀 #CloudArchitecture", delay=50)
                page.wait_for_timeout(1000)
                
                # Click Post button
                print("   Clicking Post...")
                posted = page.evaluate("""
                    () => {
                        const buttons = document.querySelectorAll('button');
                        for (const btn of buttons) {
                            if (btn.textContent.includes('Post') && btn.offsetParent) {
                                btn.click();
                                return true;
                            }
                        }
                        return false;
                    }
                """)
                
                if posted:
                    page.wait_for_timeout(3000)
                    print("   ✅ Post submitted!")
                    print("\n🎉 SUCCESS! LinkedIn Agent is working!")
                else:
                    print("   ❌ Post button not found")
            else:
                print("   ❌ Post box not found")
                print("   (You might not be on the feed page)")
            
            print("\n✅ Test complete!")
            print("   Browser will stay open for 5 seconds...")
            page.wait_for_timeout(5000)
            context.close()
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
