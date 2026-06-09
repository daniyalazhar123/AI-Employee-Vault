"""
Batch Processor — read oldest 20 files from Needs_Action, process, move to Done.

Usage:
    python batch_processor.py                    # Process 20 files
    python batch_processor.py --count 50         # Process 50 files
    python batch_processor.py --dry-run          # Show what would be done
"""

import os, sys, json, shutil, time
from pathlib import Path
from datetime import datetime

VAULT = Path(__file__).parent
NEEDS_ACTION = VAULT / 'Needs_Action'
DONE = VAULT / 'Done'
IN_PROGRESS = VAULT / 'In_Progress'
LOGS = VAULT / 'Logs'

def oldest_md_files(folder: Path, count: int):
    """Return the `count` oldest .md files by last write time."""
    files = [f for f in folder.iterdir() if f.suffix == '.md' and f.is_file()]
    files.sort(key=lambda f: f.stat().st_mtime)  # oldest first
    return files[:count]

def process_file(src: Path, dry_run: bool = False):
    """Read a Needs_Action file, create a processing log entry, move to Done."""
    now = datetime.now()
    content = src.read_text(encoding='utf-8', errors='replace') if src.exists() else ''

    log_entry = {
        'timestamp': now.isoformat(),
        'source': str(src.relative_to(VAULT)),
        'filename': src.name,
        'size_bytes': src.stat().st_size,
        'action': 'move_to_done',
        'status': 'processed'
    }

    if dry_run:
        return log_entry

    # Move to In_Progress briefly
    in_prog = IN_PROGRESS / 'batch' / src.name
    in_prog.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(in_prog))

    # Write a summary note
    summary = f"""---
type: batch_processed
original: {src.name}
processed: {now.isoformat()}
---

# Batch Processed: {src.name}

This item was auto-processed by batch_processor.py on {now.strftime('%Y-%m-%d %H:%M')}.

## Original Content (first 500 chars)

{content[:500]}
"""
    done_path = DONE / f'BATCH_{now.strftime("%Y%m%d_%H%M%S")}_{src.name}'
    done_path.write_text(summary, encoding='utf-8')

    # Remove from In_Progress
    if in_prog.exists():
        in_prog.unlink()

    return log_entry

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Batch process Needs_Action backlog')
    parser.add_argument('--count', type=int, default=20, help='Number of files to process (default: 20)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without moving')
    args = parser.parse_args()

    LOGS.mkdir(parents=True, exist_ok=True)

    files = oldest_md_files(NEEDS_ACTION, args.count)
    if not files:
        print(f'No .md files found in {NEEDS_ACTION}')
        return

    print(f'Found {len(files)} files to process in {NEEDS_ACTION}')
    results = []

    for f in files:
        if not f.exists():
            print(f"  [SKIP] {f.name} (disappeared before processing)")
            continue
        entry = process_file(f, dry_run=args.dry_run)
        results.append(entry)
        prefix = '[DRY-RUN]' if args.dry_run else '[OK]'
        size = f.stat().st_size if f.exists() else 0
        print(f"  {prefix} {f.name} ({size}b)")

    # Save log
    log_file = LOGS / f'batch_{datetime.now().strftime("%Y-%m-%d")}.json'
    if not args.dry_run:
        with open(log_file, 'w', encoding='utf-8') as lf:
            json.dump({'processed_at': datetime.now().isoformat(), 'count': len(results), 'files': results}, lf, indent=2, ensure_ascii=False)
        print(f'\nLog saved: {log_file}')
    else:
        print(f'\nDry-run only. Would log to: {log_file}')

    print(f'\nDone. Processed {len(results)} file(s) from Needs_Action to Done.')

if __name__ == '__main__':
    main()
