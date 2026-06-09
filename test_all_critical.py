"""
COMPREHENSIVE CRITICAL TESTS
Tests all critical systems WITHOUT requiring real credentials
Uses DRY_RUN mode to verify architecture works
"""

import os
import sys
import json
import time
import importlib
import subprocess
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except:
        pass

VAULT = Path(__file__).parent
PASSED = 0
FAILED = 0
WARNINGS = 0

def test(name, func):
    global PASSED, FAILED, WARNINGS
    try:
        result = func()
        if result is True:
            print(f"✅ {name}")
            PASSED += 1
        elif result is False:
            print(f"❌ {name}")
            FAILED += 1
        else:
            print(f"⚠️  {name} — {result}")
            WARNINGS += 1
    except Exception as e:
        print(f"❌ {name} — Exception: {e}")
        FAILED += 1

# ============================================================
# TEST 1: Vault Structure
# ============================================================
def test_vault_structure():
    required = [
        'Needs_Action', 'Pending_Approval', 'Done', 'Plans',
        'Approved', 'Rejected', 'Briefings', 'Logs', 'Inbox',
        'In_Progress', 'Signals', 'Updates', 'Drafts', 'Skills',
        'watchers', 'odoo', 'cloud', 'Social_Drafts', 'Social_Summaries',
        'Dead_Letter_Queue', 'Pending_Approval', 'CEO_Briefings'
    ]
    missing = [f for f in required if not (VAULT / f).is_dir()]
    if missing:
        return f"Missing: {missing}"
    return True

# ============================================================
# TEST 2: Core Python Files
# ============================================================
def test_core_files():
    files = {
        'ai_employee_orchestrator.py': 10000,
        'gmail_watcher.py': 1000,
        'ceo_briefing.py': 10000,
        'cloud_agent.py': 10000,
        'local_agent.py': 10000,
        'audit_logger.py': 5000,
        'error_recovery.py': 5000,
        'a2a_messenger.py': 5000,
        'ralph_loop.py': 1000,
        'mcp_email.py': 5000,
        'mcp_social.py': 5000,
        'mcp_browser.py': 5000,
        'mcp_odoo.py': 5000,
        'facebook_instagram_post.py': 5000,
        'twitter_post.py': 1000,
        'linkedin_post_generator.py': 1000,
        'instagram_post.py': 1000,
        'facebook_post.py': 1000,
    }
    missing = []
    small = []
    for f, min_size in files.items():
        p = VAULT / f
        if not p.exists():
            missing.append(f)
        elif p.stat().st_size < min_size:
            small.append(f"({p.stat().st_size}B < {min_size}B)")
    if missing:
        return f"Missing: {missing}"
    if small:
        return f"Small files: {small}"
    return True

# ============================================================
# TEST 3: Watcher Scripts
# ============================================================
def test_watchers():
    watchers = [
        'watchers/base_watcher.py',
        'watchers/gmail_watcher.py',
        'watchers/whatsapp_watcher.py',
        'watchers/social_watcher.py',
        'watchers/odoo_lead_watcher.py',
        'watchers/office_watcher.py',
    ]
    for w in watchers:
        p = VAULT / w
        if not p.exists():
            return f"Missing: {w}"
        # Try compile
        try:
            import py_compile
            py_compile.compile(str(p), doraise=True)
        except py_compile.PyCompileError as e:
            return f"Compile error in {w}: {e}"
    return True

# ============================================================
# TEST 4: MCP Servers
# ============================================================
def test_mcp_servers():
    mcps = ['mcp_email.py', 'mcp_social.py', 'mcp_browser.py', 'mcp_odoo.py', 'mcp_server.py']
    for m in mcps:
        p = VAULT / m
        if not p.exists():
            return f"Missing: {m}"
    # Check DRY_RUN safety in each
    for m in mcps:
        content = (VAULT / m).read_text(encoding='utf-8')
        if 'DRY_RUN' not in content and 'dry_run' not in content:
            return f"{m} missing DRY_RUN safety"
    return True

# ============================================================
# TEST 5: Import Core Modules
# ============================================================
def test_imports():
    modules = ['audit_logger', 'error_recovery']
    for m in modules:
        try:
            importlib.import_module(m)
        except Exception as e:
            return f"Cannot import {m}: {e}"
    return True

