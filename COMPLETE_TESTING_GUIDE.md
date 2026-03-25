# 🧪 COMPLETE TESTING GUIDE - AI EMPLOYEE VAULT

**Personal AI Employee Hackathon 0**
**Version:** March 25, 2026
**Status:** Step-by-Step Testing Instructions

---

## 📋 **TABLE OF CONTENTS**

1. [Pre-Testing Checklist](#pre-testing-checklist)
2. [Phase 1: Folder Structure](#phase-1-folder-structure)
3. [Phase 2: MCP Servers](#phase-2-mcp-servers)
4. [Phase 3: Watchers](#phase-3-watchers)
5. [Phase 4: Core Systems](#phase-4-core-systems)
6. [Phase 5: Business Logic](#phase-5-business-logic)
7. [Phase 6: Platinum Deployment](#phase-6-platinum-deployment)
8. [Phase 7: Integration Testing](#phase-7-integration-testing)

---

## ✅ **PRE-TESTING CHECKLIST**

### **Required Software:**
```bash
# Check Python version (3.13+ required)
python --version
# Expected: Python 3.13.x or higher

# Check Git
git --version
# Expected: git version 2.x

# Check Playwright browsers
playwright --version
# Expected: Version number
```

### **Install Dependencies:**
```bash
cd "D:\Desktop4\Obsidian Vault"

# Install Python packages
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### **Environment Setup:**
```bash
# Copy example environment file
copy .env.example .env

# Edit .env with your credentials (if testing with real services)
notepad .env
```

---

## 📁 **PHASE 1: FOLDER STRUCTURE VERIFICATION**

### **Test 1.1: Verify All Required Folders**

```bash
cd "D:\Desktop4\Obsidian Vault"

# Run automated test
python test_all_components.py --folders
```

### **Expected Result:**
```
✅ All 20 folders should exist
```

### **Manual Verification:**
```bash
# List all folders
dir /ad /b

# Should show:
Approved
Briefings
CEO_Briefings
cloud
config
data
Dead_Letter_Queue
docs
Done
Drafts
In_Progress
Inbox
kubernetes
local
Logs
Needs_Action
odoo
odoo_installer
Office_Files
Pending_Approval
Plans
Signals
Skills
Social_Drafts
Social_Summaries
Updates
watchers
whatsapp_session
```

---

## 📡 **PHASE 2: MCP SERVERS TESTING**

### **Overview:**
- **mcp_email.py** - Email operations (5 commands)
- **mcp_browser.py** - Browser automation (14 commands)
- **mcp_odoo.py** - Odoo ERP (8 commands)
- **mcp_social.py** - Social media (7 commands)

---

### **Test 2.1: Email MCP Server**

**File:** `mcp_email.py`

**Commands to Test:**
```bash
# 1. Check if file compiles
python -m py_compile mcp_email.py && echo "✅ Compiles"

# 2. Show help
python mcp_email.py --help

# 3. List emails (requires credentials)
python mcp_email.py --action list

# 4. Send test email (requires credentials)
python mcp_email.py --action send --to "test@example.com" --subject "Test" 
```

**Expected Output:**
```
✅ File compiles without errors
✅ Help shows available commands
✅ Lists emails (if credentials configured)
```

**Troubleshooting:**
- If "Module not found": `pip install google-api-python-client`
- If "Credentials error": Check `.env` file

---

### **Test 2.2: Browser MCP Server**

**File:** `mcp_browser.py`

**Commands to Test:**
```bash
# 1. Check compilation
python -m py_compile mcp_browser.py && echo "✅ Compiles"

# 2. Show available commands
python mcp_browser.py --action help

# 3. Test navigation (dry run)
python mcp_browser.py --action navigate --url "https://example.com"
```

**Expected Output:**
```
✅ File compiles
✅ Shows 14 available commands
✅ Browser automation ready
```

---

### **Test 2.3: Odoo MCP Server**

**File:** `mcp_odoo.py`

**Commands to Test:**
```bash
# 1. Check compilation
python -m py_compile mcp_odoo.py && echo "✅ Compiles"

# 2. Show help
python mcp_odoo.py --help

# 3. List available commands
python mcp_odoo.py --action help

# 4. Get leads from Odoo (requires Odoo running)
python mcp_odoo.py --action get_leads
```

**Expected Output:**
```
✅ File compiles
✅ Shows 8 Odoo commands
✅ Can connect to Odoo (if running)
```

**Prerequisites:**
- Odoo must be running on `http://localhost:8069`
- Or update `.env` with your Odoo URL

---

### **Test 2.4: Social MCP Server**

**File:** `mcp_social.py`

**Commands to Test:**
```bash
# 1. Check compilation
python -m py_compile mcp_social.py && echo "✅ Compiles"

# 2. Show help
python mcp_social.py --help

# 3. Post to LinkedIn (requires credentials)
python mcp_social.py --action linkedin --content "Test post from AI Employee"
```

**Expected Output:**
```
✅ File compiles
✅ Shows 7 social media commands
✅ Can post to platforms (if credentials configured)
```

---

## 👁️ **PHASE 3: WATCHERS TESTING**

### **Overview:**
- **gmail_watcher.py** - Gmail monitoring (120s interval)
- **whatsapp_watcher.py** - WhatsApp monitoring (30s interval)
- **office_watcher.py** - File system monitoring (1s interval)
- **social_watcher.py** - Social media monitoring (60s interval)
- **odoo_lead_watcher.py** - Odoo CRM monitoring (300s interval)

---

### **Test 3.1: Base Watcher**

**File:** `watchers/base_watcher.py`

```bash
# Test compilation
python -m py_compile watchers/base_watcher.py && echo "✅ Base Watcher OK"
```

---

### **Test 3.2: Gmail Watcher**

**File:** `watchers/gmail_watcher.py`

```bash
# 1. Check compilation
python -m py_compile watchers/gmail_watcher.py && echo "✅ Compiles"

# 2. Test run (1 iteration)
python watchers/gmail_watcher.py --test

# 3. Check if creates files in Needs_Action
dir Needs_Action\EMAIL_*.md
```

**Expected:**
```
✅ Compiles without errors
✅ Monitors Gmail every 120 seconds
✅ Creates .md files for new emails
```

**Credentials Needed:**
- Gmail API credentials in `config/credentials.json`
- See `CREDENTIALS_GUIDE.md` for setup

---

### **Test 3.3: WhatsApp Watcher**

**File:** `watchers/whatsapp_watcher.py`

```bash
# 1. Check compilation
python -m py_compile watchers/whatsapp_watcher.py && echo "✅ Compiles"

# 2. Test run (requires WhatsApp Web session)
python watchers/whatsapp_watcher.py --test
```

**Expected:**
```
✅ Compiles
✅ Monitors WhatsApp Web
✅ Detects urgent keywords
```

**Prerequisites:**
- Playwright installed: `playwright install chromium`
- WhatsApp Web session in `whatsapp_session/`

---

### **Test 3.4: Office Watcher**

**File:** `watchers/office_watcher.py`

```bash
# 1. Check compilation
python -m py_compile watchers/office_watcher.py && echo "✅ Compiles"

# 2. Test file drop
echo "Test content" > Office_Files\test.txt

# 3. Watcher should detect and create action file
dir Needs_Action\FILE_*.md
```

**Expected:**
```
✅ Compiles
✅ Detects new files in Office_Files/
✅ Creates action items
```

---

### **Test 3.5: Social Watcher**

**File:** `watchers/social_watcher.py`

```bash
# 1. Check compilation
python -m py_compile watchers/social_watcher.py && echo "✅ Compiles"

# 2. Test run
python watchers/social_watcher.py --test
```

**Expected:**
```
✅ Compiles
✅ Monitors social media platforms
✅ Generates summaries
```

---

### **Test 3.6: Odoo Lead Watcher**

**File:** `watchers/odoo_lead_watcher.py`

```bash
# 1. Check compilation
python -m py_compile watchers/odoo_lead_watcher.py && echo "✅ Compiles"

# 2. Test with Odoo (requires Odoo running)
python watchers/odoo_lead_watcher.py --test
```

**Expected:**
```
✅ Compiles
✅ Fetches leads from Odoo CRM
✅ Creates action items for new leads
```

---

## 🎯 **PHASE 4: CORE SYSTEMS TESTING**

### **Test 4.1: Orchestrator**

**File:** `orchestrator.py`

```bash
# 1. Check compilation
python -m py_compile orchestrator.py && echo "✅ Compiles"

# 2. Health check
python orchestrator.py --health

# 3. Dry run (test without starting watchers)
python orchestrator.py --dry-run

# 4. Start all watchers
python orchestrator.py
```

**Expected Output:**
```
✅ Compiles
✅ Health check returns JSON status
✅ Dry run shows what would start
✅ Full run starts all watchers
```

**Health Check Response:**
```json
{
  "status": "healthy",
  "watchers_running": 5,
  "timestamp": "2026-03-25T04:00:00"
}
```

---

### **Test 4.2: Ralph Loop**

**File:** `ralph_loop.py`

```bash
# 1. Check compilation
python -m py_compile ralph_loop.py && echo "✅ Compiles"

# 2. Show help
python ralph_loop.py --help

# 3. Test with sample task
python ralph_loop.py "Process all files in Needs_Action folder"
```

**Expected:**
```
✅ Compiles
✅ Creates task file in Needs_Action
✅ Loops until task complete
✅ Moves to Done when finished
```

**How It Works:**
1. Creates task file
2. Calls Claude/Qwen to process
3. Checks if task done
4. If not, loops again (max 10 iterations)
5. Moves to Done when complete

---

### **Test 4.3: Audit Logger**

**File:** `audit_logger.py`

```bash
# 1. Check compilation
python -m py_compile audit_logger.py && echo "✅ Compiles"

# 2. Test logging
python audit_logger.py --test

# 3. View logs
dir Logs\Audit\audit_*.jsonl
```

**Expected:**
```
✅ Compiles
✅ Creates audit log entries
✅ Logs saved to Logs/Audit/
```

**Log Format:**
```jsonl
{"timestamp": "2026-03-25T04:00:00", "action": "email_processed", "details": {...}}
```

---

### **Test 4.4: Error Recovery**

**File:** `error_recovery.py`

```bash
# 1. Check compilation
python -m py_compile error_recovery.py && echo "✅ Compiles"

# 2. Test circuit breaker
python error_recovery.py --test

# 3. View Dead Letter Queue
dir Dead_Letter_Queue\
```

**Expected:**
```
✅ Compiles
✅ Circuit breaker working
✅ Retry logic implemented
✅ Dead Letter Queue for failed items
```

---

### **Test 4.5: Health Monitor**

**File:** `health_monitor.py`

```bash
# 1. Check compilation
python -m py_compile health_monitor.py && echo "✅ Compiles"

# 2. Run health check
python health_monitor.py

# 3. View health status
type Logs\health.jsonl
```

**Expected:**
```
✅ Compiles
✅ Monitors all components
✅ Reports health status
```

---

## 💼 **PHASE 5: BUSINESS LOGIC TESTING**

### **Test 5.1: CEO Briefing Generator**

**File:** `ceo_briefing_enhanced.py`

```bash
# 1. Check compilation
python -m py_compile ceo_briefing_enhanced.py && echo "✅ Compiles"

# 2. Generate briefing
python ceo_briefing_enhanced.py

# 3. View generated briefing
type Briefings\CEO_Briefing_*.md
```

**Expected Output:**
```
✅ Compiles
✅ Generates CEO Briefing in Briefings/
✅ Includes revenue, tasks, bottlenecks
✅ Proactive suggestions included
```

**Briefing Contents:**
- Revenue summary
- Completed tasks
- Bottlenecks identified
- Cost optimization suggestions
- Upcoming deadlines

---

### **Test 5.2: Social Summary Generator**

**File:** `social_summary_generator.py`

```bash
# 1. Check compilation
python -m py_compile social_summary_generator.py && echo "✅ Compiles"

# 2. Generate summary (last 7 days)
python social_summary_generator.py all 7

# 3. View summary
type Social_Summaries\social_summary_*.md
```

**Expected:**
```
✅ Compiles
✅ Generates social media summary
✅ Includes posts, hashtags, engagement
```

---

### **Test 5.3: LinkedIn Post Generator**

**File:** `linkedin_post_generator.py`

```bash
# 1. Check compilation
python -m py_compile linkedin_post_generator.py && echo "✅ Compiles"

# 2. Generate test post
python linkedin_post_generator.py "AI Employee Hackathon Project"

# 3. View draft
type Social_Drafts\linkedin_*.md
```

**Expected:**
```
✅ Compiles
✅ Generates professional LinkedIn post
✅ Includes hashtags
✅ Saves to Social_Drafts/
```

---

### **Test 5.4: Facebook/Instagram Post Generator**

**File:** `facebook_instagram_post.py`

```bash
# 1. Check compilation
python -m py_compile facebook_instagram_post.py && echo "✅ Compiles"

# 2. Generate test post
python facebook_instagram_post.py "New Product Launch"

# 3. View drafts
type Social_Drafts\facebook_*.md
type Social_Drafts\instagram_*.md
```

**Expected:**
```
✅ Compiles
✅ Generates posts for both platforms
✅ Platform-specific formatting
```

---

### **Test 5.5: Twitter Post Generator**

**File:** `twitter_post.py`

```bash
# 1. Check compilation
python -m py_compile twitter_post.py && echo "✅ Compiles"

# 2. Generate test tweet
python twitter_post.py "AI Employee is ready for Hackathon!"

# 3. View draft
type Social_Drafts\twitter_*.md
```

**Expected:**
```
✅ Compiles
✅ Generates tweet (280 chars)
✅ Includes hashtags
```

---

## 💿 **PHASE 6: PLATINUM DEPLOYMENT TESTING**

### **Test 6.1: Cloud Orchestrator**

**File:** `cloud_orchestrator.py`

```bash
# 1. Check compilation
python -m py_compile cloud_orchestrator.py && echo "✅ Compiles"

# 2. Show help
python cloud_orchestrator.py --help

# 3. Test run (draft-only mode)
python cloud_orchestrator.py --test
```

**Expected:**
```
✅ Compiles
✅ Runs in DRAFT-ONLY mode
✅ Monitors Needs_Action/cloud/
✅ Creates drafts in Updates/
```

**Cloud Agent Behavior:**
- Reads emails → Drafts replies (CANNOT send)
- Monitors social → Drafts posts (CANNOT post)
- Writes to Updates/ folder
- Claims tasks by moving to In_Progress/cloud/

---

### **Test 6.2: Local Orchestrator**

**File:** `local_orchestrator.py`

```bash
# 1. Check compilation
python -m py_compile local_orchestrator.py && echo "✅ Compiles"

# 2. Test run
python local_orchestrator.py --test
```

**Expected:**
```
✅ Compiles
✅ Monitors Updates/ and Pending_Approval/
✅ Executes approved actions
✅ Updates Dashboard.md
```

**Local Agent Behavior:**
- Reviews cloud drafts
- Executes approved actions via MCP
- Sends emails, posts social
- Moves tasks to Done/

---

### **Test 6.3: Vault Sync**

**File:** `vault_sync.py`

```bash
# 1. Check compilation
python -m py_compile vault_sync.py && echo "✅ Compiles"

# 2. Test sync
python vault_sync.py --test

# 3. View sync log
type Logs\sync.log
```

**Expected:**
```
✅ Compiles
✅ Git pull every 5 minutes
✅ Git add, commit, push
✅ Excludes sensitive files
```

---

### **Test 6.4: Platinum Demo**

**File:** `platinum_demo.py`

```bash
# 1. Check compilation
python -m py_compile platinum_demo.py && echo "✅ Compiles"

# 2. Run full demo
python platinum_demo.py

# 3. View demo result
type Done\PLATINUM_DEMO_RESULT.md
```

**Expected Workflow:**
```
Step 1: Email arrives (Local offline)
Step 2: Cloud drafts reply
Step 3: Cloud creates approval request
Step 4: Human approves
Step 5: Local executes send
Step 6: Task moved to Done

✅ PLATINUM DEMO COMPLETE!
```

---

### **Test 6.5: A2A Messenger**

**File:** `a2a_messenger.py`

```bash
# 1. Check compilation
python -m py_compile a2a_messenger.py && echo "✅ Compiles"

# 2. Test messaging
python a2a_messenger.py --test
```

**Expected:**
```
✅ Compiles
✅ Agent-to-Agent communication
✅ HTTP endpoints working
```

---

## 🔗 **PHASE 7: INTEGRATION TESTING**

### **Test 7.1: End-to-End Email Flow**

```bash
# 1. Create test email file
echo "Test email from customer" > Needs_Action\EMAIL_TEST_001.md

# 2. Start orchestrator
python orchestrator.py

# 3. Check if draft created
dir Pending_Approval\*.md

# 4. Approve (move file)
move Pending_Approval\*.md Approved\

# 5. Check if executed
dir Done\*.md
```

**Expected Flow:**
```
Needs_Action → Processing → Pending_Approval → Approved → Done
```

---

### **Test 7.2: CEO Briefing Integration**

```bash
# 1. Ensure some tasks in Done/
# 2. Generate briefing
python ceo_briefing_enhanced.py

# 3. Verify briefing includes all data
type Briefings\CEO_Briefing_*.md
```

**Expected:**
```
✅ Revenue from Odoo
✅ Completed tasks from Done/
✅ Bottlenecks identified
✅ Actionable suggestions
```

---

### **Test 7.3: Social Media Integration**

```bash
# 1. Generate social summary
python social_summary_generator.py all 7

# 2. Generate LinkedIn post
python linkedin_post_generator.py "Hackathon Project"

# 3. Post to LinkedIn (if credentials)
python mcp_social.py --action linkedin --content "Test post"
```

**Expected:**
```
✅ Summary generated
✅ Post drafted
✅ Posted to LinkedIn (if credentials)
```

---

## 📊 **TESTING CHECKLIST**

### **Quick Test Commands:**

```bash
# All-in-one test script
python test_all_components.py --all

# Test specific component
python test_all_components.py --mcp
python test_all_components.py --watchers
python test_all_components.py --core
python test_all_components.py --business
python test_all_components.py --platinum

# Compile check all Python files
for %f in (*.py) do python -m py_compile "%f" && echo "✅ %f"
for %f in (watchers\*.py) do python -m py_compile "%f" && echo "✅ %f"
```

---

## 🎯 **SUCCESS CRITERIA**

### **Bronze Tier (Minimum):**
- ✅ All folders exist
- ✅ 1 watcher working
- ✅ Claude/Qwen integrated
- ✅ Basic workflow functional

### **Silver Tier:**
- ✅ 2+ watchers working
- ✅ 1 MCP server working
- ✅ LinkedIn posting works
- ✅ HITL approval workflow

### **Gold Tier:**
- ✅ 5 watchers working
- ✅ 4 MCP servers working
- ✅ Odoo integration
- ✅ CEO briefing generates
- ✅ Error recovery working
- ✅ Audit logging active

### **Platinum Tier:**
- ✅ Cloud/Local separation
- ✅ Vault sync working
- ✅ Platinum demo passes
- ✅ Draft/Execute separation

---

## 🐛 **COMMON ISSUES & FIXES**

### **Issue 1: "Module not found"**
```bash
# Fix: Install dependencies
pip install -r requirements.txt
playwright install chromium
```

### **Issue 2: "Credentials error"**
```bash
# Fix: Copy and configure .env
copy .env.example .env
notepad .env
# Add your credentials
```

### **Issue 3: "Odoo connection failed"**
```bash
# Fix: Start Odoo
cd odoo
docker-compose up -d

# Or update .env with your Odoo URL
```

### **Issue 4: "Watcher timeout"**
```bash
# Fix: Increase timeout in test script
# Or run watcher directly
python watchers/gmail_watcher.py
```

---

## 📞 **NEXT STEPS**

1. ✅ Run Phase 1 (Folder structure)
2. ✅ Run Phase 2 (MCP servers - compile check)
3. ✅ Run Phase 3 (Watchers - compile check)
4. ✅ Run Phase 4 (Core systems - compile check)
5. ✅ Run Phase 5 (Business logic - compile check)
6. ✅ Run Phase 6 (Platinum - compile check)
7. ✅ Run Phase 7 (Integration - optional)

**Note:** Full functional testing requires credentials. Compile checks work without credentials.

---

**Ready to start testing? Batayein kaunsa phase test karna hai!** 🚀
