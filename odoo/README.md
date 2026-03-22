# 📊 ODOO INTEGRATION - COMPLETE GUIDE

**Personal AI Employee Hackathon 0**  
**Gold & Platinum Tier - Odoo Community Edition**  
**Created:** March 21, 2026

---

## 📋 **TABLE OF CONTENTS**

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [MCP Integration](#mcp-integration)
6. [Testing](#testing)
7. [Hackathon Requirements](#hackathon-requirements)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 **OVERVIEW**

### **What is Odoo Integration?**

Odoo Community Edition is the ERP system integrated into your AI Employee for:
- **Gold Tier:** Accounting, invoicing, CRM
- **Platinum Tier:** Cloud deployment with HTTPS

### **Architecture**

```
┌─────────────────────────────────────────┐
│  AI Employee Vault                     │
│  ┌─────────────────────────────────┐   │
│  │  mcp-odoo/                      │   │
│  │  - Odoo MCP Server              │   │
│  │  - JSON-RPC API                 │   │
│  └──────────────┬──────────────────┘   │
│                 │                       │
│  ┌──────────────▼──────────────────┐   │
│  │  odoo_lead_watcher.py           │   │
│  │  - Monitors Odoo leads          │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  Odoo Community Edition (Docker)       │
│  ┌─────────────────────────────────┐   │
│  │  PostgreSQL Database            │   │
│  │  - Odoo Data                    │   │
│  └─────────────────────────────────┘   │
│                                         │
│  Modules:                               │
│  - CRM (Lead Management)               │
│  - Invoicing (Accounting)              │
│  - Sales                               │
│  - Contacts                            │
└─────────────────────────────────────────┘
```

---

## 🚀 **QUICK START**

### **5-Minute Setup**

```bash
# 1. Navigate to odoo folder
cd "C:\Users\CC\Documents\Obsidian Vault\odoo"

# 2. Copy environment file
copy example.env .env

# 3. Edit .env with your credentials
notepad .env

# 4. Start Odoo
docker-compose up -d

# 5. Access Odoo
# Open browser: http://localhost:8069

# 6. Check status
docker-compose ps
```

### **Default Credentials**

- **Master Password:** `admin_master_password_change_me`
- **Admin Email:** `admin@example.com`
- **Admin Password:** `admin_password_change_me`

**⚠️ Change these immediately in production!**

---

## 📥 **INSTALLATION**

### **Prerequisites**

- Docker Desktop installed
- 4GB RAM available
- 10GB disk space
- Python 3.13+
- Node.js 18+

### **Step 1: Install Docker Desktop**

```bash
# Download from: https://www.docker.com/products/docker-desktop
# Install and restart computer
```

### **Step 2: Setup Odoo**

```bash
cd "C:\Users\CC\Documents\Obsidian Vault"

# Create odoo folder (if not exists)
mkdir odoo
cd odoo

# Copy environment file
copy example.env .env

# Edit .env
notepad .env
```

### **Step 3: Start Odoo**

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f odoo
```

### **Step 4: Install Modules**

1. Open browser: http://localhost:8069
2. Login with admin credentials
3. Go to Apps
4. Install required modules:
   - **CRM** (Lead Management)
   - **Invoicing** (Accounting)
   - **Sales** (Sales Orders)
   - **Contacts** (Customer Database)

---

## ⚙️ **CONFIGURATION**

### **Environment Variables (.env)**

```bash
# Database
ODOO_DB_PASSWORD=your_secure_password
ODOO_ADMIN_PASSWORD=your_admin_password

# Odoo API (for MCP)
ODOO_URL=http://localhost:8069
ODOO_DB=odoo_production
ODOO_USERNAME=admin
ODOO_API_KEY=your_api_key
```

### **Odoo Configuration (odoo.config)**

Key settings:
- `admin_passwd` - Master password
- `db_host` - Database host
- `db_port` - Database port
- `proxy_mode` - Enable for HTTPS

### **MCP Configuration**

Update `mcp-odoo/index.js`:

```javascript
const ODOO_CONFIG = {
  url: process.env.ODOO_URL || 'http://localhost:8069',
  db: process.env.ODOO_DB || 'odoo_production',
  username: process.env.ODOO_USERNAME,
  password: process.env.ODOO_API_KEY,
};
```

---

## 🔗 **MCP INTEGRATION**

### **Odoo MCP Commands**

The `mcp-odoo/` server provides these commands:

1. **create_invoice** - Create customer invoices
2. **record_payment** - Record payments
3. **get_invoices** - List invoices
4. **get_leads** - Get CRM leads
5. **update_lead** - Update lead status
6. **get_transactions** - Get bank transactions
7. **create_partner** - Create customer/partner
8. **search_partners** - Search partners

### **Usage Example**

```javascript
// Create Invoice
await odoo_mcp.create_invoice({
  partner_id: 1,
  invoice_date: '2026-03-21',
  due_date: '2026-04-21',
  lines: [
    {
      product_id: 1,
      quantity: 1,
      price_unit: 1000,
      name: 'Service'
    }
  ]
});

// Get Leads
const leads = await odoo_mcp.get_leads();
```

### **Integration with Watchers**

```python
# odoo_lead_watcher.py
class OdooLeadWatcher:
    def check_for_leads(self):
        # Call Odoo API
        leads = odoo_api.get_leads(new=True)
        
        # Create action files
        for lead in leads:
            self.create_action_file(lead)
```

---

## 🧪 **TESTING**

### **Test Odoo is Running**

```bash
# Check container status
docker-compose ps

# Expected output:
# NAME                      STATUS
# ai-employee-odoo          Up (healthy)
# ai-employee-odoo-db       Up (healthy)
```

### **Test Web Access**

```bash
# Open browser
http://localhost:8069

# Should see Odoo login page
```

### **Test MCP Server**

```bash
cd mcp-odoo
npm start

# Expected: Server starts without errors
```

### **Test Odoo Lead Watcher**

```bash
python odoo_lead_watcher.py

# Expected: Connects to Odoo, checks for leads
```

### **Test Invoice Creation**

```bash
# Via MCP
cd mcp-odoo
npm start

# In another terminal, test create_invoice command
```

---

## ✅ **HACKATHON REQUIREMENTS**

### **Gold Tier Requirements**

| Requirement | Status | File |
|-------------|--------|------|
| Odoo Accounting MCP | ✅ | `mcp-odoo/index.js` |
| Invoice Creation | ✅ | `create_invoice` command |
| Payment Recording | ✅ | `record_payment` command |
| Lead Management | ✅ | `odoo_lead_watcher.py` |
| CRM Integration | ✅ | `get_leads`, `update_lead` |

### **Platinum Tier Requirements**

| Requirement | Status | File |
|-------------|--------|------|
| Cloud Deployment | ✅ | `docker-compose.yml` |
| HTTPS Support | ✅ | Nginx config (deploy script) |
| Backups | ✅ | `backups/` folder |
| Health Monitoring | ✅ | Health checks in docker-compose |
| Draft-Only Mode | ✅ | Cloud mode in MCP |

---

## 📊 **ODOO MODULES FOR HACKATHON**

### **Required Modules**

1. **CRM** (`crm`)
   - Lead management
   - Opportunity tracking
   - Customer communication

2. **Invoicing** (`account_invoice`)
   - Customer invoices
   - Vendor bills
   - Payment tracking

3. **Sales** (`sale_management`)
   - Sales orders
   - Quotations
   - Customer management

4. **Contacts** (`base`)
   - Customer database
   - Partner management

5. **Discuss** (`mail`)
   - Internal communication
   - Customer messages

### **Optional Modules**

- **Website** - Company website
- **eCommerce** - Online store
- **Inventory** - Stock management
- **Project** - Project management
- **Timesheets** - Time tracking

---

## 🗂️ **FILE STRUCTURE**

```
odoo/
├── docker-compose.yml          # Docker setup
├── odoo.config                 # Odoo configuration
├── example.env                 # Environment template
├── .env                        # Environment (create from template)
├── README.md                   # This file
├── logs/                       # Odoo logs
├── backups/                    # Database backups
├── odoo-custom-addons/         # Custom modules (optional)
└── docs/
    ├── ODOO_SETUP.md          # Setup guide
    └── ODOO_MCP.md            # MCP integration
```

---

## 🐛 **TROUBLESHOOTING**

### **Odoo Won't Start**

```bash
# Check logs
docker-compose logs odoo

# Common issues:
# - Port 8069 already in use
# - Database not ready
# - Configuration error

# Fix port conflict
docker-compose down
# Edit docker-compose.yml, change port
docker-compose up -d
```

### **Database Connection Error**

```bash
# Restart database
docker-compose restart db

# Check database logs
docker-compose logs db

# Verify credentials in .env
```

### **MCP Connection Error**

```bash
# Test Odoo API directly
curl http://localhost:8069/web/login

# Check MCP configuration
cat mcp-odoo/index.js | grep ODOO_CONFIG

# Verify credentials
python -c "import xmlrpc.client; print(xmlrpc.client.ServerProxy('http://localhost:8069/xmlrpc/2/common').version())"
```

### **Slow Performance**

```bash
# Increase Odoo workers
# Edit odoo.config: workers = 4

# Increase memory limits
# Edit docker-compose.yml: mem_limit

# Check database performance
docker-compose exec db psql -U odoo -c "SELECT * FROM pg_stat_activity;"
```

---

## 📞 **SUPPORT**

### **Documentation**

- Odoo Official: https://www.odoo.com/documentation
- Odoo 19 API: https://www.odoo.com/documentation/19.0/developer/reference/external_api.html
- Docker Compose: https://docs.docker.com/compose/

### **Hackathon Resources**

- `mcp-odoo/README.md` - MCP server documentation
- `docs/ODOO_SETUP.md` - Detailed setup guide
- `PLATINUM_TIER_ROADMAP.md` - Cloud deployment

---

## 🎯 **NEXT STEPS**

### **After Installation**

1. ✅ Install required modules (CRM, Invoicing, Sales)
2. ✅ Create test customer
3. ✅ Create test invoice
4. ✅ Test MCP commands
5. ✅ Configure odoo_lead_watcher.py
6. ✅ Setup automated backups

### **For Platinum Tier**

1. Deploy to cloud VM
2. Configure HTTPS with Let's Encrypt
3. Setup daily backups
4. Configure cloud monitoring
5. Test draft-only mode

---

**📊 ODOO INTEGRATION COMPLETE!**

*Created: March 21, 2026*  
*Personal AI Employee Hackathon 0*
