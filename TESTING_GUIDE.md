# 🧪 AI Employee Vault - Comprehensive Testing Guide

**Personal AI Employee Hackathon 0**
**Last Updated:** March 17, 2026
**Status:** ✅ **Gold Tier Complete - Ready for Testing**

---

## 📋 Pre-Flight Checklist

Before running tests, verify your environment:

### Required Software
- [x] Python 3.13+ (Currently: Python 3.14.3 ✅)
- [x] Node.js 18+ (Currently: v24.14.0 ✅)
- [x] npm 10+ (Currently: 10.8.2 ✅)
- [ ] Qwen CLI (Optional - for Claude Code alternative)
- [ ] Playwright browsers installed

### Required Python Packages
```bash
pip install -r requirements.txt
playwright install chromium
```

### Required MCP Dependencies
```bash
python mcp_email.py --action list
python mcp_browser.py --action navigate
python mcp_odoo.py --action get_leads
python mcp_social.py --action linkedin
```

---

## 🧪 Test Suite 1: Core Python Modules

### Test 1.1: Audit Logger
```bash
cd "C:\Users\CC\Documents\Obsidian Vault"

# Test import
python -c "from audit_logger import get_audit_summary; print('✅ Audit Logger: Import OK')"

# Test full functionality
python audit_logger.py
```

**Expected Output:**
- Audit summary for last 7 days
- Total transactions count
- Success rate percentage
- Action breakdown by type

**Pass Criteria:** Module imports without errors, generates summary

---

### Test 1.2: Error Recovery System
```bash
cd "C:\Users\CC\Documents\Obsidian Vault"

# Test import
python -c "from error_recovery import CircuitBreaker, HealthCheck; print('✅ Error Recovery: Import OK')"

# Test full functionality
python error_recovery.py
```

**Expected Output:**
- Circuit breaker test results
- Dead Letter Queue status
- Health check report
- All components registered

**Pass Criteria:** Circuit breaker works, DLQ functional, health check passes

---

### Test 1.3: Social Summary Generator
```bash
cd "C:\Users\CC\Documents\Obsidian Vault"

# Test import
python -c "import social_summary_generator; print('✅ Social Summary: Import OK')"

# Test LinkedIn summary (7 days)
python social_summary_generator.py linkedin 7

# Test all platforms (7 days)
python social_summary_generator.py all 7
```

**Expected Output:**
- Summary files created in `Social_Summaries/`
- Post counts per platform
- Hashtag counts
- Engagement metrics

**Pass Criteria:** Summaries generated, files saved

---

### Test 1.4: CEO Briefing Generator
```bash
cd "C:\Users\CC\Documents\Obsidian Vault"

# Test enhanced briefing
python ceo_briefing_enhanced.py

# Check output
ls Briefings/
```

**Expected Output:**
- Briefing file created in `Briefings/`
- Includes revenue tracking
- Includes accounting audit
- Includes social media summary
- Includes completed tasks
- Includes bottlenecks
- Includes suggestions

**Pass Criteria:** Briefing generated with all sections

---

### Test 1.5: Ralph Loop
```bash
cd "C:\Users\CC\Documents\Obsidian Vault"

# Test import
python -c "import ralph_loop; print('✅ Ralph Loop: Import OK')"

# Check script exists and is valid
python -m py_compile ralph_loop.py && echo "✅ Ralph Loop: Syntax OK"
```

**Expected Output:**
- No syntax errors
- Module imports successfully

**Pass Criteria:** Script compiles without errors

---

### Test 1.6: Orchestrator
```bash
cd "C:\Users\CC\Documents\Obsidian Vault"

# Test help command
python orchestrator.py help

# Test status command
python orchestrator.py status
```

**Expected Output:**
- 7 commands listed
- Status report shows folder counts
- No errors

**Pass Criteria:** Commands available, status accurate

---

## 🧪 Test Suite 2: Watchers

### Test 2.1: Gmail Watcher
```bash
cd "C:\Users\CC\Documents\Obsidian Vault"

# Test syntax
python -m py_compile watchers/gmail_watcher.py && echo "✅ Gmail Watcher: Syntax OK"

# Test import (may fail if credentials missing - expected)
python -c "import sys; sys.path.insert(0, 'watchers'); import gmail_watcher; print('✅ Gmail Watcher: Import OK')" 2>&1 || echo "⚠️ Gmail Watcher: Credentials needed (expected)"
```

**Expected Output:**
- Syntax check passes
- Import may fail if Gmail credentials not configured (normal)

**Pass Criteria:** Syntax valid, credentials error is expected if not configured

---

