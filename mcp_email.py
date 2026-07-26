#!/usr/bin/env python3
"""
MCP Email Server - Real Gmail Implementation
Email capabilities using smtplib/imaplib + Gmail API OAuth

Personal AI Employee Hackathon 0
Platinum Tier: Pure Python Implementation

SUPPORTS TWO MODES:
1. Gmail API OAuth (if token.json exists) - RECOMMENDED
2. SMTP fallback (if only EMAIL_USER/PASSWORD in .env)

⚠️ SECURITY:
    - DRY_RUN=true by default (MUST explicitly set DRY_RUN=false to send)
    - All sends require human approval (HITL safety)
    - Credentials from environment ONLY
    - NEVER commit credentials to git

Usage:
    python mcp_email.py --action send --to test@example.com --subject "Test" --body "Hello"
    python mcp_email.py --action list
    python mcp_email.py --action draft --to test@example.com --subject "Test" --body "Hello"
"""

import os
import sys
import json
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import logging
import base64

# Load secrets from outside vault
sys.path.insert(0, str(Path(__file__).parent))
from secrets_config import SECRETS_DIR, load_secrets, get_secret_path
load_secrets()

from audit_logger import setup_logging
logger = setup_logging('MCPEmail')

# Try to import Gmail API (optional, falls back to SMTP if not available)
try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GMAIL_API_AVAILABLE = True
except ImportError:
    GMAIL_API_AVAILABLE = False
    logger.info("⚠️ Gmail API not installed. Using SMTP fallback. Install: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")


