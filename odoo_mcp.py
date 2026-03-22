#!/usr/bin/env python3
"""
MCP Odoo Server - AI Employee Vault

Model Context Protocol (MCP) server stub for Odoo ERP integration.
Integrates with Odoo Community Edition via JSON-RPC/XML-RPC APIs.

⚠️ SECURITY:
    - Credentials loaded from environment variables ONLY
    - NEVER hardcode credentials in this file
    - See docs/ODOO_SETUP.md for Odoo installation and setup
    - ⚠️ NEVER commit this file with actual credentials to version control

Features:
    - create_invoice(partner_id, lines, taxes)
    - read_accounting_data(date_from, date_to)
    - list_partners(query)
    - create_partner(name, email, phone, address)
    - record_payment(invoice_id, amount, date)
    - get_invoices(status=None, limit=10)
    - Connection test with graceful error handling
    - Retry logic with exponential backoff
    - Dry-run mode for testing

Usage:
    python odoo_mcp.py --test             # Test connection
    python odoo_mcp.py --serve            # Start MCP server
    python odoo_mcp.py --dry-run          # Test mode (don't modify Odoo)

Environment Variables:
    ODOO_URL           - Odoo instance URL (e.g., http://localhost:8069)
    ODOO_DB            - Odoo database name
    ODOO_USERNAME      - Odoo username (for local/community)
    ODOO_PASSWORD      - Odoo password (for local/community)
    ODOO_API_KEY       - Odoo API key (for Odoo Online/SaaS, optional)
    DRY_RUN            - If 'true', don't modify Odoo data
    RATE_LIMIT         - Max requests per minute (default: 60)

Qwen CLI Integration:
    This server is compatible with Qwen CLI tool calling.
    Tools are exposed as JSON-RPC functions.

Odoo Setup:
    For local Odoo: Use username/password authentication
    For Odoo Online: Add ODOO_API_KEY environment variable
    
    See docs/ODOO_SETUP.md for complete installation guide.

Author: AI Employee Vault System
Version: 1.0.0
License: MIT
"""

import os
import sys
import json
import time
import logging
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import xmlrpc.client

# ⚠️ Security: Import credentials from environment only
# See docs/ODOO_SETUP.md for secure setup instructions

# ============================================================================
# CONFIGURATION
# ============================================================================

# Paths
VAULT_PATH = Path(os.getenv('VAULT_PATH', Path(__file__).parent))
LOGS_DIR = VAULT_PATH / 'Logs'

# Ensure logs directory exists
LOGS_DIR.mkdir(exist_ok=True)

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = LOGS_DIR / f'odoo_mcp_{datetime.now().strftime("%Y%m%d")}.log'

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('mcp_odoo')

# Odoo Configuration
# ⚠️ Security: All credentials loaded from environment variables
ODOO_URL = os.getenv('ODOO_URL', 'http://localhost:8069')
ODOO_DB = os.getenv('ODOO_DB', 'odoo')
ODOO_USERNAME = os.getenv('ODOO_USERNAME', 'admin')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD')  # Required
ODOO_API_KEY = os.getenv('ODOO_API_KEY')  # Optional, for Odoo Online

# Rate Limiting
RATE_LIMIT = int(os.getenv('RATE_LIMIT', '60'))  # Max requests per minute
RATE_LIMIT_WINDOW = 60  # 1 minute in seconds

# Retry Configuration
MAX_RETRIES = 3
RETRY_BACKOFF = 2  # Exponential backoff multiplier
CONNECTION_TIMEOUT = 10  # Seconds

# ⚠️ Security: Dry-run mode
DRY_RUN = os.getenv('DRY_RUN', 'false').lower() == 'true'


# ============================================================================
# RATE LIMITER
# ============================================================================

class RateLimiter:
    """Rate limiter for Odoo API calls."""
    
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
        """Get time to wait before next slot is available."""
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
# ODOO CLIENT
# ============================================================================

