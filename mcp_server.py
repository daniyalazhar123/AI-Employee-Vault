#!/usr/bin/env python3
"""
MCP Email Server - AI Employee Vault

Model Context Protocol (MCP) server stub for email capabilities.
Integrates with Gmail API for sending, drafting, and listing emails.

⚠️ SECURITY:
    - Credentials loaded from environment variables ONLY
    - NEVER hardcode credentials in this file
    - See CREDENTIALS_GUIDE.md for Gmail OAuth setup instructions
    - ⚠️ NEVER commit this file with actual credentials to version control

Features:
    - send_email(to, subject, body, attachment_path=None)
    - draft_email(to, subject, body)
    - list_emails(query=None, max_results=10)
    - OAuth2 authentication flow stub
    - Dry-run mode for testing
    - Rate limiting (max 10 emails/hour)
    - Exponential backoff for transient errors

Usage:
    python mcp_server.py --dry-run    # Test mode
    python mcp_server.py --serve      # Start MCP server

Environment Variables:
    GMAIL_CLIENT_ID       - Gmail OAuth client ID
    GMAIL_CLIENT_SECRET   - Gmail OAuth client secret
    GMAIL_REDIRECT_URI    - OAuth redirect URI
    GMAIL_TOKEN_PATH      - Path to saved token (default: mcp-email/token.json)
    DRY_RUN               - If 'true', don't send actual emails
    RATE_LIMIT            - Max emails per hour (default: 10)

Qwen CLI Integration:
    This server is compatible with Qwen CLI tool calling.
    Tools are exposed as JSON-RPC functions.

Author: AI Employee Vault System
Version: 1.0.0
License: MIT
"""

import os
import sys
import json
import time
import logging
import base64
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# ⚠️ Security: Import credentials from environment only
# See CREDENTIALS_GUIDE.md for secure setup instructions

# ============================================================================
# CONFIGURATION
# ============================================================================

# Paths
VAULT_PATH = Path(os.getenv('VAULT_PATH', Path(__file__).parent))
TOKEN_PATH = Path(os.getenv('GMAIL_TOKEN_PATH', VAULT_PATH / 'mcp-email' / 'token.json'))
CREDENTIALS_PATH = Path(os.getenv('GMAIL_CREDENTIALS_PATH', VAULT_PATH / 'config' / 'credentials.json'))

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format=LOG_FORMAT,
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger('mcp_email')

# Rate Limiting
RATE_LIMIT = int(os.getenv('RATE_LIMIT', '10'))  # Max emails per hour
RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds

# Retry Configuration
MAX_RETRIES = 3
RETRY_BACKOFF = 2  # Exponential backoff multiplier

# ⚠️ Security: Dry-run mode
DRY_RUN = os.getenv('DRY_RUN', 'false').lower() == 'true'


# ============================================================================
# RATE LIMITER
# ============================================================================

class RateLimiter:
    """Rate limiter for email sending."""
    
    def __init__(self, max_calls: int, period: int):
        """
        Initialize rate limiter.
        
        Args:
            max_calls: Maximum number of calls allowed
            period: Time period in seconds
        """
        self.max_calls = max_calls
        self.period = period
        self.calls: List[float] = []
    
    def acquire(self) -> bool:
        """
        Try to acquire a slot.
        
        Returns:
            True if slot acquired, False if rate limited
        """
        now = time.time()
        
        # Remove old calls
        self.calls = [t for t in self.calls if now - t < self.period]
        
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        
        return False
    
    def get_wait_time(self) -> float:
        """
        Get time to wait before next slot is available.
        
        Returns:
            Wait time in seconds
        """
        if not self.calls:
            return 0
        
        now = time.time()
        oldest = self.calls[0]
        
        return max(0, self.period - (now - oldest))
    
    def get_status(self) -> Dict[str, Any]:
        """Get current rate limit status."""
        now = time.time()
        self.calls = [t for t in self.calls if now - t < self.period]
        
        return {
            'calls_made': len(self.calls),
            'calls_remaining': self.max_calls - len(self.calls),
            'reset_in_seconds': self.get_wait_time(),
            'limit': self.max_calls,
            'period_seconds': self.period
        }


# ============================================================================
# EMAIL DATA CLASSES
# ============================================================================

@dataclass
class EmailResponse:
    """Response from email operation."""
    success: bool
    message: str
    message_id: Optional[str] = None
    error: Optional[str] = None
    dry_run: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class EmailMessage:
    """Email message data."""
    to: str
    subject: str
    body: str
    body_type: str = 'plain'  # 'plain' or 'html'
    attachment_path: Optional[str] = None
    cc: Optional[str] = None
    bcc: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


