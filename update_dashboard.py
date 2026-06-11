#!/usr/bin/env python3
"""Update Dashboard.md with real file counts"""
import re
from pathlib import Path
from datetime import datetime

VAULT = Path(__file__).parent
na = len(list((VAULT/'Needs_Action').glob('*.md')))
done = len(list((VAULT/'Done').glob('*.md')))
pa = len(list((VAULT/'Pending_Approval').glob('*.md')))

dashboard = VAULT / 'Dashboard.md'
content = dashboard.read_text(encoding='utf-8', errors='replace')

# Update task counts in the summary table
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'Needs_Action' in line and '|' in line:
        parts = line.split('|')
        if len(parts) >= 3:
            parts[1] = f' Needs_Action (Pending) '
            parts[2] = f' {na} '
            lines[i] = '|'.join(parts)
    elif line.strip().startswith('| Done') and '|' in line:
        parts = line.split('|')
        if len(parts) >= 3:
            parts[2] = f' {done} '
            lines[i] = '|'.join(parts)

content = '\n'.join(lines)
dashboard.write_text(content, encoding='utf-8')
print(f'Dashboard updated: NA={na}, Done={done}, PA={pa}')
print(f'Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
