"""
Error Recovery & Graceful Degradation System for AI Employee Vault

Gold Tier Requirement #8 - Error recovery and graceful degradation

Features:
- Circuit Breaker pattern
- Dead Letter Queue for failed items
- Automatic retry with exponential backoff
- Health check system
- Fallback mechanisms
- Error classification

Usage:
    from error_recovery import CircuitBreaker, DeadLetterQueue
    
    cb = CircuitBreaker('email_service')
    if cb.can_execute():
        try:
            result = send_email()
            cb.record_success()
        except Exception as e:
            cb.record_failure(e)
"""

import time
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable, List
from functools import wraps
import traceback
from enum import Enum


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, stop executing
    HALF_OPEN = "half_open"  # Testing if service recovered


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"  # Can retry
    MEDIUM = "medium"  # Should retry with backoff
    HIGH = "high"  # Manual intervention may be needed
    CRITICAL = "critical"  # Stop all operations


class CircuitBreaker:
    """
    Circuit Breaker pattern implementation.
    
    Prevents cascading failures by stopping execution
    when a service is failing repeatedly.
    """
    
    def __init__(
        self,
        service_name: str,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout: int = 60
    ):
        """
        Initialize circuit breaker.
        
        Args:
            service_name: Name of the service
            failure_threshold: Failures before opening circuit
            success_threshold: Successes before closing circuit
            timeout: Seconds to wait before trying again (open → half-open)
        """
        self.service_name = service_name
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout = timeout
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.last_success_time: Optional[datetime] = None
        
        self.logger = logging.getLogger(f'circuit_breaker.{service_name}')
    
    def can_execute(self) -> bool:
        """Check if execution is allowed."""
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            # Check if timeout has passed
            if self.last_failure_time:
                elapsed = (datetime.now() - self.last_failure_time).total_seconds()
                if elapsed >= self.timeout:
                    self.state = CircuitState.HALF_OPEN
                    self.logger.info(f"Circuit {self.service_name} moved to HALF_OPEN")
                    return True
            return False
        
        if self.state == CircuitState.HALF_OPEN:
            return True
        
        return False
    
    def record_success(self):
        """Record a successful execution."""
        self.success_count += 1
        self.last_success_time = datetime.now()
        
        if self.state == CircuitState.HALF_OPEN:
            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                self.logger.info(f"Circuit {self.service_name} CLOSED after recovery")
        
        self.logger.debug(f"Success recorded for {self.service_name} (count: {self.success_count})")
    
    def record_failure(self, error: Optional[Exception] = None):
        """Record a failed execution."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.state == CircuitState.CLOSED:
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                self.logger.warning(
                    f"Circuit {self.service_name} OPENED after {self.failure_count} failures"
                )
        
        elif self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            self.logger.warning(
                f"Circuit {self.service_name} re-OPENED during half-open test"
            )
        
        error_msg = str(error) if error else "Unknown error"
        self.logger.error(f"Failure recorded for {self.service_name}: {error_msg}")
    
    def get_state(self) -> Dict[str, Any]:
        """Get circuit breaker state."""
        return {
            'service': self.service_name,
            'state': self.state.value,
            'failure_count': self.failure_count,
            'success_count': self.success_count,
            'last_failure': self.last_failure_time.isoformat() if self.last_failure_time else None,
            'last_success': self.last_success_time.isoformat() if self.last_success_time else None
        }
    
    def reset(self):
        """Reset circuit breaker to initial state."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.logger.info(f"Circuit {self.service_name} manually reset")


