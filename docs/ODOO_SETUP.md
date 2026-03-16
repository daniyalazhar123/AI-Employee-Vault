# Odoo 19 Community - Setup Guide

**Status:** Required for Gold Tier
**Purpose:** Local accounting system for AI Employee
**Tier:** Gold Tier Requirement #3

---

## Overview

Odoo Community Edition provides:
- ✅ Accounting & Invoicing
- ✅ CRM & Lead Management
- ✅ Bank Reconciliation
- ✅ Financial Reports
- ✅ Payment Processing

**Gold Tier Requirement:** Create an accounting system in Odoo Community (self-hosted, local) and integrate via MCP server using Odoo's JSON-RPC APIs.

---

## Installation Options

### Option 1: Docker (Recommended - Easiest)

**Prerequisites:**
- Docker Desktop installed
- 2GB free disk space
- Port 8069 available

**Steps:**

1. **Create Docker Compose file:**

```yaml
# docker-compose.yml
version: '3.8'
services:
  odoo:
    image: odoo:19.0
    container_name: odoo_community
    ports:
      - "8069:8069"
    volumes:
      - odoo-data:/var/lib/odoo
      - ./odoo-config:/etc/odoo
    environment:
      - ODOO_DATABASE=odoo
      - ODOO_ADMIN_PASSWORD=admin
    restart: unless-stopped

  db:
    image: postgres:15
    container_name: odoo_postgres
    environment:
      - POSTGRES_DB=odoo
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=odoo
    volumes:
      - postgres-data:/var/lib/postgresql/data

volumes:
  odoo-data:
  postgres-data:
```

2. **Start Odoo:**

```bash
docker-compose up -d
```

3. **Access Odoo:**
   - URL: http://localhost:8069
   - Master Password: admin
   - Create database: odoo
   - Email: admin
   - Password: admin

**Time:** 10-15 minutes

---

### Option 2: Windows Installer

**Steps:**

1. **Download Odoo 19:**
   - Visit: https://www.odoo.com/page/download
   - Select: Community Edition 19.0
   - Download Windows installer

2. **Install:**
   - Run installer
   - Choose installation directory
   - Install PostgreSQL when prompted
   - Set master password: admin

3. **Configure:**
   - Access: http://localhost:8069
   - Create database
   - Install apps

**Time:** 20-30 minutes

---

### Option 3: Ubuntu/Debian

```bash
# Add Odoo repository
wget -O - https://raw.githubusercontent.com/odoo/odoo/master/odoo/release.py | python3 -
sudo apt install odoo

# Start service
sudo systemctl start odoo
sudo systemctl enable odoo

# Access
http://localhost:8069
```

---

## Database Setup

### Step 1: Create Database

1. Go to http://localhost:8069
2. Click "Create Database"
3. Enter:
   - Master Password: admin
   - Database Name: odoo
   - Email: admin@example.com
   - Password: admin

### Step 2: Install Required Apps

Navigate to **Apps** menu and install:

1. **Invoicing** (account)
   - Customer invoices
   - Vendor bills
   - Payments
   - Bank reconciliation

2. **CRM** (crm)
   - Lead management
   - Pipeline tracking
   - Opportunities

3. **Contacts** (contacts)
   - Customer database
   - Vendor database
   - Partner management

4. **Sales** (sale_management) - Optional
   - Quotations
   - Sales orders

**Time:** 5-10 minutes

---

## Configuration

### Step 1: Configure Company

1. Go to **Settings → Companies**
2. Update:
   - Company Name: Your Company
   - Address
   - Currency
   - Fiscal Year

### Step 2: Configure Accounting

1. Go to **Invoicing → Configuration → Settings**
2. Enable:
   - ✅ Customer Invoices
   - ✅ Vendor Bills
   - ✅ Payments
   - ✅ Bank Synchronization

### Step 3: Create Products

1. Go to **Invoicing → Products → Products**
2. Create sample products:
   - Consulting Services ($100/hour)
   - Product A ($50)
   - Product B ($75)

### Step 4: Create Test Customer

1. Go to **Contacts → Create**
2. Enter:
   - Name: Test Customer
   - Email: customer@example.com
   - Type: Invoice Address

