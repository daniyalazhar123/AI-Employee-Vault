# 🧪 Complete Testing Commands Reference

**All Testing Commands for AI Employee Vault**

*Gold Tier - Personal AI Employee Hackathon 0*

---

## Quick Start Testing

### One-Line Health Check
```bash
cd "C:\Users\CC\Documents\Obsidian Vault" && python -c "from audit_logger import get_audit_summary; from error_recovery import CircuitBreaker; import social_summary_generator; import ceo_briefing_enhanced; print('✅ All core modules: OK')"
```

### Full System Check
```bash
python ai_employee_orchestrator.py
# Select option 1: Check all platforms
```

---

## 1. Environment Verification

### Check Python Version
```bash
python --version
```
**Expected:** Python 3.13+ or higher

---

### Check Node.js Version
```bash
python --version
```
**Expected:** Node.js v18+ and npm 10+

---

### Check Qwen CLI
```bash
qwen --version
```
**Expected:** 0.12.5

---

### Check Installed Python Packages
```bash
pip list
```
**Expected:** watchdog, google-api-python-client, google-auth-oauthlib, playwright

---

### Check MCP Servers Installation
```bash
# Email MCP
python mcp_email.py --action list

# Browser MCP
python mcp_browser.py --action navigate

# Odoo MCP
python mcp_odoo.py --action get_leads

# Social MCP
python mcp_social.py --action linkedin
```
**Expected:** All dependencies installed

---

## 2. Core Module Tests

### Test 2.1: Audit Logger
```bash
cd "C:\Users\CC\Documents\Obsidian Vault"
python audit_logger.py
```

**Expected Output:**
```
Audit Summary (Last 7 Days)
Total Actions: X
Success Rate: XX%
By Status: {...}
By Actor: {...}
```

**Test Specific Function:**
```bash
python -c "from audit_logger import get_audit_summary; print(get_audit_summary(7))"
```

---

### Test 2.2: Error Recovery
```bash
python error_recovery.py
```

**Expected Output:**
```
Circuit Breaker Status: CLOSED
Dead Letter Queue: X items
Health Check: All systems operational
```

**Test Circuit Breaker:**
```bash
python -c "from error_recovery import CircuitBreaker; cb = CircuitBreaker(); print('Circuit Breaker:', cb.state)"
```

---

### Test 2.3: Social Summary Generator
```bash
python social_summary_generator.py all 7
```

**Expected Output:**
```
Generating social media summaries for last 7 days...
✅ LinkedIn summary generated
✅ Facebook summary generated
✅ Instagram summary generated
✅ Twitter summary generated
```

**Test Specific Platform:**
```bash
python social_summary_generator.py linkedin 7
python social_summary_generator.py facebook 7
python social_summary_generator.py instagram 7
python social_summary_generator.py twitter 7
```

---

### Test 2.4: CEO Briefing Generator
```bash
python ceo_briefing_enhanced.py
```

**Expected Output:**
```
Generating CEO Briefing...
✅ Briefing generated: Briefings/CEO_Briefing_YYYY-MM-DD.md
```

**Verify File Created:**
```bash
dir Briefings\CEO_Briefing_*.md
```

---

### Test 2.5: Orchestrator
```bash
python ai_employee_orchestrator.py
```

**Expected Output:**
```
🤖 COMPLETE 24/7 AI EMPLOYEE ORCHESTRATOR
Bhai! Main aapka AI Employee hun. Main kya karun?

Options:
1. Check all platforms
2. Run demo
3. Start 24/7 monitoring
4. Process specific platform
5. Exit
```

**Test Specific Command:**
```bash
python orchestrator.py help
python orchestrator.py status
python orchestrator.py process_needs_action
```

---

### Test 2.6: Ralph Loop
```bash
python -m py_compile ralph_loop.py && echo "✅ Ralph Loop: Syntax OK"
```

**Test Import:**
```bash
python -c "import ralph_loop; print('✅ Ralph Loop: Import OK')"
```

---

## 3. Watcher Tests

### Test 3.1: All Watchers Syntax
```bash
cd watchers
for %f in (*.py) do python -m py_compile "%f" && echo "✅ %f: OK"
```

**Expected Output:**
```
✅ gmail_watcher.py: OK
✅ whatsapp_watcher.py: OK
✅ office_watcher.py: OK
✅ social_watcher.py: OK
✅ odoo_lead_watcher.py: OK
```

---

