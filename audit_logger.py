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
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from logging.handlers import TimedRotatingFileHandler
import re


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
        
        # Log format - JSON structured
        log_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
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
