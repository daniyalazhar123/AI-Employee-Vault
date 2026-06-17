import xmlrpc.client
import importlib.util
import sys
from pathlib import Path

print("=== GOLD TIER FINAL VERIFICATION ===")
print()

# 1. Odoo
print("[Odoo 19]")
try:
    c = xmlrpc.client.ServerProxy('http://localhost:8069/xmlrpc/2/common')
    uid = c.authenticate('odoo', 'admin', 'admin', {})
    m = xmlrpc.client.ServerProxy('http://localhost:8069/xmlrpc/2/object')
    inv = m.execute_kw('odoo', uid, 'admin', 'account.move', 'search_read',
        [[['move_type', '=', 'out_invoice']]], {'fields': ['id', 'name', 'state'], 'limit': 3})
    print(f"  Invoices: {len(inv)}")
    for i in inv:
        print(f"    ID {i['id']}: name={i['name']} state={i['state']}")
    cust = m.execute_kw('odoo', uid, 'admin', 'res.partner', 'search_count', [[['customer_rank', '>', 0]]])
    print(f"  Customers: {cust}")
    print("  STATUS: PASS")
except Exception as e:
    print(f"  STATUS: FAIL - {e}")

# 2. MCP Servers
print("\n[MCP Servers]")
all_ok = True
for n in ['mcp_email', 'mcp_odoo', 'mcp_social', 'mcp_browser']:
    s = importlib.util.find_spec(n)
    status = "PASS" if s else "FAIL"
    if not s: all_ok = False
    print(f"  {n}: {status}")
print(f"  STATUS: {'PASS' if all_ok else 'PARTIAL'}")

# 3. Watcher path fix
print("\n[Watcher Path]")
sys.path.insert(0, str(Path('.').resolve()))
from base_watcher import BaseWatcher
w = BaseWatcher('test', str(Path('.').resolve()))
print(f"  vault_path type: {type(w.vault_path).__name__}")
print(f"  vault_path: {w.vault_path}")
print(f"  logs_folder: {w.logs_folder}")
print(f"  STATUS: {'PASS' if isinstance(w.vault_path, Path) else 'FAIL'}")

# 4. Ralph Loop
print("\n[Ralph Loop]")
ralph_content = Path('ralph_loop.py').read_text(encoding='utf-8')
if "'--yes'" in ralph_content:
    print("  CLI flag: --yes")
    print("  STATUS: PASS")
else:
    print("  CLI flag: NOT FIXED")
    print("  STATUS: FAIL")

# 5. Audit logs
print("\n[Audit Logs]")
audit_dir = Path('Logs/Audit')
if audit_dir.exists():
    files = list(audit_dir.glob('*.json'))
    print(f"  Audit files: {len(files)}")
    print(f"  STATUS: PASS")
else:
    print("  STATUS: FAIL - directory not found")

# 6. Agent Skills
print("\n[Agent Skills]")
skills_dir = Path('.claude/skills')
if skills_dir.exists():
    skills = [d.name for d in skills_dir.iterdir() if d.is_dir()]
    print(f"  Skills: {len(skills)}")
    for s in skills:
        print(f"    - {s}")
    print(f"  STATUS: PASS")
else:
    print("  STATUS: FAIL")

# 7. Sessions
print("\n[Browser Sessions]")
secrets_dir = Path.home() / '.ai_employee' / 'secrets'
sessions = ['linkedin_session.json', 'facebook_session.json', 'instagram_session.json']
all_sessions = True
for s in sessions:
    exists = (secrets_dir / s).exists()
    if not exists: all_sessions = False
    print(f"  {s}: {'PASS' if exists else 'FAIL'}")
print(f"  STATUS: {'PASS' if all_sessions else 'PARTIAL'}")

# 8. Needs_Action
print("\n[Backlog]")
na_files = list(Path('Needs_Action').glob('*.md'))
print(f"  Pending files: {len(na_files)}")
print(f"  STATUS: {'PASS' if len(na_files) < 50 else 'WARN - backlog still large'}")

print("\n=== VERIFICATION COMPLETE ===")