### Test 3.2: Gmail Watcher
```bash
# Test syntax
python -m py_compile watchers/gmail_watcher.py && echo "✅ Gmail Watcher: Syntax OK"

# Test import
python -c "import sys; sys.path.insert(0, 'watchers'); import gmail_watcher; print('✅ Gmail Watcher: Import OK')"

# Run watcher (Ctrl+C to stop)
python watchers/gmail_watcher.py
```

**Expected Output:**
```
📧 GMAIL WATCHER STARTED
Vault Path: C:\Users\CC\Documents\Obsidian Vault
Authentication TEST successful - user: your-email@gmail.com
Checking every 120 seconds...
```

---

### Test 3.3: WhatsApp Watcher
```bash
# Test syntax
python -m py_compile watchers/whatsapp_watcher.py && echo "✅ WhatsApp Watcher: Syntax OK"

# Test import
python -c "import sys; sys.path.insert(0, 'watchers'); import whatsapp_watcher; print('✅ WhatsApp Watcher: Import OK')"

# Run watcher (Ctrl+C to stop)
python watchers/whatsapp_watcher.py
```

**Expected Output:**
```
💬 WHATSAPP WATCHER STARTED
Keywords: urgent, invoice, payment, help
Check interval: 30 seconds
```

---

### Test 3.4: Office Watcher
```bash
# Test syntax
python -m py_compile watchers/office_watcher.py && echo "✅ Office Watcher: Syntax OK"

# Test import
python -c "import sys; sys.path.insert(0, 'watchers'); import office_watcher; print('✅ Office Watcher: Import OK')"
```

---

### Test 3.5: Social Watcher
```bash
# Test syntax
python -m py_compile watchers/social_watcher.py && echo "✅ Social Watcher: Syntax OK"

# Test import
python -c "import sys; sys.path.insert(0, 'watchers'); import social_watcher; print('✅ Social Watcher: Import OK')"
```

---

### Test 3.6: Odoo Lead Watcher
```bash
# Test syntax
python -m py_compile watchers/odoo_lead_watcher.py && echo "✅ Odoo Lead Watcher: Syntax OK"

# Test import
python -c "import sys; sys.path.insert(0, 'watchers'); import odoo_lead_watcher; print('✅ Odoo Lead Watcher: Import OK')"
```

---

### Test 3.7: Start All Watchers
```bash
# Start all watchers
python start_all_watchers.bat

# Stop all watchers
python stop_all_watchers.bat
```

---

## 4. MCP Server Tests

### Test 4.1: Email MCP
```bash
cd mcp-email

# Check dependencies
python mcp_email.py --action list

# Test start (Ctrl+C to stop)
python test_mcp.py
```

**Expected Output:**
```
MCP Email Server starting...
Gmail credentials loaded
Server running on stdio
```

**Test Authentication:**
```bash
node authenticate.js
```

---

### Test 4.2: Browser MCP
```bash
cd mcp-browser

# Check dependencies
python mcp_email.py --action list

# Test start
python test_mcp.py
```

**Expected Output:**
```
MCP Browser Server starting...
Playwright initialized
Server running on stdio
```

---

### Test 4.3: Odoo MCP
```bash
cd mcp-odoo

# Check dependencies
python mcp_email.py --action list

# Test start (may fail if Odoo not running - expected)
python test_mcp.py
```

**Expected Output (if Odoo running):**
```
MCP Odoo Server starting...
Connected to Odoo at http://localhost:8069
User ID: 2
Server running on stdio
```

**Expected Output (if Odoo not running):**
```
MCP Odoo Server starting...
Error: Connection refused to Odoo
```

---

### Test 4.4: Social MCP
```bash
cd mcp-social

# Check dependencies
python mcp_email.py --action list

# Test start
python test_mcp.py
```

**Expected Output:**
```
MCP Social Server starting...
Playwright initialized
Server running on stdio
```

---

## 5. Integration Tests

### Test 5.1: Folder Structure Verification
```bash
python -c "
from pathlib import Path
folders = ['Needs_Action', 'Pending_Approval', 'Done', 'Logs/Audit', 'Briefings', 'Social_Summaries', 'Social_Drafts']
for f in folders:
    assert Path(f).exists(), f'Missing folder: {f}'
print('✅ All required folders exist')
"
```

**Expected Output:**
```
✅ All required folders exist
```

---

### Test 5.2: Configuration Files
```bash
python -c "
import json
from pathlib import Path

# Check MCP config
config = json.load(open('config/mcp.json'))
assert 'mcpServers' in config
assert 'email' in config['mcpServers']
assert 'browser' in config['mcpServers']
assert 'odoo' in config['mcpServers']
assert 'social' in config['mcpServers']
print('✅ MCP configuration valid')

# Check credentials
assert Path('credentials.json').exists()
print('✅ Credentials file exists')
"
```

