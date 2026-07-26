import sys, os, json, urllib.request

sys.path.insert(0, r'D:\Desktop4\Obsidian Vault')
secrets_dir = os.path.join(os.environ['USERPROFILE'], '.ai_employee', 'secrets')

print('=== ODOO INTEGRATION ===')

odoo_host = 'localhost'
odoo_port = '8069'
odoo_db = ''
odoo_user = 'admin'
odoo_password = 'admin'

env_path = os.path.join(secrets_dir, '.env')
if os.path.exists(env_path):
    with open(env_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            parts = line.split('=', 1)
            if len(parts) == 2:
                k, v = parts[0].strip(), parts[1].strip().strip("'").strip('"')
                if k == 'ODOO_URL': 
                    odoo_url = v
                    from urllib.parse import urlparse
                    parsed = urlparse(v)
                    odoo_host = parsed.hostname or 'localhost'
                    odoo_port = str(parsed.port or 8069)
                if k == 'ODOO_DB': odoo_db = v
                if k == 'ODOO_USERNAME': odoo_user = v
                if k == 'ODOO_PASSWORD': odoo_password = v

print(f'Odoo URL: http://{odoo_host}:{odoo_port}')
print(f'Odoo DB: {odoo_db}')
print(f'Odoo User: {odoo_user}')

# Test JSON-RPC
url = f'http://{odoo_host}:{odoo_port}/jsonrpc'
payload = json.dumps({
    'jsonrpc': '2.0',
    'method': 'call',
    'params': {'service': 'common', 'method': 'version'},
    'id': 1
}).encode()

try:
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    resp = urllib.request.urlopen(req, timeout=5)
    result = json.loads(resp.read())
    odoo_version = result.get('result', {}).get('server_version', 'unknown')
    print(f'Odoo server version: {odoo_version}')
    print('ODOO: VERIFIED (JSON-RPC connected)')
except Exception as e:
    print(f'Odoo connection FAILED: {e}')
    print(f'Tried: {url}')
    print('Is Odoo server running on localhost:8069?')

# Test MCP Odoo
try:
    from pathlib import Path
    from mcp_odoo import MCPOdooServer
    odoo_mcp = MCPOdooServer(vault_path=Path(r'D:\Desktop4\Obsidian Vault'))
    print('MCP Odoo server init: OK')
    # Test listing partners
    partners = odoo_mcp.list_partners()
    print(f'Partners: {partners}')
except Exception as e:
    print(f'MCP Odoo: {e}')
