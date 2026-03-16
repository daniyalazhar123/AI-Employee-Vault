# 📘 How to Get Odoo API Key / JSON Credentials

**Complete guide with screenshots-style instructions**

---

## 🎯 Quick Answer

### Do You Need Odoo API Key?

| Odoo Version | API Key Available? | What to Use |
|-------------|-------------------|-------------|
| **Odoo Online** (cloud.odoo.com) | ✅ **YES** | API Key (recommended) |
| **Odoo.sh** (hosting) | ✅ **YES** | API Key (recommended) |
| **Odoo Community** (self-hosted/local) | ❌ **NO** | Username + Password only |

**If you're using local Docker Odoo → You DON'T need API key!**

Your current config uses **username/password** which works for local Odoo:

```json
{
  "ODOO_URL": "http://localhost:8069",
  "ODOO_DB": "odoo",
  "ODOO_USERNAME": "admin",
  "ODOO_PASSWORD": "admin"
}
```

This is **already configured** in your `config/mcp.json` ✅

---

## 📋 Step-by-Step: Get Odoo API Key (Odoo Online Only)

### Prerequisites:
- Odoo Online account (cloud.odoo.com)
- Admin access to your Odoo database

---

### Step 1: Login to Odoo Online

Go to your Odoo URL:
```
https://yourcompany.odoo.com
```

Login with:
- **Email:** your-email@example.com
- **Password:** your-password

---

### Step 2: Open User Menu

Click your **profile picture / avatar** in the **top-right corner**:

```
[Your Avatar ▼]  ← Click here
```

---

### Step 3: Go to My Profile

From dropdown menu, click:

```
My Profile
```

or

```
Preferences
```

---

### Step 4: Find Security Section

Scroll down to find:

```
┌─────────────────────────────────┐
│  Security                       │
│                                 │
│  Password:  ●●●●●●●●  [Change] │
│                                 │
│  API Keys:                      │
│  • Personal Access Token        │
│    [Add API Key]                │
└─────────────────────────────────┘
```

---

### Step 5: Add API Key

Click **"[Add API Key]"** or **"[Generate API Key]"**

A popup appears:

```
┌──────────────────────────────────┐
│  Add API Key                     │
│                                  │
│  Description: [_______________]  │
│                                  │
│  [Cancel]  [Add]                 │
└──────────────────────────────────┘
```

**Fill in:**
- **Description:** `AI Employee MCP Server`

Click **"[Add]"**

---

### Step 6: Copy API Key Immediately!

**⚠️ IMPORTANT:** API key shown **ONLY ONCE**!

```
┌──────────────────────────────────┐
│  Your New API Key                │
│                                  │
│  7f8a9b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a  │
│                                  │
│  ⚠️ Copy this key now!           │
│  It won't be shown again!        │
│                                  │
│  [Copy]  [Done]                  │
└──────────────────────────────────┘
```

**COPY IT NOW!** Save it somewhere secure:
- Password manager (1Password, Bitwarden, LastPass)
- Text file (encrypted)
- Paper (physical backup)

**Example API Key:**
```
7f8a9b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a
```

---

### Step 7: Add API Key to MCP Configuration

Edit your `config/mcp.json`:

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

**Replace:**
- `yourcompany.odoo.com` with your actual URL
- `your-email@example.com` with your email
- `your-password` with your password
- Add the API key you just copied

---

### Step 8: Test Connection

```bash
cd "C:\Users\CC\Documents\Obsidian Vault\mcp-odoo"
npm start
```

**Expected Output:**
```
Odoo MCP Server running
Connected to Odoo at https://yourcompany.odoo.com
User ID: 2
```

**Success!** ✅

---

## 🔧 For Local Odoo (Docker) - NO API KEY NEEDED

If you're using **local Odoo** (Docker or installed), you **don't need API key**.

Your current configuration is already correct:

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

**This works perfectly without API key!** ✅

---

## 📊 API Key vs Password Comparison

| Feature | Password | API Key |
|---------|----------|---------|
| **Works with Local Odoo** | ✅ Yes | ❌ No |
| **Works with Odoo Online** | ✅ Yes | ✅ Yes |
| **More Secure** | ❌ No | ✅ Yes |
| **Can Be Revoked** | ❌ No (must change password) | ✅ Yes |
| **Expires** | ❌ Never | ❌ Never |
| **Recommended For** | Testing/Development | Production |

---

## 🎯 Which Should You Use?

### Use **Password** If:
- ✅ Using local Odoo (Docker/install)
- ✅ Testing/development
- ✅ Don't want to setup API key

### Use **API Key** If:
- ✅ Using Odoo Online
- ✅ Production deployment
- ✅ Want better security
- ✅ Need to revoke access later

---

## 🔒 Security Best Practices

### For API Keys:

1. **Never share your API key**
   - Don't commit to Git
   - Don't paste in chat
   - Don't email unencrypted

2. **Store securely**
   - Use password manager
   - Encrypt if storing in file
   - Add to `.gitignore`

3. **Rotate if compromised**
   - Revoke old key
   - Generate new key
   - Update configuration

