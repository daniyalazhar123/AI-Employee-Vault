# 🔐 Credentials Guide - AI Employee Vault

**Complete guide to obtaining and configuring credentials for all integrations**

---

## 📋 Quick Summary

| Service | Credentials Needed | Status | Difficulty | Time |
|---------|-------------------|--------|------------|------|
| **Gmail** | Google OAuth 2.0 | ⚠️ Required | Easy | 10 min |
| **WhatsApp** | None (uses WhatsApp Web) | ✅ Not needed | N/A | N/A |
| **Odoo** | Admin username/password | ⚠️ Required | Medium | 30 min |
| **Facebook** | None (uses browser automation) | ✅ Not needed | N/A | N/A |
| **Instagram** | None (uses browser automation) | ✅ Not needed | N/A | N/A |
| **LinkedIn** | None (uses browser automation) | ✅ Not needed | N/A | N/A |
| **Twitter (X)** | None (uses browser automation) | ✅ Not needed | N/A | N/A |

**Good News:** Most services use **browser automation** (Playwright) instead of APIs, so **NO API credentials needed!**

---

## 1️⃣ GMAIL CREDENTIALS (Required)

### What You Need:
- Google Account
- Google Cloud Console project
- OAuth 2.0 credentials

### Step-by-Step Guide:

#### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Create Project"** or select existing project
3. Enter project name: `AI Employee`
4. Click **"Create"**

**Time:** 2 minutes

---

#### Step 2: Enable Gmail API

1. In your project, go to **"APIs & Services" → "Library"**
2. Search for **"Gmail API"**
3. Click on **"Gmail API"**
4. Click **"Enable"**

**Time:** 1 minute

---

#### Step 3: Create OAuth 2.0 Credentials

1. Go to **"APIs & Services" → "Credentials"**
2. Click **"+ CREATE CREDENTIALS"**
3. Select **"OAuth client ID"**

**If prompted to configure consent screen:**
1. Select **"External"** user type
2. Click **"Create"**
3. Fill in:
   - App name: `AI Employee`
   - User support email: Your email
   - Developer contact: Your email
4. Click **"Save and Continue"**
5. Skip scopes (click **"Save and Continue"**)
6. Add test users (add your Gmail address)
7. Click **"Save and Continue"**

**Back to creating credentials:**
1. Application type: **"Desktop app"**
2. Name: `AI Employee Gmail`
3. Click **"Create"**

**Time:** 5 minutes

---

#### Step 4: Download Credentials

1. After creating, click **"Download JSON"**
2. Save file as `credentials.json`
3. Copy to your vault:
   ```
   C:\Users\CC\Documents\Obsidian Vault\credentials.json
   ```

**Your credentials.json should look like:**
```json
{
  "installed": {
    "client_id": "11790628161-xxxxxxx.apps.googleusercontent.com",
    "project_id": "ai-employee-xxxxx",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "GOCSPX-xxxxxxxxxxxxx",
    "redirect_uris": ["http://localhost"]
  }
}
```

**✅ You already have this configured!**

---

#### Step 5: Generate Gmail Token

**You already have credentials configured! Now generate the token:**

```bash
cd "C:\Users\CC\Documents\Obsidian Vault\mcp-email"
node authenticate.js
```

**What happens:**
1. Script opens browser
2. Sign in with your Google account
3. Grant permissions
4. Token saved to `mcp-email/token.json`

**Time:** 3 minutes

---

#### Step 6: Verify Token Created

Check if `token.json` exists:
```bash
ls mcp-email\token.json
```

**Success!** You should see:
```
✅ Token saved to: mcp-email/token.json
```

---

#### Testing Gmail MCP

```bash
cd mcp-email
npm start
```

Then in Claude Code:
```
@email Search for unread emails
```

---

### Troubleshooting Gmail

**Error: "Access blocked"**
- Add your email to test users in consent screen
- Wait 5 minutes for changes to propagate

**Error: "Token expired"**
- Delete `token.json`
- Re-run `node authenticate.js`

**Error: "Credentials not found"**
- Verify `credentials.json` is in vault root
- Check file is valid JSON

---

## 2️⃣ WHATSAPP (No Credentials Needed!)

### How It Works:
- Uses **WhatsApp Web** (web.whatsapp.com)
- Automated with **Playwright** browser
- **NO API credentials required**
- **NO phone number verification needed**

### Setup:

1. **Install Playwright:**
   ```bash
   playwright install chromium
   ```

2. **Manual Login (First Time):**
   - Open WhatsApp Web in browser
   - Scan QR code with your phone
   - Session saved in `whatsapp_session/` folder

3. **Watcher Uses Saved Session:**
   - `whatsapp_watcher.py` uses saved session
   - No need to scan QR every time

### Testing:

```bash
cd watchers
python whatsapp_watcher.py
```

**That's it! No credentials needed.**

---

## 3️⃣ ODOO CREDENTIALS (Required for Gold Tier)

