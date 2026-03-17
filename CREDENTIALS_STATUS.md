# 🔐 CREDENTIALS STATUS REPORT

**Date:** March 17, 2026
**Project:** AI Employee Vault

---

## 📊 CURRENT CREDENTIALS STATUS

### ✅ **PRESENT (Already Configured)**

| Credential | Location | Status | Ready to Use? |
|------------|----------|--------|---------------|
| **Gmail OAuth** | `credentials.json` | ✅ Present | ⚠️ Need to generate token |
| **Odoo Config** | `config/mcp.json` | ✅ Present | ⚠️ Need Odoo installed |
| **Social Media** | Browser-based | ✅ No credentials needed | ✅ Ready |
| **WhatsApp** | Browser-based | ✅ No credentials needed | ✅ Ready |

---

## ⚠️ **MISSING (Need to Create/Generate)**

| Credential | What's Missing | How to Get | Time |
|------------|---------------|------------|------|
| **Gmail Token** | `mcp-email/token.json` | Run `node authenticate.js` | 5 min |
| **Odoo System** | Odoo not installed | Install via Docker | 30 min |
| **Environment File** | `config/.env` | Copy from `.env.example` | 2 min |

---

## 🎯 STEP-BY-STEP: GET MISSING CREDENTIALS

---

## 1️⃣ GMAIL TOKEN (Missing)

### Current Status:
- ✅ `credentials.json` - **PRESENT** (Google OAuth credentials)
- ❌ `mcp-email/token.json` - **MISSING** (Authentication token)

### How to Generate Token:

```bash
cd "C:\Users\CC\Documents\Obsidian Vault\mcp-email"
node authenticate.js
```

**What Happens:**
1. Browser opens automatically
2. You sign in with your Google account
3. You grant permissions
4. Token saved to `mcp-email/token.json`

**After Completion:**
```
✅ Token saved to: mcp-email/token.json
You can now use the MCP Email Server!
```

**Test It:**
```bash
npm start
```

---

## 2️⃣ ODOO CREDENTIALS (Missing - Odoo Not Installed)

### Current Status:
- ❌ Odoo server - **NOT INSTALLED**
- ✅ MCP config - **PRESENT** (admin/admin)
- ❌ API Key - **NOT NEEDED** (uses password auth)

---

### 📘 HOW TO GET ODOO CREDENTIALS

### **Option A: Install Odoo Locally (Recommended)**

#### Step 1: Install Docker Desktop

1. Download: https://www.docker.com/products/docker-desktop/
2. Install Docker Desktop
3. Start Docker Desktop

**Time:** 10 minutes

---

#### Step 2: Run Odoo Container

```bash
docker run -d -p 8069:8069 \
  --name odoo_community \
  -e ODOO_DATABASE=odoo \
  -e ODOO_ADMIN_PASSWORD=admin \
  odoo:19.0
```

**What This Does:**
- Downloads Odoo 19.0 image
- Starts Odoo on port 8069
- Sets admin password to "admin"
- Creates database named "odoo"

**Time:** 5 minutes (first time downloads ~500MB)

---

#### Step 3: Create Odoo Database

1. Open browser: http://localhost:8069
2. Click **"Create Database"**
3. Fill in:
   - **Master Password:** `admin`
   - **Database Name:** `odoo`
   - **Email:** `admin@example.com`
   - **Password:** `admin`
4. Click **"Create Database"**
5. Wait 2-3 minutes for database creation

**Time:** 3 minutes

---

#### Step 4: Install Odoo Apps

After database created:

1. Go to **Apps** menu (top)
2. Search and install these apps:
   - Click **"Invoicing"** → Install
   - Click **"CRM"** → Install
   - Click **"Contacts"** → Install

**Time:** 5 minutes

---

#### Step 5: Your Odoo Credentials

After installation, your credentials are:

```
URL:      http://localhost:8069
Database: odoo
Username: admin
Password: admin
API Key:  NOT NEEDED (uses password authentication)
```

**These are already configured in your MCP!** ✅

---

#### Step 6: Test Odoo Connection

```bash
cd "C:\Users\CC\Documents\Obsidian Vault\mcp-odoo"
npm start
```

If you see:
```
Odoo MCP Server running
Connected to Odoo at http://localhost:8069
```

**Success!** ✅

---

### **Option B: Use Odoo Online (Cloud - No Installation)**

If you don't want to install Docker:

#### Step 1: Sign Up for Odoo Trial

1. Go to: https://www.odoo.com/trial
2. Enter your email
3. Choose apps: Invoicing, CRM, Contacts
4. Click **"Start Now"**

**Time:** 5 minutes

---

#### Step 2: Get Your Odoo URL

After signup, you get:
```
Your Odoo URL: https://yourcompany.odoo.com
```

---

#### Step 3: Update MCP Configuration

Edit `config/mcp.json`:

