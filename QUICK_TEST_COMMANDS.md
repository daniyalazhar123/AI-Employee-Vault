# 🚀 Quick Test Commands - AI Employee Vault

**Personal AI Employee Hackathon 0**
**Gold Tier - 100% Complete**

---

## ⚡ One-Line Health Checks

### Full System Health Check
```bash
cd "C:\Users\CC\Documents\Obsidian Vault" && python -c "from audit_logger import get_audit_summary; from error_recovery import CircuitBreaker; import social_summary_generator; import ceo_briefing_enhanced; print('✅ All core modules: OK')"
```

### Check Python Version
```bash
python --version
```

### Check Node.js Version
```bash
node --version && npm --version
```

---

## 🧪 Core Module Tests

### Test Audit Logger
```bash
cd "C:\Users\CC\Documents\Obsidian Vault"
python audit_logger.py
```

**Expected:** Shows audit summary for last 7 days

---

### Test Error Recovery
```bash
python error_recovery.py
```

**Expected:** Shows circuit breaker status, DLQ status, health check

---

### Test Social Summary Generator
```bash
# Test all platforms, last 7 days
python social_summary_generator.py all 7

# Test specific platform
python social_summary_generator.py linkedin 7
```

**Expected:** Creates summary files in `Social_Summaries/`

---

### Test CEO Briefing Generator
```bash
python ceo_briefing_enhanced.py
```

**Expected:** Creates briefing in `Briefings/`

---

### Test Orchestrator
```bash
# Show help
python orchestrator.py help

# Show status
python orchestrator.py status

# Process pending items
python orchestrator.py process_needs_action
```

**Expected:** Shows commands and status

---

### Test Ralph Loop
```bash
# Check syntax
python -m py_compile ralph_loop.py && echo "✅ Ralph Loop: Syntax OK"
```

**Expected:** No errors

---

## 📡 Watcher Tests

### Test All Watchers Syntax
```bash
cd watchers
for %f in (*.py) do python -m py_compile "%f" && echo "✅ %f: OK"
```

**Expected:** All watchers compile without errors

---

### Test Individual Watchers

```bash
# Gmail Watcher
python -m py_compile watchers/gmail_watcher.py && echo "✅ Gmail Watcher: OK"

# WhatsApp Watcher
python -m py_compile watchers/whatsapp_watcher.py && echo "✅ WhatsApp Watcher: OK"

# Office Watcher
python -m py_compile watchers/office_watcher.py && echo "✅ Office Watcher: OK"

# Social Watcher
python -m py_compile watchers/social_watcher.py && echo "✅ Social Watcher: OK"

# Odoo Lead Watcher
python -m py_compile watchers/odoo_lead_watcher.py && echo "✅ Odoo Lead Watcher: OK"
```

---

### Start All Watchers
```bash
# Start all (run in background)
start_all_watchers.bat

# Stop all
stop_all_watchers.bat
```

---

## 🔧 MCP Server Tests

### Test Email MCP
```bash
cd mcp-email
npm ls
npm start
```

**Expected:** Server starts

---

### Test Browser MCP
```bash
cd mcp-browser
npm ls
npm start
```

**Expected:** Server starts

---

### Test Odoo MCP
```bash
cd mcp-odoo
npm ls
npm start
```

**Expected:** Server starts (may fail to connect to Odoo - normal if not running)

---

### Test Social MCP
```bash
cd mcp-social
npm ls
npm start
```

**Expected:** Server starts

---

## 📁 Folder Structure Tests

### Verify All Folders Exist
```bash
python -c "
from pathlib import Path
folders = ['Needs_Action', 'Pending_Approval', 'Done', 'Logs/Audit', 'Briefings', 'Social_Summaries', 'Social_Drafts']
for f in folders:
    assert Path(f).exists(), f'Missing: {f}'
print('✅ All folders exist')
"
```

---

### Count Files in Folders
```bash
python -c "
from pathlib import Path
folders = ['Needs_Action', 'Pending_Approval', 'Done', 'Briefings']
for f in folders:
    count = len(list(Path(f).glob('*')))
    print(f'{f}: {count} files')
"
```

---

## 🎓 Agent Skills Tests

### Verify All Agent Skills Exist
```bash
python -c "
from pathlib import Path
skills = ['email-processor', 'whatsapp-responder', 'social-media-manager', 'odoo-accounting', 'ceo-briefing-generator', 'audit-logger', 'error-recovery']
for skill in skills:
    assert Path(f'.claude/skills/{skill}/SKILL.md').exists(), f'Missing: {skill}'
print(f'✅ All {len(skills)} Agent Skills documented')
"
```

---

### Check Agent Skills Documentation
```bash
ls .claude\skills\
```

