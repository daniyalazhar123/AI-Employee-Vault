import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess

# Vault folder automatically detect
VAULT_PATH = Path(__file__).parent
OFFICE_FOLDER = VAULT_PATH / "Office_Files"
NEEDS_ACTION = VAULT_PATH / "Needs_Action"

class OfficeHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        
        # Skip already processed files
        if ".md.md" in file_path.name:
            return
            
        print(f"New office file detected: {file_path.name}")

        # FIX 1: Use file_path.name instead of stem to avoid .md.md
        action_file = NEEDS_ACTION / f"OFFICE_{file_path.name}"
        
        content = f"""---
type: office_file
file_name: {file_path.name}
path: {file_path}
created: {time.strftime("%Y-%m-%d %H:%M:%S")}
status: pending
---

New office file added: {file_path.name}

Task: Read this file, summarize content, make it professional if needed, and update Dashboard.md.
"""
        # FIX 2: UTF-8 encoding
        action_file.write_text(content, encoding='utf-8')
        print(f"Action file created: {action_file}")

        # FIX 3: Qwen trigger with proper encoding
        try:
            result = subprocess.run(
                ["qwen", "Process Needs_Action folder and handle the latest OFFICE file"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=60
            )
            print("Qwen triggered automatically")
            if result.stdout:
                print("Qwen output:", result.stdout)
            if result.stderr:
                print("Qwen error:", result.stderr)
        except FileNotFoundError:
            print("Qwen CLI not found - action file created, run Qwen manually")
        except Exception as e:
            print(f"Error triggering Qwen: {e}")

if __name__ == "__main__":
    NEEDS_ACTION.mkdir(exist_ok=True)
    OFFICE_FOLDER.mkdir(exist_ok=True)

    event_handler = OfficeHandler()
    observer = Observer()
    observer.schedule(event_handler, OFFICE_FOLDER, recursive=False)
    observer.start()

    print("=" * 50)
    print("AI Employee - Office Watcher Started!")
    print(f"Watching: {OFFICE_FOLDER}")
    print(f"Vault: {VAULT_PATH}")
    print("=" * 50)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nWatcher stopped")
    observer.join()