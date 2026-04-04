from playwright.sync_api import sync_playwright
from pathlib import Path

print("🔄 Saving LinkedIn session...")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        viewport={'width': 1280, 'height': 800},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    )
    page = context.new_page()

    print("Browser khul gaya... LinkedIn pe manually login karo agar zarurat ho")

    page.goto("https://www.linkedin.com/feed/")

    input("\nPress Enter jab LinkedIn fully load ho jaaye aur tum logged in dikho...")

    context.storage_state(path="linkedin_session.json")
    
    print("✅ Session successfully saved in linkedin_session.json")
    print("Ab is file ko mcp_social.py mein use kar sakte hain")

    input("Browser band karne ke liye Enter dabao...")
    browser.close()