"""
Office Watcher for AI Employee Vault

Monitors Office_Files folder for new documents.
Features:
- File system event monitoring
- Robust error handling with retry logic
- JSON logging to /Logs/ folder
- Duplicate detection
"""

import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent
from watchdog.events import EVENT_TYPE_FILE_CREATED

from base_watcher import BaseWatcher


# Configuration
CHECK_INTERVAL = 1  # seconds (watchdog internal)


class OfficeHandler(FileSystemEventHandler):
    """Handle file system events for office files."""
    
    def __init__(self, watcher: 'OfficeWatcher'):
        self.watcher = watcher
    
    def on_created(self, event):
        """Handle file creation events."""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        self.watcher.process_new_file(file_path)


class OfficeWatcher(BaseWatcher):
    """Office files monitoring watcher."""
    
    def __init__(self, vault_path: Optional[Path] = None):
        super().__init__('office', vault_path)
        
        self.office_folder = self.vault_path / 'Office_Files'
        self.needs_action_folder = self.vault_path / 'Needs_Action'
        
        self.processed_files: set = set()
        self.handler = OfficeHandler(self)
        self.observer: Optional[Observer] = None
        
        # Ensure folders exist
        self.office_folder.mkdir(exist_ok=True)
        self.needs_action_folder.mkdir(exist_ok=True)
    
    def is_valid_file(self, file_path: Path) -> bool:
        """
        Check if file is valid for processing.
        
        Args:
            file_path: Path to file
        
        Returns:
            True if file should be processed
        """
        # Skip hidden files
        if file_path.name.startswith('.'):
            return False
        
        # Skip already processed (duplicate detection)
        if file_path.name in self.processed_files:
            self.log_warning(f"Skipping already processed file: {file_path.name}")
            return False
        
        # Skip malformed names
        if '.md.md' in file_path.name:
            self.log_warning(f"Skipping malformed filename: {file_path.name}")
            return False
        
        return True
    
    def create_action_file(self, file_path: Path) -> Optional[Path]:
        """
        Create action file for office document.
        
        Args:
            file_path: Path to new office file
        
        Returns:
            Path to action file or None if failed
        """
        try:
            filename = f"OFFICE_{file_path.name}.md"
            filepath = self.needs_action_folder / filename
            
            content = f"""---
type: office_file
file_name: {file_path.name}
path: {file_path}
created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
status: pending
---

New office file added: {file_path.name}

Full Path: `{file_path}`

## Task
Read this file, summarize content, make it professional if needed, and update Dashboard.md.

## Suggested Actions
- [ ] Read and understand content
- [ ] Summarize key points
- [ ] Update Dashboard.md if relevant
- [ ] Archive after processing
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
    
    def trigger_qwen(self, action_file: Path) -> bool:
        """Trigger Qwen CLI to process file."""
        prompt = (
            f"Process Needs_Action folder and handle the latest OFFICE file: {action_file.name}. "
            f"Read the file, summarize content, and update Dashboard.md if relevant."
        )
        
        return self.trigger_qwen(prompt)
    
    def process_new_file(self, file_path: Path):
        """
        Process a newly detected file.
        
        Args:
            file_path: Path to new file
        """
        self.log_info(f"New file detected: {file_path.name}")
        
        # Validate file
        if not self.is_valid_file(file_path):
            return
        
        try:
            # Create action file
            action_file = self.create_action_file(file_path)
            
            if action_file:
                # Trigger Qwen
                self.trigger_qwen(action_file)
                
                # Mark as processed
                self.processed_files.add(file_path.name)
                self.save_processed_ids('processed_office_files.txt', self.processed_files)
            
        except Exception as e:
            self.log_error(f"Failed to process file {file_path.name}: {e}", exc=e)
    
    def run(self):
        """Main watcher loop."""
        self.print_status_header("🏢 OFFICE WATCHER STARTED")
        self.log_info(f"Watching folder: {self.office_folder}")
        
        # Load processed files
        self.processed_files = self.load_processed_ids('processed_office_files.txt')
        
        # Setup observer
        self.observer = Observer()
        self.observer.schedule(self.handler, str(self.office_folder), recursive=False)
        
        try:
            self.observer.start()
            self.log_info("✅ File watcher started")
            self.log_info("Press Ctrl+C to stop\n")
            
            while True:
                time.sleep(CHECK_INTERVAL)
        
        except KeyboardInterrupt:
            self.log_info("\n\n⏹️  Stopping Office Watcher...")
            self.observer.stop()
            self.log_info(f"Final uptime: {self.get_uptime()}")
            self.log_info("✅ Watcher stopped successfully")
        
        finally:
            if self.observer:
                self.observer.join()


def main():
    """Entry point."""
    watcher = OfficeWatcher()
    watcher.run()


if __name__ == '__main__':
    main()