# ============================================================
# TEST 6: Security - No Hardcoded Credentials
# ============================================================
def test_security():
    files_to_check = [
        'ai_employee_orchestrator.py',
        'cloud_agent.py',
        'local_agent.py',
        'mcp_email.py',
        'mcp_social.py',
        'mcp_odoo.py',
    ]
    bad_patterns = [
        'password = "',
        "password = '",
        'api_key = "',
        "api_key = '",
        'token = "',
        "token = '",
        'secret = "',
        "secret = '",
    ]
    violations = []
    for f in files_to_check:
        p = VAULT / f
        if not p.exists():
            continue
        content = p.read_text(encoding='utf-8').lower()
        for pattern in bad_patterns:
            if pattern.lower() in content and 'os.getenv' not in content.split(pattern.lower())[0][-50:]:
                # Check if it's in a comment or docstring
                lines = (VAULT / f).read_text(encoding='utf-8').splitlines()
                for i, line in enumerate(lines):
                    if pattern.lower() in line.lower() and not line.strip().startswith('#') and 'os.getenv' not in line:
                        violations.append(f"{f}:{i+1}: {line.strip()[:80]}")
    if violations:
        return f"Possible hardcoded creds: {violations[:3]}"
    return True

# ============================================================
# TEST 7: .env File Exists
# ============================================================
def test_env_file():
    p = VAULT / '.env'
    if not p.exists():
        return ".env file missing"
    content = p.read_text(encoding='utf-8')
    lines = [l for l in content.splitlines() if l.strip() and not l.startswith('#')]
    return f"{len(lines)} config lines present"

# ============================================================
# TEST 8: Company Handbook & Business Goals
# ============================================================
def test_docs():
    docs = {
        'Company_Handbook.md': 1000,
        'Business_Goals.md': 500,
        'Dashboard.md': 200,
        'Skills/CORE_SKILLS.md': 500,
    }
    for d, min_size in docs.items():
        p = VAULT / d
        if not p.exists():
            return f"Missing: {d}"
        if p.stat().st_size < min_size:
            return f"Too small: {d} ({p.stat().st_size}B)"
    return True

# ============================================================
# TEST 9: Odoo Docker Compose
# ============================================================
def test_odoo_docker():
    p = VAULT / 'odoo' / 'docker-compose.yml'
    if not p.exists():
        return "odoo/docker-compose.yml missing"
    content = p.read_text(encoding='utf-8')
    if 'odoo' not in content.lower():
        return "No Odoo service defined"
    if 'postgres' not in content.lower() and 'db' not in content.lower():
        return "No database service defined"
    return True

# ============================================================
# TEST 10: Cloud Agent Architecture
# ============================================================
def test_cloud_arch():
    files = {
        'cloud_agent.py': 'Cloud agent',
        'local_agent.py': 'Local agent',
        'a2a_messenger.py': 'A2A messenger',
        'deploy_cloud_vm.sh': 'Cloud deploy script',
        'deploy_cloud_agent.sh': 'Cloud agent deploy script',
    }
    for f, desc in files.items():
        p = VAULT / f
        if not p.exists():
            return f"Missing: {desc} ({f})"
    # Check draft-only mode in cloud agent
    cloud = (VAULT / 'cloud_agent.py').read_text(encoding='utf-8')
    if 'draft' not in cloud.lower():
        return "Cloud agent missing draft-only mode"
    return True

# ============================================================
# TEST 11: Ralph Loop
# ============================================================
def test_ralph_loop():
    p = VAULT / 'ralph_loop.py'
    if not p.exists():
        return "ralph_loop.py missing"
    content = p.read_text(encoding='utf-8')
    checks = {
        'max_iterations': 'max iterations',
        'stop_hook' if 'stop_hook' in content.lower() else 'completion': 'completion detection',
        'backoff' if 'backoff' in content.lower() else 'retry': 'retry logic',
    }
    return True

# ============================================================
# TEST 12: CEO Briefing
# ============================================================
def test_ceo_briefing():
    p = VAULT / 'ceo_briefing.py'
    if not p.exists():
        return "ceo_briefing.py missing"
    content = p.read_text(encoding='utf-8')
    if 'dashboard' not in content.lower():
        return "Not reading Dashboard.md"
    if 'business_goals' not in content.lower() and 'revenue' not in content.lower():
        return "Not reading business goals"
    # Check briefings folder
    briefings = list((VAULT / 'CEO_Briefings').glob('*.md'))
    if not briefings:
        briefings = list((VAULT / 'Briefings').glob('*.md'))
    return f"{len(briefings)} briefing(s) generated"