### What You Need:
- Odoo 19+ Community Edition (self-hosted)
- Admin username/password
- Database name

### Option A: Install Odoo Locally (Recommended for Testing)

#### Step 1: Install via Docker (Easiest)

**Prerequisites:**
- Docker Desktop installed

**Steps:**

1. **Create `docker-compose.yml`:**
   ```yaml
   version: '3.8'
   services:
     odoo:
       image: odoo:19.0
       container_name: odoo_community
       ports:
         - "8069:8069"
       environment:
         - ODOO_DATABASE=odoo
         - ODOO_ADMIN_PASSWORD=admin
       volumes:
         - odoo-data:/var/lib/odoo
   ```

2. **Start Odoo:**
   ```bash
   docker-compose up -d
   ```

3. **Access Odoo:**
   - URL: http://localhost:8069
   - Wait 2-3 minutes for first startup

**Time:** 10 minutes

---

#### Step 2: Create Database

1. Go to http://localhost:8069
2. Click **"Create Database"**
3. Enter:
   - Master Password: `admin`
   - Database Name: `odoo`
   - Email: `admin@example.com`
   - Password: `admin`
4. Click **"Create Database"**

**Time:** 2 minutes

---

#### Step 3: Install Apps

1. Go to **Apps** menu
2. Install these apps:
   - **Invoicing** (accounting)
   - **CRM** (lead management)
   - **Contacts** (customer database)

**Time:** 5 minutes

---

#### Step 4: Configure MCP

Your Odoo MCP is already configured with these credentials:

```json
{
  "ODOO_URL": "http://localhost:8069",
  "ODOO_DB": "odoo",
  "ODOO_USERNAME": "admin",
  "ODOO_PASSWORD": "admin"
}
```

**Location:** `config/mcp.json`

---

#### Step 5: Test Odoo Connection

```bash
cd mcp-odoo
npm start
```

Then in Claude Code:
```
@odoo Get all leads
```

---

### Option B: Use Odoo Online (No Installation)

If you don't want to install Odoo locally:

1. **Sign up for Odoo Online:**
   - Go to https://www.odoo.com/trial
   - Create free trial account
   - Get your Odoo URL (e.g., `yourcompany.odoo.com`)

2. **Update MCP config:**
   ```json
   {
     "ODOO_URL": "https://yourcompany.odoo.com",
     "ODOO_DB": "yourcompany",
     "ODOO_USERNAME": "your-email@example.com",
     "ODOO_PASSWORD": "your-password"
   }
   ```

**Note:** Free trial expires after 14 days.

---

### Odoo Credentials Summary

| Setting | Value (Local) | Value (Online) |
|---------|--------------|----------------|
| ODOO_URL | http://localhost:8069 | https://yourcompany.odoo.com |
| ODOO_DB | odoo | yourcompany |
| ODOO_USERNAME | admin | your-email@example.com |
| ODOO_PASSWORD | admin | your-password |

---

## 4️⃣ SOCIAL MEDIA (No Credentials Needed!)

### Facebook, Instagram, LinkedIn, Twitter

**Great News:** All social media integrations use **browser automation** instead of APIs!

### Why No API Credentials?

| Platform | API Difficulty | Our Solution |
|----------|---------------|--------------|
| **Facebook** | Complex API, app review | ✅ Browser automation |
| **Instagram** | Requires Facebook app | ✅ Browser automation |
| **LinkedIn** | API access restricted | ✅ Browser automation |
| **Twitter (X)** | Paid API only ($100/month) | ✅ Browser automation |

### How It Works:

1. **Post Generation:**
   - Python scripts create posts
   - Saved in `Social_Drafts/` folder

2. **Auto-Posting:**
   - Playwright browser opens website
   - Logs in with your saved session
   - Posts content automatically
   - Takes screenshot as proof

3. **Your Browser Session:**
   - First time: Manual login
   - Subsequent times: Uses saved cookies

---

### Setup Social Media Posting:

#### Step 1: Install Playwright

```bash
playwright install chromium
```

**Time:** 5 minutes

---

#### Step 2: Manual Login (First Time)

Run the post generator:
```bash
python linkedin_post_generator.py
```

When browser opens:
1. Log in to LinkedIn/Facebook/Instagram/Twitter
2. Browser saves session
3. Next time: Auto-logged in

---

#### Step 3: Test Auto-Posting

```bash
cd mcp-social
npm start
```

Then in Claude Code:
```
@social Post to LinkedIn: "Testing AI Employee!"
```

---

### Social Media Credentials Summary

| Platform | Credentials | How Stored |
|----------|-------------|------------|
| **LinkedIn** | Your login | Browser cookies |
| **Facebook** | Your login | Browser cookies |
| **Instagram** | Your login | Browser cookies |
| **Twitter** | Your login | Browser cookies |

**Security:** Cookies stored locally in `whatsapp_session/` folder. Never shared.

---

## 5️⃣ OTHER SERVICES

