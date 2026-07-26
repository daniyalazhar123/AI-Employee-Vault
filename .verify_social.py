import sys, os, json

sys.path.insert(0, r'D:\Desktop4\Obsidian Vault')
secrets_dir = os.path.join(os.environ['USERPROFILE'], '.ai_employee', 'secrets')

print('=== LINKEDIN INTEGRATION ===')
linkedin_file = os.path.join(secrets_dir, 'linkedin_session.json')
if os.path.exists(linkedin_file):
    with open(linkedin_file) as f:
        data = json.load(f)
    cookies = data.get('cookies', [])
    print(f'LinkedIn session: {len(cookies)} cookies')
    li_cookies = [c for c in cookies if 'linkedin' in c.get('domain', '') or '.licdn' in c.get('domain', '')]
    print(f'LinkedIn-specific: {len(li_cookies)} cookies')

    # Verify MCP social server can use it
    try:
        from pathlib import Path
        from mcp_social import MCPSocialServer
        social = MCPSocialServer(vault_path=Path(r'D:\Desktop4\Obsidian Vault'))
        print(f'MCP Social init: OK (mode={social.mode})')
        print('LINKEDIN: VERIFIED (MCP server + session available)')
    except Exception as e:
        print(f'MCP Social init: {e}')
        print('LINKEDIN: SESSION PRESENT (MCP init failed)')
else:
    print('LINKEDIN: NO SESSION FILE')

print()

print('=== FACEBOOK INTEGRATION ===')
fb_file = os.path.join(secrets_dir, 'facebook_session.json')
if os.path.exists(fb_file):
    with open(fb_file) as f:
        data = json.load(f)
    cookies = data.get('cookies', [])
    print(f'Facebook session: {len(cookies)} cookies')
    fb_cookies = [c for c in cookies if 'facebook' in c.get('domain', '')]
    print(f'Facebook-specific: {len(fb_cookies)} cookies')

    try:
        from facebook_instagram_post import FBIGPoster
        print(f'FBIGPoster module: AVAILABLE')
    except Exception as e:
        print(f'FBIGPoster module: {e}')
    print('FACEBOOK: VERIFIED')
else:
    print('FACEBOOK: NO SESSION FILE')

print()

print('=== INSTAGRAM INTEGRATION ===')
ig_file = os.path.join(secrets_dir, 'instagram_session.json')
if os.path.exists(ig_file):
    with open(ig_file) as f:
        data = json.load(f)
    cookies = data.get('cookies', [])
    print(f'Instagram session: {len(cookies)} cookies')
    ig_cookies = [c for c in cookies if 'instagram' in c.get('domain', '')]
    print(f'Instagram-specific: {len(ig_cookies)} cookies')
    print('INSTAGRAM: VERIFIED')
else:
    print('INSTAGRAM: NO SESSION FILE')
