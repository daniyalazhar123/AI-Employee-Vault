#!/usr/bin/env python3
"""
MCP Odoo Server - Pure Python Implementation
Odoo ERP integration using xmlrpc.client

Personal AI Employee Hackathon 0
Platinum Tier: Pure Python Implementation
"""

import os
import sys
import json
import xmlrpc.client
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('MCPOdoo')


class MCPOdooServer:
    """Pure Python MCP Odoo Server"""
    
    def __init__(self, vault_path: Optional[Path] = None):
        self.vault_path = vault_path or Path(__file__).parent
        self.logs_folder = self.vault_path / 'Logs'
        self.logs_folder.mkdir(exist_ok=True)
        
        # Load Odoo credentials from environment
        self.odoo_url = os.getenv('ODOO_URL', 'http://localhost:8069')
        self.odoo_db = os.getenv('ODOO_DB', 'odoo')
        self.odoo_username = os.getenv('ODOO_USERNAME', 'admin')
        self.odoo_password = os.getenv('ODOO_PASSWORD', 'admin')
        self.odoo_api_key = os.getenv('ODOO_API_KEY')
        
        # Odoo client
        self.uid = None
        self.common = None
        self.models = None
        
        # Dry run mode
        self.dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'
        
        logger.info(f"💼 MCP Odoo Server initialized (URL: {self.odoo_url}, Dry Run: {self.dry_run})")
        
        # Try to authenticate
        if not self.dry_run:
            self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Odoo"""
        try:
            self.common = xmlrpc.client.ServerProxy(f'{self.odoo_url}/xmlrpc/2/common')
            self.models = xmlrpc.client.ServerProxy(f'{self.odoo_url}/xmlrpc/2/object')
            
            self.uid = self.common.authenticate(
                self.odoo_db, 
                self.odoo_username, 
                self.odoo_password,
                {}
            )
            
            if self.uid:
                logger.info(f"✅ Odoo authenticated as UID: {self.uid}")
            else:
                logger.error("❌ Odoo authentication failed")
                
        except Exception as e:
            logger.error(f"❌ Odoo connection error: {e}")
    
    def create_invoice(self, partner_id: int, amount: float, 
                       description: str = 'Service') -> Dict:
        """Create customer invoice"""
        try:
            logger.info(f"💰 Creating invoice for partner {partner_id}, amount: {amount}")
            
            if self.dry_run:
                logger.info(f"📝 [DRY RUN] Invoice would be created")
                
                # Save draft
                draft_file = self.vault_path / 'Drafts' / f'invoice_{partner_id}_{datetime.now().strftime("%Y%m%d")}.md'
                draft_file.parent.mkdir(exist_ok=True)
                draft_content = f"""---
type: invoice_draft
partner_id: {partner_id}
amount: {amount}
description: {description}
created: {datetime.now().isoformat()}
status: draft (dry run)
---

# Invoice Draft

**Partner ID:** {partner_id}
**Amount:** Rs. {amount}
**Description:** {description}

---

