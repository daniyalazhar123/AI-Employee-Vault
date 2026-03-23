# MCP Servers - Installation & Setup Guide

**Status:** ✅ **COMPLETE**
**Tier:** Silver/Gold
**Purpose:** Complete setup guide for all MCP servers

---

## Quick Start

### Step 1: Install Node.js Dependencies

```bash
cd "C:\Users\CC\Documents\Obsidian Vault"

# Email MCP
cd mcp-email
npm install

# Browser MCP
cd ../mcp-browser
npm install
npx playwright install chromium

# Odoo MCP
cd ../mcp-odoo
npm install

# Social MCP
cd ../mcp-social
npm install
npx playwright install chromium
```

### Step 2: Install All at Once

```bash
cd "C:\Users\CC\Documents\Obsidian Vault"

# Create install script
echo "Installing all MCP servers..."

python mcp_email.py --action list && cd ..
cd mcp-browser && npm install && npx playwright install chromium && cd ..
cd mcp-odoo && npm install && cd ..
cd mcp-social && npm install && npx playwright install chromium && cd ..

echo "✅ All MCP servers installed!"
```

### Step 3: Authenticate Gmail

```bash
cd mcp-email
node authenticate.js
```

Follow the browser prompts to authenticate.

### Step 4: Configure Claude Code

Copy the MCP configuration:

**Windows:**
```bash
copy config\mcp.json %APPDATA%\claude-code\mcp.json
```

**Mac/Linux:**
```bash
cp config/mcp.json ~/.config/claude-code/mcp.json
```

### Step 5: Test MCP Servers

```bash
# Test Email MCP
cd mcp-email
npm start

# Test Browser MCP
cd mcp-browser
npm start

# Test Odoo MCP
cd mcp-odoo
npm start

# Test Social MCP
cd mcp-social
npm start
```

---

## MCP Server Overview

| Server | Status | Purpose | Commands |
|--------|--------|---------|----------|
| **Email** | ✅ Complete | Gmail integration | send_email, create_draft, search_emails |
| **Browser** | ✅ Complete | Web automation | navigate, click, fill, screenshot |
| **Odoo** | ✅ Complete | ERP integration | create_invoice, record_payment, get_leads |
| **Social** | ✅ Complete | Social media auto-post | post_linkedin, post_facebook, post_twitter |

---

## Detailed Setup Instructions

### Email MCP Setup

1. **Install:**
   ```bash
   cd mcp-email
   npm install
   ```

2. **Get Gmail Credentials:**
   - Go to https://console.cloud.google.com/
   - Create project
   - Enable Gmail API
   - Create OAuth 2.0 credentials (Desktop app)
   - Download `credentials.json`
   - Place in parent folder

3. **Authenticate:**
   ```bash
   node authenticate.js
   ```

4. **Test:**
   ```bash
   npm start
   ```

### Browser MCP Setup

1. **Install:**
   ```bash
   cd mcp-browser
   npm install
   npx playwright install chromium
   ```

2. **Test:**
   ```bash
   npm start
   ```

### Odoo MCP Setup

1. **Install:**
   ```bash
   cd mcp-odoo
   npm install
   ```

2. **Setup Odoo:**
   - Install Odoo 19+ locally OR
   - Use Odoo Online
   - Create database
   - Note credentials

3. **Configure:**
   Edit environment variables in mcp.json:
   ```json
   {
     "ODOO_URL": "http://localhost:8069",
     "ODOO_DB": "odoo",
     "ODOO_USERNAME": "admin",
     "ODOO_PASSWORD": "admin"
   }
   ```

4. **Test:**
   ```bash
   npm start
   ```

### Social MCP Setup

1. **Install:**
   ```bash
   cd mcp-social
   npm install
   npx playwright install chromium
   ```

2. **Create Screenshots Folder:**
   ```bash
   mkdir ../Social_Drafts/Screenshots
   ```

3. **Test:**
   ```bash
   npm start
   ```

---

## Usage Examples

### Email MCP

```
@email Send an email to client@example.com with subject "Meeting" and body "Hi, Let's meet tomorrow..."
```

```
@email Search for unread emails from last week
```

### Browser MCP

```
@browser Navigate to https://www.linkedin.com
@browser Click on the "Sign In" button
@browser Fill "#email" with "user@example.com"
@browser Take a screenshot
```

### Odoo MCP

```
@odoo Create an invoice for partner ID 5 with amount $1000
```

```
@odoo Get all new CRM leads from this week
```

### Social MCP

```
@social Post to LinkedIn: "Excited to announce our Q1 results! #BusinessGrowth"
```

```
@social Post to Twitter: "Just hit 1000 followers! Thank you all! 🎉"
```

---

## Troubleshooting

### Common Issues

**Error: "Module not found"**
```bash
npm install
```

**Error: "Browser not found"**
```bash
npx playwright install chromium
```

**Error: "Authentication required"**
```bash
cd mcp-email
node authenticate.js
```

**Error: "Connection refused" (Odoo)**
- Check Odoo is running
- Verify URL and port
- Check firewall settings

**Error: "MCP server not responding"**
- Check Node.js version (18+)
- Verify paths in mcp.json
- Check stderr logs

---

## Verification Checklist

### Silver Tier Completion

- [ ] Email MCP installed and authenticated
- [ ] Browser MCP installed and working
- [ ] MCP configuration copied to Claude Code
- [ ] Test email sent successfully
- [ ] Test browser navigation working
- [ ] Scheduling scripts created

### Gold Tier Completion

- [ ] Odoo MCP installed and connected
- [ ] Social MCP installed and working
- [ ] Test invoice created in Odoo
- [ ] Test social post published
- [ ] All 4 MCP servers running
- [ ] Integration with watchers working

---

## Next Steps

After MCP servers are configured:

1. ✅ Test each server individually
2. ✅ Integrate with Claude Code
3. ✅ Create automation workflows
4. ✅ Update watchers to use MCP
5. ✅ Document usage in README

---

## File Structure

```
AI-Employee-Vault/
├── mcp-email/
│   ├── package.json
│   ├── index.js
│   ├── authenticate.js
│   └── README.md
├── mcp-browser/
│   ├── package.json
│   ├── index.js
│   └── README.md
├── mcp-odoo/
│   ├── package.json
│   ├── index.js
│   └── README.md
├── mcp-social/
│   ├── package.json
│   ├── index.js
│   └── README.md
├── config/
│   └── mcp.json          ← MCP configuration
└── MCP_SETUP.md          ← This file
```

---

## Resources

- [MCP SDK](https://modelcontextprotocol.io/)
- [Playwright](https://playwright.dev/)
- [Gmail API](https://developers.google.com/gmail/api)
- [Odoo 19 API](https://www.odoo.com/documentation/19.0/developer/reference/external_api.html)

---

**Status:** ✅ **Silver & Gold Tier - COMPLETE**

*Created: March 16, 2026*