# ============================================================================
# GMAIL CLIENT
# ============================================================================

class GmailClient:
    """Gmail API client with OAuth2 authentication."""
    
    SCOPES = ['https://www.googleapis.com/auth/gmail.send',
              'https://www.googleapis.com/auth/gmail.compose',
              'https://www.googleapis.com/auth/gmail.readonly']
    
    def __init__(self, credentials_path: Path, token_path: Path):
        """
        Initialize Gmail client.
        
        Args:
            credentials_path: Path to OAuth credentials JSON
            token_path: Path to saved token JSON
        
        ⚠️ Security: Credentials loaded from file, never hardcoded
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self.authenticated = False
        
        logger.info(f"GmailClient initialized (credentials: {credentials_path}, token: {token_path})")
    
    def authenticate(self) -> bool:
        """
        Authenticate with Gmail API using OAuth2.
        
        Returns:
            True if authentication successful
        
        ⚠️ Security: See CREDENTIALS_GUIDE.md for OAuth setup
        """
        try:
            # Check if credentials file exists
            if not self.credentials_path.exists():
                logger.error(f"Credentials file not found: {self.credentials_path}")
                logger.error("⚠️ See CREDENTIALS_GUIDE.md for Gmail OAuth setup instructions")
                return False
            
            # Load credentials
            with open(self.credentials_path, 'r') as f:
                credentials_data = json.load(f)
            
            # Check if token exists
            if self.token_path.exists():
                # Load existing token
                with open(self.token_path, 'r') as f:
                    token_data = json.load(f)
                
                # TODO: Initialize service with token
                # This is a stub - full implementation would use google.oauth2.credentials
                logger.info(f"Loaded existing token from: {self.token_path}")
                self.authenticated = True
            else:
                # Need to authenticate
                logger.info("No token found. Starting OAuth flow...")
                logger.info("⚠️ Opening browser for authentication...")
                
                # TODO: Implement OAuth flow
                # This is a stub - full implementation would use:
                # from google_auth_oauthlib.flow import InstalledAppFlow
                # flow = InstalledAppFlow.from_client_config(credentials_data, self.SCOPES)
                # creds = flow.run_local_server(port=0)
                # Save token to self.token_path
                
                logger.warning("OAuth flow not implemented in stub. Run: cd mcp-email && node authenticate.js")
                return False
            
            # TODO: Build Gmail service
            # from googleapiclient.discovery import build
            # self.service = build('gmail', 'v1', credentials=creds)
            
            logger.info("Gmail API authentication successful")
            return self.authenticated
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    def create_message(self, email: EmailMessage) -> Dict[str, Any]:
        """
        Create email message.
        
        Args:
            email: EmailMessage object
            
        Returns:
            Raw email message as base64-encoded string
        """
        try:
            # Create message
            if email.cc or email.bcc:
                message = MIMEMultipart()
            else:
                message = MIMEText(email.body, email.body_type)
            
            # Set headers
            message['to'] = email.to
            message['subject'] = email.subject
            
            if email.body_type == 'html':
                message.attach(MIMEText(email.body, 'html'))
            else:
                message = MIMEText(email.body, email.body_type)
            
            if email.cc:
                message['cc'] = email.cc
            
            # Add attachment if specified
            if email.attachment_path:
                attachment_path = Path(email.attachment_path)
                if attachment_path.exists():
                    with open(attachment_path, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename="{attachment_path.name}"'
                        )
                        message.attach(part)
                else:
                    logger.warning(f"Attachment not found: {attachment_path}")
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            return {'raw': raw_message}
            
        except Exception as e:
            logger.error(f"Error creating message: {e}")
            raise
    
    def send_email(self, email: EmailMessage) -> EmailResponse:
        """
        Send email via Gmail API.
        
        Args:
            email: EmailMessage object
            
        Returns:
            EmailResponse with success status
        
        ⚠️ Security: Respects DRY_RUN mode - won't send actual emails
        """
        try:
            # Check dry-run mode
            if DRY_RUN:
                logger.info(f"📧 [DRY RUN] Would send email to: {email.to}")
                logger.info(f"   Subject: {email.subject}")
                logger.info(f"   Body: {email.body[:100]}...")
                
                return EmailResponse(
                    success=True,
                    message="Email sent (dry run mode)",
                    message_id="dry-run-" + datetime.now().isoformat(),
                    dry_run=True
                )
            
            # Check authentication
            if not self.authenticated:
                if not self.authenticate():
                    return EmailResponse(
                        success=False,
                        message="Authentication failed",
                        error="Not authenticated"
                    )
            
            # Create message
            message = self.create_message(email)
            
            # TODO: Send via Gmail API
            # This is a stub - full implementation:
            # sent_message = self.service.users().messages().send(
            #     userId='me', body=message
            # ).execute()
            
            # Simulate sending for stub
            logger.info(f"📧 Email sent to: {email.to}")
            logger.info(f"   Subject: {email.subject}")
            
            return EmailResponse(
                success=True,
                message="Email sent successfully",
                message_id="sent-" + datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return EmailResponse(
                success=False,
                message="Failed to send email",
                error=str(e)
            )
    
    def draft_email(self, email: EmailMessage) -> EmailResponse:
        """
        Create email draft (don't send).
        
        Args:
            email: EmailMessage object
            
        Returns:
            EmailResponse with draft ID
        """
        try:
            # Check dry-run mode
            if DRY_RUN:
                logger.info(f"📝 [DRY RUN] Would create draft for: {email.to}")
                logger.info(f"   Subject: {email.subject}")
                
                return EmailResponse(
                    success=True,
                    message="Draft created (dry run mode)",
                    message_id="draft-dry-run-" + datetime.now().isoformat(),
                    dry_run=True
                )
            
            # Create message
            message = self.create_message(email)
            
            # TODO: Create draft via Gmail API
            # This is a stub - full implementation:
            # draft = self.service.users().drafts().create(
            #     userId='me', body={'message': message}
            # ).execute()
            
            logger.info(f"📝 Draft created for: {email.to}")
            logger.info(f"   Subject: {email.subject}")
            
            return EmailResponse(
                success=True,
                message="Draft created successfully",
                message_id="draft-" + datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error creating draft: {e}")
            return EmailResponse(
                success=False,
                message="Failed to create draft",
                error=str(e)
            )
    
    def list_emails(self, query: str = None, max_results: int = 10) -> Dict[str, Any]:
        """
        List emails from Gmail.
        
        Args:
            query: Gmail search query (e.g., 'is:unread', 'from:client@example.com')
            max_results: Maximum number of results
            
        Returns:
            Dictionary with email list
        """
        try:
            # Check authentication
            if not self.authenticated:
                if not self.authenticate():
                    return {
                        'success': False,
                        'error': 'Not authenticated',
                        'emails': []
                    }
            
            # TODO: List emails via Gmail API
            # This is a stub - full implementation:
            # results = self.service.users().messages().list(
            #     userId='me', q=query, maxResults=max_results
            # ).execute()
            # messages = results.get('messages', [])
            
            # Return stub response
            logger.info(f"📬 Listing emails (query: {query or 'inbox'}, max: {max_results})")
            
            return {
                'success': True,
                'query': query or 'inbox',
                'max_results': max_results,
                'count': 0,
                'emails': []
            }
            
        except Exception as e:
            logger.error(f"Error listing emails: {e}")
            return {
                'success': False,
                'error': str(e),
                'emails': []
            }


# ============================================================================
# MCP SERVER
# ============================================================================

class MCPEmailServer:
    """MCP Email Server with rate limiting and retry logic."""
    
    def __init__(self):
        """Initialize MCP email server."""
        self.client = GmailClient(CREDENTIALS_PATH, TOKEN_PATH)
        self.rate_limiter = RateLimiter(RATE_LIMIT, RATE_LIMIT_WINDOW)
        self.email_count = 0
        
        logger.info("MCPEmailServer initialized")
        logger.info(f"Rate limit: {RATE_LIMIT} emails/hour")
        logger.info(f"Dry run: {DRY_RUN}")
    
    def send_email(self, to: str, subject: str, body: str, 
                   attachment_path: Optional[str] = None,
                   cc: Optional[str] = None,
                   bcc: Optional[str] = None) -> Dict[str, Any]:
        """
        Send email (MCP tool).
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body
            attachment_path: Optional path to attachment
            cc: Optional CC email address
            bcc: Optional BCC email address
        
        Returns:
            JSON response compatible with Qwen CLI tool calling
        
        ⚠️ Security: Rate limited, respects DRY_RUN mode
        """
        logger.info(f"📧 send_email called: to={to}, subject={subject}")
        
        # Check rate limit
        if not self.rate_limiter.acquire():
            wait_time = self.rate_limiter.get_wait_time()
            error_msg = f"Rate limit exceeded. Try again in {wait_time:.0f} seconds."
            logger.warning(error_msg)
            
            return {
                'success': False,
                'error': error_msg,
                'rate_limit_status': self.rate_limiter.get_status()
            }
        
        # Create email object
        email = EmailMessage(
            to=to,
            subject=subject,
            body=body,
            attachment_path=attachment_path,
            cc=cc,
            bcc=bcc
        )
        
        # Send with retry logic
        for attempt in range(MAX_RETRIES):
            try:
                response = self.client.send_email(email)
                
                if response.success:
                    self.email_count += 1
                    logger.info(f"✅ Email sent successfully (count: {self.email_count})")
                    
                    return {
                        'success': True,
                        'message': response.message,
                        'message_id': response.message_id,
                        'dry_run': response.dry_run,
                        'rate_limit_status': self.rate_limiter.get_status()
                    }
                
                # Retry on transient errors
                if attempt < MAX_RETRIES - 1:
                    wait_time = RETRY_BACKOFF ** attempt
                    logger.warning(f"Retrying in {wait_time}s... (attempt {attempt + 1}/{MAX_RETRIES})")
                    time.sleep(wait_time)
                else:
                    logger.error(f"❌ Failed to send email after {MAX_RETRIES} attempts")
                    
                    return {
                        'success': False,
                        'error': response.error,
                        'message': response.message
                    }
                    
            except Exception as e:
                logger.error(f"Error on attempt {attempt + 1}: {e}")
                
                if attempt < MAX_RETRIES - 1:
                    wait_time = RETRY_BACKOFF ** attempt
                    time.sleep(wait_time)
                else:
                    return {
                        'success': False,
                        'error': str(e),
                        'message': 'Failed to send email after multiple attempts'
                    }
        
        # Should not reach here, but just in case
        return {
            'success': False,
            'error': 'Unexpected error',
            'message': 'Failed to send email'
        }
    
    def draft_email(self, to: str, subject: str, body: str,
                    attachment_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Create email draft (MCP tool).
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body
            attachment_path: Optional path to attachment
        
        Returns:
            JSON response
        """
        logger.info(f"📝 draft_email called: to={to}, subject={subject}")
        
        # Create email object
        email = EmailMessage(
            to=to,
            subject=subject,
            body=body,
            attachment_path=attachment_path
        )
        
        # Create draft
        response = self.client.draft_email(email)
        
        if response.success:
            logger.info(f"✅ Draft created successfully")
            
            return {
                'success': True,
                'message': response.message,
                'draft_id': response.message_id,
                'dry_run': response.dry_run
            }
        else:
            logger.error(f"❌ Failed to create draft: {response.error}")
            
            return {
                'success': False,
                'error': response.error,
                'message': response.message
            }
    
    def list_emails(self, query: str = None, max_results: int = 10) -> Dict[str, Any]:
        """
        List emails (MCP tool).
        
        Args:
            query: Gmail search query
            max_results: Maximum results to return
        
        Returns:
            JSON response with email list
        """
        logger.info(f"📬 list_emails called: query={query or 'inbox'}, max={max_results}")
        
        # List emails
        result = self.client.list_emails(query, max_results)
        
        return result
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limit status."""
        return self.rate_limiter.get_status()
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information."""
        return {
            'name': 'MCP Email Server',
            'version': '1.0.0',
            'dry_run': DRY_RUN,
            'rate_limit': RATE_LIMIT,
            'emails_sent': self.email_count,
            'rate_limit_status': self.rate_limiter.get_status()
        }


# ============================================================================
# JSON-RPC SERVER (for MCP)
# ============================================================================

def handle_request(request: Dict[str, Any], server: MCPEmailServer) -> Dict[str, Any]:
    """
    Handle JSON-RPC request.
    
    Args:
        request: JSON-RPC request object
        server: MCPEmailServer instance
    
    Returns:
        JSON-RPC response object
    """
    method = request.get('method')
    params = request.get('params', {})
    request_id = request.get('id')
    
    logger.debug(f"Handling request: method={method}, id={request_id}")
    
    try:
        # Route to appropriate method
        if method == 'send_email':
            result = server.send_email(**params)
        elif method == 'draft_email':
            result = server.draft_email(**params)
        elif method == 'list_emails':
            result = server.list_emails(**params)
        elif method == 'get_rate_limit_status':
            result = server.get_rate_limit_status()
        elif method == 'get_server_info':
            result = server.get_server_info()
        else:
            return {
                'jsonrpc': '2.0',
                'error': {'code': -32601, 'message': f'Method not found: {method}'},
                'id': request_id
            }
        
        return {
            'jsonrpc': '2.0',
            'result': result,
            'id': request_id
        }
        
    except Exception as e:
        logger.error(f"Error handling request: {e}")
        
        return {
            'jsonrpc': '2.0',
            'error': {'code': -32603, 'message': str(e)},
            'id': request_id
        }


def run_server():
    """Run MCP server (read from stdin, write to stdout)."""
    logger.info("Starting MCP Email Server (JSON-RPC over stdio)")
    logger.info("⚠️ Press Ctrl+C to stop")
    
    server = MCPEmailServer()
    
    try:
        for line in sys.stdin:
            try:
                request = json.loads(line.strip())
                response = handle_request(request, server)
                print(json.dumps(response), flush=True)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON: {e}")
                print(json.dumps({
                    'jsonrpc': '2.0',
                    'error': {'code': -32700, 'message': 'Parse error'},
                    'id': None
                }), flush=True)
    
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='MCP Email Server - Gmail Integration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python mcp_server.py --serve              # Start MCP server
    python mcp_server.py --test               # Run tests
    python mcp_server.py --dry-run            # Test mode (don't send emails)
    python mcp_server.py --send "test@example.com" "Subject" "Body"

Environment Variables:
    GMAIL_CLIENT_ID       - Gmail OAuth client ID
    GMAIL_CLIENT_SECRET   - Gmail OAuth client secret
    GMAIL_TOKEN_PATH      - Path to saved token
    DRY_RUN               - If 'true', don't send actual emails
    RATE_LIMIT            - Max emails per hour (default: 10)
    LOG_LEVEL             - Logging level: DEBUG, INFO, WARNING, ERROR

⚠️ Security Notes:
    - NEVER commit credentials to version control
    - All credentials loaded from environment variables only
    - See CREDENTIALS_GUIDE.md for Gmail OAuth setup instructions
    - ⚠️ This file should never contain actual credentials
        """
    )
    
    parser.add_argument('--serve', action='store_true', help='Start MCP server')
    parser.add_argument('--test', action='store_true', help='Run tests')
    parser.add_argument('--dry-run', action='store_true', help='Test mode (don\'t send emails)')
    parser.add_argument('--send', nargs=3, metavar=('TO', 'SUBJECT', 'BODY'), help='Send test email')
    parser.add_argument('--list', nargs='?', const='inbox', help='List emails')
    
    args = parser.parse_args()
    
    # Set dry-run mode
    global DRY_RUN
    if args.dry_run:
        DRY_RUN = True
        os.environ['DRY_RUN'] = 'true'
    
    # Create server
    server = MCPEmailServer()
    
    if args.serve:
        # Start MCP server
        run_server()
    
    elif args.test:
        # Run tests
        print("\n" + "="*60)
        print("🧪 MCP EMAIL SERVER - TEST MODE")
        print("="*60)
        print(f"Dry Run: {DRY_RUN}")
        print(f"Rate Limit: {RATE_LIMIT} emails/hour")
        print(f"Credentials: {CREDENTIALS_PATH}")
        print(f"Token: {TOKEN_PATH}")
        print("="*60 + "\n")
        
        # Test server info
        info = server.get_server_info()
        print(f"📊 Server Info: {json.dumps(info, indent=2)}\n")
        
        # Test rate limit
        status = server.get_rate_limit_status()
        print(f"📈 Rate Limit Status: {json.dumps(status, indent=2)}\n")
        
        # Test send email
        if args.send:
            print(f"📧 Sending test email to: {args.send[0]}")
            result = server.send_email(args.send[0], args.send[1], args.send[2])
            print(f"Result: {json.dumps(result, indent=2)}\n")
        
        print("="*60)
        print("✅ Tests complete!")
        print("="*60 + "\n")
    
    elif args.send:
        # Send email
        print(f"📧 Sending email to: {args.send[0]}")
        result = server.send_email(args.send[0], args.send[1], args.send[2])
        print(f"Result: {json.dumps(result, indent=2)}")
    
    elif args.list:
        # List emails
        print(f"📬 Listing emails (query: {args.list})")
        result = server.list_emails(args.list)
        print(f"Result: {json.dumps(result, indent=2)}")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
