#!/usr/bin/env python3
"""
MCP Email Server - Pure Python Implementation
Email capabilities using smtplib/imaplib

Personal AI Employee Hackathon 0
Platinum Tier: Pure Python Implementation
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

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('MCPEmail')


class MCPEmailServer:
    """Pure Python MCP Email Server"""
    
    def __init__(self, vault_path: Optional[Path] = None):
        self.vault_path = vault_path or Path(__file__).parent
        self.logs_folder = self.vault_path / 'Logs'
        self.logs_folder.mkdir(exist_ok=True)
        
        # Load credentials from environment
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email_user = os.getenv('EMAIL_USER', '')
        self.email_password = os.getenv('EMAIL_PASSWORD', '')
        self.imap_server = os.getenv('IMAP_SERVER', 'imap.gmail.com')
        
        # Dry run mode (default for safety)
        self.dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'
        
        logger.info(f"📧 MCP Email Server initialized (Dry Run: {self.dry_run})")
    
    def send_email(self, to: str, subject: str, body: str, 
                   attachment_path: Optional[str] = None) -> Dict:
        """Send email via SMTP"""
        try:
            logger.info(f"📧 Sending email to: {to}")
            
            if self.dry_run:
                logger.info(f"📝 [DRY RUN] Email would be sent to {to}")
                logger.info(f"📝 Subject: {subject}")
                logger.info(f"📝 Body: {body[:100]}...")
                
                # Save draft
                draft_file = self.vault_path / 'Drafts' / f'email_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
                draft_file.parent.mkdir(exist_ok=True)
                draft_content = f"""---
type: email_draft
to: {to}
subject: {subject}
created: {datetime.now().isoformat()}
status: draft (dry run)
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
                    'message': 'Email draft created (dry run mode)',
                    'draft_file': str(draft_file)
                }
            
            # Actual send (when not in dry run)
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = to
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Add attachment if provided
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, 'rb') as f:
                    part = MIMEText(f.read())
                    part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment_path))
                    msg.attach(part)
            
            # Send via SMTP
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"✅ Email sent successfully to {to}")
            
            return {
                'success': True,
                'message': f'Email sent to {to}'
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to send email: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def list_emails(self, query: str = 'INBOX', max_results: int = 10) -> Dict:
        """List emails via IMAP"""
        try:
            logger.info(f"📬 Listing emails from: {query}")
            
            if self.dry_run or not self.email_user:
                # Return mock data for dry run
                mock_emails = [
                    {
                        'id': '1',
                        'from': 'client@example.com',
                        'subject': 'Project Update',
                        'date': datetime.now().isoformat(),
                        'preview': 'Hi, I wanted to update you on the project...'
                    },
                    {
                        'id': '2',
                        'from': 'team@company.com',
                        'subject': 'Meeting Tomorrow',
                        'date': datetime.now().isoformat(),
                        'preview': 'Don\'t forget about the meeting tomorrow at 2 PM...'
                    }
                ]
                return {
                    'success': True,
                    'emails': mock_emails[:max_results],
                    'count': len(mock_emails)
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