---

## Testing Odoo MCP Connection

### Test Script

Create `test_odoo_mcp.js`:

```javascript
const xmlrpc = require('xmlrpc');

const config = {
  url: 'http://localhost:8069',
  db: 'odoo',
  username: 'admin',
  password: 'admin'
};

function testConnection() {
  const client = xmlrpc.createClient({ 
    host: new URL(config.url).hostname,
    port: 8069,
    path: '/xmlrpc/2/common'
  });

  client.method_call(
    'authenticate',
    [config.db, config.username, config.password, {}],
    (err, uid) => {
      if (err) {
        console.error('❌ Connection failed:', err.message);
      } else if (uid) {
        console.log('✅ Connected successfully!');
        console.log('User ID:', uid);
        testLeads(uid);
      } else {
        console.error('❌ Authentication failed');
      }
    }
  );
}

function testLeads(uid) {
  const modelsClient = xmlrpc.createClient({ 
    host: new URL(config.url).hostname,
    port: 8069,
    path: '/xmlrpc/2/object'
  });

  modelsClient.method_call(
    'execute_kw',
    [config.db, uid, config.password, 'crm.lead', 'search_read', [[]], {
      fields: ['id', 'name', 'partner_name', 'email_from'],
      limit: 5
    }],
    (err, result) => {
      if (err) {
        console.error('Error:', err.message);
      } else {
        console.log('✅ Leads retrieved:', result.length);
        console.log(result);
      }
    }
  );
}

testConnection();
```

**Run:**
```bash
cd mcp-odoo
node test_odoo_mcp.js
```

---

## Integration with AI Employee

### Workflow: Invoice Creation

```
1. Odoo Lead Watcher detects new lead
2. Creates ODOO_LEAD_*.md in Needs_Action/
3. Orchestrator processes with Qwen
4. Qwen drafts invoice details
5. Human approves in Pending_Approval/
6. Odoo MCP creates invoice
7. Email MCP sends invoice
8. Logged in Dashboard.md
```

### Workflow: Payment Recording

```
1. Finance Watcher detects bank transaction
2. Creates BANK_TRANSACTION_*.md
3. Qwen matches with open invoice
4. Odoo MCP records payment
5. Updates accounting ledger
6. CEO Briefing includes payment data
```

---

## Odoo MCP Commands

### Create Invoice

```javascript
@odoo Create invoice for Test Customer:
- Product: Consulting Services
- Quantity: 10 hours
- Price: $100/hour
- Due: 30 days
```

### Record Payment

```javascript
@odoo Record payment:
- Invoice: INV/2026/0001
- Amount: $1000
- Date: Today
- Reference: Bank Transfer
```

### Get Invoices

```javascript
@odoo Get all posted invoices from last month
```

### Get Financial Summary

```javascript
@odoo Get accounts receivable summary
```

---

## Troubleshooting

### Error: "Connection refused"

**Solution:**
- Check Odoo is running: http://localhost:8069
- Verify port 8069 not blocked
- Check Docker container: `docker ps`

### Error: "Database not found"

**Solution:**
- Verify database name: odoo
- Check database exists
- Recreate if needed

### Error: "Authentication failed"

**Solution:**
- Check username/password
- Reset password in Odoo
- Verify database access

---

## Next Steps

After Odoo is setup:

1. ✅ Test Odoo MCP connection
2. ✅ Create test invoices
3. ✅ Record test payments
4. ✅ Integrate with CEO Briefing
5. ✅ Setup bank reconciliation
6. ✅ Generate financial reports

---

## Gold Tier Status

| Component | Status |
|-----------|--------|
| Odoo Installed | ⚠️ Pending |
| Database Created | ⚠️ Pending |
| Apps Installed | ⚠️ Pending |
| MCP Connection | ⚠️ Pending |
| Test Invoices | ⚠️ Pending |
| CEO Briefing Integration | ⚠️ Pending |

---

**Estimated Setup Time:** 30-60 minutes
**Difficulty:** Intermediate
**Gold Tier Points:** 15%

---

*Odoo 19 Community Setup Guide for AI Employee Gold Tier*
