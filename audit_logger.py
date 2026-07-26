"""
Comprehensive Audit Logger for AI Employee Vault

Gold Tier Requirement #9 - Comprehensive audit logging

Features:
- Structured JSON logging
- Log rotation (daily)
- Audit trail for all actions
- Search and filter capabilities
- Log aggregation

Usage:
    from audit_logger import AuditLogger
    
    logger = AuditLogger()
    logger.log_action('email_send', {'to': 'user@example.com'}, 'success')
"""

import json
import logging
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from logging.handlers import TimedRotatingFileHandler
import re


# ---------------------------------------------------------------------------
# Emoji sanitization for cp1252/win32 environments
# ---------------------------------------------------------------------------

_EMOJI_REPLACEMENTS = {
    '\u2705': '[SUCCESS]',
    '\u274C': '[FAIL]',
    '\u26A0\uFE0F': '[WARN]',
    '\u26A0': '[WARN]',
    '\u2139\uFE0F': '[INFO]',
    '\u2139': '[INFO]',
    '\u2B06\uFE0F': '[UP]',
    '\u2B07\uFE0F': '[DOWN]',
    '\uD83D\uDCC8': '[TREND_UP]',
    '\uD83D\uDCC9': '[TREND_DOWN]',
    '\uD83D\uDCB0': '[MONEY]',
    '\uD83C\uDFAF': '[TARGET]',
    '\uD83D\uDD0D': '[SEARCH]',
    '\uD83D\uDCE7': '[EMAIL]',
    '\uD83D\uDCE8': '[MAIL]',
    '\uD83D\uDCE9': '[MAIL]',
    '\uD83D\uDCE4': '[SENT]',
    '\uD83D\uDCE5': '[INBOX]',
    '\uD83D\uDD14': '[ALERT]',
    '\uD83D\uDD0A': '[SOUND]',
    '\uD83D\uDD07': '[MUTE]',
    '\uD83D\uDD04': '[REFRESH]',
    '\uD83D\uDD01': '[RELOAD]',
    '\uD83D\uDD0E': '[LOCK]',
    '\uD83D\uDD10': '[LOCKED]',
    '\uD83D\uDD13': '[UNLOCKED]',
    '\uD83D\uDD11': '[KEY]',
    '\uD83D\uDCC1': '[FOLDER]',
    '\uD83D\uDCC2': '[FOLDER]',
    '\uD83D\uDCC4': '[DOC]',
    '\uD83D\uDCC5': '[CALENDAR]',
    '\uD83D\uDCC6': '[NOTE]',
    '\uD83D\uDCDD': '[PENCIL]',
    '\uD83D\uDCCC': '[PIN]',
    '\uD83D\uDCCD': '[PIN]',
    '\uD83D\uDCE2': '[ANNOUNCE]',
    '\uD83D\uDCAC': '[CHAT]',
    '\uD83D\uDDE3\uFE0F': '[SPEECH]',
    '\uD83D\uDC64': '[USER]',
    '\uD83D\uDC65': '[USERS]',
    '\uD83E\uDD16': '[ROBOT]',
    '\uD83D\uDC4D': '[THUMBS_UP]',
    '\uD83D\uDC4E': '[THUMBS_DOWN]',
    '\uD83D\uDC4F': '[CLAP]',
    '\uD83C\uDF89': '[CELEBRATE]',
    '\uD83C\uDFC6': '[TROPHY]',
    '\uD83E\uDD47': '[GOLD]',
    '\uD83E\uDD48': '[SILVER]',
    '\uD83E\uDD49': '[BRONZE]',
    '\u26A1': '[BOLT]',
    '\uD83D\uDE80': '[ROCKET]',
    '\uD83C\uDF10': '[GLOBE]',
    '\uD83D\uDEE0\uFE0F': '[TOOLS]',
    '\u2699\uFE0F': '[GEAR]',
    '\u2699': '[GEAR]',
    '\uD83D\uDD27': '[FIX]',
    '\uD83D\uDD28': '[HAMMER]',
    '\uD83D\uDD29': '[WRENCH]',
    '\uD83D\uDD17': '[LINK]',
    '\uD83D\uDCCE': '[ATTACH]',
    '\uD83D\uDCD0': '[BOOKMARK]',
    '\uD83D\uDCAD': '[IDEA]',
    '\u2753': '[QUERY]',
    '\u2757': '[EXCLAM]',
    '\u203C\uFE0F': '[EXCLAM]',
    '\uD83D\uDD34': '[CRIT]',
    '\uD83D\uDFE2': '[OK]',
    '\uD83D\uDFE1': '[WARN]',
    '\uD83D\uDD35': '[INFO]',
    '\u26AA': '[NONE]',
    '\u2B50': '[STAR]',
    '\u2728': '[SPARKLE]',
    '\u2764\uFE0F': '[HEART]',
    '\u2764': '[HEART]',
    '\u23F3': '[WAIT]',
    '\u23F1\uFE0F': '[TIMER]',
    '\u23F1': '[TIMER]',
    '\u26D4': '[STOP]',
    '\uD83D\uDEAB': '[BANNED]',
    '\uD83D\uDED1': '[HALT]',
    '\u2714\uFE0F': '[CHECK]',
    '\u2714': '[CHECK]',
    '\u2716\uFE0F': '[CROSS]',
    '\u2716': '[CROSS]',
    '\u2795': '[PLUS]',
    '\u2796': '[MINUS]',
    '\u2797': '[DIVIDE]',
    '\u2702\uFE0F': '[SCISSORS]',
    '\u2702': '[SCISSORS]',
    '\u2708\uFE0F': '[AIRPLANE]',
    '\u2708': '[AIRPLANE]',
    '\u2709\uFE0F': '[ENVELOPE]',
    '\u2709': '[ENVELOPE]',
    '\u270F\uFE0F': '[PENCIL]',
    '\u270F': '[PENCIL]',
}

