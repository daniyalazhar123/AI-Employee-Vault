# 🔐 Credentials Needed - Quick Reference

**Last Updated:** March 17, 2026

---

## ✅ GOOD NEWS: Most Services Need NO Credentials!

| Service | Credentials? | What You Need |
|---------|-------------|---------------|
| 📧 **Gmail** | ✅ YES | Google OAuth (already configured!) |
| 💬 **WhatsApp** | ❌ NO | Just scan QR code |
| 📱 **Facebook** | ❌ NO | Just login in browser |
| 📸 **Instagram** | ❌ NO | Just login in browser |
| 💼 **LinkedIn** | ❌ NO | Just login in browser |
| 🐦 **Twitter** | ❌ NO | Just login in browser |
| 📊 **Odoo** | ✅ YES | Install Odoo (admin/admin) |

---

## 🎯 What You Need to Do

### 1. Gmail Token (5 minutes) ✅ Already Have Credentials

**Your credentials are already configured!** Just generate the token:

```bash
cd "C:\Users\CC\Documents\Obsidian Vault\mcp-email"
node authenticate.js
```

This will:
1. Open browser
2. Sign in with Google
3. Save token automatically

**Done!** ✅

---

### 2. Odoo Installation (30 minutes) ⚠️ Need to Setup

**Option A: Docker (Easiest)**

```bash
# Create docker-compose.yml
docker run -d -p 8069:8069 --name odoo odoo:19.0
```

**Credentials:**
- URL: http://localhost:8069
- Username: admin
- Password: admin
- Database: odoo

**Option B: Skip for Now**

Odoo is for Gold Tier accounting. You can test everything else without it!

---

### 3. WhatsApp & Social Media (10 minutes) ✅ No Credentials

**Just login once in browser:**

```bash
# WhatsApp
python watchers/whatsapp_watcher.py

# Social Media
python linkedin_post_generator.py
```

Browser will save your session. **No API keys needed!**

---

## 📋 Complete Setup Checklist

### Immediate (Required for Testing)

- [ ] **Generate Gmail Token**
  ```bash
  cd mcp-email && node authenticate.js
  ```
  **Time:** 5 minutes

- [ ] **Install Playwright Browsers**
  ```bash
  playwright install chromium
  ```
  **Time:** 5 minutes

### Optional (For Full Gold Tier)

- [ ] **Install Odoo** (for accounting)
  ```bash
  docker run -d -p 8069:8069 --name odoo odoo:19.0
  ```
  **Time:** 30 minutes

- [ ] **Login to Social Platforms** (first time)
  - LinkedIn
  - Facebook
  - Instagram
  - Twitter
  
  **Time:** 10 minutes

---

## 🚀 Quick Test Commands

### After Gmail Token
```bash
cd mcp-email
npm start
```

### After Playwright Install
```bash
python linkedin_post_generator.py
python social_summary_generator.py all 7
```

### After Odoo Setup
```bash
cd mcp-odoo
npm start
```

---

## 📊 Current Status

| Component | Credentials | Status |
|-----------|-------------|--------|
| Gmail OAuth | ✅ Already configured | Generate token |
| WhatsApp | ❌ Not needed | First login |
| Facebook | ❌ Not needed | First login |
| Instagram | ❌ Not needed | First login |
| LinkedIn | ❌ Not needed | First login |
| Twitter | ❌ Not needed | First login |
| Odoo | ⚠️ Need to install | Not installed |

---

## 🔧 What's Already Configured

✅ **credentials.json** - Gmail OAuth credentials present
✅ **config/mcp.json** - All MCP servers configured
✅ **watchers/** - All 5 watchers ready
✅ **mcp-*/** - All 4 MCP servers ready

**You just need to:**
1. Generate Gmail token (5 min)
2. Install Odoo if you want accounting (30 min)

---

## 📞 Help Resources

- **Full Guide:** `CREDENTIALS_GUIDE.md`
- **Testing Guide:** `TESTING_GUIDE.md`
- **Quick Commands:** `QUICK_TEST_COMMANDS.md`

---

## 💡 Why Most Services Don't Need Credentials

We use **browser automation** (Playwright) instead of APIs:

| Traditional API | Our Approach |
|----------------|--------------|
| Complex API setup | ✅ Just login |
| App review process | ✅ No approval needed |
| Rate limits | ✅ No limits |
| Paid API access | ✅ Free |
| API keys to manage | ✅ Browser cookies |

**This is intentional and by design!** 🎉

---

## 🎯 Minimum Credentials for Testing

To test your AI Employee Vault, you need:

1. **Gmail Token** (5 min) - For email features
2. **Playwright** (5 min) - For WhatsApp & Social

**That's it!** Everything else is optional.

---

**Status:** Ready to test with minimal setup
**Time Required:** 10 minutes minimum
**Difficulty:** Easy

---

*Your AI Employee uses browser automation to avoid complex API credentials!*