class DeadLetterQueue:
    """
    Dead Letter Queue for failed items.
    
    Stores items that failed processing after all retries
    for later analysis and manual processing.
    """
    
    def __init__(self, vault_path: Optional[Path] = None):
        """
        Initialize dead letter queue.
        
        Args:
            vault_path: Path to vault root
        """
        self.vault_path = vault_path or Path(__file__).parent
        self.dlq_folder = self.vault_path / 'Dead_Letter_Queue'
        self.dlq_folder.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger('dead_letter_queue')
        self.items_added = 0
    
    def add(
        self,
        item_id: str,
        item_type: str,
        error: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        retry_count: int = 0,
        original_data: Optional[Dict] = None
    ):
        """
        Add item to dead letter queue.
        
        Args:
            item_id: Unique item identifier
            item_type: Type of item (email, whatsapp, invoice, etc.)
            error: Error message
            severity: Error severity
            retry_count: Number of retry attempts
            original_data: Original item data
        """
        dlq_entry = {
            'id': item_id,
            'type': item_type,
            'error': error,
            'severity': severity.value,
            'retry_count': retry_count,
            'added_at': datetime.now().isoformat(),
            'status': 'pending',
            'original_data': original_data or {}
        }
        
        # Save to file
        filename = f"DLQ_{item_type}_{item_id}_{datetime.now():%Y%m%d_%H%M%S}.json"
        filepath = self.dlq_folder / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(dlq_entry, f, indent=2, ensure_ascii=False)
        
        self.items_added += 1
        self.logger.warning(
            f"Item {item_id} ({item_type}) added to DLQ: {error}"
        )
        
        return filepath
    
    def get_pending_items(self) -> List[Dict]:
        """Get all pending items in DLQ."""
        pending = []
        
        for file in self.dlq_folder.glob('DLQ_*.json'):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    entry = json.load(f)
                    if entry.get('status') == 'pending':
                        pending.append(entry)
            except Exception as e:
                self.logger.error(f"Error reading DLQ file {file}: {e}")
        
        return pending
    
    def mark_processed(self, item_id: str, status: str = 'processed'):
        """Mark item as processed."""
        for file in self.dlq_folder.glob(f'DLQ_*_{item_id}_*.json'):
            try:
                with open(file, 'r+', encoding='utf-8') as f:
                    entry = json.load(f)
                    entry['status'] = status
                    entry['processed_at'] = datetime.now().isoformat()
                    f.seek(0)
                    json.dump(entry, f, indent=2, ensure_ascii=False)
                    f.truncate()
                
                self.logger.info(f"DLQ item {item_id} marked as {status}")
            except Exception as e:
                self.logger.error(f"Error updating DLQ item {item_id}: {e}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get DLQ summary."""
        pending = self.get_pending_items()
        
        by_type = {}
        by_severity = {}
        
        for item in pending:
            item_type = item.get('type', 'unknown')
            severity = item.get('severity', 'unknown')
            
            by_type[item_type] = by_type.get(item_type, 0) + 1
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        return {
            'total_pending': len(pending),
            'by_type': by_type,
            'by_severity': by_severity,
            'oldest_item': min(
                [item.get('added_at', '') for item in pending],
                default=None
            )
        }


class RetryHandler:
    """
    Retry handler with exponential backoff.
    """
    
    @staticmethod
    def with_retry(
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential: bool = True,
        retryable_exceptions: tuple = (Exception,)
    ):
        """
        Decorator for retry logic.
        
        Args:
            max_retries: Maximum retry attempts
            base_delay: Base delay between retries
            max_delay: Maximum delay cap
            exponential: Use exponential backoff
            retryable_exceptions: Exceptions that trigger retry
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                
                for attempt in range(max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    
                    except Exception as e:
                        last_exception = e
                        
                        # Check if exception is retryable
                        if not isinstance(e, retryable_exceptions):
                            raise
                        
                        # Don't retry if exhausted
                        if attempt >= max_retries:
                            raise
                        
                        # Calculate delay
                        if exponential:
                            delay = min(base_delay * (2 ** attempt), max_delay)
                        else:
                            delay = base_delay
                        
                        logging.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed: {e}. "
                            f"Retrying in {delay:.1f}s"
                        )
                        
                        time.sleep(delay)
                
                if last_exception:
                    raise last_exception
            
            return wrapper
        return decorator


class HealthCheck:
    """
    Health check system for monitoring components.
    """
    
    def __init__(self):
        """Initialize health check."""
        self.components: Dict[str, Callable] = {}
        self.logger = logging.getLogger('health_check')
    
    def register(self, name: str, check_func: Callable):
        """Register a component health check."""
        self.components[name] = check_func
        self.logger.info(f"Health check registered for {name}")
    
    def check_all(self) -> Dict[str, Any]:
        """Check health of all components."""
        results = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'components': {}
        }
        
        for name, check_func in self.components.items():
            try:
                status = check_func()
                results['components'][name] = {
                    'status': 'healthy' if status else 'unhealthy',
                    'checked_at': datetime.now().isoformat()
                }
                
                if not status:
                    results['overall_status'] = 'degraded'
            
            except Exception as e:
                results['components'][name] = {
                    'status': 'error',
                    'error': str(e),
                    'checked_at': datetime.now().isoformat()
                }
                results['overall_status'] = 'unhealthy'
        
        return results
    
    def print_status(self):
        """Print health status to console."""
        results = self.check_all()
        
        print("\n" + "="*70)
        print("🏥 SYSTEM HEALTH CHECK")
        print("="*70)
        print(f"Timestamp: {results['timestamp']}")
        print(f"Overall Status: {results['overall_status'].upper()}")
        
        print(f"\n📊 COMPONENTS")
        for name, component in results['components'].items():
            status = component['status']
            emoji = "✅" if status == 'healthy' else "❌" if status == 'error' else "⚠️"
            print(f"   {emoji} {name}: {status}")
        
        print("="*70)


# Global instances
_circuit_breakers: Dict[str, CircuitBreaker] = {}
_dlq: Optional[DeadLetterQueue] = None
_health_check: Optional[HealthCheck] = None


def get_circuit_breaker(service_name: str) -> CircuitBreaker:
    """Get or create circuit breaker for service."""
    if service_name not in _circuit_breakers:
        _circuit_breakers[service_name] = CircuitBreaker(service_name)
    return _circuit_breakers[service_name]


def get_dlq(vault_path: Optional[Path] = None) -> DeadLetterQueue:
    """Get or create dead letter queue."""
    global _dlq
    if _dlq is None:
        _dlq = DeadLetterQueue(vault_path)
    return _dlq


def get_health_check() -> HealthCheck:
    """Get or create health check."""
    global _health_check
    if _health_check is None:
        _health_check = HealthCheck()
    return _health_check


# Convenience functions
def record_success(service: str):
    """Record success for service."""
    get_circuit_breaker(service).record_success()

def record_failure(service: str, error: Exception):
    """Record failure for service."""
    get_circuit_breaker(service).record_failure(error)

def can_execute(service: str) -> bool:
    """Check if service can execute."""
    return get_circuit_breaker(service).can_execute()

def add_to_dlq(item_id: str, item_type: str, error: str, **kwargs):
    """Add item to DLQ."""
    get_dlq().add(item_id, item_type, error, **kwargs)


if __name__ == "__main__":
    # Test error recovery system
    logging.basicConfig(level=logging.INFO)
    
    print("="*70)
    print("🛡️  ERROR RECOVERY SYSTEM TEST")
    print("="*70)
    
    # Test Circuit Breaker
    print("\n📊 Testing Circuit Breaker...")
    cb = CircuitBreaker('test_service', failure_threshold=3, timeout=5)
    
    print(f"Initial state: {cb.get_state()}")
    
    # Simulate failures
    for i in range(3):
        cb.record_failure(Exception(f"Test error {i}"))
        print(f"After failure {i+1}: {cb.state.value}")
    
    print(f"Can execute? {cb.can_execute()}")
    
    # Simulate timeout
    print("Waiting 5 seconds for timeout...")
    time.sleep(5)
    
    print(f"After timeout: {cb.state.value}")
    print(f"Can execute? {cb.can_execute()}")
    
    # Test Dead Letter Queue
    print("\n📥 Testing Dead Letter Queue...")
    dlq = DeadLetterQueue()
    
    dlq.add(
        item_id='TEST_001',
        item_type='email',
        error='Connection timeout',
        severity=ErrorSeverity.MEDIUM,
        retry_count=3
    )
    
    dlq.add(
        item_id='TEST_002',
        item_type='whatsapp',
        error='Authentication failed',
        severity=ErrorSeverity.HIGH,
        retry_count=5
    )
    
    summary = dlq.get_summary()
    print(f"DLQ Summary: {summary}")
    
    # Test Health Check
    print("\n🏥 Testing Health Check...")
    hc = HealthCheck()
    
    hc.register('email_service', lambda: True)
    hc.register('whatsapp_service', lambda: True)
    hc.register('odoo_service', lambda: False)  # Simulate unhealthy
    
    hc.print_status()
    
    print("\n" + "="*70)
    print("✅ ERROR RECOVERY SYSTEM TEST COMPLETE")
    print("="*70)
