"""
Fix Unicode Encoding Issues in All Python Files
Adds UTF-8 encoding support for Windows console output
"""
import os
import sys
from pathlib import Path

ENCODING_FIX = '''
import sys
import io
# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
'''

def fix_file(filepath):
    """Add encoding fix to a Python file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if already has the fix
        if 'sys.stdout.reconfigure' in content or 'TextIOWrapper' in content:
            return False
        
        # Find the main() function and add fix before it
        if 'def main():' in content:
            # Add import at top after existing imports
            lines = content.split('\n')
            insert_pos = 0
            
            # Find last import line
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    insert_pos = i + 1
            
            # Insert encoding fix
            lines.insert(insert_pos, '# Fix Windows console encoding')
            lines.insert(insert_pos + 1, 'if sys.platform == "win32":')
            lines.insert(insert_pos + 2, '    try:')
            lines.insert(insert_pos + 3, '        sys.stdout.reconfigure(encoding="utf-8", errors="replace")')
            lines.insert(insert_pos + 4, '        sys.stderr.reconfigure(encoding="utf-8", errors="replace")')
            lines.insert(insert_pos + 5, '    except (AttributeError, Exception):')
            lines.insert(insert_pos + 6, '        import io')
            lines.insert(insert_pos + 7, '        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")')
            lines.insert(insert_pos + 8, '        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")')
            
            # Add 'import sys' if not present
            if not any(line.startswith('import sys') for line in lines):
                lines.insert(0, 'import sys')
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            return True
        
        return False
    except Exception as e:
        print(f"  ❌ Error fixing {filepath}: {e}")
        return False

def main():
    vault_path = Path(__file__).parent
    
    # Files to fix (from ecosystem.config.js)
    files_to_fix = [
        'ai_employee_orchestrator.py',
        'cloud_agent.py',
        'local_agent.py',
        'health_monitor.py',
        'security_guard.py',
        'multi_language_agent.py',
        'watchers/gmail_watcher.py',
        'watchers/whatsapp_watcher.py',
        'watchers/office_watcher.py',
        'watchers/social_watcher.py',
        'watchers/odoo_lead_watcher.py',
    ]
    
    print("🔧 Fixing Unicode Encoding Issues...\n")
    
    fixed_count = 0
    for file in files_to_fix:
        filepath = vault_path / file
        if filepath.exists():
            if fix_file(filepath):
                print(f"  ✅ Fixed: {file}")
                fixed_count += 1
            else:
                print(f"  ⏭️  Already fixed or no main(): {file}")
        else:
            print(f"  ⚠️  Not found: {file}")
    
    print(f"\n✅ Fixed {fixed_count}/{len(files_to_fix)} files")
    print("\nNow restart PM2: pm2 restart all")

if __name__ == '__main__':
    main()