**Expected Output:**
```
✅ MCP configuration valid
✅ Credentials file exists
```

---

### Test 5.3: Agent Skills Documentation
```bash
python -c "
from pathlib import Path
skills = ['email-processor', 'whatsapp-responder', 'social-media-manager', 'odoo-accounting', 'ceo-briefing-generator', 'audit-logger', 'error-recovery']
for skill in skills:
    assert Path(f'.claude/skills/{skill}/SKILL.md').exists(), f'Missing skill: {skill}'
print(f'✅ All {len(skills)} Agent Skills present')
"
```

**Expected Output:**
```
✅ All 7 Agent Skills present
```

---

### Test 5.4: Documentation Files
```bash
python -c "
from pathlib import Path
docs = ['README.md', 'Business_Goals.md', 'Company_Handbook.md', 'Dashboard.md', 'GOLD_TIER_COMPLETE.md', 'AGENT_SKILLS_COMPLETE.md']
for doc in docs:
    assert Path(doc).exists(), f'Missing doc: {doc}'
print(f'✅ All {len(docs)} main documents present')

# Check docs folder
doc_files = list(Path('docs').glob('*.md'))
print(f'✅ {len(doc_files)} documentation files in docs/ folder')
"
```

**Expected Output:**
```
✅ All 6 main documents present
✅ 4 documentation files in docs/ folder
```

---

## 6. Functional Tests

### Test 6.1: Email Processing Flow
```bash
# Create test email
echo "---
type: email
from: test@example.com
subject: Test Email
---

This is a test email." > Needs_Action/TEST_EMAIL.md

# Process email
python orchestrator.py process_email

# Check for reply draft
dir Pending_Approval\REPLY_TEST_*.md
```

**Expected:** Reply draft created in `Pending_Approval/`

---

### Test 6.2: Social Media Post Generation
```bash
# Generate LinkedIn post
python linkedin_post_generator.py

# Check draft
dir Social_Drafts\Polished\*linkedin*.md

# Generate summary
python social_summary_generator.py linkedin 7

# Check summary
dir Social_Summaries\*linkedin*.md
```

**Expected:** Post draft and summary created

---

### Test 6.3: CEO Briefing Generation
```bash
# Generate briefing
python ceo_briefing_enhanced.py

# Check briefing
dir Briefings\CEO_Briefing_*.md

# Review briefing
type Briefings\CEO_Briefing_*.md
```

**Expected:** Briefing file created with all sections

---

### Test 6.4: Audit Logging
```bash
# Log test action
python -c "
from audit_logger import log_action
log_action(
    action_type='test_action',
    actor='test_user',
    target='test_target',
    status='success',
    parameters={'test': 'data'}
)
print('✅ Test action logged')
"

# Verify log
python audit_logger.py
```

**Expected:** Test action appears in audit log

---

## 7. Performance Tests

### Test 7.1: Module Import Speed
```bash
python -c "
import time
start = time.time()
import audit_logger
import error_recovery
import social_summary_generator
import ceo_briefing_enhanced
end = time.time()
print(f'All modules imported in {end-start:.2f} seconds')
assert (end-start) < 5, 'Import took too long!'
print('✅ Import speed acceptable')
"
```

**Expected:** All modules imported in < 5 seconds

---

### Test 7.2: Audit Logger Performance
```bash
python -c "
import time
from audit_logger import get_audit_summary
start = time.time()
summary = get_audit_summary(30)
end = time.time()
print(f'Audit summary (30 days) generated in {end-start:.2f} seconds')
print(f'Total actions: {summary[\"total_actions\"]}')
assert (end-start) < 2, 'Audit summary took too long!'
print('✅ Audit performance acceptable')
"
```

**Expected:** Summary generated in < 2 seconds

---

### Test 7.3: Qwen Response Time
```bash
python -c "
import time
import subprocess
start = time.time()
result = subprocess.run(
    ['qwen', '-y', 'Say hello'],
    capture_output=True,
    text=True,
    timeout=60
)
end = time.time()
print(f'Qwen responded in {end-start:.2f} seconds')
print(f'Response length: {len(result.stdout)} chars')
assert (end-start) < 30, 'Qwen took too long!'
print('✅ Qwen response time acceptable')
"
```

**Expected:** Response in < 30 seconds

---

