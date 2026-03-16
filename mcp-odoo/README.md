# MCP Odoo Server

**Status:** ✅ **COMPLETE**
**Tier:** Gold
**Purpose:** Enable Claude Code to integrate with Odoo ERP for accounting and CRM

---

## Overview

This MCP (Model Context Protocol) server provides Odoo ERP capabilities to Claude Code:

- 📄 **create_invoice** - Create customer invoices
- 💰 **record_payment** - Record payments
- 📋 **get_invoices** - List invoices
- 🎯 **get_leads** - Get CRM leads
- ✏️ **update_lead** - Update lead status
- 🏦 **get_transactions** - Get bank transactions
- 👤 **create_partner** - Create customer/partner
- 🔍 **search_partners** - Search partners

---

## Installation

### Step 1: Install Dependencies

```bash
cd mcp-odoo
npm install
```

### Step 2: Setup Odoo

You need Odoo 19+ Community or Enterprise edition:

**Option A: Local Installation**
```bash
# Download Odoo 19 Community
# https://www.odoo.com/page/download
# Install locally on port 8069
```

**Option B: Docker**
```bash
docker run -d -p 8069:8069 --name odoo -e ODOO_DATABASE=odoo odoo:19.0
```

**Option C: Odoo Online**
- Use Odoo.sh or Odoo Online
- Update ODOO_URL in configuration

---

## Configuration

### Environment Variables

Create `.env` file or set environment variables:

```bash
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=admin
ODOO_PASSWORD=admin
ODOO_API_KEY=  # Optional for newer Odoo versions
```

### Claude Code MCP Config

Add to your Claude Code MCP settings:

**Windows:** `%APPDATA%\claude-code\mcp.json`
**Mac/Linux:** `~/.config/claude-code/mcp.json`

```json
{
  "mcpServers": {
    "odoo": {
      "command": "node",
      "args": ["C:/Users/CC/Documents/Obsidian Vault/mcp-odoo/index.js"],
      "env": {
        "ODOO_URL": "http://localhost:8069",
        "ODOO_DB": "odoo",
        "ODOO_USERNAME": "admin",
        "ODOO_PASSWORD": "admin"
      }
    }
  }
}
```

---

## Usage in Claude Code

Once configured, you can use Odoo capabilities in Claude Code:

### Create Invoice

```
@odoo Create an invoice for partner ID 5 with these items:
- Product: Consulting Services
- Quantity: 10 hours
- Price: $100/hour
- Due date: 30 days from now
```

### Record Payment

```
@odoo Record a payment of $1000 for invoice #INV-2026-001 received via bank transfer
```

### Get Invoices

```
@odoo Show me all posted invoices from the last month
```

### Get CRM Leads

```
@odoo Get all new leads from this week
```

### Update Lead

```
@odoo Update lead ID 10 to stage "Qualified" and priority to 4/5
```

### Get Transactions

```
@odoo Show me the last 20 bank transactions
```

### Create Partner

```
@odoo Create a new customer:
- Name: John Smith
- Email: john@example.com
- Phone: +1-555-0123
- Company: ABC Corp
```

---

## API Reference

### create_invoice

Create a customer invoice.

**Parameters:**
- `partner_id` (required): Customer/partner ID
- `invoice_date` (optional): Invoice date (YYYY-MM-DD)
- `due_date` (optional): Due date (YYYY-MM-DD)
- `lines` (required): Invoice line items
  - `product_id`: Product ID
  - `name`: Description
  - `quantity`: Quantity
  - `price_unit`: Unit price

**Example:**
```json
{
  "partner_id": 5,
  "invoice_date": "2026-03-16",
  "due_date": "2026-04-15",
  "lines": [
    {
      "product_id": 1,
      "name": "Consulting Services",
      "quantity": 10,
      "price_unit": 100
    }
  ]
}
```

### record_payment

Record a payment for an invoice.

**Parameters:**
- `invoice_id` (required): Invoice ID
- `amount` (required): Payment amount
- `payment_date` (optional): Payment date
- `reference` (optional): Payment reference

### get_invoices

List invoices.

**Parameters:**
- `state` (optional): Invoice state (draft, posted, cancel)
- `limit` (optional): Maximum results
- `partner_id` (optional): Filter by partner

### get_leads

Get CRM leads.

**Parameters:**
- `stage` (optional): Filter by stage
- `limit` (optional): Maximum results
- `my_leads` (optional): Only my leads

### update_lead

Update a CRM lead.

**Parameters:**
- `lead_id` (required): Lead ID
- `values` (required): Fields to update

### get_transactions

Get bank transactions.