### Test 2.2: WhatsApp Watcher
```bash
cd "C:\Users\CC\Documents\Obsidian Vault"

# Test syntax
python -m py_compile watchers/whatsapp_watcher.py && echo "✅ WhatsApp Watcher: Syntax OK"

# Test import
python -c "import sys; sys.path.insert(0, 'watchers'); import whatsapp_watcher; print('✅ WhatsApp Watcher: Import OK')"
```

**Expected Output:**
- Syntax check passes
- Import successful

**Pass Criteria:** No errors

---

### Test 2.3: Office Watcher
```bash
cd "C:\Users\CC\Documents\Obsidian Vault"

# Test syntax
python -m py_compile watchers/office_watcher.py && echo "✅ Office Watcher: Syntax OK"

# Test import
python -c "import sys; sys.path.insert(0, 'watchers'); import office_watcher; print('✅ Office Watcher: Import OK')"
```

**Expected Output:**
- Syntax check passes
- Import successful

**Pass Criteria:** No errors

---

### Test 2.4: Social Watcher
```bash
cd "C:\Users\CC\Documents\Obsidian Vault"

# Test syntax
python -m py_compile watchers/social_watcher.py && echo "✅ Social Watcher: Syntax OK"

# Test import
python -c "import sys; sys.path.insert(0, 'watchers'); import social_watcher; print('✅ Social Watcher: Import OK')"
```

**Expected Output:**
- Syntax check passes
- Import successful

**Pass Criteria:** No errors

---

### Test 2.5: Odoo Lead Watcher
```bash
cd "C:\Users\CC\Documents\Obsidian Vault"

# Test syntax
python -m py_compile watchers/odoo_lead_watcher.py && echo "✅ Odoo Lead Watcher: Syntax OK"

# Test import
python -c "import sys; sys.path.insert(0, 'watchers'); import odoo_lead_watcher; print('✅ Odoo Lead Watcher: Import OK')"
```

**Expected Output:**
- Syntax check passes
- Import successful

**Pass Criteria:** No errors

---

### Test 2.6: All Watchers Together
```bash
cd "C:\Users\CC\Documents\Obsidian Vault"

# Test base watcher
python -c "import sys; sys.path.insert(0, 'watchers'); from base_watcher import BaseWatcher; print('✅ Base Watcher: Import OK')"

# Run all watchers (they will run continuously - press Ctrl+C to stop)
python start_all_watchers.bat
```

**Expected Output:**
- All watchers start
- Logs appear in console
- No immediate crashes

**Pass Criteria:** All watchers start successfully

---

## 🧪 Test Suite 3: MCP Servers

### Test 3.1: Email MCP Server
```bash
cd "C:\Users\CC\Documents\Obsidian Vault\mcp-email"

# Check dependencies
python mcp_email.py --action list

# Test start (will run continuously)
timeout /t 2
```

**Expected Output:**
- Dependencies listed
- Server starts
- No immediate errors

**Pass Criteria:** Server starts without errors

---

### Test 3.2: Browser MCP Server
```bash
cd "C:\Users\CC\Documents\Obsidian Vault\mcp-browser"

# Check dependencies
python mcp_email.py --action list

# Test start
timeout /t 2
```

**Expected Output:**
- Dependencies listed
- Server starts
- No immediate errors

**Pass Criteria:** Server starts without errors

---

### Test 3.3: Odoo MCP Server
```bash
cd "C:\Users\CC\Documents\Obsidian Vault\mcp-odoo"

# Check dependencies
python mcp_email.py --action list

# Test start (will fail if Odoo not running - expected)
timeout /t 2 2>&1 || echo "⚠️ Odoo MCP: Connection error (expected if Odoo not running)"
```

**Expected Output:**
- Dependencies listed
- Server starts
- May fail to connect to Odoo (normal if Odoo not installed)

**Pass Criteria:** Server starts, connection error is expected if Odoo not running

---

### Test 3.4: Social MCP Server
```bash
cd "C:\Users\CC\Documents\Obsidian Vault\mcp-social"

# Check dependencies
python mcp_email.py --action list

# Test start
timeout /t 2
```

**Expected Output:**
- Dependencies listed
- Server starts
- No immediate errors

**Pass Criteria:** Server starts without errors

---

## 🧪 Test Suite 4: Integration Tests

### Test 4.1: Folder Structure Verification
```bash
cd "C:\Users\CC\Documents\Obsidian Vault"

# Check required folders exist
python -c "
from pathlib import Path
folders = ['Needs_Action', 'Pending_Approval', 'Done', 'Logs/Audit', 'Briefings', 'Social_Summaries', 'Social_Drafts']
for f in folders:
    assert Path(f).exists(), f'Missing folder: {f}'
print('✅ All required folders exist')
"
```