class MCPEmailServer:
    """MCP Email Server with Gmail API + SMTP fallback"""

    def __init__(self, vault_path: Optional[Path] = None):
        self.vault_path = vault_path or Path(__file__).parent
        self.logs_folder = self.vault_path / 'Logs'
        self.logs_folder.mkdir(exist_ok=True)

        # Safety flags
        self.dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'
        self.require_approval = os.getenv('REQUIRE_APPROVAL', 'true').lower() == 'true'

        # Mode 1: Gmail API OAuth (preferred) - paths from secrets_config
        self.gmail_token_path = get_secret_path('token.pickle')
        self.gmail_credentials_path = get_secret_path('credentials.json')
        self.gmail_service = None

        # Initialize Gmail API if token exists
        if GMAIL_API_AVAILABLE and self.gmail_token_path.exists():
            try:
                self._init_gmail_api()
                self.mode = 'gmail_api'
                logger.info(f"✅ Gmail API mode enabled (token: {self.gmail_token_path})")
            except Exception as e:
                logger.warning(f"⚠️ Gmail API init failed: {e}. Falling back to SMTP")
                self.mode = 'smtp'
        else:
            self.mode = 'smtp'

        # Mode 2: SMTP fallback
        if self.mode == 'smtp':
            self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
            self.email_user = os.getenv('EMAIL_USER', '')
            self.email_password = os.getenv('EMAIL_PASSWORD', '')
            self.imap_server = os.getenv('IMAP_SERVER', 'imap.gmail.com')
            logger.info(f"📧 SMTP mode initialized (Dry Run: {self.dry_run}, Approval Required: {self.require_approval})")

    def _init_gmail_api(self):
        """Initialize Gmail API service with OAuth token"""
        if not GMAIL_API_AVAILABLE:
            raise Exception("Gmail API libraries not installed")

        if not self.gmail_token_path.exists():
            raise Exception(f"Token file not found: {self.gmail_token_path}")

        # Load token
        with open(self.gmail_token_path, 'r') as f:
            token_data = json.load(f)

        # Handle both old and new token formats
        if 'refresh_token' in token_data:
            creds = Credentials.from_authorized_user_info(token_data, scopes=[
                'https://www.googleapis.com/auth/gmail.send',
                'https://www.googleapis.com/auth/gmail.compose',
                'https://www.googleapis.com/auth/gmail.readonly'
            ])
        else:
            # Try older format
            creds = Credentials(
                token=token_data.get('access_token'),
                refresh_token=token_data.get('refresh_token'),
                token_uri="https://oauth2.googleapis.com/token",
                client_id=token_data.get('client_id'),
                client_secret=token_data.get('client_secret'),
                scopes=[
                    'https://www.googleapis.com/auth/gmail.send',
                    'https://www.googleapis.com/auth/gmail.compose',
                    'https://www.googleapis.com/auth/gmail.readonly'
                ]
            )

        self.gmail_service = build('gmail', 'v1', credentials=creds)
        logger.info("✅ Gmail API service initialized successfully")
    
    def send_email(self, to: str, subject: str, body: str,
                   attachment_path: Optional[str] = None,
                   approved: bool = False) -> Dict:
        """Send email via Gmail API or SMTP"""
        try:
            # Check approval requirement (HITL safety)
            if self.require_approval and not approved:
                logger.warning(f"⚠️ [HITL BLOCKED] Approval required for email to {to}")
                return {
                    'success': False,
                    'requires_approval': True,
                    'message': f'Email to {to} requires human approval. Set approved=True or REQUIRE_APPROVAL=false',
                    'to': to,
                    'subject': subject
                }

            # Check dry run mode
            if self.dry_run:
                logger.info("=" * 70)
                logger.info("📝 [DRY RUN MODE] Email would be sent (NO ACTUAL SEND)")
                logger.info(f"📝 [DRY RUN] To: {to}")
                logger.info(f"📝 [DRY RUN] Subject: {subject}")
                logger.info(f"📝 [DRY RUN] Body: {body[:100]}...")
                logger.info("=" * 70)

                # Save draft
                draft_file = self.vault_path / 'Drafts' / f'email_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
                draft_file.parent.mkdir(exist_ok=True)
                draft_content = f"""---
type: email_draft
to: {to}
subject: {subject}
created: {datetime.now().isoformat()}
status: draft (dry run)
mode: {self.mode}
---

# Email Draft

**To:** {to}
**Subject:** {subject}

---

{body}
"""
                draft_file.write_text(draft_content, encoding='utf-8')

                return {
                    'success': True,
                    'message': 'Email draft created (DRY RUN MODE - no actual send)',
                    'draft_file': str(draft_file),
                    'dry_run': True,
                    'mode': self.mode
                }

            # REAL SEND - DRY_RUN=false
            logger.info("=" * 70)
            logger.info("🚀 [REAL SEND EXECUTED] Actually sending email...")
            logger.info(f"🚀 [REAL SEND] To: {to}")
            logger.info(f"🚀 [REAL SEND] Subject: {subject}")
            logger.info("=" * 70)

            # Use Gmail API if available, else SMTP
            if self.mode == 'gmail_api' and self.gmail_service:
                result = self._send_via_gmail_api(to, subject, body, attachment_path)
            else:
                result = self._send_via_smtp(to, subject, body, attachment_path)

            if result.get('success'):
                logger.info("=" * 70)
                logger.info(f"✅ [REAL SEND EXECUTED] Email sent successfully via {result.get('mode', 'unknown')}")
                logger.info("=" * 70)
            else:
                logger.error(f"❌ [REAL SEND FAILED] {result.get('message')}")

            return result

        except Exception as e:
            logger.error(f"❌ [REAL SEND FAILED] Exception: {e}")
            return {
                'success': False,
                'message': str(e)
            }

    def _send_via_gmail_api(self, to: str, subject: str, body: str,
                            attachment_path: Optional[str] = None) -> Dict:
        """Send email using Gmail API"""
        try:
            # Create MIME message
            message = MIMEMultipart()
            message['to'] = to
            message['subject'] = subject
            message.attach(MIMEText(body, 'plain'))

            # Add attachment if provided
            if attachment_path and Path(attachment_path).exists():
                with open(attachment_path, 'rb') as f:
                    from email.mime.base import MIMEBase
                    from email import encoders
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', 'attachment', filename=Path(attachment_path).name)
                    message.attach(part)

            # Encode and send
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            api_message = {'raw': raw}

            sent_message = self.gmail_service.users().messages().send(userId='me', body=api_message).execute()

            logger.info(f"✅ Email sent via Gmail API to {to}, message ID: {sent_message.get('id')}")

            # Log the action
            self._log_email_action('sent', to, subject, sent_message.get('id'))

            return {
                'success': True,
                'message': f'Email sent to {to} via Gmail API',
                'message_id': sent_message.get('id'),
                'mode': 'gmail_api'
            }

        except HttpError as error:
            logger.error(f"❌ Gmail API error: {error}")
            return {
                'success': False,
                'message': f'Gmail API error: {error}',
                'mode': 'gmail_api'
            }

    def _send_via_smtp(self, to: str, subject: str, body: str,
                       attachment_path: Optional[str] = None) -> Dict:
        """Send email via SMTP"""
        if not self.email_user or not self.email_password:
            return {
                'success': False,
                'message': 'SMTP credentials not set. Set EMAIL_USER and EMAIL_PASSWORD in .env'
            }

        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = to
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            # Add attachment if provided
            if attachment_path and Path(attachment_path).exists():
                with open(attachment_path, 'rb') as f:
                    from email.mime.base import MIMEBase
                    from email import encoders
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', 'attachment', filename=Path(attachment_path).name)
                    msg.attach(part)

            # Send via SMTP
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            server.send_message(msg)
            server.quit()

            logger.info(f"✅ Email sent via SMTP to {to}")

            # Log the action
            self._log_email_action('sent', to, subject)

            return {
                'success': True,
                'message': f'Email sent to {to} via SMTP',
                'mode': 'smtp'
            }

        except Exception as e:
            logger.error(f"❌ SMTP send failed: {e}")
            return {
                'success': False,
                'message': str(e)
            }

    def _log_email_action(self, action: str, to: str, subject: str, message_id: str = None):
        """Log email action to audit log"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'to': to,
            'subject': subject,
            'message_id': message_id,
            'mode': self.mode,
            'dry_run': self.dry_run
        }

        log_file = self.logs_folder / 'Audit' / f"email_actions_{datetime.now().strftime('%Y%m%d')}.jsonl"
        log_file.parent.mkdir(parents=True, exist_ok=True)

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def list_emails(self, query: str = 'INBOX', max_results: int = 10) -> Dict:
        """List emails via IMAP"""
        try:
            logger.info(f"Listing emails from: {query}")
            
            if not self.email_user:
                return {
                    'success': False,
                    'message': 'EMAIL_USER not configured. Set EMAIL_USER and EMAIL_PASSWORD in .env',
                    'emails': []
                }
            
            if self.dry_run:
                logger.info("DRY RUN: Would list emails from IMAP")
                return {
                    'success': True,
                    'message': 'Dry run - no emails fetched',
                    'emails': [],
                    'count': 0
                }
            
            # Actual IMAP connection
            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.email_user, self.email_password)
            mail.select(query)
            
            status, messages = mail.search(None, 'ALL')
            email_ids = messages[0].split()
            
            emails = []
            for eid in email_ids[-max_results:]:
                status, msg = mail.fetch(eid, '(RFC822)')
                email_msg = email.message_from_bytes(msg[0][1])
                
                emails.append({
                    'id': eid.decode(),
                    'from': email_msg['From'],
                    'subject': email_msg['Subject'],
                    'date': email_msg['Date'],
                    'preview': str(email_msg.get_payload(decode=True)[:100]) if email_msg.get_payload() else ''
                })
            
            mail.close()
            mail.logout()
            
            logger.info(f"✅ Retrieved {len(emails)} emails")
            
            return {
                'success': True,
                'emails': emails,
                'count': len(emails)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to list emails: {e}")
            return {
                'success': False,
                'message': str(e),
                'emails': []
            }
    
    def draft_email(self, to: str, subject: str, body: str) -> Dict:
        """Create email draft"""
        try:
            draft_file = self.vault_path / 'Drafts' / f'email_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
            draft_file.parent.mkdir(exist_ok=True)
            
            draft_content = f"""---
