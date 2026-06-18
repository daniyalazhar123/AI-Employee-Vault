import sys, os
from playwright.sync_api import sync_playwright
from pathlib import Path

# Save to the secrets directory
sys.path.insert(0, str(Path(__file__).parent))
from secrets_config import SECRETS_DIR, get_secret_path

output_path = get_secret_path('linkedin_session.json')
print(f"Saving LinkedIn session to: {output_path}")

print("🔄 Saving LinkedIn session...")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        viewport={'width': 1280, 'height': 800},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    )
    page = context.new_page()

    print("\nBrowser khul gaya... LinkedIn pe manually login karo agar zarurat ho")
    print("1. Agar already logged in ho to feed load hone tak wait karo")
    print("2. Agar login nahi ho to manually karo")

    page.goto("https://www.linkedin.com/feed/")

    input("\nPress Enter jab LinkedIn fully load ho jaaye aur tum logged in dikho...")

    context.storage_state(path=str(output_path))
    
    print(f"\n✅ Session successfully saved to: {output_path}")
    
    # Verify
    import json
    with open(output_path) as f:
        data = json.load(f)
    cookies = data.get('cookies', [])
    li_at = any(c.get('name') == 'li_at' for c in cookies)
    print(f"   Cookies: {len(cookies)}, li_at present: {li_at}")
    print("Ab aap real LinkedIn post test kar sakte hain!")

    input("\nBrowser band karne ke liye Enter dabao...")
    browser.close()