**Parameters:**
- `account_id` (optional): Bank account ID
- `limit` (optional): Maximum results

### create_partner

Create a new partner.

**Parameters:**
- `name` (required): Partner name
- `email` (optional): Email
- `phone` (optional): Phone
- `company_name` (optional): Company
- `is_customer` (optional): Mark as customer

### search_partners

Search for partners.

**Parameters:**
- `query` (optional): Search query
- `limit` (optional): Maximum results

---

## Use Cases for AI Employee

### 1. Automated Invoicing

When a project is completed:
```
1. Check project completion in tracker
2. @odoo Create invoice for customer
3. @email Send invoice to customer
4. Log in Dashboard.md
```

### 2. Payment Reconciliation

When bank transaction detected:
```
1. @odoo Get transactions
2. Match with open invoices
3. @odoo Record payment
4. Update Dashboard.md
```

### 3. Lead Follow-up

When new lead created:
```
1. @odoo Get new leads
2. Create action file in Needs_Action/
3. Draft follow-up email
4. Schedule call
```

### 4. Weekly Accounting Audit

Every Monday:
```
1. @odoo Get invoices from last week
2. @odoo Get payments received
3. @odoo Get outstanding receivables
4. Generate CEO Briefing
```

---

## Integration with AI Employee

### Workflow: Invoice Creation

```
Project completed
  → Odoo Lead Watcher detects
  → Action file created
  → Claude drafts invoice details
  → Human approves
  → Odoo MCP creates invoice
  → Email MCP sends invoice
  → Logged in Done/
```

### Workflow: Payment Recording

```
Bank transaction detected
  → Finance Watcher logs transaction
  → Odoo MCP matches with invoice
  → Creates payment entry
  → Updates Dashboard.md
  → Moves to Done/
```

---

## Troubleshooting

### Error: "Authentication failed"

**Solution:**
- Check ODOO_USERNAME and ODOO_PASSWORD
- Verify Odoo server is running
- Check database name is correct

### Error: "Connection refused"

**Solution:**
- Verify ODOO_URL is correct
- Check Odoo is listening on port 8069
- Check firewall settings

### Error: "Model not found"

**Solution:**
- Verify Odoo version (19+)
- Check module is installed (account, crm)
- Verify model name is correct

---

## Security Considerations

1. **Never expose Odoo** directly to internet without HTTPS
2. **Use API keys** instead of passwords when possible
3. **Implement approval workflow** for payments > $500
4. **Log all actions** for audit trail
5. **Restrict user permissions** in Odoo
6. **Backup regularly**

---

## Odoo Setup Guide

### Install Odoo 19 Community

**Ubuntu/Debian:**
```bash
wget -O - https://raw.githubusercontent.com/odoo/odoo/master/odoo/release.py | python3 -
sudo apt install odoo
```

**Docker:**
```bash
docker run -d -p 8069:8069 \
  -e ODOO_DATABASE=odoo \
  -e ODOO_ADMIN_PASSWORD=admin \
  --name odoo \
  odoo:19.0
```

**Windows:**
1. Download installer from odoo.com
2. Run installer
3. Set master password
4. Create database

### Configure Database

1. Go to http://localhost:8069
2. Create database: `odoo`
3. Install apps:
   - Invoicing (account)
   - CRM (crm)
   - Contacts (contacts)

### Create User

1. Go to Settings → Users
2. Create user: `admin`
3. Set password: `admin`
4. Grant permissions:
   - Accounting / User
   - CRM / User

---

## Files

```
mcp-odoo/
├── package.json          # Dependencies
├── index.js             # Main MCP server
├── README.md            # This file
└── .env.example         # Environment template
```

---

## Development

### Run in Development

```bash
npm start
```

### Test Connection

```bash
node -e "
const xmlrpc = require('xmlrpc');
const client = xmlrpc.createClient({ host: 'localhost', port: 8069, path: '/xmlrpc/2/common' });
client.method_call('authenticate', ['odoo', 'admin', 'admin', {}], (err, uid) => {
  console.log('UID:', uid);
});
"
```

---

## Next Steps

After Odoo MCP is working:

1. ✅ Test with Claude Code
2. ✅ Create invoice workflows
3. ✅ Integrate with Gmail Watcher
4. ⏭️ Build Social MCP
5. ⏭️ Setup cloud deployment

---

## References

- [MCP SDK Documentation](https://modelcontextprotocol.io/)
- [Odoo 19 External API](https://www.odoo.com/documentation/19.0/developer/reference/external_api.html)
- [Official MCP Examples](https://github.com/modelcontextprotocol/servers)

---

**Status:** ✅ **Gold Tier - COMPLETE**

*Created: March 16, 2026*
