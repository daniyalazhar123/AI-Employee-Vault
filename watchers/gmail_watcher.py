"""
Gmail Watcher for AI Employee Vault
Monitors Gmail for new unread emails and creates action items.
Features:
- Robust error handling with retry logic
- JSON logging to /Logs/ folder
- Graceful failure handling
- Processed email tracking
"""
import pickle
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from base_watcher import BaseWatcher, ConfigurationError

# Configuration
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
CHECK_INTERVAL = 120  # seconds
MAX_RESULTS = 5
MAX_RETRIES = 3


class GmailWatcher(BaseWatcher):
    """Gmail monitoring watcher with robust error handling."""

    def __init__(self, vault_path: Optional[Path] = None):
        super().__init__('gmail', vault_path)

        self.credentials_file = self.vault_path / 'config' / 'credentials.json'
        self.token_file = self.vault_path / 'config' / 'token.pickle'
        self.processed_file = self.vault_path / 'data' / 'processed_emails.txt'
        self.needs_action_folder = self.vault_path / 'Needs_Action'
        self.pending_approval_folder = self.vault_path / 'Pending_Approval'

        self.gmail_service = None
        self.processed_ids: Set[str] = set()

        # Ensure folders exist
        self.needs_action_folder.mkdir(exist_ok=True)
        self.pending_approval_folder.mkdir(exist_ok=True)

    def authenticate(self) -> bool:
        creds: Optional[Credentials] = None

        if self.token_file.exists():
            try:
                with open(self.token_file, 'rb') as token:
                    creds = pickle.load(token)
                self.log_info("Loaded existing authentication token")
            except (pickle.UnpicklingError, EOFError) as e:
                self.log_warning(f"Corrupted token file, will re-authenticate: {e}")
                creds = None

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    self.log_info("Refreshed expired credentials")
                except RefreshError as e:
                    self.log_warning(f"Token refresh failed, will re-authenticate: {e}")
                    creds = None

            if not creds:
                if not self.credentials_file.exists():
                    raise ConfigurationError(
                        f"Credentials file not found: {self.credentials_file}. "
                        "Please download from Google Cloud Console."
                    )

                self.log_info("Starting OAuth flow...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_file), SCOPES
                )
                creds = flow.run_local_server(port=0)
                self.log_info("OAuth flow completed successfully")

            try:
                with open(self.token_file, 'wb') as token:
                    pickle.dump(creds, token)
                self.log_info(f"Token saved to {self.token_file}")
            except IOError as e:
                self.log_error(f"Failed to save token: {e}", exc=e)

        try:
            self.gmail_service = build('gmail', 'v1', credentials=creds)
            self.log_info("Gmail service built successfully")
        except Exception as e:
            self.log_error(f"Failed to build Gmail service: {e}", exc=e)
            return False

        try:
            profile = self.gmail_service.users().getProfile(userId='me').execute()
            email = profile.get('emailAddress', 'unknown')
            self.log_info(f"Authentication TEST successful - user: {email}")
            return True
        except HttpError as api_err:
            self.log_error(f"Gmail API test failed (HttpError): {api_err}", exc=api_err)
            return False
        except Exception as e:
            self.log_error(f"Unexpected error during auth test: {e}", exc=e)
            return False

    def fetch_unread_emails(self) -> List[Dict]:
        def _fetch():
            return self.gmail_service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=MAX_RESULTS
            ).execute()

        try:
            results = self.with_retry(
                _fetch,
                max_retries=MAX_RETRIES,
                retryable_exceptions=(HttpError,)
            )
            messages = results.get('messages', [])
            
            new_messages = [msg for msg in messages if msg['id'] not in self.processed_ids]
            
            if new_messages:
                self.log_info(f"Found {len(new_messages)} new unread email(s)")
            else:
                self.log_info(f"No new emails (checked {len(messages)} total unread)")
            
            return new_messages
        except Exception as e:
            self.log_error(f"Error fetching unread emails: {e}", exc=e)
            return []

    def get_email_details(self, message_id: str) -> Optional[Dict]:
        def _fetch():
            return self.gmail_service.users().messages().get(
                userId='me',
                id=message_id,
                format='metadata',
                metadataHeaders=['From', 'Subject', 'Date', 'To']
            ).execute()

        try:
            msg = self.with_retry(
                _fetch,
                max_retries=MAX_RETRIES,
                retryable_exceptions=(HttpError,)
            )
            
            headers = {}
            for header in msg['payload']['headers']:
                headers[header['name']] = header['value']
            
            return {
                'id': message_id,
                'from': headers.get('From', 'Unknown'),
                'subject': headers.get('Subject', 'No Subject'),
                'date': headers.get('Date', ''),
                'to': headers.get('To', ''),
                'snippet': msg.get('snippet', '')
            }
        except Exception as e:
            self.log_error(f"Failed to get details for email {message_id}: {e}", exc=e)
            return None

    def create_action_file(self, email_data: Dict) -> Optional[Path]:
        try:
            safe_subject = email_data['subject'][:40]
            safe_subject = ''.join(
                c if c.isalnum() or c in ' _-' else '_'
                for c in safe_subject
            ).strip('_ ')
            
            short_id = email_data['id'][:8]
            filename = f"EMAIL_{safe_subject}_{short_id}.md"
            filepath = self.needs_action_folder / filename
            
            content = f"""---
type: email
from: {email_data['from']}
subject: {email_data['subject']}
date: {email_data['date']}
message_id: {email_data['id']}
status: pending
created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
---
## Email Preview
{email_data['snippet']}
## Suggested Actions
- [ ] Draft professional reply
- [ ] Forward if needed
- [ ] Archive after processing
## Notes
*Add notes here after processing*
"""
            
            filepath.write_text(content, encoding='utf-8')
            self.log_info(f"Action file created: {filename}")
            return filepath
        except Exception as e:
            self.log_error(f"Failed to create action file: {e}", exc=e)
            return None

    def trigger_qwen(self, action_file: Path) -> bool:
        """Trigger Qwen CLI to process email."""
        prompt = (
            f"Read the email action file: {action_file.name} in Needs_Action folder. "
            f"Draft a professional reply following Company_Handbook rules. "
            f"Save the reply draft in Pending_Approval folder as REPLY_{action_file.stem}.md"
        )
        
        return self.trigger_qwen(prompt)

    def mark_as_read(self, message_id: str) -> bool:
        def _mark():
            self.gmail_service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()

        try:
            self.with_retry(
                _mark,
                max_retries=MAX_RETRIES,
                retryable_exceptions=(HttpError,)
            )
            self.log_info(f"Marked email {message_id[:8]}... as read")
            return True
        except Exception as e:
            self.log_error(f"Failed to mark as read {message_id}: {e}", exc=e)
            return False

    def run(self):
        self.print_status_header("📧 GMAIL WATCHER STARTED")

        self.processed_ids = self.load_processed_ids('processed_emails.txt')
        self.log_info(f"Loaded {len(self.processed_ids)} previously processed email IDs")

        if not self.authenticate():
            self.log_error("Authentication failed. Exiting.")
            return

        self.log_info(f"Checking every {CHECK_INTERVAL} seconds...")
        self.log_info("Press Ctrl+C to stop\n")

        try:
            while True:
                cycle_start = datetime.now()
                self.log_info(f"--- Check cycle started at {cycle_start.strftime('%H:%M:%S')} ---")

                try:
                    new_emails = self.fetch_unread_emails()

                    if new_emails:
                        self.log_info(f"Processing {len(new_emails)} new email(s)...")
                        for msg in new_emails:
                            email_id = msg['id']
                            email_data = self.get_email_details(email_id)
                            if not email_data:
                                self.log_warning(f"Skipping {email_id[:8]} - no details")
                                continue

                            action_file = self.create_action_file(email_data)
                            if action_file:
                                self.trigger_qwen(action_file)
                                # self.mark_as_read(email_id)  # Uncomment agar read karna ho
                                self.processed_ids.add(email_id)

                        self.save_processed_ids('processed_emails.txt', self.processed_ids)
                        self.log_info(f"✅ Processed {len(new_emails)} email(s) successfully")
                    else:
                        self.log_info(f"⏳ No new emails - {datetime.now().strftime('%H:%M:%S')}")

                except Exception as e:
                    self.log_error(f"Error in check cycle: {e}", exc=e)

                elapsed = (datetime.now() - cycle_start).total_seconds()
                time.sleep(max(0, CHECK_INTERVAL - elapsed))

        except KeyboardInterrupt:
            self.log_info("\n\n⏹️ Stopping Gmail Watcher...")
            self.log_info(f"Final uptime: {self.get_uptime()}")
            self.save_processed_ids('processed_emails.txt', self.processed_ids)
            self.log_info("✅ Watcher stopped successfully")


def main():
    watcher = GmailWatcher()
    watcher.run()


if __name__ == '__main__':
    main()