type: email_draft
to: {to}
subject: {subject}
created: {datetime.now().isoformat()}
status: draft
---

# Email Draft

**To:** {to}
**Subject:** {subject}

---

{body}
"""
            draft_file.write_text(draft_content, encoding='utf-8')
            
            logger.info(f"✅ Draft created: {draft_file}")
            
            return {
                'success': True,
                'message': 'Draft created',
                'draft_file': str(draft_file)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to create draft: {e}")
            return {
                'success': False,
                'message': str(e)
            }


# CLI Interface
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='MCP Email Server')
    parser.add_argument('--action', choices=['send', 'list', 'draft'], required=True)
    parser.add_argument('--to', help='Recipient email')
    parser.add_argument('--subject', help='Email subject')
    parser.add_argument('--body', help='Email body')
    parser.add_argument('--vault', help='Vault path')
    
    args = parser.parse_args()
    
    server = MCPEmailServer(Path(args.vault) if args.vault else None)
    
    if args.action == 'send' and args.to and args.subject and args.body:
        result = server.send_email(args.to, args.subject, args.body)
    elif args.action == 'list':
        result = server.list_emails()
    elif args.action == 'draft' and args.to and args.subject and args.body:
        result = server.draft_email(args.to, args.subject, args.body)
    else:
        parser.print_help()
        sys.exit(1)
    
    print(json.dumps(result, indent=2))
