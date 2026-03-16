# ✅ Credentials Checklist - AI Employee Vault

**Quick Reference Card**

---

## 📊 CURRENT STATUS

```
┌────────────────────────────────────────────────────────────┐
│  CREDENTIALS STATUS                                        │
├────────────────────────────────────────────────────────────┤
│  ✅ Gmail OAuth       → Present (credentials.json)         │
│  ⚠️  Gmail Token      → MISSING (generate token)           │
│  ⚠️  Odoo Server      → NOT INSTALLED                      │
│  ✅ Odoo Config       → Present (admin/admin)              │
│  ❌ Odoo API Key      → NOT NEEDED (local Odoo)            │
│  ✅ Social Media      → NO CREDENTIALS NEEDED              │
│  ✅ WhatsApp          → NO CREDENTIALS NEEDED              │
│  ⚠️  Environment File → MISSING (create .env)              │
└────────────────────────────────────────────────────────────┘
```

---

## 🎯 WHAT YOU NEED TO DO

### **Priority 1: Generate Gmail Token** (5 minutes)

```bash
cd "C:\Users\CC\Documents\Obsidian Vault\mcp-email"
node authenticate.js
```

**Result:** ✅ Token created in `mcp-email/token.json`

---

### **Priority 2: Install Odoo** (30 minutes - Optional)

**For Local Odoo (Docker):**

```bash
docker run -d -p 8069:8069 \
  --name odoo_community \
  -e ODOO_DATABASE=odoo \
  -e ODOO_ADMIN_PASSWORD=admin \
  odoo:19.0
```

**Then:**
1. Open http://localhost:8069
2. Create database: `odoo`
3. Install apps: Invoicing, CRM, Contacts

**Result:** ✅ Odoo running with credentials:
```
URL:      http://localhost:8069
Database: odoo
Username: admin
Password: admin
```

**NO API KEY NEEDED!** ✅

---

### **Priority 3: Create .env File** (2 minutes)

```bash
cd "C:\Users\CC\Documents\Obsidian Vault\config"
copy .env.example .env
```

**Done!** No need to edit (already configured).

---

## ❌ WHAT YOU DON'T NEED

```
┌────────────────────────────────────────────────────────┐
│  NO CREDENTIALS NEEDED FOR:                            │
├────────────────────────────────────────────────────────┤
│  ❌ Facebook API Key    → Uses browser automation      │
│  ❌ Instagram API Key   → Uses browser automation      │
│  ❌ LinkedIn API Key    → Uses browser automation      │
│  ❌ Twitter API Key     → Uses browser automation      │
│  ❌ WhatsApp API Key    → Uses browser automation      │
│  ❌ Odoo API Key        → Uses username/password       │
└────────────────────────────────────────────────────────┘
```

**Why?** All social media uses **Playwright browser automation** instead of APIs!

---

## 📋 COMPLETE CHECKLIST

### Gmail Integration
```
[✅] credentials.json exists
[⚠️] Generate token: cd mcp-email && node authenticate.js
[  ] Test: npm start
```

### Odoo Integration (Optional for Gold Tier)
```
[⚠️] Install Odoo: docker run -d -p 8069:8069 odoo:19.0
[  ] Create database at http://localhost:8069
[  ] Install apps (Invoicing, CRM, Contacts)
[✅] Config already set (admin/admin)
[  ] Test: cd mcp-odoo && npm start
```

### Social Media (No Setup Needed)
```
[✅] Browser automation configured
[  ] First login when script runs
```

### WhatsApp (No Setup Needed)
```
[✅] Browser automation configured
[  ] First QR scan when script runs
```

---

## 🚀 QUICK START COMMANDS

### Minimum Setup (10 minutes)
```bash
# 1. Generate Gmail token
cd mcp-email && node authenticate.js

# 2. Install Playwright
playwright install chromium

# 3. Test
python ceo_briefing_enhanced.py
python social_summary_generator.py all 7
```

### Full Gold Tier (45 minutes)
```bash
# 1. Generate Gmail token
cd mcp-email && node authenticate.js

# 2. Install Odoo
docker run -d -p 8069:8069 --name odoo_community odoo:19.0

# 3. Create database at http://localhost:8069

# 4. Install Odoo apps (Invoicing, CRM, Contacts)

# 5. Test Odoo
cd mcp-odoo && npm start

# 6. Test everything
python ceo_briefing_enhanced.py
```

---

## 📊 CREDENTIALS SUMMARY

| Service | Credentials | Status | Action |
|---------|-------------|--------|--------|
| **Gmail** | OAuth + Token | ⚠️ Partial | Generate token |
| **WhatsApp** | None | ✅ Ready | First QR scan |
| **Facebook** | None | ✅ Ready | First login |
| **Instagram** | None | ✅ Ready | First login |
| **LinkedIn** | None | ✅ Ready | First login |
| **Twitter** | None | ✅ Ready | First login |
| **Odoo** | Username/Password | ⚠️ Not installed | Install Odoo |
| **Odoo API Key** | Not needed (local) | ✅ N/A | Skip |

---

## 🎯 RECOMMENDED ORDER

### For Testing (Minimum)
1. ✅ Generate Gmail token (5 min)
2. ✅ Install Playwright (5 min)

**Total: 10 minutes**

### For Full Gold Tier
1. ✅ Generate Gmail token (5 min)
2. ✅ Install Odoo (30 min)
3. ✅ Create .env file (2 min)

**Total: 37 minutes**

---

## 📞 HELP FILES

For detailed instructions, see:

1. **`CREDENTIALS_STATUS.md`** - Complete status report
2. **`CREDENTIALS_GUIDE.md`** - Step-by-step guide
3. **`ODOO_API_KEY_GUIDE.md`** - Odoo API key instructions
4. **`TESTING_GUIDE.md`** - How to test everything

---

## 🔒 SECURITY REMINDER

**Never share these files:**
- ❌ `credentials.json`
- ❌ `mcp-email/token.json`
- ❌ `config/.env`
- ❌ Odoo API keys

**Already in .gitignore:** ✅

---

**Status:** Ready to setup
**Time Required:** 10-45 minutes
**Difficulty:** Easy

---

*Your AI Employee uses browser automation to avoid complex API credentials!*