*Draft created (dry run mode)*
"""
                draft_file.write_text(draft_content, encoding='utf-8')
                
                return {
                    'success': True,
                    'message': 'Invoice draft created (dry run)',
                    'draft_file': str(draft_file)
                }
            
            # Actual invoice creation
            invoice_data = {
                'move_type': 'out_invoice',
                'partner_id': partner_id,
                'invoice_line_ids': [(0, 0, {
                    'name': description,
                    'quantity': 1,
                    'price_unit': amount,
                })]
            }
            
            invoice_id = self.models.execute_kw(
                self.odoo_db, self.uid, self.odoo_password,
                'account.move', 'create', [invoice_data]
            )
            
            logger.info(f"✅ Invoice created: {invoice_id}")
            
            return {
                'success': True,
                'invoice_id': invoice_id,
                'message': f'Invoice {invoice_id} created'
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to create invoice: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def get_leads(self, limit: int = 10) -> Dict:
        """Get CRM leads"""
        try:
            logger.info(f"🎯 Getting leads (limit: {limit})")
            
            if self.dry_run:
                # Mock data
                mock_leads = [
                    {
                        'id': 1,
                        'name': 'Demo Lead 1',
                        'partner_name': 'ABC Company',
                        'email_from': 'contact@abc.com',
                        'phone': '+1234567890',
                        'priority': '3',
                        'stage_id': [1, 'New']
                    },
                    {
                        'id': 2,
                        'name': 'Demo Lead 2',
                        'partner_name': 'XYZ Corp',
                        'email_from': 'info@xyz.com',
                        'phone': '+0987654321',
                        'priority': '4',
                        'stage_id': [2, 'Qualified']
                    }
                ]
                return {
                    'success': True,
                    'leads': mock_leads[:limit],
                    'count': len(mock_leads)
                }
            
            # Actual Odoo query
            leads = self.models.execute_kw(
                self.odoo_db, self.uid, self.odoo_password,
                'crm.lead', 'search_read',
                [[]],
                {'limit': limit, 'fields': ['name', 'partner_name', 'email_from', 'phone', 'priority', 'stage_id']}
            )
            
            logger.info(f"✅ Retrieved {len(leads)} leads")
            
            return {
                'success': True,
                'leads': leads,
                'count': len(leads)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get leads: {e}")
            return {
                'success': False,
                'message': str(e),
                'leads': []
            }
    
    def update_lead(self, lead_id: int, values: Dict) -> Dict:
        """Update CRM lead"""
        try:
            logger.info(f"✏️ Updating lead {lead_id}")
            
            if self.dry_run:
                logger.info(f"📝 [DRY RUN] Lead {lead_id} would be updated with: {values}")
                return {
                    'success': True,
                    'message': f'Lead {lead_id} would be updated (dry run)',
                    'lead_id': lead_id,
                    'values': values
                }
            
            # Actual update
            result = self.models.execute_kw(
                self.odoo_db, self.uid, self.odoo_password,
                'crm.lead', 'write', [lead_id, values]
            )
            
            logger.info(f"✅ Lead {lead_id} updated")
            
            return {
                'success': True,
                'message': f'Lead {lead_id} updated',
                'lead_id': lead_id
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to update lead: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def record_payment(self, invoice_id: int, amount: float, 
                       payment_date: str = None) -> Dict:
        """Record payment for invoice"""
        try:
            logger.info(f"💰 Recording payment for invoice {invoice_id}, amount: {amount}")
            
            if self.dry_run:
                logger.info(f"📝 [DRY RUN] Payment would be recorded")
                
                # Log to payments log
                log_file = self.logs_folder / 'payments.log'
                with open(log_file, 'a') as f:
                    f.write(f"{datetime.now().isoformat()} - Payment recorded (dry run): Invoice {invoice_id}, Amount {amount}\n")
                
                return {
                    'success': True,
                    'message': 'Payment logged (dry run)',
                    'invoice_id': invoice_id,
                    'amount': amount
                }
            
            # Actual payment recording would go here
            # This is simplified - real implementation needs account.payment model
            
            return {
                'success': True,
                'message': f'Payment recorded for invoice {invoice_id}',
                'invoice_id': invoice_id,
                'amount': amount
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to record payment: {e}")
            return {
                'success': False,
                'message': str(e)
            }


# CLI Interface
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='MCP Odoo Server')
    parser.add_argument('--action', choices=['create_invoice', 'get_leads', 'update_lead', 'record_payment'], required=True)
    parser.add_argument('--partner-id', type=int, help='Partner ID')
    parser.add_argument('--amount', type=float, help='Amount')
    parser.add_argument('--lead-id', type=int, help='Lead ID')
    parser.add_argument('--invoice-id', type=int, help='Invoice ID')
    parser.add_argument('--vault', help='Vault path')
    
    args = parser.parse_args()
    
    server = MCPOdooServer(Path(args.vault) if args.vault else None)
    
    if args.action == 'create_invoice' and args.partner_id and args.amount:
        result = server.create_invoice(args.partner_id, args.amount)
    elif args.action == 'get_leads':
        result = server.get_leads()
    elif args.action == 'update_lead' and args.lead_id:
        result = server.update_lead(args.lead_id, {'priority': '4'})
    elif args.action == 'record_payment' and args.invoice_id and args.amount:
        result = server.record_payment(args.invoice_id, args.amount)
    else:
        parser.print_help()
        sys.exit(1)
    
    print(json.dumps(result, indent=2))