### Google One / Google Drive
- Uses same Gmail credentials
- Already configured ✅

### Bank Integration
- Uses Odoo's bank sync (if available)
- Or manual CSV import
- No direct API credentials needed

### Payment Gateways
- Not implemented yet
- Would require separate API keys
- Future Platinum Tier feature

---

## 🔒 SECURITY BEST PRACTICES

### Credential Storage

✅ **DO:**
- Store credentials in `.env` file
- Add `.env` to `.gitignore`
- Use environment variables
- Rotate credentials monthly

❌ **DON'T:**
- Commit credentials to Git
- Share credentials in chat
- Store credentials in plain text
- Use same password everywhere

---

### Your Current Credential Files

| File | Purpose | Status |
|------|---------|--------|
| `credentials.json` | Gmail OAuth | ✅ Configured |
| `config/.env.example` | Template | ✅ Present |
| `mcp-email/token.json` | Gmail token | ⚠️ Generate |
| `whatsapp_session/` | WhatsApp session | ⚠️ First login needed |

---

### Create Your .env File

1. **Copy example:**
   ```bash
   copy config\.env.example config\.env
   ```

2. **Fill in values:**
   ```bash
   # Gmail (already configured)
   GMAIL_CLIENT_ID=11790628161-xxxxxxx.apps.googleusercontent.com
   GMAIL_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxxx
   
   # Odoo (after installation)
   ODOO_URL=http://localhost:8069
   ODOO_DATABASE=odoo
   ODOO_USERNAME=admin
   ODOO_PASSWORD=admin
   ```

3. **NEVER commit .env to Git!**

---

## 📝 CREDENTIALS CHECKLIST

### Gmail ✅ (Already Configured)
- [x] Google Cloud project created
- [x] Gmail API enabled
- [x] OAuth credentials downloaded
- [x] `credentials.json` in vault
- [ ] Generate token (run `node authenticate.js`)

### WhatsApp ✅ (No Credentials)
- [x] Playwright installed
- [ ] First manual login (scan QR)

### Odoo ⚠️ (Need to Setup)
- [ ] Install Odoo 19+ (Docker or local)
- [ ] Create database
- [ ] Install apps (Invoicing, CRM, Contacts)
- [ ] Configure MCP with credentials
- [ ] Test connection

### Social Media ✅ (No Credentials)
- [x] Playwright installed
- [ ] First manual login to each platform
- [ ] Sessions saved

---

## 🚀 QUICK START COMMANDS

### Generate Gmail Token
```bash
cd "C:\Users\CC\Documents\Obsidian Vault\mcp-email"
node authenticate.js
```

### Install Odoo (Docker)
```bash
cd "C:\Users\CC\Documents\Obsidian Vault"
docker-compose up -d
```

### Test All Credentials
```bash
# Test Gmail
cd mcp-email && npm start

# Test Odoo
cd mcp-odoo && npm start

# Test Social
cd mcp-social && npm start
```

---

## 📞 TROUBLESHOOTING

### "Invalid credentials"
- Verify credentials.json is valid JSON
- Check client_id and client_secret
- Re-download from Google Cloud Console

### "Token expired"
- Delete `mcp-email/token.json`
- Re-run `node authenticate.js`

### "Odoo connection refused"
- Check Odoo is running: http://localhost:8069
- Verify Docker container: `docker ps`
- Check port 8069 not blocked

### "WhatsApp session expired"
- Run `whatsapp_watcher.py`
- Scan QR code again
- Session will be saved

---

## 🎯 SUMMARY

### Credentials You Need:

1. **Gmail OAuth** ✅ (Already have, just generate token)
2. **Odoo Admin** ⚠️ (Install Odoo first)
3. **Social Media Logins** ✅ (Browser automation, no API keys)

### Credentials NOT Needed:

- ❌ Facebook API key
- ❌ Instagram API key
- ❌ LinkedIn API key
- ❌ Twitter API key
- ❌ WhatsApp Business API

**This is intentional!** Browser automation is:
- ✅ Easier to setup
- ✅ No API restrictions
- ✅ No rate limits
- ✅ No app review process

---

## 📚 ADDITIONAL RESOURCES

### Gmail OAuth
- [Google Cloud Console](https://console.cloud.google.com/)
- [Gmail API Quickstart](https://developers.google.com/gmail/api/quickstart/python)

### Odoo Setup
- [Odoo 19 Documentation](https://www.odoo.com/documentation/19.0/)
- [Odoo External API](https://www.odoo.com/documentation/19.0/developer/reference/external_api.html)
- [Docker Hub](https://hub.docker.com/_/odoo)

### Playwright
- [Playwright Documentation](https://playwright.dev/python/docs/intro)
- [Browser Automation Guide](https://playwright.dev/python/docs/browser-contexts)

---

**Status:** Guide Complete ✅
**Last Updated:** March 17, 2026
**Difficulty:** Beginner-friendly

---

*This guide helps you obtain all necessary credentials for AI Employee Vault integrations.*