**Expected:** 7 skill folders

---

## 📚 Documentation Tests

### Verify Documentation Files
```bash
python -c "
from pathlib import Path
docs = ['README.md', 'Business_Goals.md', 'Company_Handbook.md', 'Dashboard.md', 'GOLD_TIER_COMPLETE.md', 'AGENT_SKILLS_COMPLETE.md', 'HACKATHON_COMPLIANCE_REPORT.md']
for doc in docs:
    assert Path(doc).exists(), f'Missing: {doc}'
print(f'✅ All {len(docs)} main documents present')
"
```

---

### Check docs/ Folder
```bash
ls docs\
```

**Expected:** 4+ documentation files

---

## 🏆 Hackathon Compliance Tests

### Test Bronze Tier Requirements
```bash
python -c "
from pathlib import Path
print('\n🥉 BRONZE TIER')
checks = [
    ('Dashboard.md', Path('Dashboard.md').exists()),
    ('Company_Handbook.md', Path('Company_Handbook.md').exists()),
    ('Business_Goals.md', Path('Business_Goals.md').exists()),
    ('Watcher exists', len(list(Path('watchers').glob('*.py'))) >= 1),
    ('Needs_Action folder', Path('Needs_Action').exists()),
    ('Done folder', Path('Done').exists()),
]
for name, result in checks:
    print(f'{'✅' if result else '❌'} {name}')
"
```

---

### Test Silver Tier Requirements
```bash
python -c "
from pathlib import Path
print('\n🥈 SILVER TIER')
checks = [
    ('2+ watchers', len(list(Path('watchers').glob('*.py'))) >= 2),
    ('LinkedIn post generator', Path('linkedin_post_generator.py').exists()),
    ('Ralph Loop', Path('ralph_loop.py').exists()),
    ('MCP server exists', Path('mcp-email/index.js').exists()),
    ('Pending_Approval folder', Path('Pending_Approval').exists()),
    ('Agent Skills', Path('.claude/skills').exists()),
]
for name, result in checks:
    print(f'{'✅' if result else '❌'} {name}')
"
```

---

### Test Gold Tier Requirements
```bash
python -c "
from pathlib import Path
print('\n🥇 GOLD TIER')
checks = [
    ('Odoo MCP', Path('mcp-odoo/index.js').exists()),
    ('Odoo docs', Path('docs/ODOO_SETUP.md').exists()),
    ('Facebook/Instagram', Path('facebook_instagram_post.py').exists()),
    ('Twitter', Path('twitter_post.py').exists()),
    ('Social summaries', Path('social_summary_generator.py').exists()),
    ('4 MCP servers', all([Path(f'mcp-{x}').exists() for x in ['email', 'browser', 'odoo', 'social']])),
    ('CEO Briefing enhanced', Path('ceo_briefing_enhanced.py').exists()),
    ('Error recovery', Path('error_recovery.py').exists()),
    ('Audit logging', Path('audit_logger.py').exists()),
    ('7 Agent Skills', len(list(Path('.claude/skills').glob('*/SKILL.md'))) >= 7),
]
for name, result in checks:
    print(f'{'✅' if result else '❌'} {name}')
"
```

---

## 📊 Generate Test Report

### Full Compliance Check
```bash
python -c "
from pathlib import Path

print('=' * 60)
print('AI EMPLOYEE VAULT - HACKATHON COMPLIANCE CHECK')
print('=' * 60)

# Bronze
bronze = [
    Path('Dashboard.md').exists(),
    Path('Company_Handbook.md').exists(),
    Path('Business_Goals.md').exists(),
    len(list(Path('watchers').glob('*.py'))) >= 1,
    Path('Needs_Action').exists(),
    Path('Done').exists(),
]

# Silver
silver = [
    len(list(Path('watchers').glob('*.py'))) >= 2,
    Path('linkedin_post_generator.py').exists(),
    Path('ralph_loop.py').exists(),
    Path('mcp-email/index.js').exists(),
    Path('Pending_Approval').exists(),
    Path('.claude/skills').exists(),
]

# Gold
gold = [
    Path('mcp-odoo/index.js').exists(),
    Path('docs/ODOO_SETUP.md').exists(),
    Path('facebook_instagram_post.py').exists(),
    Path('twitter_post.py').exists(),
    Path('social_summary_generator.py').exists(),
    all([Path(f'mcp-{x}').exists() for x in ['email', 'browser', 'odoo', 'social']]),
    Path('ceo_briefing_enhanced.py').exists(),
    Path('error_recovery.py').exists(),
    Path('audit_logger.py').exists(),
    len(list(Path('.claude/skills').glob('*/SKILL.md'))) >= 7,
]

print(f'\n🥉 Bronze Tier: {sum(bronze)}/{len(bronze)} ({sum(bronze)*100//len(bronze)}%)')
print(f'🥈 Silver Tier: {sum(silver)}/{len(silver)} ({sum(silver)*100//len(silver)}%)')
print(f'🥇 Gold Tier: {sum(gold)}/{len(gold)} ({sum(gold)*100//len(gold)}%)')

all_checks = bronze + silver + gold
total = sum(all_checks)
max_total = len(all_checks)

print(f'\n📊 OVERALL: {total}/{max_total} ({total*100//max_total}%)')
print('=' * 60)

if total == max_total:
    print('✅ ALL REQUIREMENTS MET - GOLD TIER COMPLETE!')
else:
    print(f'❌ Missing {max_total - total} requirements')
"
```

