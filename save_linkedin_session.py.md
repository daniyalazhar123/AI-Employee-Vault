from playwright.sync_api import sync_playwright import json from pathlib import Path

print("🔄 Saving LinkedIn session...")

with sync_playwright() as p: # Headless=False rakho taake browser dikhe browser = p.chromium.launch(headless=False) context = browser.new_context( viewport={"width": 1280, "height": 800}, user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" ) page = context.new_page()

print("Browser khul gaya... ab LinkedIn pe manually login karo agar logout ho gaya ho")

page.goto("https://www.linkedin.com/feed/") # ya https://www.linkedin.com/

# Yahan ruk jaayega - tum manually login kar lo (agar already logged in hai toh direct feed khulega) input("\nPress Enter jab LinkedIn fully load ho jaaye aur tum logged in dikho...")

# Session save karo state = context.storage_state(path="linkedin_session.json")

print("✅ Session saved successfully in 'linkedin_session.json'") print("Ab is file ko mcp_social.py mein use kar sakte hain")

# Browser band karne se pehle thoda wait input("Browser band karne ke liye Enter dabao...") browser.close()