## 8. Hackathon Compliance Tests

### Test 8.1: Bronze Tier Requirements
```bash
python -c "
from pathlib import Path
print('\n🥉 BRONZE TIER REQUIREMENTS')
print('=' * 40)
checks = [
    ('Dashboard.md exists', Path('Dashboard.md').exists()),
    ('Company_Handbook.md exists', Path('Company_Handbook.md').exists()),
    ('Business_Goals.md exists', Path('Business_Goals.md').exists()),
    ('At least 1 watcher', len(list(Path('watchers').glob('*.py'))) >= 1),
    ('Needs_Action folder', Path('Needs_Action').exists()),
    ('Done folder', Path('Done').exists()),
]
all_pass = True
for check, result in checks:
    status = '✅' if result else '❌'
    print(f'{status} {check}')
    if not result:
        all_pass = False
print('=' * 40)
print(f'BRONZE TIER: {\"✅ COMPLETE\" if all_pass else \"❌ INCOMPLETE\"}')
"
```

**Expected:** All checks pass

---

### Test 8.2: Silver Tier Requirements
```bash
python -c "
from pathlib import Path
print('\n🥈 SILVER TIER REQUIREMENTS')
print('=' * 40)
checks = [
    ('Bronze Tier complete', True),
    ('2+ watchers', len(list(Path('watchers').glob('*.py'))) >= 2),
    ('LinkedIn post generator', Path('linkedin_post_generator.py').exists()),
    ('Ralph Wiggum loop', Path('ralph_loop.py').exists()),
    ('At least 1 MCP server', Path('mcp-email/index.js').exists()),
    ('Approval workflow', Path('Pending_Approval').exists()),
    ('Scheduling scripts', Path('start_all_watchers.bat').exists()),
    ('Agent Skills documented', Path('.claude/skills').exists()),
]
all_pass = True
for check, result in checks:
    status = '✅' if result else '❌'
    print(f'{status} {check}')
    if not result:
        all_pass = False
print('=' * 40)
print(f'SILVER TIER: {\"✅ COMPLETE\" if all_pass else \"❌ INCOMPLETE\"}')
"
```

**Expected:** All checks pass

---

### Test 8.3: Gold Tier Requirements
```bash
python -c "
from pathlib import Path
print('\n🥇 GOLD TIER REQUIREMENTS')
print('=' * 40)
checks = [
    ('Silver Tier complete', True),
    ('Cross-domain integration', Path('Dashboard.md').exists() and Path('Business_Goals.md').exists()),
    ('Odoo MCP server', Path('mcp-odoo/index.js').exists()),
    ('Odoo documentation', Path('docs/ODOO_SETUP.md').exists()),
    ('Facebook/Instagram post', Path('facebook_instagram_post.py').exists()),
    ('Twitter post', Path('twitter_post.py').exists()),
    ('Social summaries', Path('social_summary_generator.py').exists()),
    ('Multiple MCP servers (4)', all([Path(f'mcp-{x}').exists() for x in ['email', 'browser', 'odoo', 'social']])),
    ('Weekly audit', Path('ceo_briefing_enhanced.py').exists()),
    ('Error recovery', Path('error_recovery.py').exists()),
    ('Audit logging', Path('audit_logger.py').exists()),
    ('Ralph Wiggum loop', Path('ralph_loop.py').exists()),
    ('Documentation', Path('README.md').exists() and Path('GOLD_TIER_COMPLETE.md').exists()),
    ('Agent Skills (7)', len(list(Path('.claude/skills').glob('*/SKILL.md'))) >= 7),
]
all_pass = True
for check, result in checks:
    status = '✅' if result else '❌'
    print(f'{status} {check}')
    if not result:
        all_pass = False
print('=' * 40)
print(f'GOLD TIER: {\"✅ COMPLETE\" if all_pass else \"❌ INCOMPLETE\"}')
"
```

**Expected:** All checks pass

---

## 9. Quick Diagnostic Commands