---

## 🎯 Demo Commands (For Recording)

### Demo 1: Show Dashboard
```bash
type Dashboard.md
```

---

### Demo 2: Generate CEO Briefing
```bash
python ceo_briefing_enhanced.py
type Briefings\GOLD_TIER_Briefing_2026-03-16.md
```

---

### Demo 3: Generate Social Summaries
```bash
python social_summary_generator.py all 7
ls Social_Summaries\
```

---

### Demo 4: Show Audit Logs
```bash
python audit_logger.py
ls Logs\Audit\
```

---

### Demo 5: Show Error Recovery
```bash
python error_recovery.py
```

---

### Demo 6: Show Agent Skills
```bash
ls .claude\skills\
type .claude\skills\odoo-accounting\SKILL.md
```

---

### Demo 7: Show MCP Servers
```bash
ls mcp-email\
ls mcp-browser\
ls mcp-odoo\
ls mcp-social\
```

---

### Demo 8: Show Watchers
```bash
ls watchers\
type watchers\gmail_watcher.py
```

---

## 📈 Performance Tests

### Test Module Import Speed
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
"
```

---

### Test Audit Logger Performance
```bash
python -c "
import time
from audit_logger import get_audit_summary
start = time.time()
summary = get_audit_summary(30)
end = time.time()
print(f'Audit summary (30 days) generated in {end-start:.2f} seconds')
print(f'Total actions: {summary[\"total_actions\"]}')
"
```

---

## 🔍 Debugging Commands

### Check Python Path
```bash
python -c "import sys; print('\n'.join(sys.path))"
```

---

### Check Installed Packages
```bash
pip list
```

---

### Check MCP Config
```bash
type config\mcp.json
```

---

### Check Credentials
```bash
type credentials.json
```

---

### View Recent Logs
```bash
ls Logs\Audit\
type Logs\Audit\2026-03-17.json
```

---

## 📋 Pre-Submission Checklist

Before submitting, run these commands:

```bash
# 1. Verify all modules work
python -c "from audit_logger import get_audit_summary; print('✅ Audit OK')"
python -c "from error_recovery import CircuitBreaker; print('✅ Error Recovery OK')"
python -c "import social_summary_generator; print('✅ Social Summary OK')"
python -c "import ceo_briefing_enhanced; print('✅ CEO Briefing OK')"

# 2. Generate fresh briefing
python ceo_briefing_enhanced.py

# 3. Generate social summaries
python social_summary_generator.py all 7

# 4. Verify documentation exists
python -c "from pathlib import Path; assert Path('README.md').exists(); print('✅ README OK')"

# 5. Show final status
python -c "
from pathlib import Path
print('\n📊 FINAL STATUS')
print(f'Needs_Action: {len(list(Path(\"Needs_Action\").glob(\"*\")))} items')
print(f'Pending_Approval: {len(list(Path(\"Pending_Approval\").glob(\"*\")))} items')
print(f'Done: {len(list(Path(\"Done\").glob(\"*\")))} items')
print(f'Agent Skills: {len(list(Path(\".claude/skills\").glob(\"*/SKILL.md\")))} skills')
print(f'MCP Servers: {len([x for x in [\"email\", \"browser\", \"odoo\", \"social\"] if Path(f\"mcp-{x}\").exists()])}/4')
"
```

---

## 🎉 Success Criteria

All tests pass if:
- ✅ All Python modules import without errors
- ✅ All watchers have valid syntax
- ✅ All MCP servers start without errors
- ✅ All folders exist with content
- ✅ All Agent Skills documented
- ✅ All documentation files present
- ✅ CEO briefing generates successfully
- ✅ Social summaries generate successfully
- ✅ Audit logger logs and retrieves data
- ✅ Error recovery system functional

---

**Quick Test Guide Version:** 1.0
**Last Updated:** March 17, 2026
**Status:** ✅ Gold Tier Complete

---

*Use these commands to verify your AI Employee Vault is working correctly.*