```json
{
  "mcpServers": {
    "odoo": {
      "command": "node",
      "args": ["C:/Users/CC/Documents/Obsidian Vault/mcp-odoo/index.js"],
      "env": {
        "ODOO_URL": "https://yourcompany.odoo.com",
        "ODOO_DB": "yourcompany",
        "ODOO_USERNAME": "your-email@example.com",
        "ODOO_PASSWORD": "your-password"
      }
    }
  }
}
```

**Replace:**
- `yourcompany.odoo.com` with your actual URL
- `your-email@example.com` with your login email
- `your-password` with your password

---

#### Step 4: Get Odoo API Key (Optional but Recommended)

**Why Get API Key:**
- More secure than password
- Doesn't expire
- Can be revoked anytime

**How to Get API Key:**

1. Login to your Odoo
2. Click your profile (top right)
3. Click **"My Profile"**
4. Scroll to **"API Keys"** section
5. Click **"Add API Key"**
6. Enter description: "AI Employee MCP"
7. Click **"Add"**
8. **Copy the API key immediately** (won't show again!)

**Example API Key:**
```
7f8a9b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a
```

---

#### Step 5: Add API Key to Configuration

Edit `config/mcp.json` again:

```json
{
  "mcpServers": {
    "odoo": {
      "command": "node",
      "args": ["C:/Users/CC/Documents/Obsidian Vault/mcp-odoo/index.js"],
      "env": {
        "ODOO_URL": "https://yourcompany.odoo.com",
        "ODOO_DB": "yourcompany",
        "ODOO_USERNAME": "your-email@example.com",
        "ODOO_PASSWORD": "your-password",
        "ODOO_API_KEY": "7f8a9b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a"
      }
    }
  }
}
```

**Note:** API Key is **optional** for Odoo Online, **not available** for local Odoo.

---

## 3️⃣ ENVIRONMENT FILE (Missing)

### Current Status:
- ✅ `config/.env.example` - **PRESENT**
- ❌ `config/.env` - **MISSING**

### How to Create:

```bash
cd "C:\Users\CC\Documents\Obsidian Vault\config"
copy .env.example .env
```

Then edit `.env` with your values:

```bash
# Gmail (already configured in credentials.json)
GMAIL_CLIENT_ID=11790628161-9b6jjvfvgq918cp3rtg3fjads5s30dvg.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=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

# Odoo (after installation)
ODOO_URL=http://localhost:8069
ODOO_DATABASE=odoo
ODOO_USERNAME=admin
ODOO_PASSWORD=admin

# Odoo API Key (if using Odoo Online)
# ODOO_API_KEY=your-api-key-here
```

**Time:** 2 minutes

---

## 📋 COMPLETE CREDENTIALS CHECKLIST

### Gmail (Email Integration)
- [x] ✅ `credentials.json` exists
- [ ] ⚠️ Generate token: `cd mcp-email && node authenticate.js`
- [ ] ⚠️ Test: `npm start`

### Odoo (Accounting Integration)
- [ ] ⚠️ Install Odoo (Docker or Online)
- [ ] ⚠️ Create database
- [ ] ⚠️ Install apps (Invoicing, CRM, Contacts)
- [ ] ⚠️ Get credentials (URL, DB, username, password)
- [ ] ⚠️ (Optional) Get API key from Odoo Online
- [ ] ⚠️ Update `config/mcp.json` if using Odoo Online
- [ ] ⚠️ Test: `cd mcp-odoo && npm start`

### Social Media (No Credentials Needed)
- [x] ✅ Browser automation configured
- [ ] ⚠️ First login when script runs

### WhatsApp (No Credentials Needed)
- [x] ✅ Browser automation configured
- [ ] ⚠️ First QR scan when script runs

### Environment File
- [ ] ⚠️ Create `config/.env` from `.env.example`
- [ ] ⚠️ Fill in values

---

## 🔑 ODOO API KEY - DETAILED GUIDE

### What is Odoo API Key?

An API key is an **alternative to password** for authenticating with Odoo:

| Feature | Password | API Key |
|---------|----------|---------|
| **Security** | Less secure | More secure |
| **Expiration** | Never | Never (but can revoke) |
| **Availability** | Local & Online | Online only |
| **Recommended** | For testing | For production |

---

### Who Can Get API Key?

- ✅ **Odoo Online** (cloud.odoo.com) - **YES**
- ✅ **Odoo.sh** (hosting) - **YES**
- ❌ **Odoo Community** (self-hosted) - **NO** (uses password only)

**If you're using local Docker Odoo, you DON'T need API key!**

---

### How to Get API Key from Odoo Online

#### Step 1: Login to Odoo Online

```
https://yourcompany.odoo.com
```

---

#### Step 2: Go to My Profile

1. Click your **avatar/profile picture** (top right corner)
2. Click **"My Profile"** or **"Preferences"**

---

#### Step 3: Find API Keys Section

Scroll down to **"Security"** or **"API Keys"** section

---

#### Step 4: Create New API Key

1. Click **"Add API Key"** or **"Generate API Key"**
2. Enter description: `AI Employee MCP Server`
3. Click **"Add"** or **"Generate"**

---

#### Step 5: Copy API Key Immediately

**IMPORTANT:** The API key is shown **ONLY ONCE**!

Example:
```
7f8a9b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a
```

**Copy it now and save it securely!**

---

#### Step 6: Store API Key Securely

**Option 1: In MCP Config**

Edit `config/mcp.json`:

```json
{
  "mcpServers": {
    "odoo": {
      "env": {
        "ODOO_API_KEY": "7f8a9b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a"
      }
    }
  }
}
```

**Option 2: In .env File**

Create `config/.env`:

```bash
ODOO_API_KEY=7f8a9b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a
```

**Option 3: In Password Manager**

Save in 1Password, LastPass, Bitwarden, etc.

---

### How to Use API Key in MCP

Your Odoo MCP already supports API keys!

**With API Key:**
```json
{
  "env": {
    "ODOO_URL": "https://yourcompany.odoo.com",
    "ODOO_DB": "yourcompany",
    "ODOO_USERNAME": "admin@example.com",
    "ODOO_PASSWORD": "your-password",
    "ODOO_API_KEY": "7f8a9b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a"
  }
}
```

**Without API Key (Local Odoo):**
```json
{
  "env": {
    "ODOO_URL": "http://localhost:8069",
    "ODOO_DB": "odoo",
    "ODOO_USERNAME": "admin",
    "ODOO_PASSWORD": "admin"
  }
}
```

---

### API Key vs Password - Which to Use?

| Scenario | Use Password | Use API Key |
|----------|--------------|-------------|
| **Local Odoo (Docker)** | ✅ Yes | ❌ Not available |
| **Odoo Online Trial** | ⚠️ OK | ✅ Recommended |
| **Production Odoo** | ❌ No | ✅ Required |
| **Testing/Development** | ✅ Yes | ⚠️ Optional |

---

## 🎯 RECOMMENDED SETUP ORDER

### For Testing (Minimum Credentials)

1. **Generate Gmail Token** (5 min)
   ```bash
   cd mcp-email && node authenticate.js
   ```

2. **Install Playwright** (5 min)
   ```bash
   playwright install chromium
   ```

**Done!** You can test email, WhatsApp, and social media features.

---

### For Full Gold Tier (All Credentials)

1. **Generate Gmail Token** (5 min)
2. **Install Odoo via Docker** (30 min)
3. **Create Odoo Database** (3 min)
4. **Install Odoo Apps** (5 min)
5. **Create Environment File** (2 min)

**Total Time:** 45 minutes

---

## 📞 VERIFICATION COMMANDS

### Check Gmail Credentials
```bash
cd mcp-email
dir token.json
# Should show file if exists
```

### Check Odoo Connection
```bash
cd mcp-odoo
npm start
# Should show "Connected to Odoo"
```

### Check All Credentials
```bash
# Check credentials.json
dir credentials.json

# Check MCP config
type config\mcp.json

# Check .env file
dir config\.env
```

---

## 🔒 SECURITY NOTES

### Never Share These Files:
- ❌ `credentials.json` (Gmail OAuth)
- ❌ `mcp-email/token.json` (Gmail token)
- ❌ `config/.env` (Environment variables)
- ❌ Odoo API keys

### Add to .gitignore:
```gitignore
# Credentials
credentials.json
mcp-email/token.json
config/.env
*.env
```

### Rotate Credentials:
- Gmail token: Every 30 days
- Odoo password: Every 90 days
- Odoo API key: If compromised

---

## 📊 FINAL STATUS

| Credential | Status | Action Needed |
|------------|--------|---------------|
| Gmail OAuth | ✅ Present | Generate token |
| Gmail Token | ❌ Missing | Run authenticate.js |
| Odoo Server | ❌ Not installed | Install via Docker |
| Odoo Credentials | ⚠️ Default (admin/admin) | Change after install |
| Odoo API Key | ❌ Not needed (local) | Optional for Online |
| Environment File | ❌ Missing | Copy from .env.example |
| Social Media | ✅ Not needed | First login in browser |
| WhatsApp | ✅ Not needed | First QR scan |

---

## 🎉 SUMMARY

### What You Have:
- ✅ Gmail OAuth credentials (`credentials.json`)
- ✅ MCP configuration (`config/mcp.json`)
- ✅ All code ready to use

### What You Need:
- ⚠️ Generate Gmail token (5 min)
- ⚠️ Install Odoo (30 min) - optional for testing
- ⚠️ Create .env file (2 min)

### What You DON'T Need:
- ❌ Facebook API key
- ❌ Instagram API key
- ❌ LinkedIn API key
- ❌ Twitter API key
- ❌ WhatsApp API key

**All social media uses browser automation - NO API keys needed!**

---

**Status:** Ready to setup
**Time Required:** 5-45 minutes (depending on features needed)
**Difficulty:** Easy to Intermediate

---

*This guide helps you get all missing credentials for AI Employee Vault.*
