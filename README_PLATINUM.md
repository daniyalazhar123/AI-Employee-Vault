# 💿 PLATINUM TIER - COMPLETE IMPLEMENTATION GUIDE

**Personal AI Employee Hackathon 0**  
**Always-On Cloud + Local Executive**  
**Created:** March 21, 2026

---

## 📚 **TABLE OF CONTENTS**

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Requirements](#requirements)
4. [Quick Start](#quick-start)
5. [Installation](#installation)
6. [Configuration](#configuration)
7. [Deployment](#deployment)
8. [Testing](#testing)
9. [Troubleshooting](#troubleshooting)
10. [Security](#security)

---

## 🎯 **OVERVIEW**

### **What is Platinum Tier?**

Platinum Tier is the **highest achievement level** in the Personal AI Employee Hackathon 0, transforming your local AI Employee into a **production-grade, always-on cloud executive**.

### **Key Innovation: Two-Agent Architecture**

```
┌─────────────────────────────────────────┐
│  ☁️ CLOUD AGENT (Oracle VM - 24/7)     │
│  - Email triage & draft replies        │
│  - Social post drafts                  │
│  - Odoo draft invoices                 │
│  - ❌ NO final send (security!)        │
└──────────────┬──────────────────────────┘
               │ Git Sync (every 5 min)
┌──────────────┴──────────────────────────┐
│  🏠 LOCAL AGENT (Your Machine)         │
│  - Human approvals                     │
│  - WhatsApp (session local)            │
│  - Final email send                    │
│  - Final social post                   │
│  - Banking/payments                    │
└─────────────────────────────────────────┘
```

### **Benefits**

- ✅ **24/7 Operation** - AI Employee never sleeps
- ✅ **Faster Response** - Cloud detects emails in minutes
- ✅ **Global Access** - Access from anywhere
- ✅ **Reliability** - Cloud VM uptime >99%
- ✅ **Security** - Proper credential separation
- ✅ **Scalability** - Easy to add more agents

---

## 🏗️ **ARCHITECTURE**

### **Components**

1. **Cloud Agent** (`cloud_agent.py`)
   - Runs on Oracle Cloud VM
   - Draft-only mode
   - Monitors `Needs_Action/cloud/`
   - Creates drafts in `Drafts/`
   - Creates approval requests in `Pending_Approval/`

2. **Local Agent** (`local_agent.py`)
   - Runs on your local machine
   - Approval + Execute mode
   - Monitors `/Approved/`
   - Executes final actions via MCP
   - Updates `Dashboard.md`

3. **Health Monitor** (`health_monitor.py`)
   - Monitors agent health
   - Checks Git sync status
   - Alerts on failures
   - Runs every 5 minutes

4. **Security Guard** (`security_guard.py`)
   - Enforces permissions
   - Validates credentials
   - Prevents secret sync
   - Audit logging

5. **A2A Messenger** (`a2a_messenger.py`) - Optional
   - Direct agent communication
   - HTTP endpoints
   - File-based fallback
   - Runs on ports 8081/8082

### **Folder Structure**

```
C:\Users\CC\Documents\Obsidian Vault\
├── cloud_agent.py              # Cloud Agent
├── local_agent.py              # Local Agent
├── health_monitor.py           # Health Monitor
├── security_guard.py           # Security Guard
├── a2a_messenger.py            # A2A Messenger (optional)
├── platinum_demo.py            # Demo script
├── sync_vault.bat              # Local sync (Windows)
├── sync_vault.sh               # Cloud sync (Linux)
├── deploy_cloud_vm.sh          # VM deployment
├── deploy_cloud_agent.sh       # Cloud Agent deployment
├── .env.cloud.template         # Cloud credentials template
├── .env.local.template         # Local credentials template
├── .gitignore                  # Updated for Platinum
├── cloud/                      # Cloud-specific files
├── local/                      # Local-specific files
├── Drafts/
│   ├── email/                  # Email drafts
│   ├── social/                 # Social drafts
│   └── odoo/                   # Odoo drafts
├── In_Progress/
│   ├── cloud/                  # Cloud in-progress
│   └── local/                  # Local in-progress
├── Updates/                    # Cloud→Local updates
├── Signals/                    # A2A signals
└── Needs_Action/
    ├── cloud/                  # Cloud-owned items
    └── local/                  # Local-owned items
```

---

## ✅ **REQUIREMENTS**

### **Platinum Tier Requirements (7 Total)**

1. ✅ **Run AI Employee on Cloud 24/7**
   - Oracle Cloud Free VM
   - PM2 process management
   - Health monitoring

2. ✅ **Work-Zone Specialization**
   - Cloud: Draft-only
   - Local: Approval + Execute

3. ✅ **Delegation via Synced Vault**
   - Git-based sync
   - Claim-by-move rule
   - Single-writer Dashboard

4. ✅ **Security Rule (Secrets Never Sync)**
   - Separate credentials
   - `.gitignore` updated
   - Security Guard

5. ✅ **Deploy Odoo on Cloud VM**
   - Odoo Community
   - HTTPS with Let's Encrypt
   - Daily backups

6. ✅ **Optional A2A Upgrade**
   - Direct messaging
   - File fallback
   - HTTP endpoints

7. ✅ **Platinum Demo**
   - Minimum passing gate
   - Email→Draft→Approve→Execute

---

## 🚀 **QUICK START**

### **5-Minute Setup**

```bash
# 1. Clone your vault (if not already done)
cd "C:\Users\CC\Documents\Obsidian Vault"
git init
git add .
git commit -m "Platinum ready"

# 2. Test Platinum Demo
python platinum_demo.py

# 3. Test Cloud Agent
python cloud_agent.py

# 4. Test Local Agent
python local_agent.py

# 5. Test Health Monitor
python health_monitor.py cloud
```

### **Full Deployment (1 hour)**

1. **Sign up for Oracle Cloud**: https://www.oracle.com/cloud/free/
2. **Create VM**: Follow `deploy_cloud_vm.sh`
3. **Deploy Cloud Agent**: SSH and run `deploy_cloud_agent.sh`
4. **Setup Local Agent**: Run `python local_agent.py`
5. **Configure Git Sync**: Setup cron/Task Scheduler

---

## 📥 **INSTALLATION**

### **Local Machine (Windows)**

```bash
# 1. Install Python 3.13+
# Download from python.org

# 2. Install Git
# Download from git-scm.com

# 3. Clone vault
cd "C:\Users\CC\Documents"
git clone <YOUR_REPO> "Obsidian Vault"
cd "Obsidian Vault"

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create .env.local
copy .env.local.template .env.local
notepad .env.local  # Edit with credentials

# 6. Test Local Agent
python local_agent.py
```

### **Cloud VM (Oracle Cloud)**

```bash
# 1. SSH into VM
ssh -i ~/.ssh/id_rsa ubuntu@<PUBLIC_IP>

# 2. Run deployment script
cd /home/ubuntu
./deploy_cloud_agent.sh

# 3. Verify
pm2 status
```

---

## ⚙️ **CONFIGURATION**

### **Cloud Configuration (.env.cloud)**

```bash
# Copy template
cp .env.cloud.template .env.cloud

# Edit with your credentials
nano .env.cloud

# Required variables:
GMAIL_CLIENT_ID=your_cloud_client_id
GMAIL_CLIENT_SECRET=your_cloud_client_secret
ODOO_URL=http://localhost:8069
ODOO_DB=odoo_production
ODOO_USERNAME=cloud_user
ODOO_API_KEY=cloud_draft_only_key
CLOUD_AGENT_MODE=draft_only
```

### **Local Configuration (.env.local)**

```bash
# Copy template
copy .env.local.template .env.local

# Edit with your credentials
notepad .env.local

# Required variables:
GMAIL_CLIENT_ID=your_local_client_id
GMAIL_CLIENT_SECRET=your_local_client_secret
WHATSAPP_SESSION_PATH=C:/Users/CC/Documents/Obsidian Vault/whatsapp_session
BANK_API_URL=https://your-bank-api.com
BANK_API_KEY=your_bank_key
ODOO_URL=http://localhost:8069
ODOO_USERNAME=local_admin
ODOO_API_KEY=local_full_access_key
LOCAL_AGENT_MODE=execute
```

### **Git Sync Configuration**

**Local (Windows Task Scheduler):**

```batch
# Run sync_vault.bat every 5 minutes
# Already configured in sync_vault.bat
```

**Cloud (Cron):**

```bash
# Edit crontab
crontab -e

# Add line (already added by deploy script):
*/5 * * * * /home/ubuntu/sync_vault.sh
```

---

## 🚀 **DEPLOYMENT**

### **Deploy Cloud VM**

```bash
# 1. Run VM deployment script
./deploy_cloud_vm.sh

# 2. Note the public IP
# 3. Configure security list (ports 22, 443, 8069)
# 4. SSH into VM
ssh ubuntu@<PUBLIC_IP>

# 5. Run Cloud Agent deployment
./deploy_cloud_agent.sh
```

### **Deploy Local Agent**

```bash
# 1. On local machine
cd "C:\Users\CC\Documents\Obsidian Vault"

# 2. Create .env.local
copy .env.local.template .env.local

# 3. Edit credentials
notepad .env.local

# 4. Start Local Agent
python local_agent.py

# 5. (Optional) Setup Task Scheduler for auto-start
```

### **Deploy with PM2 (Cloud)**

```bash
# Start Cloud Agent
pm2 start cloud_agent.py --name cloud-agent --interpreter python3

# Start Health Monitor
pm2 start health_monitor.py --name health-monitor --interpreter python3 -- cloud

# Save PM2 configuration
pm2 save

# Setup PM2 startup
pm2 startup
```

---

## 🧪 **TESTING**

### **Run Platinum Demo**

```bash
cd "C:\Users\CC\Documents\Obsidian Vault"
python platinum_demo.py
```

**Expected Output:**
```
✅ PLATINUM DEMO COMPLETE!
📊 DEMO SUMMARY:
✅ 1. Email arrived while Local offline
✅ 2. Cloud Agent drafted reply (cannot send)
✅ 3. Cloud created approval request
✅ 4. Local (human) approved
✅ 5. Local executed send via MCP
✅ 6. Logged and moved to /Done
✅ 7. Dashboard updated
🏆 PLATINUM TIER MINIMUM PASSING GATE: PASSED!
```

### **Test Individual Components**

```bash
# Test Cloud Agent
python cloud_agent.py

# Test Local Agent
python local_agent.py

# Test Health Monitor
python health_monitor.py cloud

# Test Security Guard
python security_guard.py cloud

# Test A2A Messenger (optional)
python a2a_messenger.py cloud 8081
```

### **Test Git Sync**

```bash
# Manual sync test
cd "C:\Users\CC\Documents\Obsidian Vault"
sync_vault.bat

# Check sync.log for results
type sync.log
```

---

## 🔧 **TROUBLESHOOTING**

### **Cloud Agent Not Starting**

```bash
# Check logs
pm2 logs cloud-agent

# Restart
pm2 restart cloud-agent

# Check .env.cloud
cat .env.cloud

# Verify credentials
python security_guard.py cloud
```

### **Git Sync Failing**

```bash
# Check Git status
git status

# Force pull
git fetch --all
git reset --hard origin/main

# Re-push
git add .
git commit -m "Fix sync"
git push origin main
```

### **Health Monitor Alerts**

```bash
# Check health log
cat Logs/health.jsonl

# Check specific component
python health_monitor.py cloud

# Review alert files
ls Needs_Action/local/ALERT_*.md
```

### **Security Guard Issues**

```bash
# Run security check
python security_guard.py cloud

# Check .gitignore
cat .gitignore

# Verify credentials not in git
git ls-files | grep -E '\.env|credentials|token'
```

---

## 🔒 **SECURITY**

### **Credential Separation**

- **Cloud (`.env.cloud`)**: Draft-only credentials
- **Local (`.env.local`)**: Full-access credentials
- **NEVER sync**: `.env`, `credentials.json`, `token.json`, `whatsapp_session/`

### **.gitignore (Platinum Section)**

```gitignore
# 💿 PLATINUM TIER - Cloud/Local Separation
.env.cloud
.env.local
*.env
credentials.json
token.json
*.session
*.pickle
node_modules/
__pycache__/
*.pyc
Logs/
Dead_Letter_Queue/
In_Progress/
Updates/
Signals/
*.pem
*.key
*.crt
secrets/
```

### **Security Checklist**

- [ ] `.env.cloud` has draft-only credentials
- [ ] `.env.local` has full-access credentials
- [ ] `.gitignore` includes all sensitive patterns
- [ ] WhatsApp session on Local only
- [ ] Banking credentials on Local only
- [ ] Git sync working correctly
- [ ] Security Guard passing all checks

---

## 📊 **STATISTICS**

### **Code Statistics**

| Metric | Count |
|--------|-------|
| Python Scripts | 12+ files |
| Total Lines of Code | 5,000+ |
| Documentation Files | 6+ |
| Documentation Lines | 2,000+ |

### **Agents Created**

| Agent | Lines | Status |
|-------|-------|--------|
| `cloud_agent.py` | 1,000+ | ✅ |
| `local_agent.py` | 800+ | ✅ |
| `health_monitor.py` | 400+ | ✅ |
| `security_guard.py` | 400+ | ✅ |
| `a2a_messenger.py` | 400+ | ✅ |
| `platinum_demo.py` | 500+ | ✅ |

---

## 🎯 **SUBMISSION**

### **Hackathon Submission Checklist**

- [ ] All 7 Platinum requirements met
- [ ] `PLATINUM_TIER_COMPLETE.md` created
- [ ] Demo video recorded (5-10 min)
- [ ] Security checklist complete
- [ ] Architecture documented
- [ ] Code reviewed and tested
- [ ] Git repository public (or shared)
- [ ] Submit form: https://forms.gle/JR9T1SJq5rmQyGkGA

---

## 📞 **SUPPORT**

### **Documentation**

- `PLATINUM_TIER_COMPLETE.md` - Completion certificate
- `PLATINUM_START_HERE.md` - Quick overview
- `PLATINUM_QUICK_START.md` - Fast-track guide
- `PLATINUM_TEMPLATES.md` - Code templates

### **Resources**

- Oracle Cloud: https://www.oracle.com/cloud/free/
- Hackathon Document: `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`
- Wednesday Meetings: Zoom ID 871 8870 7642

---

**💿 PLATINUM TIER - READY FOR DEPLOYMENT!**

*Created: March 21, 2026*  
*Personal AI Employee Hackathon 0*
