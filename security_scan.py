import re
from pathlib import Path

print('🔒 SECURITY SCAN: Checking for hardcoded credentials...')
print('='*60)

files_scanned = 0
issues_found = 0

for py_file in Path('.').glob('**/*.py'):
    if '__pycache__' in str(py_file) or 'sessions' in str(py_file):
        continue
    
    files_scanned += 1
    content = py_file.read_text(encoding='utf-8', errors='ignore')
    
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
            continue
        
        if re.search(r'(PASSWORD|SECRET|API_KEY|TOKEN)\s*=\s*["\'][a-zA-Z0-9]{8,}["\']', line, re.IGNORECASE):
            if 'os.getenv' not in line and 'os.environ' not in line:
                print(f'⚠️  {py_file}:{i} - Possible hardcoded credential')
                issues_found += 1

print(f'Files scanned: {files_scanned}')
print(f'Issues found: {issues_found}')
print('='*60)

if issues_found == 0:
    print('✅ SECURITY SCAN PASSED: No hardcoded credentials found')
else:
    print(f'❌ SECURITY SCAN FAILED: {issues_found} issues found')