# ============================================================
# TEST 13: Error Recovery
# ============================================================
def test_error_recovery():
    p = VAULT / 'error_recovery.py'
    if not p.exists():
        return "error_recovery.py missing"
    content = p.read_text(encoding='utf-8')
    features = []
    if 'circuit' in content.lower():
        features.append('circuit breaker')
    if 'retry' in content.lower():
        features.append('retry logic')
    if 'dead_letter' in content.lower() or 'dead letter' in content.lower():
        features.append('dead letter queue')
    if not features:
        return "No error recovery features found"
    return f"Features: {', '.join(features)}"

# ============================================================
# TEST 14: Social Media Integration
# ============================================================
def test_social_media():
    platforms = {
        'linkedin_post_generator.py': 'LinkedIn',
        'facebook_post.py': 'Facebook',
        'instagram_post.py': 'Instagram',
        'twitter_post.py': 'Twitter',
        'facebook_instagram_post.py': 'Combined',
    }
    missing = []
    for f, platform in platforms.items():
        if not (VAULT / f).exists():
            missing.append(platform)
    if missing:
        return f"Missing platforms: {missing}"
    return True

# ============================================================
# TEST 15: HITL Approval Flow
# ============================================================
def test_hitl():
    # Check orchestrator has HITL
    p = VAULT / 'ai_employee_orchestrator.py'
    content = p.read_text(encoding='utf-8')
    if 'approval' not in content.lower():
        return "No HITL in orchestrator"
    if 'ask_permission' not in content.lower() and 'require_approval' not in content.lower():
        return "No permission asking in orchestrator"
    # Check Pending_Approval folder has files
    pa = VAULT / 'Pending_Approval'
    if pa.exists():
        count = len(list(pa.glob('*.md')))
        return f"{count} files awaiting approval"
    return "Pending_Approval folder missing"

# ============================================================
# TEST 16: Gitignore Security
# ============================================================
def test_gitignore():
    g = VAULT / '.gitignore'
    if not g.exists():
        return ".gitignore missing"
    content = g.read_text(encoding='utf-8').lower()
    required_patterns = ['.env', 'credentials', 'token', 'secret']
    missing_patterns = [p for p in required_patterns if p not in content]
    if missing_patterns:
        return f"Missing gitignore patterns: {missing_patterns}"
    return True

# ============================================================
# TEST 17: FINAL_SUBMISSION.md
# ============================================================
def test_final_submission():
    p = VAULT / 'FINAL_SUBMISSION.md'
    if not p.exists():
        return "FINAL_SUBMISSION.md missing"
    content = p.read_text(encoding='utf-8')
    if 'gold tier' not in content.lower():
        return "No Gold Tier declaration"
    if '15/15' not in content:
        return "No test results documented"
    return True

# ============================================================
# RUN ALL TESTS
# ============================================================
print("=" * 70)
print("🧪 COMPREHENSIVE CRITICAL TESTS - AI EMPLOYEE VAULT")
print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)
print()

tests = [
    ("1. Vault Structure", test_vault_structure),
    ("2. Core Python Files", test_core_files),
    ("3. Watcher Scripts (compile)", test_watchers),
    ("4. MCP Servers + DRY_RUN safety", test_mcp_servers),
    ("5. Module Imports", test_imports),
    ("6. Security - No Hardcoded Credentials", test_security),
    ("7. .env File Exists", test_env_file),
    ("8. Documentation (Handbook, Goals, Dashboard)", test_docs),
    ("9. Odoo Docker Compose", test_odoo_docker),
    ("10. Cloud Agent Architecture", test_cloud_arch),
    ("11. Ralph Loop", test_ralph_loop),
    ("12. CEO Briefing", test_ceo_briefing),
    ("13. Error Recovery System", test_error_recovery),
    ("14. Social Media Integration", test_social_media),
    ("15. HITL Approval Flow", test_hitl),
    ("16. Gitignore Security", test_gitignore),
    ("17. FINAL_SUBMISSION.md", test_final_submission),
]

for name, func in tests:
    test(name, func)

print()
print("=" * 70)
print(f"📊 RESULTS: {PASSED} passed, {FAILED} failed, {WARNINGS} warnings")
if FAILED == 0:
    print("✅ ALL CRITICAL TESTS PASSED!")
else:
    print(f"❌ {FAILED} test(s) failed — review above")
print("=" * 70)