4. **Use descriptive names**
   - `AI Employee MCP Server`
   - `Mobile App Integration`
   - `Website Integration`

### For Passwords:

1. **Change default password**
   ```
   admin → YourStrongPassword123!
   ```

2. **Use strong password**
   - 12+ characters
   - Mix of upper/lower/numbers/symbols
   - Not used elsewhere

3. **Store securely**
   - Password manager
   - Encrypted file

---

## 📝 Configuration Examples

### Example 1: Local Odoo (Docker) - NO API KEY

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
        "ODOO_PASSWORD": "MyNewSecurePassword123!"
      }
    }
  }
}
```

**Note:** No `ODOO_API_KEY` needed!

---

### Example 2: Odoo Online - WITH API KEY

```json
{
  "mcpServers": {
    "odoo": {
      "command": "node",
      "args": ["C:/Users/CC/Documents/Obsidian Vault/mcp-odoo/index.js"],
      "env": {
        "ODOO_URL": "https://mycompany.odoo.com",
        "ODOO_DB": "mycompany",
        "ODOO_USERNAME": "admin@mycompany.com",
        "ODOO_PASSWORD": "MyPassword123!",
        "ODOO_API_KEY": "7f8a9b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a"
      }
    }
  }
}
```

**Note:** API key is **optional** but **recommended** for Odoo Online.

---

### Example 3: Using .env File

Instead of putting credentials in `mcp.json`, use `.env`:

**Create `config/.env`:**
```bash
ODOO_URL=https://mycompany.odoo.com
ODOO_DB=mycompany
ODOO_USERNAME=admin@mycompany.com
ODOO_PASSWORD=MyPassword123!
ODOO_API_KEY=7f8a9b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a
```

**Then `config/mcp.json`:**
```json
{
  "mcpServers": {
    "odoo": {
      "command": "node",
      "args": ["C:/Users/CC/Documents/Obsidian Vault/mcp-odoo/index.js"],
      "env": {}
    }
  }
}
```

**Benefit:** `.env` file can be added to `.gitignore` for security.

---

## 🧪 Testing Your Odoo Connection

### Test 1: Check if Odoo is Running

**Local Odoo:**
```bash
curl http://localhost:8069
```

Should return HTML or redirect.

**Odoo Online:**
```bash
curl https://yourcompany.odoo.com
```

Should return HTML.

---

### Test 2: Test MCP Server

```bash
cd "C:\Users\CC\Documents\Obsidian Vault\mcp-odoo"
npm start
```

**Expected:**
```
Odoo MCP Server running
Connected to Odoo at http://localhost:8069
User ID: 2
```

---

### Test 3: Test in Claude Code

```
@odoo Get all leads
```

**Expected:**
```
Found 3 leads:
1. Test Lead - new@example.com
2. Another Lead - interested@example.com
3. ...
```

---

## ❌ Troubleshooting

### Error: "Authentication failed"

**Possible Causes:**
1. Wrong username/password
2. Wrong database name
3. User doesn't have permissions

**Solution:**
```bash
# Check credentials in config/mcp.json
type config\mcp.json

# Verify Odoo login works in browser
# http://localhost:8069 or https://yourcompany.odoo.com
```

---

### Error: "Connection refused"

**Possible Causes:**
1. Odoo not running
2. Wrong port
3. Firewall blocking

**Solution:**
```bash
# Check if Odoo is running (Docker)
docker ps

# Should show odoo container
# If not, start it:
docker start odoo_community
```

---

### Error: "Database not found"

**Possible Causes:**
1. Wrong database name
2. Database doesn't exist

**Solution:**
```bash
# Check database name in config
# Should match what you created

# List databases (local Odoo)
# http://localhost:8069/web/database/manager
```

---

### Error: "API key invalid"

**Possible Causes:**
1. API key copied incorrectly
2. API key was revoked
3. Using API key with local Odoo (not supported)

**Solution:**
```bash
# For Odoo Online:
# 1. Generate new API key
# 2. Update config/mcp.json
# 3. Restart MCP server

# For Local Odoo:
# Remove ODOO_API_KEY from config
# Use username/password only
```

---

## 📞 Quick Reference

### Local Odoo (Docker)
```
URL:      http://localhost:8069
Database: odoo
Username: admin
Password: admin (change after install!)
API Key:  NOT AVAILABLE
```

### Odoo Online
```
URL:      https://yourcompany.odoo.com
Database: yourcompany
Username: your-email@example.com
Password: your-password
API Key:  Available in My Profile → Security
```

---

## 🎉 Summary

### For Local Odoo:
- ❌ **Don't need API key**
- ✅ **Use username/password**
- ✅ **Already configured correctly**

### For Odoo Online:
- ✅ **Can get API key** (recommended)
- ✅ **Go to:** My Profile → Security → Add API Key
- ✅ **Copy immediately** (shown only once)
- ✅ **Add to config/mcp.json**

---

**Status:** Guide Complete ✅
**Last Updated:** March 17, 2026

---

*This guide shows you exactly how to get Odoo API key for AI Employee Vault.*