_EMOJI_WIDE_PATTERN = re.compile(
    '[\U0001F600-\U0001F64F'
    '\U0001F300-\U0001F5FF'
    '\U0001F680-\U0001F6FF'
    '\U0001F1E0-\U0001F1FF'
    '\U0001F900-\U0001F9FF'
    '\U0001FA00-\U0001FA6F'
    '\U0001FA70-\U0001FAFF'
    '\U00002702-\U000027B0'
    '\U000024C2-\U0001F251'
    '\U00002600-\U000026FF'
    '\U00002B50\uFE0F?'
    '\U00002934-\U00002935'
    '\U000025AA-\U000025AB'
    '\U000025B6'
    '\U000025C0'
    '\U000025FB-\U000025FE'
    '\U00002614-\U00002615'
    '\U00002648-\U00002653'
    '\U0000267F'
    '\U00002693'
    '\U000026A1'
    '\U000026AA-\U000026AB'
    '\U000026BD-\U000026BE'
    '\U000026C4-\U000026C5'
    '\U000026D4'
    '\U000026EA'
    '\U000026F2-\U000026F3'
    '\U000026F5'
    '\U000026FA'
    '\U000026FD'
    '\U00002702'
    '\U00002708-\U0000270F'
    '\U00002712'
    '\U00002714'
    '\U00002716'
    '\U0000271D'
    '\U00002721'
    '\U00002728'
    '\U00002733-\U00002734'
    '\U00002744'
    '\U00002747'
    '\U00002764'
    '\U00002795-\U00002797'
    '\U000027A1'
    '\U000027B0'
    '\U000027BF'
    '\U00002B05-\U00002B07'
    '\U00002B1B-\U00002B1C'
    '\U00002B55'
    '\U00003030'
    '\U0000303D'
    '\U00003297'
    '\U00003299'
    '\u200D'
    '\u20E3'
    '\uFE0F'
    ']'
)


def _sanitize_emoji(text: str) -> str:
    if not text:
        return text
    for raw_emoji, replacement in _EMOJI_REPLACEMENTS.items():
        text = text.replace(raw_emoji, replacement)
    text = _EMOJI_WIDE_PATTERN.sub('', text)
    return text