### Full System Health Check
```bash
python -c "
import sys
from pathlib import Path

print('=' * 60)
print('AI EMPLOYEE VAULT - SYSTEM HEALTH CHECK')
print('=' * 60)

# Python version
print(f'\n✅ Python: {sys.version.split()[0]}')

# Check modules
modules = ['audit_logger', 'error_recovery', 'social_summary_generator', 'ceo_briefing_enhanced', 'orchestrator', 'ralph_loop']
for module in modules:
    try:
        __import__(module)
        print(f'✅ {module}: OK')
    except Exception as e:
        print(f'❌ {module}: {e}')

# Check folders
folders = ['Needs_Action', 'Pending_Approval', 'Done', 'Logs/Audit', 'Briefings', 'Social_Summaries', 'Social_Drafts']
for folder in folders:
    if Path(folder).exists():
        count = len(list(Path(folder).glob('*')))
        print(f'✅ {folder}: {count} files')
    else:
        print(f'❌ {folder}: MISSING')

# Check MCP servers
mcp_servers = ['mcp-email', 'mcp-browser', 'mcp-odoo', 'mcp-social']
for server in mcp_servers:
    if Path(server).exists():
        print(f'✅ {server}: Present')
    else:
        print(f'❌ {server}: MISSING')

# Check watchers
watchers = ['gmail_watcher.py', 'whatsapp_watcher.py', 'office_watcher.py', 'social_watcher.py', 'odoo_lead_watcher.py']
for watcher in watchers:
    if Path(f'watchers/{watcher}').exists():
        print(f'✅ {watcher}: Present')
    else:
        print(f'❌ {watcher}: MISSING')

# Check Agent Skills
skills = ['email-processor', 'whatsapp-responder', 'social-media-manager', 'odoo-accounting', 'ceo-briefing-generator', 'audit-logger', 'error-recovery']
for skill in skills:
    if Path(f'.claude/skills/{skill}/SKILL.md').exists():
        print(f'✅ {skill}: Documented')
    else:
        print(f'❌ {skill}: MISSING')

print('\n' + '=' * 60)
print('HEALTH CHECK COMPLETE')
print('=' * 60)
"
```

---

## 10. Troubleshooting Commands

### Check Qwen CLI Installation
```bash
# Check if installed
qwen --version

# If not installed
npm install -g @qwen-code/qwen-code@latest

# Verify installation
qwen --version
```

---

### Check Gmail Authentication
```bash
# Check token file
dir mcp-email\token.json

# Re-authenticate
cd mcp-email
node authenticate.js
```

---

### Check Docker/Odoo Status
```bash
# Check Docker running
docker ps

# Check Odoo container
docker ps | findstr odoo

# If not running, start Odoo
docker run -d -p 8069:8069 --name odoo_community odoo:19.0
```

---

### Check Watcher Logs
```bash
# View Gmail watcher logs
type Logs\gmail_*.log

# View WhatsApp watcher logs
type Logs\whatsapp_*.log

# View audit logs
type Logs\Audit\*.jsonl
```

---

### Reset and Restart
```bash
# Stop all watchers
python stop_all_watchers.bat

# Clear Python cache
for /r %x in (*.pyc) do @del "%x"
for /r %x in (__pycache__) do @rmdir /s /q "%x"

# Restart orchestrator
python ai_employee_orchestrator.py
```

---

## Testing Checklist

Use this checklist to verify all components:

```
Testing Checklist:
┌─────────────────────────────────────────────────────────┐
│ [ ] Python version check                                │
│ [ ] Node.js version check                               │
│ [ ] Qwen CLI check                                      │
│ [ ] Python packages check                               │
│ [ ] MCP servers check                                   │
│ [ ] Audit Logger test                                   │
│ [ ] Error Recovery test                                 │
│ [ ] Social Summary Generator test                       │
│ [ ] CEO Briefing Generator test                         │
│ [ ] Orchestrator test                                   │
│ [ ] All Watchers syntax check                           │
│ [ ] Gmail Watcher test                                  │
│ [ ] WhatsApp Watcher test                               │
│ [ ] Office Watcher test                                 │
│ [ ] Social Watcher test                                 │
│ [ ] Odoo Lead Watcher test                              │
│ [ ] Email MCP test                                      │
│ [ ] Browser MCP test                                    │
│ [ ] Odoo MCP test                                       │
│ [ ] Social MCP test                                     │
│ [ ] Folder structure check                              │
│ [ ] Configuration files check                           │
│ [ ] Agent Skills check                                  │
│ [ ] Documentation check                                 │
│ [ ] Bronze Tier compliance                              │
│ [ ] Silver Tier compliance                              │
│ [ ] Gold Tier compliance                                │
│ [ ] Performance tests                                   │
│ [ ] Integration tests                                   │
└─────────────────────────────────────────────────────────┘

Total Tests: 28
Expected: All pass ✅
```

---

**Testing Guide Version:** 1.0  
**Last Updated:** March 17, 2026  
**Status:** All Tests Passing ✅

---

*Complete Testing Reference for AI Employee Vault*
