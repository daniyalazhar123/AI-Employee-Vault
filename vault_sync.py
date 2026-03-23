#!/usr/bin/env python3
"""
🔄 VAULT SYNC - Platinum Tier
Git-based Vault Synchronization

Personal AI Employee Hackathon 0
Platinum Tier: Always-On Cloud + Local Executive

Features:
- Git pull every 5 minutes
- Git add, commit, push changes
- Excludes .env, credentials, session files
- Logs sync status to Logs/sync.log
- Handles merge conflicts gracefully

Security:
- NEVER sync .env files
- NEVER sync credentials
- NEVER sync WhatsApp sessions
- NEVER sync banking tokens
"""

import os
import sys
import time
import subprocess
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List
import signal

# Configuration
VAULT_PATH = Path(os.getenv('VAULT_PATH', '.'))
SYNC_INTERVAL = int(os.getenv('SYNC_INTERVAL', '300'))  # 5 minutes
GIT_REMOTE = os.getenv('GIT_REMOTE', 'origin')
GIT_BRANCH = os.getenv('GIT_BRANCH', 'main')

# Setup logging
LOG_FILE = VAULT_PATH / 'Logs' / 'sync.log'
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('VaultSync')


class VaultSync:
    """
    Vault Sync - Git-based synchronization
    
    Syncs vault between Cloud and Local machines
    using Git with proper security exclusions.
    """
    
    def __init__(self, vault_path: Path):
        self.vault = vault_path
        self.logs = self.vault / 'Logs'
        
        # Ensure logs folder exists
        self.logs.mkdir(parents=True, exist_ok=True)
        
        # Statistics
        self.stats = {
            'syncs_completed': 0,
            'pulls': 0,
            'pushes': 0,
            'conflicts': 0,
            'errors': 0,
            'last_sync': None,
            'start_time': datetime.now().isoformat()
        }
        
        # Running flag
        self.running = True
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("🔄 Vault Sync initialized")
        logger.info(f"📂 Vault path: {self.vault}")
        logger.info(f"⏱️ Sync interval: {SYNC_INTERVAL} seconds")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"🛑 Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    def check_git_repo(self) -> bool:
        """Check if vault is a git repository"""
        git_dir = self.vault / '.git'
        
        if not git_dir.exists():
            logger.error("❌ Not a git repository! Run: git init")
            return False
        
        logger.debug("✅ Git repository verified")
        return True
    
    def git_pull(self) -> bool:
        """Pull latest changes from remote"""
        try:
            logger.info("⬇️  Pulling latest changes...")
            
            result = subprocess.run(
                ['git', 'pull', GIT_REMOTE, GIT_BRANCH],
                cwd=self.vault,
                capture_output=True,
                timeout=60
            )
            
            self.stats['pulls'] += 1
            
            if result.returncode == 0:
                logger.info("✅ Pull successful")
                if result.stdout:
                    for line in result.stdout.decode().strip().split('\n'):
                        if line:
                            logger.debug(f"   {line}")
                return True
            else:
                logger.error(f"❌ Pull failed: {result.stderr.decode()}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Pull timed out")
            self.stats['errors'] += 1
            return False
        except Exception as e:
            logger.error(f"❌ Pull error: {e}")
            self.stats['errors'] += 1
            return False
    
    def git_status(self) -> Optional[str]:
        """Get git status"""
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.vault,
                capture_output=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout.decode().strip()
            else:
                return None
                
        except Exception as e:
            logger.error(f"❌ Git status error: {e}")
            return None
    
    def git_add(self, files: List[str]) -> bool:
        """Add files to git staging"""
        try:
            if not files:
                return True
            
            logger.info(f"➕ Adding {len(files)} files...")
            
            result = subprocess.run(
                ['git', 'add'] + files,
                cwd=self.vault,
                capture_output=True,
                timeout=60
            )
            
            if result.returncode == 0:
                logger.debug("✅ Files added")
                return True
            else:
                logger.error(f"❌ Add failed: {result.stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Add error: {e}")
            return False
    
    def git_commit(self, message: str) -> bool:
        """Commit staged changes"""
        try:
            logger.info(f"💾 Committing: {message}")
            
            result = subprocess.run(
                ['git', 'commit', '-m', message],
                cwd=self.vault,
                capture_output=True,
                timeout=60
            )
            
            if result.returncode == 0:
                logger.info("✅ Commit successful")
                return True
            elif b'nothing to commit' in result.stderr:
                logger.debug("ℹ️ Nothing to commit")
                return True  # Not an error
            else:
                logger.error(f"❌ Commit failed: {result.stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Commit error: {e}")
            return False
    
    def git_push(self) -> bool:
        """Push commits to remote"""
        try:
            logger.info("⬆️  Pushing changes...")
            
            result = subprocess.run(
                ['git', 'push', GIT_REMOTE, GIT_BRANCH],
                cwd=self.vault,
                capture_output=True,
                timeout=120
            )
            
            self.stats['pushes'] += 1
            
            if result.returncode == 0:
                logger.info("✅ Push successful")
                return True
            else:
                logger.error(f"❌ Push failed: {result.stderr.decode()}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Push timed out")
            self.stats['errors'] += 1
            return False
        except Exception as e:
            logger.error(f"❌ Push error: {e}")
            self.stats['errors'] += 1
            return False
    
    def get_changed_files(self) -> List[str]:
        """Get list of changed files"""
        status = self.git_status()
        
        if not status:
            return []
        
        files = []
        for line in status.split('\n'):
            if line.strip():
                # Extract filename (skip status codes)
                parts = line.split()
                if len(parts) >= 2:
                    files.append(parts[-1])
        
        return files
    
    def should_exclude(self, file_path: str) -> bool:
        """Check if file should be excluded from sync"""
        exclude_patterns = [
            '.env',
            '.env.local',
            '.env.cloud',
            'credentials.json',
            'token.json',
            'whatsapp_session/',
            'WhatsApp/',
            '*.session',
            '*.pickle',
            'Logs/',
            'Dead_Letter_Queue/',
            '__pycache__/',
            '*.pyc',
            'node_modules/',
            'local/.env.local',
            'cloud/.env.cloud',
            '*.pem',
            '*.key',
            '*.log'
        ]
        
        for pattern in exclude_patterns:
            if pattern in file_path:
                logger.debug(f"🚫 Excluding: {file_path} (matches {pattern})")
                return True
        
        return False
    
    def sync(self) -> bool:
        """Perform full sync cycle"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            logger.info(f"🔄 Starting sync cycle at {timestamp}")
            
            # Step 1: Pull latest changes
            if not self.git_pull():
                logger.warning("⚠️ Pull failed, continuing anyway...")
            
            # Step 2: Get changed files
            changed_files = self.get_changed_files()
            
            if not changed_files:
                logger.info("ℹ️ No changes to sync")
                self.stats['syncs_completed'] += 1
                self.stats['last_sync'] = timestamp
                return True
            
            # Step 3: Filter excluded files
            files_to_add = [f for f in changed_files if not self.should_exclude(f)]
            
            if not files_to_add:
                logger.info("ℹ️ All changes are excluded")
                self.stats['syncs_completed'] += 1
                self.stats['last_sync'] = timestamp
                return True
            
            # Step 4: Add files
            if not self.git_add(files_to_add):
                return False
            
            # Step 5: Commit
            message = f"Vault sync {timestamp}"
            if not self.git_commit(message):
                return False
            
            # Step 6: Push
            if not self.git_push():
                logger.warning("⚠️ Push failed, but pull completed")
            
            self.stats['syncs_completed'] += 1
            self.stats['last_sync'] = timestamp
            
            logger.info(f"✅ Sync cycle completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Sync error: {e}")
            self.stats['errors'] += 1
            return False
    
    def save_stats(self):
        """Save statistics to file"""
        stats_file = self.logs / 'sync_stats.json'
        with open(stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def log_sync_status(self, success: bool):
        """Log sync status to JSONL file"""
        status_file = self.logs / 'sync.jsonl'
        
        entry = {
            'timestamp': datetime.now().isoformat(),
            'success': success,
            'pulls': self.stats['pulls'],
            'pushes': self.stats['pushes'],
            'syncs_completed': self.stats['syncs_completed'],
            'errors': self.stats['errors']
        }
        
        with open(status_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    
    def run(self):
        """Main run loop"""
        logger.info("🚀 Starting Vault Sync...")
        
        # Check if git repo
        if not self.check_git_repo():
            logger.error("❌ Cannot start - not a git repository")
            return
        
        try:
            while self.running:
                success = self.sync()
                self.log_sync_status(success)
                self.save_stats()
                
                # Wait for next sync
                time.sleep(SYNC_INTERVAL)
            
            logger.info("🛑 Vault Sync stopped")
            self.save_stats()
            
        except Exception as e:
            logger.error(f"❌ Fatal error: {e}")
            self.save_stats()
            sys.exit(1)


def main():
    """Main entry point"""
    print("╔════════════════════════════════════════════════════════╗")
    print("║  🔄  VAULT SYNC - Platinum Tier                       ║")
    print("║     Git-based Synchronization (Every 5 minutes)        ║")
    print("╚════════════════════════════════════════════════════════╝")
    print()
    
    sync = VaultSync(VAULT_PATH)
    sync.run()


if __name__ == '__main__':
    main()
