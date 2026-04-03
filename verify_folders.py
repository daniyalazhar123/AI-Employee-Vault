from pathlib import Path

required_folders = [
    'Inbox', 'Needs_Action', 'Done', 'Pending_Approval', 'Approved', 'Rejected',
    'Plans', 'Logs', 'Social_Drafts', 'Drafts', 'Briefings', 'CEO_Briefings',
    'Updates', 'Signals', 'In_Progress', 'Dead_Letter_Queue', 'Office_Files',
    'watchers', 'sessions', 'cloud', 'local', 'kubernetes', 'odoo', 'config',
    'dashboard', 'data', 'docs', 'Skills', 'Social_Summaries', 'Logs/Audit',
    'In_Progress/cloud', 'In_Progress/local'
]

print('📁 FOLDER STRUCTURE VERIFICATION')
print('='*60)

missing = []
present = 0

for folder in required_folders:
    if Path(folder).exists():
        present += 1
    else:
        missing.append(folder)

print(f'Folders present: {present}/{len(required_folders)}')
print(f'Folders missing: {len(missing)}')

if missing:
    print('\nCreating missing folders...')
    for folder in missing:
        Path(folder).mkdir(parents=True, exist_ok=True)
        print(f'  ✅ Created: {folder}')
    print(f'\n✅ All {len(required_folders)} folders now present')
else:
    print('\n✅ All required folders present')

print('='*60)
