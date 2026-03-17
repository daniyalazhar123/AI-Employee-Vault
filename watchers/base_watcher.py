"""
Base Watcher Module for AI Employee Vault

Provides common functionality for all watcher scripts:
- Logging (console + file with rotation)
- Retry logic with exponential backoff
- Error handling utilities
- Performance tracking
"""

import logging
import time
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Any, Callable, Optional, List, Dict
from logging.handlers import TimedRotatingFileHandler
import traceback


class BaseWatcher:
    """
    Base class for all watcher scripts.
    Provides logging, retry logic, and error handling.
    """
    
    def __init__(self, name: str, vault_path: Optional[Path] = None):
        """
        Initialize base watcher.
        
        Args:
            name: Watcher name (e.g., 'gmail', 'whatsapp')
            vault_path: Path to vault root (defaults to script parent)
        """
        self.name = name
        self.vault_path = vault_path or Path(__file__).parent.parent
        self.logs_folder = self.vault_path / 'Logs'
        self.logger = self._setup_logging()
        self.processed_ids = set()
        self.start_time = datetime.now()
        
        # Ensure logs folder exists
        self.logs_folder.mkdir(exist_ok=True)
    
    def _setup_logging(self) -> logging.Logger:
        """
        Setup logging to both console and file with daily rotation.
        
        Returns:
            Configured logger instance
        """
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        logger.handlers = []
        
        # Log format
        log_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(log_format)
        logger.addHandler(console_handler)
        
        # File handler with daily rotation
        log_file = self.logs_folder / f'{self.name}_{datetime.now():%Y%m%d}.log'
        file_handler = TimedRotatingFileHandler(
            filename=log_file,
            when='D',
            interval=1,
            backupCount=7,  # Keep 7 days of logs
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(log_format)
        logger.addHandler(file_handler)
        
        # JSON log handler for easy parsing
        json_log_file = self.logs_folder / f'{self.name}_{datetime.now():%Y%m%d}.jsonl'
        self.json_log_file = json_log_file
        
        return logger
    
    def _log_json(self, level: str, message: str, **kwargs):
        """
        Write a JSON-formatted log entry.
        
        Args:
            level: Log level (INFO, WARNING, ERROR)
            message: Log message
            **kwargs: Additional fields to include
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'watcher': self.name,
            'message': message,
            **kwargs
        }
        
        try:
            with open(self.json_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            self.logger.error(f"Failed to write JSON log: {e}")
    
    def log_info(self, message: str, **kwargs):
        """Log info level message."""
        self.logger.info(message)
        self._log_json('INFO', message, **kwargs)
    
    def log_warning(self, message: str, **kwargs):
        """Log warning level message."""
        self.logger.warning(message)
        self._log_json('WARNING', message, **kwargs)
    
    def log_error(self, message: str, exc: Optional[Exception] = None, **kwargs):
        """Log error level message with optional exception."""
        self.logger.error(message)
        error_data = {'error': str(exc)} if exc else {}
        self._log_json('ERROR', message, **error_data, **kwargs)
        
        if exc:
            self.logger.debug(traceback.format_exc())
    
    def with_retry(
        self,
        func: Callable,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential: bool = True,
        retryable_exceptions: Optional[tuple] = None
    ) -> Any:
        """
        Execute function with retry logic and exponential backoff.
        
        Args:
            func: Function to execute
            max_retries: Maximum number of retry attempts
            base_delay: Base delay between retries in seconds
            max_delay: Maximum delay cap in seconds
            exponential: Use exponential backoff if True
            retryable_exceptions: Tuple of exceptions that should trigger retry
                                  (None means all exceptions are retryable)
        
        Returns:
            Result of successful function execution
        
        Raises:
            Last exception if all retries fail
        """
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return func()
            
            except Exception as e:
                last_exception = e
                
                # Check if exception is retryable
                if retryable_exceptions and not isinstance(e, retryable_exceptions):
                    self.log_error(
                        f"Non-retryable error: {e}",
                        exc=e,
                        attempt=attempt + 1,
                        max_retries=max_retries
                    )
                    raise
                
                # Don't retry if we've exhausted attempts
                if attempt >= max_retries:
                    self.log_error(
                        f"All {max_retries} retries exhausted",
                        exc=e,
                        attempt=attempt + 1,
                        max_retries=max_retries
                    )
                    raise
                
                # Calculate delay
                if exponential:
                    delay = min(base_delay * (2 ** attempt), max_delay)
                else:
                    delay = base_delay
                
                self.log_warning(
                    f"Attempt {attempt + 1}/{max_retries + 1} failed: {e}. Retrying in {delay:.1f}s",
                    attempt=attempt + 1,
                    max_retries=max_retries,
                    delay=delay
                )
                
                time.sleep(delay)
        
        # Should never reach here, but just in case
        if last_exception:
            raise last_exception
    
    def load_processed_ids(self, filename: str) -> set:
        """
        Load processed IDs from file.
        
        Args:
            filename: Name of file in data/ folder
        
        Returns:
            Set of processed IDs
        """
        data_file = self.vault_path / 'data' / filename
        
        if not data_file.exists():
            self.log_info(f"No existing {filename} found, starting fresh")
            return set()
        
        try:
            content = data_file.read_text(encoding='utf-8')
            processed = set(line.strip() for line in content.splitlines() if line.strip())
            self.log_info(f"Loaded {len(processed)} processed IDs from {filename}")
            return processed
        except Exception as e:
            self.log_error(f"Failed to load {filename}: {e}", exc=e)
            return set()
    
    def save_processed_ids(self, filename: str, ids: set, max_keep: int = 10000):
        """
        Save processed IDs to file.
        
        Args:
            filename: Name of file in data/ folder
            ids: Set of IDs to save
            max_keep: Maximum number of IDs to retain (prune oldest)
        """
        # Ensure data folder exists
        data_folder = self.vault_path / 'data'
        data_folder.mkdir(exist_ok=True)
        
        data_file = data_folder / filename
        
        # Prune if too large
        if len(ids) > max_keep:
            ids = set(list(ids)[-max_keep:])
            self.log_info(f"Pruned processed IDs to keep last {max_keep}")
        
        try:
            data_file.write_text('\n'.join(sorted(ids)), encoding='utf-8')
            self.log_info(f"Saved {len(ids)} processed IDs to {filename}")
        except Exception as e:
            self.log_error(f"Failed to save {filename}: {e}", exc=e)
    
    def get_uptime(self) -> str:
        """Get human-readable uptime string."""
        delta = datetime.now() - self.start_time
        total_seconds = int(delta.total_seconds())
        
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def print_status_header(self, title: str, width: int = 70):
        """Print a formatted status header."""
        self.log_info("=" * width)
        self.log_info(f"{title:^{width}}")
        self.log_info("=" * width)
        self.log_info(f"Vault Path: {self.vault_path}")
        self.log_info(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.log_info(f"Uptime: {self.get_uptime()}")
        self.log_info("=" * width)

    def trigger_qwen(self, prompt: str, timeout: int = 120) -> bool:
        """
        Trigger Qwen CLI with a prompt.
        
        This is a common method for all watchers to trigger Qwen.
        Handles missing Qwen CLI gracefully.
        
        Args:
            prompt: Prompt to send to Qwen
            timeout: Timeout in seconds (default: 120)
            
        Returns:
            True if Qwen executed successfully, False otherwise
        """
        import subprocess
        
        try:
            # First check if qwen command exists
            try:
                subprocess.run(
                    ['qwen', '--version'],
                    capture_output=True,
                    timeout=5,
                    check=True
                )
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                self.log_warning(
                    "Qwen CLI not found in PATH. Action files created for manual processing. "
                    "Install Qwen CLI with: npm install -g @anthropic/qwen"
                )
                return False

            # Run Qwen with the prompt
            result = subprocess.run(
                ['qwen', '-y', prompt],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                cwd=str(self.vault_path),
                timeout=timeout
            )

            self.log_info("Qwen processing completed")

            if result.stdout:
                self.log_info(f"Qwen output: {result.stdout.strip()[:200]}...")
            if result.stderr:
                self.log_warning(f"Qwen stderr: {result.stderr.strip()[:200]}...")

            return result.returncode == 0

        except subprocess.TimeoutExpired:
            self.log_warning(f"Qwen timeout ({timeout}s). Action file remains for manual processing.")
            return False
        except Exception as e:
            self.log_error(f"Failed to trigger Qwen: {e}", exc=e)
            return False


class WatcherError(Exception):
    """Base exception for watcher errors."""
    pass


class ConfigurationError(WatcherError):
    """Raised when configuration is invalid or missing."""
    pass


class ConnectionError(WatcherError):
    """Raised when connection to external service fails."""
    pass


class ProcessingError(WatcherError):
    """Raised when processing an item fails."""
    pass
