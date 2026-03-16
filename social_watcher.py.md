import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess

VAULT_PATH = Path(__file__).parent
SOCIAL_FOLDER = VAULT_PATH / "Social_Drafts"
POLISHED_FOLDER = SOCIAL_FOLDER / "Polished"
NEEDS_ACTION = VAULT_PATH / "Needs_Action"

class SocialHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        print(f"New raw social post detected: {file_path.name}")

        action_file = NEEDS_ACTION / f"SOCIAL_{file_path.name.replace('.', '_')}.md"
        content = f"""---
type: social_draft
file_name: {file_path.name}
path: {file_path}
created: {time.strftime("%Y-%m-%d %H:%M:%S")}
status: pending
---

New raw social post added: {file_path.name}

Task: Read this file, turn it into a professional version (LinkedIn/FB/IG/X style), add 3-5 relevant hashtags, and save the polished post in Social_Drafts/Polished.
"""

        action_file.write_text(content, encoding='utf-8')
        print(f"Action file created: {action_file}")

        try:
            result = subprocess.run(
                ["qwen", "-y", f"Read the social draft action file: {action_file.name} in Needs_Action folder. Turn it into a professional version with 3-5 hashtags. Save the polished post in Social_Drafts/Polished folder as POLISHED_{file_path.stem}.md"],
                check=False,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                cwd=str(VAULT_PATH),
                shell=True,
                timeout=120
            )
            print("Qwen triggered for social post")
            print("Qwen output:", result.stdout.strip())
            print("Qwen error (if any):", result.stderr.strip())
        except Exception as e:
            print(f"Qwen error: {e}")

if __name__ == "__main__":
    if not SOCIAL_FOLDER.exists():
        SOCIAL_FOLDER.mkdir()
        print("Created Social_Drafts folder")
    if not POLISHED_FOLDER.exists():
        POLISHED_FOLDER.mkdir()
        print("Created Polished subfolder")

    event_handler = SocialHandler()
    observer = Observer()
    observer.schedule(event_handler, SOCIAL_FOLDER, recursive=False)
    observer.start()

    print("Watching Social_Drafts folder... Press Ctrl+C to stop")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("Watcher stopped")
    observer.join()