# 📱 SOCIAL MEDIA TESTING - QUICK REFERENCE CARD

**AI Employee Vault - All Platforms Manual Testing Commands**

---

## 🚀 **QUICK START (One Command)**

```bash
# Run interactive testing menu
test_social_media.bat
```

---

## 1️⃣ **LINKEDIN** 🔗

### Generate & Post
```bash
# Generate draft
python linkedin_post_generator.py "Your topic here"

# View drafts
dir Social_Drafts\linkedin_*.md
type Social_Drafts\linkedin_post_2026-03-25.md

# Test auto-post (dry run)
python linkedin_auto_post.py "Test post! #Hackathon2026"

# Actual post (edit .env first: DRY_RUN=false)
python linkedin_auto_post.py "Actual post content"

# Post from draft
python linkedin_auto_post.py --file "Social_Drafts\linkedin_post.md"
```

### Verify
```bash
# View logs
dir Logs\linkedin_post_*.md
type Logs\linkedin_post_*.md
```

---

## 2️⃣ **FACEBOOK** 📘

### Generate & Post
```bash
# Generate post
python facebook_instagram_post.py "Your content here"

# View drafts
dir Social_Drafts\facebook_*.md
type Social_Drafts\facebook_post_*.md

# Test MCP
python mcp_social.py --action facebook --content "Test post"
```

### Manual Post
1. Open: https://www.facebook.com/
2. Copy from draft
3. Paste and post

---

## 3️⃣ **INSTAGRAM** 📸

### Generate & Post
```bash
# Generate post
python facebook_instagram_post.py "Your content"

# View drafts
dir Social_Drafts\instagram_*.md
type Social_Drafts\instagram_post_*.md

# Test MCP
python mcp_social.py --action instagram --content "Test #AI"
```

### Manual Post
1. Open: https://www.instagram.com/
2. Copy caption
3. Add image
4. Post

---

## 4️⃣ **TWITTER (X)** 🐦

### Generate & Post
```bash
# Generate tweet
python twitter_post.py "Your tweet here! #Hashtag"

# View drafts
dir Social_Drafts\twitter_*.md
type Social_Drafts\twitter_*.md

# Check length (must be <280)
python -c "print(len('Your tweet here'))"

# Test MCP
python mcp_social.py --action twitter --content "Test tweet!"
```

### Manual Post
1. Open: https://twitter.com/
2. Copy from draft
3. Post

---

## 5️⃣ **WHATSAPP** 💬

### Monitor & Test
```bash
# Check watcher
python watchers\whatsapp_watcher.py --help

# Test watcher
cd watchers
python whatsapp_watcher.py --test
cd ..

# Check session
dir whatsapp_session\

# View messages
dir Needs_Action\WHATSAPP_*.md
type Needs_Action\WHATSAPP_*.md

# Open WhatsApp Web
start https://web.whatsapp.com
```

### Manual Reply
1. Check message in `Needs_Action\`
2. Read with `type` command
3. Reply via WhatsApp Web

---

## 📊 **VIEW ALL DRAFTS**

```bash
# All social drafts
dir Social_Drafts\*.md

# LinkedIn only
dir Social_Drafts\linkedin_*.md

# Facebook only
dir Social_Drafts\facebook_*.md

# Instagram only
dir Social_Drafts\instagram_*.md

# Twitter only
dir Social_Drafts\twitter_*.md
```

---

## 📋 **VIEW ALL LOGS**

```bash
# All logs
dir Logs\*.md

# LinkedIn posts
dir Logs\linkedin_post_*.md

# Audit logs
dir Logs\Audit\audit_*.jsonl
```

---

## 🎯 **COMPLETE WORKFLOW**

### For Each Platform:
```bash
# Step 1: Generate content
python <platform>_post.py "Your topic"

# Step 2: Review draft
type Social_Drafts\<platform>_*.md

# Step 3: Test (if auto-post available)
python <platform>_auto_post.py "Test"

# Step 4: Actual post (or manual)
# Auto: python <platform>_auto_post.py "Content"
# Manual: Copy from draft, paste in browser

# Step 5: Verify
type Logs\<platform>_*.md
```

---

## ⚡ **ONE-LINER TESTS**

```bash
# Test all generators
python linkedin_post_generator.py "Test" && python facebook_instagram_post.py "Test" && python twitter_post.py "Test"

# View all new drafts
dir Social_Drafts\*.md /od

# Quick LinkedIn test
python linkedin_auto_post.py "Quick test!"
```

---

## 🔧 **TROUBLESHOOTING**

### Issue: Script not found
```bash
# Verify file exists
dir linkedin_auto_post.py
dir mcp_social.py
```

### Issue: Credentials error
```bash
# Check .env file
type .env

# Verify LinkedIn credentials
python -c "import os; print('Email:', os.getenv('LINKEDIN_EMAIL'))"
```

### Issue: No drafts generated
```bash
# Check Social_Drafts folder
dir Social_Drafts\

# Check if folder exists
if not exist Social_Drafts mkdir Social_Drafts
```

---

## 📞 **HELP COMMANDS**

```bash
# LinkedIn help
python linkedin_auto_post.py --help

# MCP Social help
python mcp_social.py --help

# Twitter help
python twitter_post.py --help

# Facebook/Instagram help
python facebook_instagram_post.py --help
```

---

## ✅ **TESTING CHECKLIST**

```
LinkedIn:
☐ Generate draft
☐ View draft
☐ Test auto-post (dry run)
☐ Actual post (optional)
☐ Verify in Logs

Facebook:
☐ Generate draft
☐ View draft
☐ Test MCP
☐ Manual post (optional)

Instagram:
☐ Generate draft
☐ View draft
☐ Test MCP
☐ Manual post (optional)

Twitter:
☐ Generate tweet
☐ Check length (<280)
☐ View draft
☐ Test MCP
☐ Manual post (optional)

WhatsApp:
☐ Check watcher
☐ Test watcher
☐ Check session
☐ View messages
☐ Open WhatsApp Web
```

---

## 🎯 **RECOMMENDED TESTING ORDER**

1. **LinkedIn** - Most important for business
2. **Twitter** - Quick updates
3. **Facebook** - Community posts
4. **Instagram** - Visual content
5. **WhatsApp** - Direct messaging

---

**Quick Start:** Run `test_social_media.bat` for interactive menu! 🚀

---

*Last Updated: March 25, 2026*
*AI Employee Vault - Personal AI Employee Hackathon 0*
