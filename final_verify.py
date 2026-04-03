import re
from pathlib import Path
import codecs
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

print('='*70)
print('🔍 FINAL VERIFICATION - AI Employee Vault')
print('='*70)

# 1. Count npm references in core files only
core_files = [
    'README.md', 'README-BRONZE.md', 'README_COMPLETE_SETUP.md',
    'TESTING_GUIDE.md', 'TESTING_COMMANDS_COMPLETE.md',
    'ai_employee_orchestrator.py', 'mcp_email.py', 'mcp_social.py',
    'mcp_browser.py', 'odoo_mcp.py', 'ralph_loop.py'
]

npm_count = 0
for file in core_files:
    try:
        content = Path(file).read_text(encoding='utf-8', errors='ignore')
        matches = re.findall(r'npm install|npm start|npm run|node index|npx ', content)
        if matches:
            npm_count += len(matches)
            print(f'  ⚠️  {file}: {len(matches)} npm references')
    except:
        pass

print(f'\n1. NPM References in Core Files: {npm_count}')

# 2. MCP files check
mcp_files = list(Path('.').glob('mcp_*.py'))
print(f'2. MCP Python Files: {len(mcp_files)} ✅')
for f in mcp_files:
    print(f'   ✅ {f.name}')

# 3. FINAL_SUBMISSION.md check
final_file = Path('FINAL_SUBMISSION.md')
if final_file.exists():
    content = final_file.read_text(encoding='utf-8', errors='ignore')
    has_gold = 'GOLD TIER' in content.upper()
    has_complete = 'COMPLETE' in content.upper()
    print(f'3. FINAL_SUBMISSION.md: EXISTS ✅')
    print(f'   - Gold Tier Status: {"✅" if has_gold else "❌"}')
    print(f'   - Complete Status: {"✅" if has_complete else "❌"}')
else:
    print(f'3. FINAL_SUBMISSION.md: ❌ MISSING')

# 4. Folder count
folders = [d for d in Path('.').iterdir() if d.is_dir() and not d.name.startswith('.')]
print(f'4. Project Folders: {len(folders)}')

# 5. Python file count
py_files = list(Path('.').glob('**/*.py'))
py_files = [f for f in py_files if '__pycache__' not in str(f)]
print(f'5. Python Files: {len(py_files)}')

print('\n' + '='*70)
print('✅ VERIFICATION COMPLETE')
print('='*70)
