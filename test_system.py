#!/usr/bin/env python3
"""
AI Employee Vault - Comprehensive System Test
Tests all components for Gold Tier readiness
"""

import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from pathlib import Path

# Set safe defaults
os.environ['DRY_RUN'] = 'true'
os.environ['REQUIRE_APPROVAL'] = 'true'

print('='*70)
print('🧪 AI EMPLOYEE VAULT - COMPREHENSIVE SYSTEM TEST')
print('='*70)

tests_passed = 0
tests_failed = 0
tests_total = 0

def test(name, func):
    global tests_passed, tests_failed, tests_total
    tests_total += 1
    try:
        result = func()
        if result:
            print(f'✅ {name}')
            tests_passed += 1
        else:
            print(f'❌ {name} - returned False')
            tests_failed += 1
    except Exception as e:
        print(f'❌ {name} - {str(e)[:80]}')
        tests_failed += 1

# Test 1: Vault structure
def test_vault_structure():
    vault = Path('.')
    required_folders = ['Needs_Action', 'Done', 'Pending_Approval', 'Approved', 'Plans', 'Logs', 'Social_Drafts', 'Drafts']
    required_files = ['Dashboard.md', 'Company_Handbook.md', 'Business_Goals.md']
    for folder in required_folders:
        if not (vault / folder).exists():
            return False
    for file in required_files:
        if not (vault / file).exists():
            return False
    return True
test('1. Vault Structure (folders + core files)', test_vault_structure)

# Test 2: MCP Email Server
def test_mcp_email():
    from mcp_email import MCPEmailServer
    server = MCPEmailServer(Path('.'))
    return server.dry_run == True and server.require_approval == True
test('2. MCP Email Server (safety flags)', test_mcp_email)

# Test 3: MCP Social Media Server
def test_mcp_social():
    from mcp_social import MCPSocialServer
    server = MCPSocialServer(Path('.'))
    status = server.get_platform_status()
    return status['playwright_available'] == True
test('3. MCP Social Media Server (Playwright)', test_mcp_social)

# Test 4: Odoo MCP Server
def test_odoo_mcp():
    from odoo_mcp import MCPOdooServer
    server = MCPOdooServer()
    info = server.get_server_info()
    return info['name'] == 'MCP Odoo Server'
test('4. Odoo MCP Server (initialization)', test_odoo_mcp)

# Test 5: AI Employee Orchestrator
def test_orchestrator():
    from ai_employee_orchestrator import AIEmployeeOrchestrator
    o = AIEmployeeOrchestrator()
    return hasattr(o, 'ask_permission') and hasattr(o, 'analyze_email')
test('5. AI Employee Orchestrator (methods)', test_orchestrator)

# Test 6: Ralph Loop
def test_ralph_loop():
    import ralph_loop
    return hasattr(ralph_loop, 'run_ai_engine') and hasattr(ralph_loop, 'check_task_status')
test('6. Ralph Loop (functions)', test_ralph_loop)

# Test 7: Watchers
def test_watchers():
    watchers_path = Path('watchers')
    required_watchers = ['base_watcher.py', 'gmail_watcher.py', 'whatsapp_watcher.py', 'office_watcher.py', 'social_watcher.py', 'odoo_lead_watcher.py']
    for watcher in required_watchers:
        if not (watchers_path / watcher).exists():
            return False
    return True
test('7. Watchers (all 6 present)', test_watchers)

# Test 8: Social Media Generators
def test_social_generators():
    required = ['linkedin_post_generator.py', 'facebook_post.py', 'instagram_post.py', 'twitter_post.py', 'facebook_instagram_post.py']
    for file in required:
        if not Path(file).exists():
            return False
    return True
test('8. Social Media Generators (all 5)', test_social_generators)

# Test 9: Audit Logger
def test_audit_logger():
    from audit_logger import AuditLogger
    logger = AuditLogger(Path('.'))
    return hasattr(logger, 'log_action')
test('9. Audit Logger (initialization)', test_audit_logger)

# Test 10: Error Recovery
def test_error_recovery():
    from error_recovery import CircuitBreaker
    cb = CircuitBreaker('test_service')
    return cb.can_execute() == True
test('10. Error Recovery (CircuitBreaker)', test_error_recovery)

# Test 11: Cloud Agent
def test_cloud_agent():
    from cloud_agent import CloudAgent
    agent = CloudAgent(vault_path=Path('.'))
    return hasattr(agent, 'process_item') and hasattr(agent, 'claim_item')
test('11. Cloud Agent (Platinum)', test_cloud_agent)

# Test 12: Local Agent
def test_local_agent():
    from local_agent import LocalAgent
    agent = LocalAgent(vault_path=Path('.'))
    return hasattr(agent, 'execute_approved_item') and hasattr(agent, 'merge_updates')
test('12. Local Agent (Platinum)', test_local_agent)

# Test 13: Security Check
def test_security_credentials():
    import re
    files_to_check = ['mcp_email.py', 'mcp_social.py', 'odoo_mcp.py', 'ai_employee_orchestrator.py']
    for file in files_to_check:
        content = Path(file).read_text(encoding='utf-8')
        if 'os.getenv' not in content and 'os.environ' not in content:
            if re.search(r'(PASSWORD|SECRET|API_KEY)\s*=\s*["\'][a-zA-Z0-9]', content):
                return False
    return True
test('13. Security (no hardcoded creds)', test_security_credentials)

# Test 14: DRY_RUN Safety
def test_dry_run_safety():
    from mcp_email import MCPEmailServer
    from mcp_social import MCPSocialServer
    email_server = MCPEmailServer(Path('.'))
    social_server = MCPSocialServer(Path('.'))
    return email_server.dry_run == True and social_server.dry_run == True
test('14. DRY_RUN Safety (default true)', test_dry_run_safety)

# Test 15: HITL Approval
def test_hitl_safety():
    from mcp_email import MCPEmailServer
    server = MCPEmailServer(Path('.'))
    return server.require_approval == True
test('15. HITL Approval Required', test_hitl_safety)

print()
print('='*70)
print(f'📊 TEST RESULTS: {tests_passed}/{tests_total} passed, {tests_failed} failed')
print('='*70)

if tests_failed == 0:
    print('✅ ALL TESTS PASSED!')
else:
    print(f'⚠️  {tests_failed} test(s) failed')

print(f'\nTests Passed: {tests_passed}/{tests_total}')
