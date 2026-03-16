"""
WhatsApp Watcher for AI Employee Vault

Monitors WhatsApp Web for messages containing specific keywords.
Features:
- Persistent browser session (QR scan once)
- Robust error handling with retry logic
- JSON logging to /Logs/ folder
- Graceful failure handling
"""

import json
import re
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout, Page, BrowserContext

from base_watcher import BaseWatcher, ConnectionError


# Configuration
KEYWORDS = ['urgent', 'invoice', 'payment', 'help', 'price', 'order']
CHECK_INTERVAL = 30  # seconds
MAX_RETRIES = 3
SESSION_TIMEOUT = 30  # seconds to wait for QR scan on first run


class WhatsAppWatcher(BaseWatcher):
    """WhatsApp Web monitoring watcher."""
    
    def __init__(self, vault_path: Optional[Path] = None):
        super().__init__('whatsapp', vault_path)
        
        self.session_folder = self.vault_path / 'sessions' / 'whatsapp_session'
        self.processed_file = self.vault_path / 'data' / 'processed_whatsapp.txt'
        self.needs_action_folder = self.vault_path / 'Needs_Action'
        self.pending_approval_folder = self.vault_path / 'Pending_Approval'
        
        self.processed_messages: Set[str] = set()
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        # Ensure folders exist
        self.session_folder.mkdir(parents=True, exist_ok=True)
        self.needs_action_folder.mkdir(exist_ok=True)
        self.pending_approval_folder.mkdir(exist_ok=True)
    
    def load_storage_state(self) -> Optional[dict]:
        """Load saved session storage state."""
        storage_file = self.session_folder / 'storage_state.json'
        
        if storage_file.exists():
            try:
                with open(storage_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                self.log_info(f"Loaded session from {storage_file}")
                return state
            except (json.JSONDecodeError, IOError) as e:
                self.log_warning(f"Failed to load session: {e}")
                return None
        return None
    
    def save_storage_state(self):
        """Save session storage state."""
        if not self.context:
            return
        
        storage_file = self.session_folder / 'storage_state.json'
        
        try:
            self.context.storage_state(path=str(storage_file))
            self.log_info(f"Session saved to {storage_file}")
        except Exception as e:
            self.log_error(f"Failed to save session: {e}", exc=e)
    
    def is_authenticated(self) -> bool:
        """Check if WhatsApp Web is authenticated."""
        if not self.page:
            return False
        
        try:
            # Multiple selectors for authenticated state
            auth_selectors = [
                '#pane-side',
                'div[aria-label="Chat list"]',
                'div[data-testid="chat-list"]'
            ]
            
            for selector in auth_selectors:
                if self.page.query_selector(selector):
                    return True
            
            return False
            
        except Exception as e:
            self.log_warning(f"Auth check failed: {e}")
            return False
    
    def setup_browser(self) -> bool:
        """
        Launch browser and navigate to WhatsApp Web.
        
        Returns:
            True if setup successful
        """
        try:
            self.log_info("Launching browser...")
            
            storage_state = self.load_storage_state()
            
            with sync_playwright() as p:
                # Launch persistent context
                self.context = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_folder),
                    headless=False,  # Visible for QR scanning
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--window-size=1280,800'
                    ],
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                
                self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
                
                self.log_info("Navigating to WhatsApp Web...")
                self.page.goto('https://web.whatsapp.com', wait_until='networkidle')
                
                # Wait for QR scan if needed
                if not self.is_authenticated():
                    self.log_info("QR code detected - waiting for scan...")
                    self.log_info(f"Please scan QR code within {SESSION_TIMEOUT} seconds")
                    
                    for i in range(SESSION_TIMEOUT, 0, -1):
                        print(f"   Time remaining: {i} seconds", end='\r')
                        time.sleep(1)
                    
                    print()  # Newline after countdown
                    
                    if not self.is_authenticated():
                        self.log_warning("QR code not scanned in time")
                        return False
                
                self.log_info("✅ WhatsApp Web authenticated successfully")
                return True
                
        except PlaywrightTimeout as e:
            self.log_error(f"Browser timeout: {e}", exc=e)
            return False
        except Exception as e:
            self.log_error(f"Browser setup failed: {e}", exc=e)
            return False
    
    def check_messages(self) -> List[Dict]:
        """
        Check for unread messages.
        
        Returns:
            List of new message dictionaries
        """
        if not self.page:
            return []
        
        try:
            # Wait for page load
            self.page.wait_for_load_state('networkidle', timeout=30000)
            time.sleep(2)
            
            # Find chat list
            chat_list_selectors = [
                '#pane-side',
                'div[aria-label="Chat list"]',
                'div[data-testid="chat-list"]'
            ]
            
            chat_list = None
            for selector in chat_list_selectors:
                chat_list = self.page.query_selector(selector)
                if chat_list:
                    break
            
            if not chat_list:
                self.log_warning("Chat list not found")
                return []
            
            # Get chat rows
            chat_rows = self.page.query_selector_all(f'{selector} > div[role="row"]')
            
            if not chat_rows:
                chat_rows = self.page.query_selector_all(f'{selector} > div')
            
            new_messages = []
            
            # Unread badge selectors
            unread_selectors = [
                'span[data-testid="icon-unread-count"]',
                'span[data-testid="unread-count"]',
                'div[aria-label*="unread"]'
            ]
            
            for row in chat_rows[:25]:  # Top 25 chats
                try:
                    # Check for unread
                    is_unread = False
                    unread_count = 0
                    
                    for unread_sel in unread_selectors:
                        unread_elem = row.query_selector(unread_sel)
                        if unread_elem:
                            is_unread = True
                            try:
                                count_text = unread_elem.inner_text()
                                unread_count = int(count_text) if count_text.isdigit() else 1
                            except:
                                unread_count = 1
                            break
                    
                    if not is_unread:
                        continue
                    
                    # Extract contact name
                    contact = "Unknown"
                    contact_elem = row.query_selector('span[title]')
                    if contact_elem:
                        contact = contact_elem.get_attribute('title') or contact_elem.inner_text()
                    
                    # Extract message preview
                    message = "No preview"
                    message_elem = row.query_selector('span[dir="auto"]:last-of-type')
                    if message_elem:
                        message = message_elem.inner_text()
                    
                    # Create unique ID
                    message_id = f"{contact}:{message[:50]}:{datetime.now().strftime('%H%M')}"
                    
                    # Skip if processed
                    if message_id in self.processed_messages:
                        continue
                    
                    # Check for keywords (optional - currently flagging ALL unread)
                    matched_keyword = 'UNREAD'
                    message_lower = message.lower()
                    for keyword in KEYWORDS:
                        if keyword in message_lower:
                            matched_keyword = keyword
                            break
                    
                    new_messages.append({
                        'contact': contact,
                        'message': message,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'keyword': matched_keyword,
                        'unread_count': unread_count,
                        'message_id': message_id
                    })
                    
                except Exception as e:
                    self.log_warning(f"Error processing chat row: {e}")
                    continue
            
            if new_messages:
                self.log_info(f"Found {len(new_messages)} unread message(s)")
            
            return new_messages
            
        except PlaywrightTimeout as e:
            self.log_error(f"Timeout checking messages: {e}", exc=e)
            return []
        except Exception as e:
            self.log_error(f"Error checking messages: {e}", exc=e)
            return []
    
    def create_action_file(self, msg: Dict) -> Optional[Path]:
        """Create action file for WhatsApp message."""
        try:
            safe_contact = re.sub(r'[^\w\s-]', '', msg['contact'][:30]).strip().replace(' ', '_')
            safe_time = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"WHATSAPP_{safe_contact}_{safe_time}.md"
            filepath = self.needs_action_folder / filename
            
            preview = msg['message'][:200] + '...' if len(msg['message']) > 200 else msg['message']
            
            content = f"""---
type: whatsapp_message
from: {msg['contact']}
timestamp: {msg['timestamp']}
matched_keyword: {msg['keyword']}
unread_count: {msg['unread_count']}
created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
status: pending
---

## Message Preview
{preview}

## Full Message
{msg['message']}

## Suggested Actions
- [ ] Read and understand the request
- [ ] Draft appropriate response
- [ ] Take action if needed
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
        """Trigger Qwen CLI to process message."""
        try:
            prompt = (
                f"Read the WhatsApp message action file: {action_file.name} in Needs_Action folder. "
                f"Draft a professional response following Company_Handbook rules. "
                f"Save the reply draft in Pending_Approval folder as REPLY_{action_file.stem}.md"
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
            
            self.log_info("Qwen processing triggered")
            
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
    
    def run(self):
        """Main watcher loop."""
        self.print_status_header("💬 WHATSAPP WATCHER STARTED")
        self.log_info(f"Keywords: {', '.join(KEYWORDS)}")
        self.log_info(f"Check interval: {CHECK_INTERVAL} seconds")
        
        # Load processed messages
        self.processed_messages = self.load_processed_ids('processed_whatsapp.txt')
        
        # Setup browser
        if not self.setup_browser():
            self.log_error("Browser setup failed. Exiting.")
            return
        
        self.log_info("👀 Monitoring for messages... Press Ctrl+C to stop\n")
        
        try:
            while True:
                cycle_start = datetime.now()
                
                try:
                    # Check for messages
                    new_messages = self.check_messages()
                    
                    if new_messages:
                        for msg in new_messages:
                            self.log_info(f"📩 {msg['contact']}: {msg['message'][:50]}...")
                            
                            # Create action file
                            action_file = self.create_action_file(msg)
                            if action_file:
                                self.trigger_qwen(action_file)
                            
                            # Mark as processed
                            self.processed_messages.add(msg['message_id'])
                        
                        # Save processed IDs
                        self.save_processed_ids('processed_whatsapp.txt', self.processed_messages)
                    
                    else:
                        self.log_info(f"⏳ No new messages - {datetime.now().strftime('%H:%M:%S')}")
                    
                    # Save session periodically
                    self.save_storage_state()
                
                except Exception as e:
                    self.log_error(f"Error in check cycle: {e}", exc=e)
                
                # Sleep
                elapsed = (datetime.now() - cycle_start).total_seconds()
                sleep_time = max(0, CHECK_INTERVAL - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
        
        except KeyboardInterrupt:
            self.log_info("\n\n⏹️  Stopping WhatsApp Watcher...")
            self.save_storage_state()
            self.save_processed_ids('processed_whatsapp.txt', self.processed_messages)
            self.log_info(f"Final uptime: {self.get_uptime()}")
            self.log_info("✅ Watcher stopped successfully")
        
        finally:
            if self.context:
                self.context.close()


def main():
    """Entry point."""
    watcher = WhatsAppWatcher()
    watcher.run()


if __name__ == '__main__':
    main()
