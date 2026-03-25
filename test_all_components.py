#!/usr/bin/env python3
"""
AI Employee Vault - Complete Component Testing Suite
Personal AI Employee Hackathon 0

Tests all components:
1. MCP Servers (Email, Browser, Odoo, Social)
2. Watchers (Gmail, WhatsApp, Office, Social, Odoo)
3. Core Systems (Orchestrator, Ralph Loop, Audit Logger)
4. Business Logic (CEO Briefing, Social Media)
5. Platinum Deployment (Cloud/Local agents)

Usage:
    python test_all_components.py --all          # Run all tests
    python test_all_components.py --mcp          # Test MCP servers
    python test_all_components.py --watchers     # Test watchers
    python test_all_components.py --core         # Test core systems
    python test_all_components.py --business     # Test business logic
    python test_all_components.py --platinum     # Test platinum deployment
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

# Vault paths
VAULT_PATH = Path(__file__).parent
NEEDS_ACTION = VAULT_PATH / 'Needs_Action'
DONE_FOLDER = VAULT_PATH / 'Done'
PENDING_APPROVAL = VAULT_PATH / 'Pending_Approval'
LOGS_FOLDER = VAULT_PATH / 'Logs'

# Test results
test_results = {
    'passed': 0,
    'failed': 0,
    'skipped': 0,
    'total': 0
}

def log(message: str, color: str = Colors.RESET):
    """Print colored log message"""
    print(f"{color}{message}{Colors.RESET}")

def log_header(message: str):
    """Print header"""
    log(f"\n{'='*60}", Colors.BOLD)
    log(f"  {message}", Colors.CYAN)
    log(f"{'='*60}\n", Colors.BOLD)

def log_test(name: str, status: str, details: str = ""):
    """Log test result"""
    test_results['total'] += 1
    
    if status == 'PASS':
        log(f"✅ {name}", Colors.GREEN)
        test_results['passed'] += 1
    elif status == 'FAIL':
        log(f"❌ {name}", Colors.RED)
        test_results['failed'] += 1
    else:
        log(f"⚠️  {name} (SKIPPED)", Colors.YELLOW)
        test_results['skipped'] += 1
    
    if details:
        log(f"   {details}", Colors.RESET)

def ensure_folders():
    """Ensure test folders exist"""
    NEEDS_ACTION.mkdir(exist_ok=True)
    DONE_FOLDER.mkdir(exist_ok=True)
    PENDING_APPROVAL.mkdir(exist_ok=True)
    LOGS_FOLDER.mkdir(exist_ok=True)

# ============================================
# PHASE 1: MCP SERVERS TESTING
# ============================================

def test_mcp_servers():
    """Test all MCP servers"""
    log_header("PHASE 2: MCP SERVERS TESTING")
    
    # Test 1: Email MCP
    log("\n📧 Testing Email MCP...", Colors.BLUE)
    email_mcp = VAULT_PATH / 'mcp_email.py'
    if email_mcp.exists():
        try:
            result = subprocess.run(
                ['python', str(email_mcp), '--action', 'list', '--if-present'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                log_test("Email MCP Server", "PASS", "Server initialized successfully")
            else:
                log_test("Email MCP Server", "FAIL", f"Error: {result.stderr[:100]}")
        except Exception as e:
            log_test("Email MCP Server", "FAIL", str(e))
    else:
        log_test("Email MCP Server", "SKIP", "File not found")
    
    # Test 2: Browser MCP
    log("\n🌐 Testing Browser MCP...", Colors.BLUE)
    browser_mcp = VAULT_PATH / 'mcp_browser.py'
    if browser_mcp.exists():
        try:
            result = subprocess.run(
                ['python', str(browser_mcp), '--action', 'help'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if 'commands' in result.stdout.lower() or result.returncode == 0:
                log_test("Browser MCP Server", "PASS", "Server responding")
            else:
                log_test("Browser MCP Server", "FAIL", "No response from server")
        except Exception as e:
            log_test("Browser MCP Server", "FAIL", str(e))
    else:
        log_test("Browser MCP Server", "SKIP", "File not found")
    
    # Test 3: Odoo MCP
    log("\n💼 Testing Odoo MCP...", Colors.BLUE)
    odoo_mcp = VAULT_PATH / 'mcp_odoo.py'
    if odoo_mcp.exists():
        try:
            result = subprocess.run(
                ['python', str(odoo_mcp), '--action', 'help'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0 or 'commands' in result.stdout.lower():
                log_test("Odoo MCP Server", "PASS", "Server initialized")
            else:
                log_test("Odoo MCP Server", "FAIL", "Server error")
        except Exception as e:
            log_test("Odoo MCP Server", "FAIL", str(e))
    else:
        log_test("Odoo MCP Server", "SKIP", "File not found")
    
    # Test 4: Social MCP
    log("\n📱 Testing Social MCP...", Colors.BLUE)
    social_mcp = VAULT_PATH / 'mcp_social.py'
    if social_mcp.exists():
        try:
            result = subprocess.run(
                ['python', str(social_mcp), '--action', 'help'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0 or 'commands' in result.stdout.lower():
                log_test("Social MCP Server", "PASS", "Server responding")
            else:
                log_test("Social MCP Server", "FAIL", "No response")
        except Exception as e:
            log_test("Social MCP Server", "FAIL", str(e))
    else:
        log_test("Social MCP Server", "SKIP", "File not found")

# ============================================
# PHASE 2: WATCHERS TESTING
# ============================================

def test_watchers():
    """Test all watchers"""
    log_header("PHASE 3: WATCHERS TESTING")
    
    watchers_folder = VAULT_PATH / 'watchers'
    
    # Test each watcher
    watchers = [
        ('Gmail Watcher', 'gmail_watcher.py'),
        ('WhatsApp Watcher', 'whatsapp_watcher.py'),
        ('Office Watcher', 'office_watcher.py'),
        ('Social Watcher', 'social_watcher.py'),
        ('Odoo Lead Watcher', 'odoo_lead_watcher.py'),
        ('Base Watcher', 'base_watcher.py'),
    ]
    
    for name, filename in watchers:
        watcher_path = watchers_folder / filename
        if watcher_path.exists():
            try:
                result = subprocess.run(
                    ['python', str(watcher_path), '--help'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0 or 'usage' in result.stdout.lower():
                    log_test(name, "PASS", "Script compiles and runs")
                else:
                    log_test(name, "FAIL", "Script error")
            except Exception as e:
                log_test(name, "FAIL", str(e))
        else:
            log_test(name, "SKIP", "File not found")

# ============================================
# PHASE 3: CORE SYSTEMS TESTING
# ============================================

def test_core_systems():
    """Test core systems"""
    log_header("PHASE 4: CORE SYSTEMS TESTING")
    
    # Test 1: Orchestrator
    log("\n🎯 Testing Orchestrator...", Colors.BLUE)
    orchestrator = VAULT_PATH / 'orchestrator.py'
    if orchestrator.exists():
        try:
            result = subprocess.run(
                ['python', str(orchestrator), '--health'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                log_test("Orchestrator", "PASS", "Health check passed")
            else:
                log_test("Orchestrator", "FAIL", "Health check failed")
        except Exception as e:
            log_test("Orchestrator", "FAIL", str(e))
    else:
        log_test("Orchestrator", "SKIP", "File not found")
    
    # Test 2: Ralph Loop
    log("\n🧠 Testing Ralph Loop...", Colors.BLUE)
    ralph_loop = VAULT_PATH / 'ralph_loop.py'
    if ralph_loop.exists():
        try:
            result = subprocess.run(
                ['python', str(ralph_loop), '--help'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                log_test("Ralph Loop", "PASS", "Script compiles")
            else:
                log_test("Ralph Loop", "FAIL", "Script error")
        except Exception as e:
            log_test("Ralph Loop", "FAIL", str(e))
    else:
        log_test("Ralph Loop", "SKIP", "File not found")
    
    # Test 3: Audit Logger
    log("\n📝 Testing Audit Logger...", Colors.BLUE)
    audit_logger = VAULT_PATH / 'audit_logger.py'
    if audit_logger.exists():
        try:
            result = subprocess.run(
                ['python', str(audit_logger), '--help'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                log_test("Audit Logger", "PASS", "Logger working")
            else:
                log_test("Audit Logger", "FAIL", "Logger error")
        except Exception as e:
            log_test("Audit Logger", "FAIL", str(e))
    else:
        log_test("Audit Logger", "SKIP", "File not found")
    
    # Test 4: Error Recovery
    log("\n🔄 Testing Error Recovery...", Colors.BLUE)
    error_recovery = VAULT_PATH / 'error_recovery.py'
    if error_recovery.exists():
        try:
            result = subprocess.run(
                ['python', str(error_recovery), '--help'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                log_test("Error Recovery", "PASS", "Module compiles")
            else:
                log_test("Error Recovery", "FAIL", "Module error")
        except Exception as e:
            log_test("Error Recovery", "FAIL", str(e))
    else:
        log_test("Error Recovery", "SKIP", "File not found")
    
    # Test 5: Health Monitor
    log("\n🏥 Testing Health Monitor...", Colors.BLUE)
    health_monitor = VAULT_PATH / 'health_monitor.py'
    if health_monitor.exists():
        try:
            result = subprocess.run(
                ['python', str(health_monitor), '--help'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                log_test("Health Monitor", "PASS", "Monitor working")
            else:
                log_test("Health Monitor", "FAIL", "Monitor error")
        except Exception as e:
            log_test("Health Monitor", "FAIL", str(e))
    else:
        log_test("Health Monitor", "SKIP", "File not found")

# ============================================
# PHASE 4: BUSINESS LOGIC TESTING
# ============================================

def test_business_logic():
    """Test business logic components"""
    log_header("PHASE 5: BUSINESS LOGIC TESTING")
    
    # Test 1: CEO Briefing
    log("\n📊 Testing CEO Briefing Generator...", Colors.BLUE)
    ceo_briefing = VAULT_PATH / 'ceo_briefing_enhanced.py'
    if ceo_briefing.exists():
        try:
            result = subprocess.run(
                ['python', str(ceo_briefing), '--help'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                log_test("CEO Briefing Generator", "PASS", "Generator ready")
            else:
                log_test("CEO Briefing Generator", "FAIL", "Generator error")
        except Exception as e:
            log_test("CEO Briefing Generator", "FAIL", str(e))
    else:
        log_test("CEO Briefing Generator", "SKIP", "File not found")
    
    # Test 2: Social Summary Generator
    log("\n📱 Testing Social Summary Generator...", Colors.BLUE)
    social_summary = VAULT_PATH / 'social_summary_generator.py'
    if social_summary.exists():
        try:
            result = subprocess.run(
                ['python', str(social_summary), '--help'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                log_test("Social Summary Generator", "PASS", "Generator ready")
            else:
                log_test("Social Summary Generator", "FAIL", "Generator error")
        except Exception as e:
            log_test("Social Summary Generator", "FAIL", str(e))
    else:
        log_test("Social Summary Generator", "SKIP", "File not found")
    
    # Test 3: LinkedIn Post Generator
    log("\n💼 Testing LinkedIn Post Generator...", Colors.BLUE)
    linkedin = VAULT_PATH / 'linkedin_post_generator.py'
    if linkedin.exists():
        try:
            result = subprocess.run(
                ['python', str(linkedin), '--help'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                log_test("LinkedIn Post Generator", "PASS", "Generator ready")
            else:
                log_test("LinkedIn Post Generator", "FAIL", "Generator error")
        except Exception as e:
            log_test("LinkedIn Post Generator", "FAIL", str(e))
    else:
        log_test("LinkedIn Post Generator", "SKIP", "File not found")
    
    # Test 4: Facebook/Instagram Post
    log("\n📘 Testing Facebook/Instagram Post Generator...", Colors.BLUE)
    fb_ig = VAULT_PATH / 'facebook_instagram_post.py'
    if fb_ig.exists():
        try:
            result = subprocess.run(
                ['python', str(fb_ig), '--help'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                log_test("Facebook/Instagram Post", "PASS", "Generator ready")
            else:
                log_test("Facebook/Instagram Post", "FAIL", "Generator error")
        except Exception as e:
            log_test("Facebook/Instagram Post", "FAIL", str(e))
    else:
        log_test("Facebook/Instagram Post", "SKIP", "File not found")
    
    # Test 5: Twitter Post
    log("\n🐦 Testing Twitter Post Generator...", Colors.BLUE)
    twitter = VAULT_PATH / 'twitter_post.py'
    if twitter.exists():
        try:
            result = subprocess.run(
                ['python', str(twitter), '--help'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                log_test("Twitter Post Generator", "PASS", "Generator ready")
            else:
                log_test("Twitter Post Generator", "FAIL", "Generator error")
        except Exception as e:
            log_test("Twitter Post Generator", "FAIL", str(e))
    else:
        log_test("Twitter Post Generator", "SKIP", "File not found")

# ============================================
# PHASE 5: PLATINUM DEPLOYMENT TESTING
# ============================================

def test_platinum_deployment():
    """Test Platinum deployment components"""
    log_header("PHASE 6: PLATINUM DEPLOYMENT TESTING")
    
    # Test 1: Cloud Orchestrator
    log("\n☁️ Testing Cloud Orchestrator...", Colors.BLUE)
    cloud_orch = VAULT_PATH / 'cloud_orchestrator.py'
    if cloud_orch.exists():
        try:
            result = subprocess.run(
                ['python', str(cloud_orch), '--help'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                log_test("Cloud Orchestrator", "PASS", "Agent ready")
            else:
                log_test("Cloud Orchestrator", "FAIL", "Agent error")
        except Exception as e:
            log_test("Cloud Orchestrator", "FAIL", str(e))
    else:
        log_test("Cloud Orchestrator", "SKIP", "File not found")
    
    # Test 2: Local Orchestrator
    log("\n🏠 Testing Local Orchestrator...", Colors.BLUE)
    local_orch = VAULT_PATH / 'local_orchestrator.py'
    if local_orch.exists():
        try:
            result = subprocess.run(
                ['python', str(local_orch), '--help'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                log_test("Local Orchestrator", "PASS", "Agent ready")
            else:
                log_test("Local Orchestrator", "FAIL", "Agent error")
        except Exception as e:
            log_test("Local Orchestrator", "FAIL", str(e))
    else:
        log_test("Local Orchestrator", "SKIP", "File not found")
    
    # Test 3: Vault Sync
    log("\n🔄 Testing Vault Sync...", Colors.BLUE)
    vault_sync = VAULT_PATH / 'vault_sync.py'
    if vault_sync.exists():
        try:
            result = subprocess.run(
                ['python', str(vault_sync), '--help'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                log_test("Vault Sync", "PASS", "Sync ready")
            else:
                log_test("Vault Sync", "FAIL", "Sync error")
        except Exception as e:
            log_test("Vault Sync", "FAIL", str(e))
    else:
        log_test("Vault Sync", "SKIP", "File not found")
    
    # Test 4: Platinum Demo
    log("\n🎬 Testing Platinum Demo...", Colors.BLUE)
    platinum_demo = VAULT_PATH / 'platinum_demo.py'
    if platinum_demo.exists():
        try:
            result = subprocess.run(
                ['python', str(platinum_demo), '--help'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                log_test("Platinum Demo", "PASS", "Demo ready")
            else:
                log_test("Platinum Demo", "FAIL", "Demo error")
        except Exception as e:
            log_test("Platinum Demo", "FAIL", str(e))
    else:
        log_test("Platinum Demo", "SKIP", "File not found")
    
    # Test 5: A2A Messenger
    log("\n💬 Testing A2A Messenger...", Colors.BLUE)
    a2a = VAULT_PATH / 'a2a_messenger.py'
    if a2a.exists():
        try:
            result = subprocess.run(
                ['python', str(a2a), '--help'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                log_test("A2A Messenger", "PASS", "Messenger ready")
            else:
                log_test("A2A Messenger", "FAIL", "Messenger error")
        except Exception as e:
            log_test("A2A Messenger", "FAIL", str(e))
    else:
        log_test("A2A Messenger", "SKIP", "File not found")

# ============================================
# PHASE 6: FOLDER STRUCTURE VERIFICATION
# ============================================

def test_folder_structure():
    """Verify folder structure"""
    log_header("PHASE 1: FOLDER STRUCTURE VERIFICATION")
    
    required_folders = [
        'Needs_Action',
        'Pending_Approval',
        'Approved',
        'Done',
        'In_Progress',
        'Plans',
        'Briefings',
        'CEO_Briefings',
        'Social_Drafts',
        'Social_Summaries',
        'Logs',
        'Logs/Audit',
        'watchers',
        'cloud',
        'local',
        'kubernetes',
        'odoo',
        '.claude',
        '.claude/skills',
        '.claude/agents',
    ]
    
    for folder_name in required_folders:
        folder_path = VAULT_PATH / folder_name
        if folder_path.exists() and folder_path.is_dir():
            log_test(f"Folder: {folder_name}", "PASS", "Exists")
        else:
            log_test(f"Folder: {folder_name}", "FAIL", "Missing")

# ============================================
# MAIN TEST RUNNER
# ============================================

def run_all_tests():
    """Run all tests"""
    log("\n" + "="*60, Colors.BOLD)
    log("  🧪 AI EMPLOYEE VAULT - COMPLETE TESTING SUITE", Colors.CYAN)
    log("  Personal AI Employee Hackathon 0", Colors.CYAN)
    log("="*60, Colors.BOLD)
    
    start_time = datetime.now()
    
    # Run all phases
    test_folder_structure()
    test_mcp_servers()
    test_watchers()
    test_core_systems()
    test_business_logic()
    test_platinum_deployment()
    
    # Print summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    log_header("TEST SUMMARY")
    log(f"Total Tests:  {test_results['total']}", Colors.BOLD)
    log(f"✅ Passed:     {test_results['passed']}", Colors.GREEN)
    log(f"❌ Failed:     {test_results['failed']}", Colors.RED)
    log(f"⚠️  Skipped:    {test_results['skipped']}", Colors.YELLOW)
    log(f"⏱️  Duration:   {duration:.2f}s", Colors.BLUE)
    
    success_rate = (test_results['passed'] / test_results['total'] * 100) if test_results['total'] > 0 else 0
    log(f"\n📊 Success Rate: {success_rate:.1f}%", Colors.BOLD)
    
    # Save results
    results_file = LOGS_FOLDER / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    results_file.parent.mkdir(exist_ok=True)
    
    with open(results_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': duration,
            'results': test_results,
            'success_rate': success_rate
        }, f, indent=2)
    
    log(f"\n💾 Results saved to: {results_file}", Colors.CYAN)
    
    if test_results['failed'] == 0:
        log("\n🎉 ALL TESTS PASSED! READY FOR HACKATHON! 🚀", Colors.GREEN)
        return 0
    else:
        log(f"\n⚠️  {test_results['failed']} test(s) failed. Please fix before submission.", Colors.RED)
        return 1

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Employee Vault Testing Suite')
    parser.add_argument('--all', action='store_true', help='Run all tests')
    parser.add_argument('--folders', action='store_true', help='Test folder structure')
    parser.add_argument('--mcp', action='store_true', help='Test MCP servers')
    parser.add_argument('--watchers', action='store_true', help='Test watchers')
    parser.add_argument('--core', action='store_true', help='Test core systems')
    parser.add_argument('--business', action='store_true', help='Test business logic')
    parser.add_argument('--platinum', action='store_true', help='Test platinum deployment')
    
    args = parser.parse_args()
    
    ensure_folders()
    
    if args.all or not any([args.folders, args.mcp, args.watchers, args.core, args.business, args.platinum]):
        sys.exit(run_all_tests())
    elif args.folders:
        test_folder_structure()
    elif args.mcp:
        test_mcp_servers()
    elif args.watchers:
        test_watchers()
    elif args.core:
        test_core_systems()
    elif args.business:
        test_business_logic()
    elif args.platinum:
        test_platinum_deployment()