class SafeConsoleFormatter(logging.Formatter):
    """
    Logging formatter that safely handles emoji on cp1252/win32 streams.

    - Detects stream encoding and replaces/strips emoji when the stream
      cannot handle full UTF-8.
    - Outputs clean JSON when PRODUCTION_JSON_LOGS=1 is set.
    """

    def __init__(self, fmt=None, datefmt=None, *, force_safe=False):
        super().__init__(fmt, datefmt)
        self._force_safe = force_safe
        self._json_mode = os.environ.get('PRODUCTION_JSON_LOGS') == '1'
        self._needs_sanitize: Optional[bool] = None

    def _stream_needs_sanitize(self, stream) -> bool:
        if self._force_safe:
            return True
        if stream is None:
            return False
        try:
            enc = getattr(stream, 'encoding', None) or sys.getdefaultencoding()
            return enc.lower() in ('cp1252', 'latin-1', 'iso-8859-1', 'ansi')
        except Exception:
            return False

    def format(self, record: logging.LogRecord) -> str:
        if self._json_mode:
            return self._format_json(record)
        if self._needs_sanitize is None:
            self._needs_sanitize = self._stream_needs_sanitize(
                getattr(self, 'stream', None) or sys.stdout
            )
        if self._needs_sanitize:
            record.msg = _sanitize_emoji(str(record.msg))
            if record.exc_text:
                record.exc_text = _sanitize_emoji(record.exc_text)
        return super().format(record)

    def _format_json(self, record: logging.LogRecord) -> str:
        msg = str(record.msg)
        if record.args:
            try:
                msg = msg % record.args
            except Exception:
                msg = f'{msg} {record.args}'
        entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'logger': record.name,
            'level': record.levelname,
            'message': _sanitize_emoji(msg) if self._needs_sanitize else msg,
            'module': record.module,
            'line': record.lineno,
            'function': record.funcName,
        }
        if record.exc_info and record.exc_info[1]:
            entry['exception'] = repr(record.exc_info[1])
        if record.process:
            entry['pid'] = record.process
        return json.dumps(entry, ensure_ascii=False, default=str)


# ---------------------------------------------------------------------------
# Centralized vault logging setup
# ---------------------------------------------------------------------------

_DEFAULT_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


