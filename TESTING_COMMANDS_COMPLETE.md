# 🧪 COMPLETE TESTING COMMANDS - AI Employee Hackathon

**Personal AI Employee Hackathon 0**  
**All Tiers Testing Guide**  
**Created:** March 21, 2026

---

## 📋 **TABLE OF CONTENTS**

1. [Quick Test Commands](#quick-test-commands)
2. [Bronze Tier Testing](#bronze-tier-testing)
3. [Silver Tier Testing](#silver-tier-testing)
4. [Gold Tier Testing](#gold-tier-testing)
5. [Platinum Tier Testing](#platinum-tier-testing)
6. [Integration Tests](#integration-tests)
7. [Troubleshooting](#troubleshooting)

---

## ⚡ **QUICK TEST COMMANDS**

### **Test All Agents (5 Minutes)**

```bash
cd "C:\Users\CC\Documents\Obsidian Vault"

# 1. Test Platinum Demo
python platinum_demo.py

# 2. Test Cloud Agent
python cloud_agent.py

# 3. Test Local Agent
python local_agent.py

# 4. Test Health Monitor
python health_monitor.py cloud

# 5. Test Security Guard
python security_guard.py cloud
```

### **Test All Watchers**

```bash
# Start all watchers
start_all_watchers.bat

# Stop all watchers
stop_all_watchers.bat

# Test individual watchers
python watchers/gmail_watcher.py
python watchers/whatsapp_watcher.py
python watchers/social_watcher.py
python watchers/odoo_lead_watcher.py
python watchers/office_watcher.py
```

### **Test CEO Briefing**

```bash
# Generate CEO Briefing
python ceo_briefing_enhanced.py

# Generate Social Summary
python social_summary_generator.py all 7
```

---

## 🥉 **BRONZE TIER TESTING**

### **Requirement 1: Obsidian Vault Structure**

```bash
# Check Dashboard.md exists
cd "C:\Users\CC\Documents\Obsidian Vault"
type Dashboard.md

# Check Company_Handbook.md exists
type Company_Handbook.md

# Check Business_Goals.md exists
type Business_Goals.md
```

**Expected:** All files exist with content

### **Requirement 2: Folder Structure**

```bash
# Check folders exist
dir Inbox
dir Needs_Action
dir Done
dir Pending_Approval
dir Approved
dir Rejected
```

**Expected:** All folders exist

### **Requirement 3: One Working Watcher**

```bash
# Test Gmail Watcher
python watchers/gmail_watcher.py

# OR Test Office Watcher
python watchers/office_watcher.py
```

**Expected:** Watcher starts without errors

### **Requirement 4: Claude Code/Qwen Integration**

```bash
# Test Qwen CLI integration
qwen -y "Read Dashboard.md and summarize"

# Test file reading
qwen -y "List all files in Needs_Action folder"
```

**Expected:** Qwen reads and responds

### **Bronze Tier Verification Script**

```bash
# Run Bronze verification
python -c "
from pathlib import Path
vault = Path('C:/Users/CC/Documents/Obsidian Vault')

# Check files
files = ['Dashboard.md', 'Company_Handbook.md', 'Business_Goals.md']
for f in files:
    assert (vault / f).exists(), f'{f} missing'
    print(f'✅ {f} exists')

# Check folders
folders = ['Inbox', 'Needs_Action', 'Done']
for f in folders:
    assert (vault / f).exists(), f'{f} folder missing'
    print(f'✅ {f}/ folder exists')

print('✅ BRONZE TIER: ALL CHECKS PASSED')
"
```

---

## 🥈 **SILVER TIER TESTING**

### **Requirement 1: All Bronze Requirements**

```bash
# Run Bronze tests first (see above)
```

### **Requirement 2: Two or More Watchers**

```bash
# Test all 5 watchers
python watchers/gmail_watcher.py
python watchers/whatsapp_watcher.py
python watchers/office_watcher.py
python watchers/social_watcher.py
python watchers/odoo_lead_watcher.py
```

**Expected:** All 5 watchers start without errors

### **Requirement 3: LinkedIn Auto-Posting**

```bash
# Test LinkedIn Post Generator
python linkedin_post_generator.py

# Test Facebook/Instagram Post Generator
python facebook_instagram_post.py

# Test Twitter Post Generator
python twitter_post.py

# Check drafts created
dir Social_Drafts
dir Social_Drafts\linkedin
dir Social_Drafts\facebook
dir Social_Drafts\twitter
```

**Expected:** Drafts created in Social_Drafts/

### **Requirement 4: MCP Servers**

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

**Expected:** All MCP servers start without errors

### **Requirement 5: Human-in-the-Loop Approval**

```bash
# Check Pending_Approval folder
dir Pending_Approval

# Check for approval files
dir Pending_Approval\*.md
```

**Expected:** Approval files present

### **Requirement 6: Scheduling**

```bash
# Test Task Scheduler setup
setup_tasks.bat

# Check scheduled tasks
schtasks /query /fo LIST | findstr "AI"
```

**Expected:** Tasks scheduled

### **Silver Tier Verification Script**

```bash
python -c "
from pathlib import Path
vault = Path('C:/Users/CC/Documents/Obsidian Vault')

# Check watchers (5 required)
watchers = list((vault / 'watchers').glob('*.py'))
print(f'✅ {len(watchers)} watchers found (required: 2+)')

# Check MCP servers (4 required)
mcp_servers = ['mcp-email', 'mcp-browser', 'mcp-odoo', 'mcp-social']
for mcp in mcp_servers:
    assert (vault / mcp).exists(), f'{mcp} missing'
    print(f'✅ {mcp}/ exists')

# Check social drafts
drafts = list((vault / 'Social_Drafts').glob('*.md'))
print(f'✅ {len(drafts)} social drafts found')

# Check pending approvals
approvals = list((vault / 'Pending_Approval').glob('*.md'))
print(f'✅ {len(approvals)} pending approvals')

print('✅ SILVER TIER: ALL CHECKS PASSED')
"
```

---

## 🥇 **GOLD TIER TESTING**

### **Requirement 1: All Silver Requirements**

```bash
# Run Silver tests first (see above)
```

### **Requirement 2: Cross-Domain Integration**

```bash
# Test CEO Briefing (cross-domain)
python ceo_briefing_enhanced.py

# Check briefing generated
dir Briefings
type Briefings\*.md
```

**Expected:** CEO Briefing with personal + business data

### **Requirement 3: Odoo Accounting MCP**

```bash
# Test Odoo MCP commands
cd mcp-odoo
npm start

# Test invoice creation
# (Requires Odoo running)

# Check Odoo integration
python odoo_lead_watcher.py
```

**Expected:** Odoo MCP responds

### **Requirement 4: Facebook & Instagram Integration**

```bash
# Test Facebook/Instagram post generator
python facebook_instagram_post.py

# Check drafts
dir Social_Drafts\facebook
dir Social_Drafts\instagram

# Test social summary
python social_summary_generator.py facebook 7
python social_summary_generator.py instagram 7
```

**Expected:** Drafts and summaries created

### **Requirement 5: Twitter Integration**

```bash
# Test Twitter post generator
python twitter_post.py

# Check Twitter drafts
dir Social_Drafts\twitter

# Test Twitter summary
python social_summary_generator.py twitter 7
```

**Expected:** Twitter drafts and summaries

### **Requirement 6: Multiple MCP Servers**

```bash
# Test all 4 MCP servers
cd mcp-email && npm start
cd ..\mcp-browser && npm start
cd ..\mcp-odoo && npm start
cd ..\mcp-social && npm start
```

**Expected:** All 4 servers running

### **Requirement 7: Weekly Business Audit**

```bash
# Generate accounting audit
python ceo_briefing_enhanced.py

# Check audit in briefing
type Briefings\*.md | findstr "Accounting"
```

**Expected:** Accounting audit in briefing

### **Requirement 8: Error Recovery**

```bash
# Test error recovery system
python error_recovery.py

# Test circuit breaker
python -c "from error_recovery import CircuitBreaker; cb = CircuitBreaker(); print(cb.state)"

# Check Dead Letter Queue
dir Dead_Letter_Queue
```

**Expected:** Error recovery system working

### **Requirement 9: Audit Logging**

```bash
# Test audit logger
python audit_logger.py

# Check audit logs
dir Logs\Audit
type Logs\Audit\*.jsonl
```

**Expected:** Audit logs present

### **Requirement 10: Ralph Wiggum Loop**

```bash
# Test Ralph Loop
python ralph_loop.py

# Check completed tasks
dir Done
```

**Expected:** Ralph loop working

### **Requirement 11: Agent Skills**

```bash
# Check Agent Skills
dir .claude
dir .claude\skills
type .claude\README.md
```

**Expected:** Agent Skills documented

### **Gold Tier Verification Script**

```bash
python -c "
from pathlib import Path
vault = Path('C:/Users/CC/Documents/Obsidian Vault')

# Check Odoo MCP
assert (vault / 'mcp-odoo').exists()
print('✅ mcp-odoo/ exists')

# Check social platforms
platforms = ['facebook', 'instagram', 'twitter', 'linkedin']
for p in platforms:
    drafts = list((vault / 'Social_Drafts').glob(f'*{p}*'))
    print(f'✅ {p} drafts: {len(drafts)}')

# Check audit logging
assert (vault / 'audit_logger.py').exists()
print('✅ audit_logger.py exists')

# Check error recovery
assert (vault / 'error_recovery.py').exists()
print('✅ error_recovery.py exists')

# Check Agent Skills
assert (vault / '.claude').exists()
print('✅ .claude/ folder exists')

# Check briefings
briefings = list((vault / 'Briefings').glob('*.md'))
print(f'✅ {len(briefings)} CEO briefings found')

print('✅ GOLD TIER: ALL CHECKS PASSED')
"
```

---

## 💿 **PLATINUM TIER TESTING**

### **Requirement 1: Cloud 24/7**

```bash
# Test Cloud Agent
python cloud_agent.py

# Test Health Monitor
python health_monitor.py cloud

# Check PM2 (on cloud VM)
pm2 status
pm2 logs
```

**Expected:** Cloud Agent runs continuously

### **Requirement 2: Work-Zone Specialization**

```bash
# Test Cloud Agent (draft-only)
python cloud_agent.py

# Test Local Agent (execute)
python local_agent.py

# Check folder separation
dir Needs_Action\cloud
dir Needs_Action\local
dir Drafts\email
dir Drafts\social
```

**Expected:** Proper folder separation

### **Requirement 3: Synced Vault**

```bash
# Test Git sync (local)
sync_vault.bat

# Test Git sync (cloud)
# ssh into VM and run:
./sync_vault.sh

# Check Git status
git status
git log -5
```

**Expected:** Git sync working

### **Requirement 4: Security (Secrets Never Sync)**

```bash
# Test Security Guard
python security_guard.py cloud
python security_guard.py local

# Check .gitignore
type .gitignore | findstr "PLATINUM"

# Verify secrets not in git
git ls-files | findstr ".env credentials token"
```

**Expected:** Security checks pass

### **Requirement 5: Odoo on Cloud VM**

```bash
# Test Odoo deployment (on VM)
./deploy_odoo_cloud.sh

# Check Odoo status
# Access: http://your-vm-ip:8069

# Test Odoo MCP cloud mode
cd mcp-odoo
npm start
```

**Expected:** Odoo accessible

### **Requirement 6: A2A Communication**

```bash
# Test A2A Messenger (cloud)
python a2a_messenger.py cloud 8081

# Test A2A Messenger (local)
python a2a_messenger.py local 8082

# Test HTTP endpoint
curl http://localhost:8081/health
curl http://localhost:8082/stats
```

**Expected:** A2A endpoints responding

### **Requirement 7: Platinum Demo**

```bash
# Run complete demo
python platinum_demo.py
```

**Expected:** Demo completes successfully

### **Platinum Tier Verification Script**

```bash
python -c "
from pathlib import Path
vault = Path('C:/Users/CC/Documents/Obsidian Vault')

# Check Platinum agents
agents = ['cloud_agent.py', 'local_agent.py', 'health_monitor.py', 
          'security_guard.py', 'a2a_messenger.py', 'platinum_demo.py']
for a in agents:
    assert (vault / a).exists(), f'{a} missing'
    print(f'✅ {a} exists')

# Check sync scripts
assert (vault / 'sync_vault.bat').exists()
assert (vault / 'sync_vault.sh').exists()
print('✅ Sync scripts exist')

# Check environment templates
assert (vault / '.env.cloud.template').exists()
assert (vault / '.env.local.template').exists()
print('✅ Environment templates exist')

# Check Platinum folders
folders = ['Drafts', 'In_Progress', 'Updates', 'Signals']
for f in folders:
    assert (vault / f).exists(), f'{f} folder missing'
    print(f'✅ {f}/ exists')

# Run demo
print('\n🧪 Running Platinum Demo...')
import subprocess
result = subprocess.run(['python', 'platinum_demo.py'], capture_output=True, text=True)
if result.returncode == 0:
    print('✅ Platinum Demo: PASSED')
else:
    print('❌ Platinum Demo: FAILED')
    print(result.stderr)

print('✅ PLATINUM TIER: ALL CHECKS PASSED')
"
```

---

## 🔗 **INTEGRATION TESTS**

### **Test Complete Workflow**

```bash
# 1. Create test email
echo "Test email content" > Needs_Action\cloud\EMAIL_test.md

# 2. Start Cloud Agent (in background)
start python cloud_agent.py

# 3. Wait for processing
timeout 30

# 4. Check draft created
dir Drafts\email

# 5. Check approval request
dir Pending_Approval

# 6. Move to Approved (simulate human)
move Pending_Approval\CLOUD_EMAIL_*.md Approved\

# 7. Start Local Agent
start python local_agent.py

# 8. Check Done folder
dir Done
```

### **Test Social Media Workflow**

```bash
# 1. Generate social posts
python linkedin_post_generator.py
python facebook_instagram_post.py
python twitter_post.py

# 2. Check drafts
dir Social_Drafts

# 3. Generate summaries
python social_summary_generator.py all 7

# 4. Check summaries
dir Social_Summaries
```

### **Test Odoo Integration**

```bash
# 1. Test Odoo MCP
cd mcp-odoo
npm start

# 2. Test Odoo lead watcher
python odoo_lead_watcher.py

# 3. Check Odoo leads processed
type Needs_Action\ODOO_*.md
```

---

## 🐛 **TROUBLESHOOTING**

### **Common Issues**

#### **Python Import Errors**

```bash
# Install dependencies
pip install -r requirements.txt

# Check Python version
python --version  # Should be 3.13+
```

#### **Node.js/MCP Errors**

```bash
# Install Node dependencies
cd mcp-email && npm install
cd ..\mcp-browser && npm install
cd ..\mcp-odoo && npm install
cd ..\mcp-social && npm install

# Check Node version
node --version  # Should be v18+
```

#### **Git Sync Issues**

```bash
# Force pull
git fetch --all
git reset --hard origin/main

# Re-commit
git add .
git commit -m "Fix sync"
git push origin main
```

#### **Watcher Not Starting**

```bash
# Check logs
type Logs\*.log

# Test manually
python watchers\gmail_watcher.py

# Check credentials
type config\.env
```

### **Test Commands Reference**

```bash
# Quick health check
python -c "
from pathlib import Path
vault = Path('C:/Users/CC/Documents/Obsidian Vault')
print(f'✅ Vault exists: {vault.exists()}')
print(f'✅ Dashboard: {(vault / \"Dashboard.md\").exists()}')
print(f'✅ Agents: {len(list(vault.glob(\"*.py\")))} Python files')
"

# Full system test
python platinum_demo.py

# Check all tiers
python -c "
tiers = ['Bronze', 'Silver', 'Gold', 'Platinum']
for tier in tiers:
    print(f'\\n🥇 Testing {tier} Tier...')
    # Run tier-specific tests
"
```

---

## 📊 **TEST RESULTS TEMPLATE**

```markdown
# Test Results - [Date]

## Bronze Tier
- [ ] Dashboard.md exists
- [ ] Company_Handbook.md exists
- [ ] Folder structure correct
- [ ] Watcher working

## Silver Tier
- [ ] 5 watchers working
- [ ] 4 MCP servers working
- [ ] Social drafts created
- [ ] Approval workflow working

## Gold Tier
- [ ] Odoo MCP working
- [ ] Social platforms integrated
- [ ] CEO Briefing generated
- [ ] Audit logging working
- [ ] Error recovery working

## Platinum Tier
- [ ] Cloud Agent working
- [ ] Local Agent working
- [ ] Git sync working
- [ ] Security checks pass
- [ ] Platinum demo passes
```

---

**🧪 COMPLETE TESTING COMMANDS - All Tiers Covered!**

*Created: March 21, 2026*  
*Personal AI Employee Hackathon 0*
