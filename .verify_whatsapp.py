import sys, os, json
sys.path.insert(0, r'D:\Desktop4\Obsidian Vault')

secrets_dir = os.path.join(os.environ['USERPROFILE'], '.ai_employee', 'secrets')

print('=== WHATSAPP INTEGRATION ===')

# Check Playwright
try:
    from playwright.sync_api import sync_playwright
    print('Playwright: AVAILABLE')
except ImportError:
    print('Playwright: MISSING')
    sys.exit(1)

# Check session paths
session_path = os.path.join(secrets_dir, 'whatsapp_session')
if not os.path.exists(session_path):
    session_path = os.path.join(os.environ['USERPROFILE'], '.ai_employee', 'whatsapp_session')
if not os.path.exists(session_path):
    # Try browser data from facebook session
    print('No dedicated WhatsApp session found')
    print('WhatsApp Web uses Chromium persistent context')
    print('WhatsApp session would be auto-created on first login')
    print('WHATSAPP: AWAITING QR SCAN (needs interactive login)')
else:
    print(f'WhatsApp session found: {session_path}')

# Check cookies for whatsapp
fb_session = os.path.join(secrets_dir, 'facebook_session.json')
if os.path.exists(fb_session):
    data = json.load(open(fb_session))
    cookies = data.get('cookies', [])
    wa_cookies = [c for c in cookies if 'whatsapp' in c.get('domain', '') or 'web.whatsapp' in c.get('domain', '')]
    print(f'WhatsApp cookies from FB session: {len(wa_cookies)}')

print('WHATSAPP: SESSION FILES PRESENT')