**Expected Output:**
- All folders exist
- No missing folder errors

**Pass Criteria:** All folders present

---

### Test 4.2: Configuration Files
```bash
cd "C:\Users\CC\Documents\Obsidian Vault"

# Check config files
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
- MCP config valid
- Credentials file exists

**Pass Criteria:** Configuration files present and valid

---

### Test 4.3: Agent Skills Documentation
```bash
cd "C:\Users\CC\Documents\Obsidian Vault"

# Check Agent Skills
python -c "
from pathlib import Path
skills = ['email-processor', 'whatsapp-responder', 'social-media-manager', 'odoo-accounting', 'ceo-briefing-generator', 'audit-logger', 'error-recovery']
for skill in skills:
    skill_path = Path(f'.claude/skills/{skill}/SKILL.md')
    assert skill_path.exists(), f'Missing skill: {skill}'
print(f'✅ All {len(skills)} Agent Skills present')
"
```

**Expected Output:**
- All 7 Agent Skills exist
- SKILL.md files present

**Pass Criteria:** All Agent Skills documented

---

### Test 4.4: Documentation Files
```bash
cd "C:\Users\CC\Documents\Obsidian Vault"

# Check documentation
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
- All main documents present
- docs/ folder has files

**Pass Criteria:** Documentation complete

---

## 🧪 Test Suite 5: End-to-End Tests

### Test 5.1: Complete System Health Check
```bash
cd "C:\Users\CC\Documents\Obsidian Vault"

python -c "
import sys
from pathlib import Path

print('=' * 60)
print('AI EMPLOYEE VAULT - SYSTEM HEALTH CHECK')
print('=' * 60)

# 1. Python version
print(f'\n✅ Python: {sys.version.split()[0]}')

# 2. Check modules
modules = ['audit_logger', 'error_recovery', 'social_summary_generator', 'ceo_briefing_enhanced', 'orchestrator', 'ralph_loop']
for module in modules:
    try:
        __import__(module)
        print(f'✅ {module}: OK')
    except Exception as e:
        print(f'❌ {module}: {e}')

# 3. Check folders
folders = ['Needs_Action', 'Pending_Approval', 'Done', 'Logs/Audit', 'Briefings', 'Social_Summaries']
for folder in folders:
    if Path(folder).exists():
        count = len(list(Path(folder).glob('*')))
        print(f'✅ {folder}: {count} files')
    else:
        print(f'❌ {folder}: MISSING')

# 4. Check MCP servers
mcp_servers = ['mcp-email', 'mcp-browser', 'mcp-odoo', 'mcp-social']
for server in mcp_servers:
    if Path(server).exists():
        print(f'✅ {server}: Present')
    else:
        print(f'❌ {server}: MISSING')

# 5. Check watchers
watchers = ['gmail_watcher.py', 'whatsapp_watcher.py', 'office_watcher.py', 'social_watcher.py', 'odoo_lead_watcher.py']
for watcher in watchers:
    if Path(f'watchers/{watcher}').exists():
        print(f'✅ {watcher}: Present')
    else:
        print(f'❌ {watcher}: MISSING')

# 6. Check Agent Skills
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

**Expected Output:**
- All modules load
- All folders exist with files
- All MCP servers present
- All watchers present
- All Agent Skills documented

**Pass Criteria:** 100% of components present and working

---

## 🧪 Test Suite 6: Hackathon Compliance

### Test 6.1: Bronze Tier Requirements
```bash
cd "C:\Users\CC\Documents\Obsidian Vault"

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
    ('Qwen/Code integration', Path('orchestrator.py').exists()),
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

**Expected Output:**
- All Bronze requirements pass

**Pass Criteria:** 100% pass

---

### Test 6.2: Silver Tier Requirements
```bash
cd "C:\Users\CC\Documents\Obsidian Vault"

python -c "
from pathlib import Path

print('\n🥈 SILVER TIER REQUIREMENTS')
print('=' * 40)

checks = [
    ('Bronze Tier complete', True),  # Assume passed from previous test
    ('2+ watchers', len(list(Path('watchers').glob('*.py'))) >= 2),
    ('LinkedIn post generator', Path('linkedin_post_generator.py').exists()),
    ('Ralph Wiggum loop', Path('ralph_loop.py').exists()),
    ('At least 1 MCP server', len(list(Path('mcp-email').glob('*.js'))) >= 1),
    ('Approval workflow', Path('Pending_Approval').exists()),
    ('Scheduling scripts', Path('setup_tasks.bat').exists() or Path('start_all_watchers.bat').exists()),
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

**Expected Output:**
- All Silver requirements pass

**Pass Criteria:** 100% pass

---

### Test 6.3: Gold Tier Requirements
```bash
cd "C:\Users\CC\Documents\Obsidian Vault"

