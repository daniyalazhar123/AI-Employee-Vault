"""
Social Watcher for AI Employee Vault

Monitors Social_Drafts folder for new draft posts.
Features:
- File system event monitoring
- Auto-polishing with AI
- Robust error handling
- JSON logging to /Logs/ folder
"""

import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from base_watcher import BaseWatcher


# Configuration
CHECK_INTERVAL = 1  # seconds


class SocialHandler(FileSystemEventHandler):
    """Handle file system events for social drafts."""
    
    def __init__(self, watcher: 'SocialWatcher'):
        self.watcher = watcher
    
    def on_created(self, event):
        """Handle file creation events."""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # Skip Polished subfolder
        if 'Polished' in file_path.parts:
            return
        
        self.watcher.process_draft(file_path)


class SocialWatcher(BaseWatcher):
    """Social media drafts monitoring watcher."""
    
    def __init__(self, vault_path: Optional[Path] = None):
        super().__init__('social', vault_path)
        
        self.social_folder = self.vault_path / 'Social_Drafts'
        self.polished_folder = self.social_folder / 'Polished'
        self.needs_action_folder = self.vault_path / 'Needs_Action'
        
        self.processed_drafts: set = set()
        self.handler = SocialHandler(self)
        self.observer: Optional[Observer] = None
        
        # Ensure folders exist
        self.social_folder.mkdir(exist_ok=True)
        self.polished_folder.mkdir(exist_ok=True)
        self.needs_action_folder.mkdir(exist_ok=True)
    
    def create_action_file(self, file_path: Path) -> Optional[Path]:
        """
        Create action file for social draft.
        
        Args:
            file_path: Path to draft file
        
        Returns:
            Path to action file or None if failed
        """
        try:
            filename = f"SOCIAL_{file_path.name.replace('.', '_')}.md"
            filepath = self.needs_action_folder / filename
            
            content = f"""---
type: social_draft
file_name: {file_path.name}
path: {file_path}
created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
status: pending
---

New raw social post added: {file_path.name}

## Task
Read this file, turn it into a professional version (LinkedIn/FB/IG/X style), 
add 3-5 relevant hashtags, and save the polished post in Social_Drafts/Polished.

## Requirements
- Professional tone (see Company_Handbook.md)
- Platform-appropriate formatting
- 3-5 relevant hashtags
- Save as: POLISHED_{{original_name}}.md
"""
            
            filepath.write_text(content, encoding='utf-8')
            self.log_info(f"Action file created: {filename}")
            return filepath
            
        except IOError as e:
            self.log_error(f"Failed to create action file: {e}", exc=e)
            return None
        except Exception as e:
            self.log_error(f"Unexpected error: {e}", exc=e)
            return None
    
    def trigger_qwen(self, action_file: Path, original_file: Path) -> bool:
        """
        Trigger Qwen CLI to polish social post.
        
        Args:
            action_file: Path to action file
            original_file: Path to original draft
        
        Returns:
            True if successful
        """
        try:
            polished_name = f"POLISHED_{original_file.stem}.md"
            
            prompt = (
                f"Read the social draft action file: {action_file.name} in Needs_Action folder. "
                f"Turn it into a professional version with 3-5 hashtags. "
                f"Save the polished post in Social_Drafts/Polished folder as {polished_name}"
            )
            
            result = subprocess.run(
                ['qwen', '-y', prompt],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                cwd=str(self.vault_path),
                timeout=120
            )
            
            self.log_info("Qwen triggered for social post")
            
            if result.stdout:
                self.log_info(f"Output: {result.stdout.strip()[:200]}")
            if result.stderr:
                self.log_warning(f"Errors: {result.stderr.strip()[:200]}")
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            self.log_warning("Qwen timeout")
            return False
        except FileNotFoundError:
            self.log_error("Qwen CLI not found")
            return False
        except Exception as e:
            self.log_error(f"Qwen error: {e}", exc=e)
            return False
    
    def process_draft(self, file_path: Path):
        """
        Process a newly detected draft.
        
        Args:
            file_path: Path to draft file
        """
        self.log_info(f"New draft detected: {file_path.name}")
        
        # Skip if already processed
        if file_path.name in self.processed_drafts:
            self.log_warning(f"Skipping already processed draft: {file_path.name}")
            return
        
        try:
            # Create action file
            action_file = self.create_action_file(file_path)
            
            if action_file:
                # Trigger Qwen
                self.trigger_qwen(action_file, file_path)
                
                # Mark as processed
                self.processed_drafts.add(file_path.name)
                self.save_processed_ids('processed_social_drafts.txt', self.processed_drafts)
            
        except Exception as e:
            self.log_error(f"Failed to process draft {file_path.name}: {e}", exc=e)
    
    def run(self):
        """Main watcher loop."""
        self.print_status_header("📱 SOCIAL WATCHER STARTED")
        self.log_info(f"Watching folder: {self.social_folder}")
        self.log_info(f"Polished folder: {self.polished_folder}")
        
        # Load processed drafts
        self.processed_drafts = self.load_processed_ids('processed_social_drafts.txt')
        
        # Setup observer
        self.observer = Observer()
        self.observer.schedule(self.handler, str(self.social_folder), recursive=False)
        
        try:
            self.observer.start()
            self.log_info("✅ Social watcher started")
            self.log_info("Press Ctrl+C to stop\n")
            
            while True:
                time.sleep(CHECK_INTERVAL)
        
        except KeyboardInterrupt:
            self.log_info("\n\n⏹️  Stopping Social Watcher...")
            self.observer.stop()
            self.log_info(f"Final uptime: {self.get_uptime()}")
            self.log_info("✅ Watcher stopped successfully")
        
        finally:
            if self.observer:
                self.observer.join()


def main():
    """Entry point."""
    watcher = SocialWatcher()
    watcher.run()


if __name__ == '__main__':
    main()