def setup_logging(
    name: str = 'vault',
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    force_safe: bool = False,
) -> logging.Logger:
    """
    Configure and return a logger with SafeConsoleFormatter.

    Parameters
    ----------
    name : str
        Logger name.
    level : int
        Logging level (default INFO).
    log_file : str or None
        Path to log file. If None, console-only.
    force_safe : bool
        Force emoji sanitization regardless of stream encoding.

    Returns
    -------
    logging.Logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if logger.handlers:
        return logger

    formatter = SafeConsoleFormatter(
        fmt=_DEFAULT_FORMAT,
        datefmt='%Y-%m-%d %H:%M:%S',
        force_safe=force_safe,
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file:
        p = Path(log_file)
        p.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def patch_root_logger(force_safe: bool = False):
    """Replace all root logger handler formatters with SafeConsoleFormatter."""
    root = logging.getLogger()
    for handler in root.handlers:
        if not isinstance(handler.formatter, SafeConsoleFormatter):
            handler.setFormatter(
                SafeConsoleFormatter(
                    fmt=getattr(handler.formatter, '_fmt', None),
                    datefmt=getattr(handler.formatter, 'datefmt', None),
                    force_safe=force_safe,
                )
            )


# ===================================================================
# Original AuditLogger class follows
# ===================================================================

class AuditLogger:
    """Comprehensive audit logger for AI Employee."""
    
    def __init__(self, vault_path: Optional[Path] = None):
        """
        Initialize audit logger.
        
        Args:
            vault_path: Path to vault root (defaults to script parent)
        """
        self.vault_path = vault_path or Path(__file__).parent
        self.logs_folder = self.vault_path / 'Logs'
        self.audit_folder = self.logs_folder / 'Audit'
        
        # Ensure folders exist
        self.logs_folder.mkdir(exist_ok=True)
        self.audit_folder.mkdir(exist_ok=True)
        
        # Setup logging
        self.logger = self._setup_logging()
        
        # Statistics
        self.actions_logged = 0
        self.start_time = datetime.now()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup structured logging."""
        logger = logging.getLogger('audit')
        logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        logger.handlers = []
        
        # Log format - SafeConsoleFormatter handles emoji + optional JSON
        log_format = SafeConsoleFormatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(log_format)
        logger.addHandler(console_handler)
        
        # File handler with daily rotation
        log_file = self.audit_folder / f"audit_{datetime.now():%Y%m%d}.log"
        file_handler = TimedRotatingFileHandler(
            filename=log_file,
            when='D',
            interval=1,
            backupCount=30,  # Keep 30 days of logs
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(log_format)
        logger.addHandler(file_handler)
        
        return logger
    
    def log_action(
        self,
        action_type: str,
        parameters: Dict[str, Any],
        status: str,
        actor: str = 'ai_employee',
        target: Optional[str] = None,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ):
        """
        Log an action for audit trail.
        
        Args:
            action_type: Type of action (e.g., 'email_send', 'invoice_create')
            parameters: Action parameters
            status: 'success', 'failed', 'pending', 'approved', 'rejected'
            actor: Who performed the action (human, ai_employee, watcher)
            target: Target of action (email, invoice, post, etc.)
            result: Action result data
            error: Error message if failed
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'actor': actor,
            'target': target,
            'parameters': parameters,
            'status': status,
            'result': result,
            'error': error,
            'session_id': id(self)
        }
        
        # Log to file
        log_level = logging.INFO if status == 'success' else logging.WARNING
        self.logger.log(log_level, json.dumps(log_entry, ensure_ascii=False))
        
        # Update statistics
        self.actions_logged += 1
        
        # Also write to daily JSON log for easy querying
        self._write_json_log(log_entry)
    
    def _write_json_log(self, log_entry: Dict[str, Any]):
        """Write to JSON log file for easy querying."""
        json_log_file = self.audit_folder / f"audit_{datetime.now():%Y%m%d}.jsonl"
        
        try:
            with open(json_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            self.logger.error(f"Failed to write JSON log: {e}")
    
    def log_watcher_action(
        self,
        watcher_name: str,
        action: str,
        item_id: str,
        status: str,
        details: Optional[Dict] = None
    ):
        """Log watcher-specific action."""
        self.log_action(
            action_type=f'watcher_{watcher_name}',
            parameters={'action': action, 'item_id': item_id, **(details or {})},
            status=status,
            actor='watcher',
            target=item_id
        )
    
    def log_mcp_action(
        self,
        mcp_server: str,
        tool_name: str,
        parameters: Dict,
        status: str,
        result: Optional[Dict] = None,
        error: Optional[str] = None
    ):
        """Log MCP server action."""
        self.log_action(
            action_type=f'mcp_{mcp_server}_{tool_name}',
            parameters=parameters,
            status=status,
            actor='mcp',
            target=mcp_server,
            result=result,
            error=error
        )
    
    def log_approval(
        self,
        action_type: str,
        item_id: str,
        decision: str,
        decided_by: str = 'human'
    ):
        """Log approval workflow action."""
        self.log_action(
            action_type='approval',
            parameters={'action_type': action_type, 'item_id': item_id},
            status=decision,
            actor=decided_by,
            target=item_id
        )
    
    def get_audit_summary(self, days: int = 7) -> Dict[str, Any]:
        """
        Get audit summary for the last N days.
        
        Args:
            days: Number of days to summarize
        
        Returns:
            Summary statistics
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Read JSON logs
        log_entries = []
        for log_file in self.audit_folder.glob('audit_*.jsonl'):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        entry = json.loads(line)
                        entry_date = datetime.fromisoformat(entry['timestamp'])
                        if entry_date >= cutoff_date:
                            log_entries.append(entry)
            except Exception as e:
                continue
        
        # Generate statistics
        summary = {
            'period_days': days,
            'total_actions': len(log_entries),
            'by_status': {},
            'by_actor': {},
            'by_action_type': {},
            'errors': 0,
            'success_rate': 0
        }
        
        for entry in log_entries:
            # By status
            status = entry.get('status', 'unknown')
            summary['by_status'][status] = summary['by_status'].get(status, 0) + 1
            
            # By actor
            actor = entry.get('actor', 'unknown')
            summary['by_actor'][actor] = summary['by_actor'].get(actor, 0) + 1
            
            # By action type
            action_type = entry.get('action_type', 'unknown')
            summary['by_action_type'][action_type] = summary['by_action_type'].get(action_type, 0) + 1
            
            # Count errors
            if entry.get('error'):
                summary['errors'] += 1
        
        # Calculate success rate
        if summary['total_actions'] > 0:
            summary['success_rate'] = (
                summary['by_status'].get('success', 0) / summary['total_actions'] * 100
            )
        
        return summary
    
    def search_logs(
        self,
        query: str,
        days: int = 7,
        action_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> list:
        """
        Search audit logs.
        
        Args:
            query: Search query (text)
            days: Number of days to search
            action_type: Filter by action type
            status: Filter by status
        
        Returns:
            List of matching log entries
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        matches = []
        
        for log_file in self.audit_folder.glob('audit_*.jsonl'):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        entry = json.loads(line)
                        entry_date = datetime.fromisoformat(entry['timestamp'])
                        
                        if entry_date < cutoff_date:
                            continue
                        
                        # Filter by action type
                        if action_type and entry.get('action_type') != action_type:
                            continue
                        
                        # Filter by status
                        if status and entry.get('status') != status:
                            continue
                        
                        # Search query
                        if query:
                            entry_text = json.dumps(entry).lower()
                            if query.lower() not in entry_text:
                                continue
                        
                        matches.append(entry)
            except Exception as e:
                continue
        
        return matches
    
    def get_uptime(self) -> str:
        """Get human-readable uptime string."""
        delta = datetime.now() - self.start_time
        total_seconds = int(delta.total_seconds())
        
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def print_summary(self, days: int = 7):
        """Print audit summary to console."""
        summary = self.get_audit_summary(days)
        
        print("\n" + "="*70)
        print("📊 AUDIT LOG SUMMARY")
        print("="*70)
        print(f"Period: Last {days} days")
        print(f"Total Actions: {summary['total_actions']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Errors: {summary['errors']}")
        
        print(f"\n📋 BY STATUS")
        for status, count in summary['by_status'].items():
            print(f"   {status}: {count}")
        
        print(f"\n👥 BY ACTOR")
        for actor, count in summary['by_actor'].items():
            print(f"   {actor}: {count}")
        
        print(f"\n🔧 BY ACTION TYPE")
        sorted_types = sorted(summary['by_action_type'].items(), key=lambda x: x[1], reverse=True)
        for action_type, count in sorted_types[:10]:  # Top 10
            print(f"   {action_type}: {count}")
        
        print(f"\n⏱️  Logger Uptime: {self.get_uptime()}")
        print("="*70)


# Global audit logger instance
_audit_logger = None

def get_audit_logger() -> AuditLogger:
    """Get or create global audit logger."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger


# Convenience functions
def log_action(*args, **kwargs):
    """Log an action using global logger."""
    get_audit_logger().log_action(*args, **kwargs)

def log_watcher_action(*args, **kwargs):
    """Log watcher action using global logger."""
    get_audit_logger().log_watcher_action(*args, **kwargs)

def log_mcp_action(*args, **kwargs):
    """Log MCP action using global logger."""
    get_audit_logger().log_mcp_action(*args, **kwargs)

def log_approval(*args, **kwargs):
    """Log approval using global logger."""
    get_audit_logger().log_approval(*args, **kwargs)

def get_audit_summary(days: int = 7):
    """Get audit summary using global logger."""
    return get_audit_logger().get_audit_summary(days)


if __name__ == "__main__":
    # Test audit logger
    logger = AuditLogger()
    
    print("Testing Audit Logger...")
    print("="*70)
    
    # Test various log types
    logger.log_action(
        action_type='email_send',
        parameters={'to': 'user@example.com', 'subject': 'Test'},
        status='success',
        actor='ai_employee',
        target='email_001'
    )
    
    logger.log_watcher_action(
        watcher_name='gmail',
        action='create_action_file',
        item_id='EMAIL_123',
        status='success'
    )
    
    logger.log_mcp_action(
        mcp_server='email',
        tool_name='send_email',
        parameters={'to': 'test@example.com'},
        status='success',
        result={'message_id': 'abc123'}
    )
    
    logger.log_approval(
        action_type='email_send',
        item_id='EMAIL_123',
        decision='approved',
        decided_by='human'
    )
    
    # Print summary
    logger.print_summary(days=1)
    
    print("\n✅ Audit Logger test complete!")
    print(f"📁 Logs saved to: {logger.audit_folder}")
