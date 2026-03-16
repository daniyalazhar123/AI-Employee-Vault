# 🛠️ Watchers Development Guide

> **Professional-grade watcher scripts with robust error handling, logging, and retry logic**

---

## 📋 Overview

All watcher scripts now inherit from `base_watcher.py` which provides:

| Feature | Description |
|---------|-------------|
| 📝 **Logging** | Console + file with daily rotation + JSON format |
| 🔄 **Retry Logic** | Exponential backoff (max 3-5 retries) |
| ⚠️ **Error Handling** | Specific exceptions, graceful failures |
| 📊 **Performance** | Processed ID tracking, batch processing |
| 🔒 **Security** | Protected credentials, session management |

---

## 🏗️ Architecture

```
watchers/
├── base_watcher.py          # Common base class (logging, retry, errors)
├── gmail_watcher.py         # Gmail API monitoring
├── whatsapp_watcher.py      # WhatsApp Web automation
├── office_watcher.py        # File system monitoring
├── social_watcher.py        # Social draft processing
└── odoo_lead_watcher.py     # Odoo CRM integration
```

---

## 📝 Logging System

### Log Files Location

```
Logs/
├── gmail_20260316.log           # Human-readable log
├── gmail_20260316.jsonl         # JSON-formatted log (easy parsing)
├── whatsapp_20260316.log
├── whatsapp_20260316.jsonl
└── ...
```

### Log Format

**Console & File (.log):**
```
2026-03-16 10:30:45 - gmail - INFO - Gmail authentication successful
2026-03-16 10:30:47 - gmail - WARNING - Token refresh failed, will re-authenticate
2026-03-16 10:30:50 - gmail - ERROR - Failed to fetch emails: HttpError 403
```

**JSON Logs (.jsonl):**
```json
{"timestamp": "2026-03-16T10:30:45", "level": "INFO", "watcher": "gmail", "message": "Authentication successful"}
{"timestamp": "2026-03-16T10:30:50", "level": "ERROR", "watcher": "gmail", "message": "Failed to fetch emails", "error": "HttpError 403"}
```

### Usage Example

```python
from base_watcher import BaseWatcher

class MyWatcher(BaseWatcher):
    def __init__(self):
        super().__init__('mywatcher')
    
    def do_something(self):
        self.log_info("Starting operation")
        
        try:
            result = self.risky_operation()
            self.log_info("Operation successful", result=result)
        except Exception as e:
            self.log_error("Operation failed", exc=e)
            raise
```

---

## 🔄 Retry Logic

### Exponential Backoff

```python
# Default: 3 retries, exponential backoff
# Attempt 1: Fail → wait 1s
# Attempt 2: Fail → wait 2s
# Attempt 3: Fail → wait 4s
# Attempt 4: Fail → raise exception

result = self.with_retry(
    func=my_function,
    max_retries=3,
    base_delay=1.0,
    max_delay=60.0,
    exponential=True
)
```

### Retryable Exceptions

```python
# Only retry on specific exceptions
result = self.with_retry(
    func=api_call,
    max_retries=3,
    retryable_exceptions=(HttpError, TimeoutError)
)

# Non-retryable exceptions (e.g., ConfigurationError) will raise immediately
```

---

## ⚠️ Error Handling

### Exception Hierarchy

```python
WatcherError              # Base exception
├── ConfigurationError    # Invalid/missing config
├── ConnectionError       # External service connection failed
└── ProcessingError       # Item processing failed
```

### Best Practices

```python
# ❌ BAD: Generic exception
try:
    do_something()
except Exception as e:
    print(f"Error: {e}")

# ✅ GOOD: Specific exceptions with logging
try:
    do_something()
except ConfigurationError as e:
    self.log_error(f"Configuration issue: {e}", exc=e)
    raise
except ConnectionError as e:
    self.log_error(f"Connection failed: {e}", exc=e)
    # Attempt reconnection
    self.reconnect()
except ProcessingError as e:
    self.log_warning(f"Processing failed, skipping: {e}")
    # Continue to next item
```

---

## 📊 Performance Tracking

### Processed IDs

```python
# Load previously processed IDs
self.processed_ids = self.load_processed_ids('processed_emails.txt')

# Add new processed ID
self.processed_ids.add(email_id)

# Save to file (auto-prunes to last 10000)
self.save_processed_ids('processed_emails.txt', self.processed_ids)
```

### Uptime Monitoring

```python
# Get human-readable uptime
uptime = self.get_uptime()
self.log_info(f"Final uptime: {uptime}")  # "02:15:30"
```

---

## 🔧 Configuration

### Using .env File

1. Copy `config/.env.example` to `config/.env`
2. Fill in your values
3. Load in script:

```python
import os
from dotenv import load_dotenv

load_dotenv('config/.env')

GMAIL_CHECK_INTERVAL = int(os.getenv('GMAIL_CHECK_INTERVAL', 120))
ODOO_URL = os.getenv('ODOO_URL', 'http://localhost:8069')
```

---

## 🧪 Testing Your Watcher

### Unit Test Example

```python
import unittest
from watchers.gmail_watcher import GmailWatcher

class TestGmailWatcher(unittest.TestCase):
    def setUp(self):
        self.watcher = GmailWatcher()
    
    def test_authentication(self):
        result = self.watcher.authenticate()
        self.assertTrue(result)
    
    def test_fetch_emails(self):
        emails = self.watcher.fetch_unread_emails()
        self.assertIsInstance(emails, list)
    
    def test_retry_logic(self):
        call_count = 0
        
        def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary error")
            return "success"
        
        result = self.watcher.with_retry(failing_function, max_retries=3)
        self.assertEqual(result, "success")
        self.assertEqual(call_count, 3)

if __name__ == '__main__':
    unittest.main()
```

---

## 📋 Checklist for New Watchers

When creating a new watcher:

- [ ] Inherit from `BaseWatcher`
- [ ] Call `super().__init__('watcher_name')`
- [ ] Implement `run()` method
- [ ] Use `self.log_info()`, `self.log_warning()`, `self.log_error()`
- [ ] Wrap risky operations in `self.with_retry()`
- [ ] Track processed items to avoid duplicates
- [ ] Handle `KeyboardInterrupt` gracefully
- [ ] Save state on shutdown
- [ ] Add JSON logging for important events
- [ ] Document configuration options

---

## 🐛 Troubleshooting

### Logs Not Appearing

```python
# Check Logs folder exists
self.logs_folder.mkdir(exist_ok=True)

# Verify logger has handlers
print(self.logger.handlers)  # Should show console + file handlers
```

### Retry Not Working

```python
# Ensure you're using with_retry correctly
result = self.with_retry(my_func)  # ✅ Pass function, don't call it

# NOT this:
result = self.with_retry(my_func())  # ❌ This calls function immediately
```

### Processed IDs Not Saving

```python
# Ensure data folder exists
(self.vault_path / 'data').mkdir(exist_ok=True)

# Call save_processed_ids after adding new IDs
self.save_processed_ids('processed_items.txt', self.processed_ids)
```

---

## 📚 Additional Resources

- [Python Logging Cookbook](https://docs.python.org/3/howto/logging-cookbook.html)
- [Exponential Backoff Explained](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)
- [Watchdog Documentation](https://pypi.org/project/watchdog/)
- [Playwright Python API](https://playwright.dev/python/)

---

*Last updated: March 16, 2026*  
*Version: 2.0 (Refactored with base_watcher)*
