"""
WhatsApp Watcher for AI Employee Vault

Monitors WhatsApp Web for messages containing specific keywords and creates action items.
Uses Playwright with persistent browser session to remember login.
"""

import os
import time
import re
from datetime import datetime
from pathlib import Path
import subprocess
import json

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


# Paths
VAULT_PATH = Path(__file__).parent
NEEDS_ACTION = VAULT_PATH / "Needs_Action"
SESSION_FOLDER = VAULT_PATH / "whatsapp_session"

# Keywords to monitor (case-insensitive)
KEYWORDS = ['urgent', 'invoice', 'payment', 'help', 'price', 'order']

# Check interval in seconds
CHECK_INTERVAL = 30


def ensure_folders():
    """Ensure required folders exist."""
    NEEDS_ACTION.mkdir(exist_ok=True)
    SESSION_FOLDER.mkdir(exist_ok=True)


def get_storage_state():
    """Load or initialize storage state for session persistence."""
    storage_file = SESSION_FOLDER / "storage_state.json"
    
    if storage_file.exists():
        try:
            with open(storage_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    return None


def save_storage_state(context):
    """Save storage state for session persistence."""
    storage_file = SESSION_FOLDER / "storage_state.json"
    try:
        context.storage_state(path=str(storage_file))
        print(f"💾 Session saved to: {storage_file}")
    except Exception as e:
        print(f"⚠️  Could not save session: {e}")


def create_action_file(contact: str, message: str, timestamp: str, matched_keyword: str, unread_count: int = 1):
    """Create an action file in Needs_Action folder."""

    # Safe filename
    safe_contact = re.sub(r'[^\w\s-]', '', contact[:30]).strip().replace(' ', '_')
    safe_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"WHATSAPP_{safe_contact}_{safe_time}.md"
    filepath = NEEDS_ACTION / filename

    # Truncate message for preview
    preview = message[:200] + "..." if len(message) > 200 else message

    content = f"""---
type: whatsapp_message
from: {contact}
timestamp: {timestamp}
matched_keyword: {matched_keyword}
unread_count: {unread_count}
created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
status: pending
---

## Message Preview
{preview}

## Full Message
{message}

## Suggested Actions
- [ ] Read and understand the request
- [ ] Draft appropriate response
- [ ] Take action if needed
- [ ] Archive after processing
"""

    filepath.write_text(content, encoding='utf-8')
    print(f"📝 Action file created: {filename}")

    return filepath


def trigger_qwen(action_file: Path):
    """Trigger Qwen CLI to process the action file."""
    
    try:
        prompt = f"Read the WhatsApp message action file: {action_file.name} in Needs_Action folder. Draft a professional response following Company_Handbook rules. Save the reply draft in Pending_Approval folder as REPLY_{action_file.stem}.md"
        
        result = subprocess.run(
            ["qwen", "-y", prompt],
            check=False,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd=str(VAULT_PATH),
            shell=True,
            timeout=120
        )
        
        print("🤖 Qwen processing triggered")
        
        if result.stdout:
            print(f"   Output: {result.stdout.strip()[:200]}")
        if result.stderr:
            print(f"   Errors: {result.stderr.strip()[:200]}")
            
    except subprocess.TimeoutExpired:
        print("⚠️  Qwen timeout – response may be long")
    except FileNotFoundError:
        print("⚠️  Qwen CLI not found – check installation")
    except Exception as e:
        print(f"⚠️  Qwen error: {e}")


def check_messages(page):
    """Check for unread messages - flags ALL unread chats."""

    processed_messages = set()
    processed_file = VAULT_PATH / "processed_whatsapp.txt"

    # Load previously processed messages
    if processed_file.exists():
        processed_messages = set(processed_file.read_text(encoding='utf-8').splitlines())

    try:
        # Wait for page to fully load
        print("   ⏳ Waiting for page to load...")
        page.wait_for_load_state('networkidle', timeout=30000)
        time.sleep(2)  # Extra wait for dynamic content

        # Try multiple chat list selectors in order
        chat_list_selectors = [
            '#pane-side',
            'div[aria-label="Chat list"]',
            'div[data-testid="chat-list"]',
            '._aigv'
        ]

        chat_list = None
        selected_selector = None

        print("   ⏳ Waiting for chat list...")
        for selector in chat_list_selectors:
            try:
                chat_list = page.wait_for_selector(selector, timeout=10000, state='visible')
                if chat_list:
                    selected_selector = selector
                    print(f"   ✅ Chat list found using: {selector}")
                    break
            except:
                print(f"   ⚠️  Selector failed: {selector}")
                continue

        if not chat_list:
            # Save screenshot for debugging
            screenshot_path = VAULT_PATH / "whatsapp_debug.png"
            page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"   📸 Screenshot saved to: {screenshot_path}")
            print("   ⚠️  Could not find chat list with any selector")
            return [], processed_messages

        time.sleep(1)  # Allow chat list to render

        # Get all chat rows - try multiple selectors
        row_selectors = ['div[role="row"]', 'div[data-testid="chat-item"]', '._aigv > div', 'div[data-testid="chat-item"] > div']
        chat_rows = []

        for row_selector in row_selectors:
            try:
                chat_rows = page.query_selector_all(f'{selected_selector} > {row_selector}')
                if chat_rows:
                    print(f"   ✅ Found {len(chat_rows)} chat rows using: > {row_selector}")
                    break
            except:
                continue

        if not chat_rows:
            # Fallback: try to find any clickable chat elements
            chat_rows = page.query_selector_all(f'{selected_selector} > div')
            print(f"   ⚠️  Using fallback selector, found {len(chat_rows)} elements")

        new_messages = []

        # Unread badge selectors - any of these indicates unread messages
        unread_selectors = [
            'span[data-testid="icon-unread-count"]',  # Unread count badge
            'span[data-testid="unread-count"]',       # Alternative unread count
            'div[aria-label*="unread"]',              # Aria label with unread
            'span[aria-label*="unread"]',             # Span with unread label
            '._aigv span._aigw',                      # Internal class for unread
            'div[data-testid="unread-count"]',        # Unread count div
        ]

        for row in chat_rows[:25]:  # Check top 25 chats
            try:
                # Check for unread badge using multiple selectors
                is_unread = False
                unread_count = 0

                for unread_sel in unread_selectors:
                    try:
                        unread_elem = row.query_selector(unread_sel)
                        if unread_elem:
                            is_unread = True
                            # Try to get count from text or attribute
                            count_text = unread_elem.inner_text()
                            if count_text and count_text.isdigit():
                                unread_count = int(count_text)
                            else:
                                unread_count = 1
                            break
                    except:
                        continue

                # Skip if no unread messages
                if not is_unread:
                    continue

                # Extract contact name - try multiple selectors
                contact = "Unknown"
                contact_selectors = [
                    'span[title]',
                    'div[title]',
                    'span[dir="auto"]',
                    '._aigv span._aigw',
                ]

                for contact_sel in contact_selectors:
                    try:
                        contact_elem = row.query_selector(contact_sel)
                        if contact_elem:
                            contact = contact_elem.get_attribute('title') or contact_elem.inner_text()
                            if contact and contact != "Unknown":
                                break
                    except:
                        continue

                # Extract last message preview - try multiple selectors
                message = "No preview available"
                message_selectors = [
                    'span[dir="auto"]:last-of-type',
                    'div[dir="auto"]:last-of-type',
                    '._aigv span:last-of-type',
                    'span[data-testid="last-message"]',
                ]

                for msg_sel in message_selectors:
                    try:
                        message_elem = row.query_selector(msg_sel)
                        if message_elem:
                            message = message_elem.inner_text()
                            if message and message != "No preview available":
                                break
                    except:
                        continue

                # Create unique message ID
                message_id = f"{contact}:{message[:50]}:{datetime.now().strftime('%H%M')}"

                # Skip if already processed
                if message_id in processed_messages:
                    continue

                # Add to new messages - flag ALL unread regardless of keywords
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                new_messages.append({
                    'contact': contact,
                    'message': message,
                    'timestamp': timestamp,
                    'keyword': 'UNREAD',  # Mark as unread detection
                    'unread_count': unread_count,
                    'message_id': message_id
                })

                print(f"   🔔 UNREAD: {contact} - {message[:40]}...")

            except Exception as e:
                print(f"   ⚠️  Error processing row: {e}")
                continue

        return new_messages, processed_messages

    except PlaywrightTimeout:
        print("⏱️  Timeout waiting for chat list")
        return [], processed_messages
    except Exception as e:
        print(f"⚠️  Error checking messages: {e}")
        return [], processed_messages