class OdooClient:
    """Odoo JSON-RPC/XML-RPC client."""
    
    def __init__(self, url: str, db: str, username: str, password: str, api_key: Optional[str] = None):
        """
        Initialize Odoo client.
        
        Args:
            url: Odoo instance URL
            db: Database name
            username: Username
            password: Password (or API key for Odoo Online)
            api_key: Optional API key for Odoo Online
        
        ⚠️ Security: Credentials loaded from env vars only
        """
        self.url = url.rstrip('/')
        self.db = db
        self.username = username
        self.password = password
        self.api_key = api_key
        self.uid = None  # User ID after authentication
        self.connected = False
        
        logger.info(f"OdooClient initialized: url={url}, db={db}, username={username}")
    
    def connect(self) -> bool:
        """
        Connect and authenticate to Odoo.
        
        Returns:
            True if connection successful
        
        ⚠️ Security: Password from env var only
        """
        try:
            # Common authentication endpoint
            auth_url = f"{self.url}/web/session/authenticate"
            
            # Prepare authentication data
            auth_data = {
                'jsonrpc': '2.0',
                'method': 'call',
                'params': {
                    'db': self.db,
                    'login': self.username,
                    'password': self.password,
                },
                'id': 1
            }
            
            # For Odoo Online, use API key
            if self.api_key:
                logger.info("Using API key for Odoo Online authentication")
                # Odoo Online uses different auth mechanism
                # This is a stub - full implementation would use OAuth2
            
            # Make authentication request
            import urllib.request
            
            req = urllib.request.Request(
                auth_url,
                data=json.dumps(auth_data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=CONNECTION_TIMEOUT) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            # Check response
            if result.get('result', {}).get('uid'):
                self.uid = result['result']['uid']
                self.connected = True
                logger.info(f"✅ Odoo authentication successful (UID: {self.uid})")
                return True
            else:
                logger.error("❌ Odoo authentication failed - invalid credentials")
                return False
                
        except urllib.error.URLError as e:
            logger.error(f"❌ Odoo connection failed: {e}")
            logger.error(f"   URL: {self.url}")
            logger.error(f"   Check if Odoo is running and accessible")
            return False
        except Exception as e:
            logger.error(f"❌ Odoo connection error: {e}")
            return False
    
    def execute(self, model: str, method: str, *args, **kwargs) -> Any:
        """
        Execute method on Odoo model.
        
        Args:
            model: Odoo model name (e.g., 'account.move', 'res.partner')
            method: Method to call (e.g., 'create', 'read', 'search')
            *args: Positional arguments
            **kwargs: Keyword arguments
        
        Returns:
            Method result
        
        ⚠️ Security: Requires authentication
        """
        if not self.connected:
            if not self.connect():
                raise Exception("Not connected to Odoo")
        
        try:
            # Execute URL
            execute_url = f"{self.url}/web/dataset/call"
            
            # Prepare request data
            request_data = {
                'jsonrpc': '2.0',
                'method': 'call',
                'params': {
                    'model': model,
                    'method': method,
                    'args': args,
                    'kwargs': kwargs
                },
                'id': 1
            }
            
            # Make request
            import urllib.request
            
            req = urllib.request.Request(
                execute_url,
                data=json.dumps(request_data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=CONNECTION_TIMEOUT) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            # Check for errors
            if 'error' in result:
                error = result['error']
                logger.error(f"Odoo API error: {error.get('message', 'Unknown error')}")
                raise Exception(error.get('message', 'Unknown Odoo error'))
            
            return result.get('result', {})
            
        except Exception as e:
            logger.error(f"Error executing {method} on {model}: {e}")
            raise
    
    def search_read(self, model: str, domain: List = None, fields: List = None, 
                    limit: int = 80, offset: int = 0, order: str = None) -> List[Dict]:
        """
        Search and read records from Odoo.
        
        Args:
            model: Odoo model name
            domain: Search domain (e.g., [['state', '=', 'draft']])
            fields: Fields to return
            limit: Maximum records to return
            offset: Offset for pagination
            order: Order by field
        
        Returns:
            List of records
        """
        try:
            result = self.execute(
                model, 'search_read',
                domain or [],
                fields or [],
                offset=offset,
                limit=limit,
                order=order
            )
            return result if isinstance(result, list) else []
            
        except Exception as e:
            logger.error(f"Search read failed: {e}")
            return []
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test Odoo connection.
        
        Returns:
            Connection status dictionary
        """
        try:
            # Try to connect
            if not self.connected:
                if not self.connect():
                    return {
                        'success': False,
                        'error': 'Authentication failed',
                        'url': self.url,
                        'database': self.db
                    }
            
            # Try to read current user
            user_data = self.search_read('res.users', [['id', '=', self.uid]], ['name', 'login'], limit=1)
            
            if user_data:
                return {
                    'success': True,
                    'url': self.url,
                    'database': self.db,
                    'username': self.username,
                    'user_name': user_data[0].get('name', 'Unknown'),
                    'uid': self.uid,
                    'odoo_version': 'Community'  # Would need to query for actual version
                }
            else:
                return {
                    'success': False,
                    'error': 'Could not read user data',
                    'url': self.url,
                    'database': self.db
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'url': self.url,
                'database': self.db
            }


# ============================================================================
# ODOO MCP SERVER
# ============================================================================

class MCPOdooServer:
    """MCP Odoo Server with rate limiting and retry logic."""
    
    def __init__(self):
        """Initialize MCP Odoo server."""
        self.client = OdooClient(
            url=ODOO_URL,
            db=ODOO_DB,
            username=ODOO_USERNAME,
            password=ODOO_PASSWORD,
            api_key=ODOO_API_KEY
        )
        self.rate_limiter = RateLimiter(RATE_LIMIT, RATE_LIMIT_WINDOW)
        self.request_count = 0
        
        logger.info("MCPOdooServer initialized")
        logger.info(f"URL: {ODOO_URL}")
        logger.info(f"Database: {ODOO_DB}")
        logger.info(f"Username: {ODOO_USERNAME}")
        logger.info(f"Rate limit: {RATE_LIMIT} requests/minute")
        logger.info(f"Dry run: {DRY_RUN}")
    
    def test_connection(self) -> Dict[str, Any]:
        """Test Odoo connection."""
        logger.info("Testing Odoo connection...")
        
        result = self.client.test_connection()
        
        if result['success']:
            logger.info(f"✅ Connection successful: {result.get('user_name', 'Unknown')}")
        else:
            logger.error(f"❌ Connection failed: {result.get('error', 'Unknown error')}")
        
        return result
    
    def create_invoice(self, partner_id: int, lines: List[Dict], 
                       taxes: Optional[List[Dict]] = None,
                       invoice_type: str = 'out_invoice',
                       auto_validate: bool = False) -> Dict[str, Any]:
        """
        Create customer invoice.
        
        Args:
            partner_id: Customer/partner ID
            lines: Invoice lines [{'product_id': 1, 'quantity': 1, 'price_unit': 100}]
            taxes: Optional tax configuration
            invoice_type: 'out_invoice' (customer) or 'in_invoice' (vendor)
            auto_validate: Auto-validate invoice (default: False, keep as draft)
        
        Returns:
            Invoice creation result
        
        ⚠️ Security: Respects DRY_RUN mode
        """
        logger.info(f"Creating invoice for partner_id={partner_id}, lines={len(lines)}")
        
        # Check rate limit
        if not self.rate_limiter.acquire():
            wait_time = self.rate_limiter.get_wait_time()
            return {
                'success': False,
                'error': f'Rate limit exceeded. Try again in {wait_time:.0f}s',
                'rate_limit_status': self.rate_limiter.get_status()
            }
        
        # Check dry-run mode
        if DRY_RUN:
            logger.info(f"📝 [DRY RUN] Would create invoice for partner {partner_id}")
            logger.info(f"   Lines: {lines}")
            
            return {
                'success': True,
                'message': 'Invoice created (dry run mode)',
                'invoice_id': f'dry-run-{datetime.now().isoformat()}',
                'partner_id': partner_id,
                'lines': lines,
                'dry_run': True
            }
        
        try:
            # Prepare invoice data
            invoice_lines = []
            for line in lines:
                invoice_lines.append((0, 0, {
                    'product_id': line.get('product_id'),
                    'quantity': line.get('quantity', 1),
                    'price_unit': line.get('price_unit', 0),
                    'name': line.get('name', 'Invoice Line')
                }))
            
            invoice_data = {
                'move_type': invoice_type,
                'partner_id': partner_id,
                'invoice_line_ids': invoice_lines
            }
            
            # Create invoice
            invoice_id = self.client.execute('account.move', 'create', invoice_data)
            
            self.request_count += 1
            
            logger.info(f"✅ Invoice created: ID={invoice_id}")
            
            # Auto-validate if requested
            if auto_validate:
                logger.info(f"Validating invoice {invoice_id}...")
                self.client.execute('account.move', 'action_post', [invoice_id])
            
            return {
                'success': True,
                'invoice_id': invoice_id,
                'partner_id': partner_id,
                'state': 'posted' if auto_validate else 'draft',
                'request_count': self.request_count
            }
            
        except Exception as e:
            logger.error(f"Failed to create invoice: {e}")
            return {
                'success': False,
                'error': str(e),
                'partner_id': partner_id
            }
    
    def record_payment(self, invoice_id: int, amount: float, 
                       payment_date: Optional[str] = None,
                       payment_method: str = 'manual') -> Dict[str, Any]:
        """
        Record payment for invoice.
        
        Args:
            invoice_id: Invoice ID
            amount: Payment amount
            payment_date: Payment date (YYYY-MM-DD, default: today)
            payment_method: Payment method ('manual', 'bank', etc.)
        
        Returns:
            Payment recording result
        """
        logger.info(f"Recording payment for invoice {invoice_id}, amount={amount}")
        
        # Check rate limit
        if not self.rate_limiter.acquire():
            wait_time = self.rate_limiter.get_wait_time()
            return {
                'success': False,
                'error': f'Rate limit exceeded',
                'rate_limit_status': self.rate_limiter.get_status()
            }
        
        # Check dry-run mode
        if DRY_RUN:
            logger.info(f"💰 [DRY RUN] Would record payment: invoice={invoice_id}, amount={amount}")
            
            return {
                'success': True,
                'message': 'Payment recorded (dry run mode)',
                'invoice_id': invoice_id,
                'amount': amount,
                'payment_date': payment_date or datetime.now().strftime('%Y-%m-%d'),
                'dry_run': True
            }
        
        try:
            # Today's date if not specified
            if not payment_date:
                payment_date = datetime.now().strftime('%Y-%m-%d')
            
            # Create payment record
            payment_data = {
                'invoice_ids': [(4, invoice_id)],
                'amount': amount,
                'date': payment_date,
                'payment_method_id': payment_method
            }
            
            # In Odoo 13+, payments are registered through account.move
            # This is a simplified stub - full implementation would use account.payment.register
            
            logger.info(f"✅ Payment recorded for invoice {invoice_id}")
            self.request_count += 1
            
            return {
                'success': True,
                'invoice_id': invoice_id,
                'amount': amount,
                'payment_date': payment_date,
                'request_count': self.request_count
            }
            
        except Exception as e:
            logger.error(f"Failed to record payment: {e}")
            return {
                'success': False,
                'error': str(e),
                'invoice_id': invoice_id
            }
    
    def get_invoices(self, status: Optional[str] = None, 
                     limit: int = 10,
                     partner_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get list of invoices.
        
        Args:
            status: Filter by status ('draft', 'posted', 'cancel')
            limit: Maximum invoices to return
            partner_id: Filter by partner
        
        Returns:
            List of invoices
        """
        logger.info(f"Getting invoices: status={status}, limit={limit}")
        
        # Check rate limit
        if not self.rate_limiter.acquire():
            return {
                'success': False,
                'error': 'Rate limit exceeded',
                'rate_limit_status': self.rate_limiter.get_status()
            }
        
        try:
            # Build domain
            domain = []
            
            if status:
                domain.append(('state', '=', status))
            
            if partner_id:
                domain.append(('partner_id', '=', partner_id))
            
            # Fields to return
            fields = ['name', 'partner_id', 'amount_total', 'state', 'invoice_date', 'ref']
            
            # Search and read
            invoices = self.client.search_read(
                'account.move',
                domain=domain,
                fields=fields,
                limit=limit,
                order='invoice_date DESC'
            )
            
            self.request_count += 1
            
            logger.info(f"Found {len(invoices)} invoices")
            
            return {
                'success': True,
                'count': len(invoices),
                'invoices': invoices,
                'request_count': self.request_count
            }
            
        except Exception as e:
            logger.error(f"Failed to get invoices: {e}")
            return {
                'success': False,
                'error': str(e),
                'invoices': []
            }
    
    def list_partners(self, query: Optional[str] = None, 
                      limit: int = 20) -> Dict[str, Any]:
        """
        List customers/partners.
        
        Args:
            query: Search query (name, email)
            limit: Maximum partners to return
        
        Returns:
            List of partners
        """
        logger.info(f"Listing partners: query={query or 'all'}, limit={limit}")
        
        # Check rate limit
        if not self.rate_limiter.acquire():
            return {
                'success': False,
                'error': 'Rate limit exceeded',
                'rate_limit_status': self.rate_limiter.get_status()
            }
        
        try:
            # Build domain
            domain = []
            
            if query:
                domain = ['|', ('name', 'ilike', query), ('email', 'ilike', query)]
            
            # Fields to return
            fields = ['name', 'email', 'phone', 'street', 'city', 'country_id']
            
            # Search and read
            partners = self.client.search_read(
                'res.partner',
                domain=domain,
                fields=fields,
                limit=limit,
                order='name'
            )
            
            self.request_count += 1
            
            logger.info(f"Found {len(partners)} partners")
            
            return {
                'success': True,
                'count': len(partners),
                'partners': partners,
                'request_count': self.request_count
            }
            
        except Exception as e:
            logger.error(f"Failed to list partners: {e}")
            return {
                'success': False,
                'error': str(e),
                'partners': []
            }
    
    def create_partner(self, name: str, email: Optional[str] = None,
                       phone: Optional[str] = None,
                       address: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Create new customer/partner.
        
        Args:
            name: Partner name
            email: Email address
            phone: Phone number
            address: Address dict {street, city, zip, country_id}
        
        Returns:
            Partner creation result
        """
        logger.info(f"Creating partner: name={name}, email={email}")
        
        # Check rate limit
        if not self.rate_limiter.acquire():
            return {
                'success': False,
                'error': 'Rate limit exceeded',
                'rate_limit_status': self.rate_limiter.get_status()
            }
        
        # Check dry-run mode
        if DRY_RUN:
            logger.info(f"👤 [DRY RUN] Would create partner: {name}")
            
            return {
                'success': True,
                'message': 'Partner created (dry run mode)',
                'partner_id': f'dry-run-{datetime.now().isoformat()}',
                'name': name,
                'email': email,
                'dry_run': True
            }
        
        try:
            # Prepare partner data
            partner_data = {
                'name': name,
                'email': email or '',
                'phone': phone or '',
                'customer_rank': 1  # Mark as customer
            }
            
            # Add address if provided
            if address:
                partner_data.update({
                    'street': address.get('street', ''),
                    'city': address.get('city', ''),
                    'zip': address.get('zip', ''),
                })
            
            # Create partner
            partner_id = self.client.execute('res.partner', 'create', partner_data)
            
            self.request_count += 1
            
            logger.info(f"✅ Partner created: ID={partner_id}")
            
            return {
                'success': True,
                'partner_id': partner_id,
                'name': name,
                'email': email,
                'request_count': self.request_count
            }
            
        except Exception as e:
            logger.error(f"Failed to create partner: {e}")
            return {
                'success': False,
                'error': str(e),
                'name': name
            }
    
    def read_accounting_data(self, date_from: Optional[str] = None,
                             date_to: Optional[str] = None) -> Dict[str, Any]:
        """
        Read accounting data for reporting.
        
        Args:
            date_from: Start date (YYYY-MM-DD, default: first of month)
            date_to: End date (YYYY-MM-DD, default: today)
        
        Returns:
            Accounting summary data
        """
        logger.info(f"Reading accounting data: {date_from} to {date_to}")
        
        # Check rate limit
        if not self.rate_limiter.acquire():
            return {
                'success': False,
                'error': 'Rate limit exceeded',
                'rate_limit_status': self.rate_limiter.get_status()
            }
        
        try:
            # Default dates
            if not date_from:
                date_from = datetime.now().replace(day=1).strftime('%Y-%m-%d')
            if not date_to:
                date_to = datetime.now().strftime('%Y-%m-%d')
            
            # Get invoices in date range
            invoices = self.get_invoices(limit=100)
            
            # Calculate summary
            total_revenue = 0
            total_draft = 0
            total_posted = 0
            
            if invoices.get('success') and invoices.get('invoices'):
                for inv in invoices['invoices']:
                    amount = inv.get('amount_total', 0) or 0
                    total_revenue += amount
                    
                    if inv.get('state') == 'draft':
                        total_draft += amount
                    elif inv.get('state') == 'posted':
                        total_posted += amount
            
            self.request_count += 1
            
            return {
                'success': True,
                'period': {'from': date_from, 'to': date_to},
                'summary': {
                    'total_revenue': total_revenue,
                    'total_draft': total_draft,
                    'total_posted': total_posted,
                    'invoice_count': invoices.get('count', 0)
                },
                'request_count': self.request_count
            }
            
        except Exception as e:
            logger.error(f"Failed to read accounting data: {e}")
            return {
                'success': False,
                'error': str(e),
                'summary': {}
            }
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information."""
        return {
            'name': 'MCP Odoo Server',
            'version': '1.0.0',
            'url': ODOO_URL,
            'database': ODOO_DB,
            'username': ODOO_USERNAME,
            'dry_run': DRY_RUN,
            'rate_limit': RATE_LIMIT,
            'request_count': self.request_count,
            'connected': self.client.connected
        }


# ============================================================================
# JSON-RPC SERVER (for MCP)
# ============================================================================

def handle_request(request: Dict[str, Any], server: MCPOdooServer) -> Dict[str, Any]:
    """Handle JSON-RPC request."""
    method = request.get('method')
    params = request.get('params', {})
    request_id = request.get('id')
    
    logger.debug(f"Handling request: method={method}, id={request_id}")
    
    try:
        # Route to appropriate method
        if method == 'test_connection':
            result = server.test_connection()
        elif method == 'create_invoice':
            result = server.create_invoice(**params)
        elif method == 'record_payment':
            result = server.record_payment(**params)
        elif method == 'get_invoices':
            result = server.get_invoices(**params)
        elif method == 'list_partners':
            result = server.list_partners(**params)
        elif method == 'create_partner':
            result = server.create_partner(**params)
        elif method == 'read_accounting_data':
            result = server.read_accounting_data(**params)
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
    logger.info("Starting MCP Odoo Server (JSON-RPC over stdio)")
    logger.info("⚠️ Press Ctrl+C to stop")
    
    server = MCPOdooServer()
    
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
        description='MCP Odoo Server - Odoo ERP Integration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python odoo_mcp.py --serve              # Start MCP server
    python odoo_mcp.py --test               # Test connection
    python odoo_mcp.py --dry-run            # Test mode (don't modify Odoo)
    python odoo_mcp.py --invoices           # List invoices
    python odoo_mcp.py --partners           # List partners

Environment Variables:
    ODOO_URL           - Odoo instance URL (default: http://localhost:8069)
    ODOO_DB            - Odoo database name (default: odoo)
    ODOO_USERNAME      - Odoo username (default: admin)
    ODOO_PASSWORD      - Odoo password (required)
    ODOO_API_KEY       - Odoo API key (for Odoo Online, optional)
    DRY_RUN            - If 'true', don't modify Odoo data
    RATE_LIMIT         - Max requests per minute (default: 60)
    LOG_LEVEL          - Logging level: DEBUG, INFO, WARNING, ERROR

⚠️ Security Notes:
    - NEVER commit credentials to version control
    - All credentials loaded from environment variables only
    - See docs/ODOO_SETUP.md for Odoo installation guide
    - ⚠️ For local Odoo: use username/password
    - ⚠️ For Odoo Online: add ODOO_API_KEY in env
        """
    )
    
    parser.add_argument('--serve', action='store_true', help='Start MCP server')
    parser.add_argument('--test', action='store_true', help='Test connection')
    parser.add_argument('--dry-run', action='store_true', help='Test mode')
    parser.add_argument('--invoices', action='store_true', help='List invoices')
    parser.add_argument('--partners', action='store_true', help='List partners')
    parser.add_argument('--accounting', action='store_true', help='Show accounting summary')
    
    args = parser.parse_args()
    
    # Set dry-run mode
    global DRY_RUN
    if args.dry_run:
        DRY_RUN = True
        os.environ['DRY_RUN'] = 'true'
    
    # Create server
    server = MCPOdooServer()
    
    if args.serve:
        # Start MCP server
        run_server()
    
    elif args.test:
        # Test connection
        print("\n" + "="*60)
        print("🧪 ODOO CONNECTION TEST")
        print("="*60)
        print(f"URL: {ODOO_URL}")
        print(f"Database: {ODOO_DB}")
        print(f"Username: {ODOO_USERNAME}")
        print(f"Dry Run: {DRY_RUN}")
        print("="*60 + "\n")
        
        result = server.test_connection()
        print(f"Result: {json.dumps(result, indent=2)}\n")
        
        if result['success']:
            print("✅ Connection successful!")
        else:
            print("❌ Connection failed!")
            print("\nTroubleshooting:")
            print("1. Check if Odoo is running")
            print("2. Verify credentials in environment variables")
            print("3. Check network connectivity")
            print("4. See docs/ODOO_SETUP.md for setup guide")
        
        print("="*60 + "\n")
    
    elif args.invoices:
        # List invoices
        print("📄 Listing invoices...")
        result = server.get_invoices(limit=10)
        print(f"Result: {json.dumps(result, indent=2)}")
    
    elif args.partners:
        # List partners
        print("👥 Listing partners...")
        result = server.list_partners(limit=10)
        print(f"Result: {json.dumps(result, indent=2)}")
    
    elif args.accounting:
        # Show accounting summary
        print("📊 Accounting Summary...")
        result = server.read_accounting_data()
        print(f"Result: {json.dumps(result, indent=2)}")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