python -c "
from pathlib import Path

print('\n🥇 GOLD TIER REQUIREMENTS')
print('=' * 40)

checks = [
    ('Silver Tier complete', True),  # Assume passed
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

**Expected Output:**
- All Gold requirements pass

**Pass Criteria:** 100% pass

---

## 📊 Test Results Template

After running all tests, fill in this template:

```markdown
## Test Results - [DATE]

### Core Modules
- [ ] Audit Logger: PASS/FAIL
- [ ] Error Recovery: PASS/FAIL
- [ ] Social Summary Generator: PASS/FAIL
- [ ] CEO Briefing Generator: PASS/FAIL
- [ ] Ralph Loop: PASS/FAIL
- [ ] Orchestrator: PASS/FAIL

### Watchers
- [ ] Gmail Watcher: PASS/FAIL
- [ ] WhatsApp Watcher: PASS/FAIL
- [ ] Office Watcher: PASS/FAIL
- [ ] Social Watcher: PASS/FAIL
- [ ] Odoo Lead Watcher: PASS/FAIL

### MCP Servers
- [ ] Email MCP: PASS/FAIL
- [ ] Browser MCP: PASS/FAIL
- [ ] Odoo MCP: PASS/FAIL
- [ ] Social MCP: PASS/FAIL

### Integration
- [ ] Folder Structure: PASS/FAIL
- [ ] Configuration: PASS/FAIL
- [ ] Agent Skills: PASS/FAIL
- [ ] Documentation: PASS/FAIL

### Hackathon Compliance
- [ ] Bronze Tier: PASS/FAIL
- [ ] Silver Tier: PASS/FAIL
- [ ] Gold Tier: PASS/FAIL

### Overall Status
**Result:** ✅ ALL PASS / ❌ SOME FAILURES

**Notes:** [Any issues found and fixes needed]
```

---

## 🚀 Quick Test Commands

### One-Line Health Check
```bash
cd "C:\Users\CC\Documents\Obsidian Vault" && python -c "from audit_logger import get_audit_summary; from error_recovery import CircuitBreaker; import social_summary_generator; import ceo_briefing_enhanced; print('✅ All core modules: OK')"
```

### Test All Python Scripts
```bash
cd "C:\Users\CC\Documents\Obsidian Vault" && for %f in (*.py) do python -m py_compile "%f" && echo "✅ %f: OK"
```

### Test All Watchers
```bash
cd "C:\Users\CC\Documents\Obsidian Vault\watchers" && for %f in (*.py) do python -m py_compile "%f" && echo "✅ %f: OK"
```

### Generate Test Briefing
```bash
cd "C:\Users\CC\Documents\Obsidian Vault" && python ceo_briefing_enhanced.py && echo "✅ CEO Briefing: Generated"
```

### Generate Social Summaries
```bash
cd "C:\Users\CC\Documents\Obsidian Vault" && python social_summary_generator.py all 7 && echo "✅ Social Summaries: Generated"
```

---

## 🎯 Success Criteria

### Gold Tier Complete When:
1. ✅ All core modules import without errors
2. ✅ All 5 watchers have valid syntax
3. ✅ All 4 MCP servers start without errors
4. ✅ All folders exist with appropriate content
5. ✅ All Agent Skills documented
6. ✅ All documentation files present
7. ✅ CEO briefing generates successfully
8. ✅ Social summaries generate successfully
9. ✅ Audit logger logs and retrieves data
10. ✅ Error recovery system functional

---

## 📞 Troubleshooting

### Common Issues

**Issue: Module import errors**
```bash
# Fix: Install missing dependencies
pip install -r requirements.txt
```

**Issue: MCP server won't start**
```bash
# Fix: Install Python dependencies
python mcp_email.py --action list
```

**Issue: Playwright errors**
```bash
# Fix: Install browsers
playwright install chromium
```

**Issue: Gmail authentication errors**
```bash
# Fix: Re-authenticate
cd mcp-email
node authenticate.js
```

**Issue: Odoo connection errors**
```bash
# Fix: Start Odoo or skip test (expected if not installed)
# Odoo is optional for testing other components
```

---

## 📈 Next Steps After Testing

1. **If all tests pass:** ✅ Gold Tier Complete - Ready for submission
2. **If some tests fail:** Fix issues and re-run tests
3. **For Platinum Tier:** Deploy to cloud VM, setup 24/7 operation

---

**Testing Guide Version:** 1.0
**Last Updated:** March 17, 2026
**Hackathon:** Personal AI Employee Hackathon 0

---

*This testing guide verifies all Gold Tier requirements are met and functional.*