def save_processed_message(processed_messages: set, message_id: str):
    """Save processed message ID to file."""
    processed_file = VAULT_PATH / "processed_whatsapp.txt"
    processed_messages.add(message_id)
    
    # Keep only last 1000 messages
    if len(processed_messages) > 1000:
        processed_messages = set(list(processed_messages)[-1000:])
    
    processed_file.write_text('\n'.join(processed_messages), encoding='utf-8')


def main():
    """Main function to run WhatsApp Watcher."""
    
    print("=" * 60)
    print("💬 AI Employee - WhatsApp Watcher Started!")
    print("=" * 60)
    print(f"\n📁 Vault: {VAULT_PATH}")
    print(f"💾 Session: {SESSION_FOLDER}")
    print(f"🔍 Keywords: {', '.join(KEYWORDS)}")
    print(f"⏱️  Check Interval: {CHECK_INTERVAL} seconds")
    print("\n" + "=" * 60)
    
    ensure_folders()

    with sync_playwright() as p:
        # Launch browser with persistent context - HEADED MODE for QR scanning
        print("🌐 Launching browser in visible mode...")
        
        # Load existing session or create new context
        storage_state = get_storage_state()

        if storage_state:
            print("📂 Loading saved session...")
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(SESSION_FOLDER),
                headless=False,  # Visible browser for QR code
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--window-size=1280,800'
                ],
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
        else:
            print("🆕 New session - QR code scan required")
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(SESSION_FOLDER),
                headless=False,  # Visible browser for QR code
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--window-size=1280,800'
                ],
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
        
        page = context.pages[0] if context.pages else context.new_page()

        # Navigate to WhatsApp Web
        print("🌐 Opening WhatsApp Web...")
        page.goto('https://web.whatsapp.com', wait_until='networkidle')

        # Wait for page to load and give user time to scan QR code
        print("\n" + "=" * 60)
        print("⏳ WAITING 30 SECONDS FOR QR CODE SCAN")
        print("=" * 60)
        print("\nIf you see a QR code, please scan it with WhatsApp on your phone.")
        print("The browser window will remain open for 30 seconds...")
        
        for i in range(30, 0, -1):
            print(f"   Time remaining: {i} seconds", end='\r')
            time.sleep(1)
        
        print("\n\n🔍 Checking authentication status...")
        
        # Check if authenticated (look for chat list or QR code)
        try:
            # Try multiple selectors for chat list
            chat_list_selectors = ['#pane-side', 'div[aria-label="Chat list"]', 'div[data-testid="chat-list"]', '._aigv']
            chat_list = None
            
            for selector in chat_list_selectors:
                chat_list = page.query_selector(selector)
                if chat_list:
                    break
            
            qr_code = page.query_selector('canvas[data-icon="qr-code"]')

            if chat_list:
                print("✅ Already authenticated! Chat list found.")
            elif qr_code:
                print("⚠️  QR code still visible. You may need more time to scan.")
                print("   Next time, scan faster or restart the script.")
            else:
                print("✅ WhatsApp Web appears to be loaded.")
        except Exception as e:
            print(f"⚠️  Status check: {e}")
        
        print("\n" + "=" * 60)
        print("👀 Monitoring for new messages...")
        print("=" * 60)
        print("📬 Detecting: ALL unread messages (unread badge)")
        print(f"⏱️  Checking every {CHECK_INTERVAL} seconds...")
        print("\nPress Ctrl+C to stop\n")
        
        try:
            while True:
                try:
                    # Check for new messages
                    new_messages, processed_ids = check_messages(page)

                    if new_messages:
                        print(f"\n🔔 Found {len(new_messages)} unread message(s)!")

                        for msg in new_messages:
                            print(f"\n   📩 From: {msg['contact']}")
                            print(f"   📊 Unread: {msg.get('unread_count', 1)} message(s)")
                            print(f"   💬 Preview: {msg['message'][:50]}...")

                            # Create action file
                            action_file = create_action_file(
                                msg['contact'],
                                msg['message'],
                                msg['timestamp'],
                                msg['keyword'],
                                msg.get('unread_count', 1)
                            )

                            # Trigger Qwen
                            trigger_qwen(action_file)

                            # Mark as processed
                            save_processed_message(processed_ids, msg['message_id'])

                        print(f"\n✅ Processed at {datetime.now().strftime('%H:%M:%S')}")
                    else:
                        print(f"⏳ No new unread messages - {datetime.now().strftime('%H:%M:%S')}")

                    # Save session periodically
                    save_storage_state(context)

                except Exception as e:
                    print(f"⚠️  Error in check cycle: {e}")
                    # Save screenshot on error for debugging
                    try:
                        screenshot_path = VAULT_PATH / "whatsapp_debug_error.png"
                        page.screenshot(path=str(screenshot_path), full_page=True)
                        print(f"   📸 Error screenshot saved to: {screenshot_path}")
                    except:
                        pass

                time.sleep(CHECK_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n\n" + "=" * 60)
            print("🛑 Stopping WhatsApp Watcher...")
            print("=" * 60)

            # Final session save
            save_storage_state(context)
            print("💾 Session saved for next run")

            context.close()
            print("✅ Watcher stopped successfully")


if __name__ == "__main__":
    main()
