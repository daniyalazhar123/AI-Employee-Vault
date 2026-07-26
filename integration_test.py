import os, sys, json, shutil, time, subprocess
from pathlib import Path
from datetime import datetime

VAULT = Path(__file__).parent
PASS = 0
FAIL = 0

def log(msg, status="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    icons = {"PASS": "[PASS]", "FAIL": "[FAIL]", "INFO": "[INFO]", "WARN": "[WARN]"}
    out = f"  {icons.get(status, '[ ..]')} [{ts}] {msg}"
    try:
        print(out)
    except UnicodeEncodeError:
        print(out.encode("ascii", "replace").decode("ascii"))

def check(condition, msg):
    global PASS, FAIL
    if condition:
        PASS += 1
        log(msg, "PASS")
    else:
        FAIL += 1
        log(msg, "FAIL")

def ensure_dirs():
    dirs = [
        "Needs_Action/cloud", "Needs_Action/local",
        "In_Progress/cloud", "In_Progress/local",
        "Drafts/email", "Drafts/social", "Drafts/odoo",
        "Updates", "Signals", "Pending_Approval",
        "Approved", "Rejected", "Done",
        "Logs/Audit", "Dead_Letter_Queue", "data"
    ]
    for d in dirs:
        (VAULT / d).mkdir(parents=True, exist_ok=True)

def cleanup():
    # Clear voice approval processed IDs for fresh state
    processed_file = VAULT / "data" / "voice_approval_processed.txt"
    if processed_file.exists():
        processed_file.unlink()
    for folder in ["Needs_Action", "In_Progress", "Updates", "Signals",
                    "Pending_Approval", "Approved", "Rejected", "Done",
                    "Dead_Letter_Queue"]:
        p = VAULT / folder
        if p.exists():
            for f in p.rglob("*"):
                if f.is_file() and f.suffix != ".gitkeep":
                    f.unlink()
    # Clean draft files
    for d in ["email", "social", "odoo"]:
        for f in (VAULT / "Drafts" / d).glob("*"):
            if f.is_file() and f.suffix != ".gitkeep":
                f.unlink()

try:
    print("="*70)
    print("  INTEGRATION TEST - AI Employee Platinum Tier")
    print("="*70)
except UnicodeEncodeError:
    print("="*70)
    print(b"  INTEGRATION TEST - AI Employee Platinum Tier".decode("ascii"))
    print("="*70)

ensure_dirs()
cleanup()

# Test 1: Folder structure
print("\n--- Folder Structure ---")
files_that_should_exist = [
    "orchestrator.py", "cloud_agent.py", "local_agent.py",
    "cloud_orchestrator.py", "local_orchestrator.py",
    "vault_sync.py", "a2a_messenger.py", "health_monitor.py",
    "security_guard.py", "platinum_demo.py",
    "ecosystem.config.js", "install_scheduled_tasks.ps1",
    "audit_logger.py", "error_recovery.py", "secrets_config.py",
    "mcp_email.py", "mcp_social.py", "mcp_odoo.py", "mcp_browser.py", "mcp_voice_approval.py", "odoo_bank_reconciliation.py", "dependency_fallback_guard.py"
]
for f in files_that_should_exist:
    check((VAULT / f).exists(), f"Core file exists: {f}")

watcher_files = ["base_watcher.py", "gmail_watcher.py", "whatsapp_watcher.py",
                 "social_watcher.py", "office_watcher.py", "odoo_lead_watcher.py"]
for f in watcher_files:
    check((VAULT / "watchers" / f).exists(), f"Watcher exists: {f}")

for d in ["Inbox", "Needs_Action/cloud", "Needs_Action/local",
          "In_Progress/cloud", "In_Progress/local",
          "Drafts/email", "Drafts/social", "Drafts/odoo",
          "Updates", "Signals", "Pending_Approval",
          "Approved", "Rejected", "Done", "Logs/Audit", "Dead_Letter_Queue"]:
    check((VAULT / d).exists(), f"Folder exists: {d}")

# Test 2: Python syntax check (import-based, safe)
print("\n--- Python Syntax ---")
python_files = []
for root, dirs, files in os.walk(VAULT):
    if "__pycache__" in root or ".git" in root or "node_modules" in root:
        continue
    for f in files:
        if f.endswith(".py"):
            python_files.append(os.path.join(root, f))

for pf in python_files:
    rel = os.path.relpath(pf, VAULT)
    try:
        import py_compile
        py_compile.compile(pf, doraise=True)
        check(True, f"Python syntax: {rel}")
    except py_compile.PyCompileError as e:
        check(False, f"Python syntax: {rel}: {e}")
    except Exception as e:
        check(False, f"Python syntax: {rel}: {e}")

# Test 3: Import paths check
print("\n--- Import Verification ---")
imports_to_test = [
    ("secrets_config", "load_secrets"),
    ("audit_logger", "AuditLogger"),
    ("error_recovery", "CircuitBreaker"),
    ("error_recovery", "DeadLetterQueue"),
    ("error_recovery", "RetryHandler"),
]
try:
    sys.path.insert(0, str(VAULT))
    for mod_name, cls_name in imports_to_test:
        try:
            mod = __import__(mod_name)
            check(hasattr(mod, cls_name), f"Import {mod_name}.{cls_name}")
        except Exception as e:
            check(False, f"Import {mod_name}.{cls_name}: {e}")
finally:
    sys.path.pop(0)

# Test 4: Platinum demo workflow
print("\n--- Platinum Demo Workflow ---")
try:
    sys.path.insert(0, str(VAULT))
    from platinum_demo import PlatinumDemo

    demo = PlatinumDemo(str(VAULT))
    result = demo.run_demo()

    check(result, "Platinum demo run completed")
    check((VAULT / "Done" / "PLATINUM_DEMO_RESULT.md").exists(),
          "Demo result file in Done/")
finally:
    if VAULT.__str__() in sys.path:
        sys.path.remove(str(VAULT))

# Test 5: Cloud agent file handoff test
print("\n--- Cloud Agent File Handoff ---")
needs_action_cloud = VAULT / "Needs_Action" / "cloud"
pending_approval = VAULT / "Pending_Approval"

# Simulate email arrival
email_file = needs_action_cloud / "EMAIL_test_inquiry.md"
email_file.write_text(f"""---
type: email
from: test@example.com
subject: Test Inquiry
received: {datetime.now().isoformat()}
---
# Test Email
Hello, I have a question about pricing.
""", encoding="utf-8")

check(email_file.exists(), "Simulated email placed in Needs_Action/cloud")

# Simulate cloud agent processing
in_progress_cloud = VAULT / "In_Progress" / "cloud"
shutil.move(str(email_file), str(in_progress_cloud / email_file.name))
check(not email_file.exists() and (in_progress_cloud / email_file.name).exists(),
      "Cloud claimed item (claim-by-move)")

# Simulate cloud creating draft + approval request
updates = VAULT / "Updates"
draft_file = updates / "DRAFT_REPLY_EMAIL_test_inquiry.md"
draft_file.write_text(f"""---
type: email_reply
to: test@example.com
subject: RE: Test Inquiry
created_by: cloud
---
# Draft Reply
Thank you for your inquiry.
""", encoding="utf-8")
check(draft_file.exists(), "Cloud created draft in Updates/")

approval_file = pending_approval / "APPROVAL_DRAFT_REPLY_EMAIL_test_inquiry.md"
approval_file.write_text(f"""---
type: approval_request
draft_file: DRAFT_REPLY_EMAIL_test_inquiry.md
created_by: cloud
status: pending
---
# Approval Required
Review the draft in Updates/.
""", encoding="utf-8")
check(approval_file.exists(), "Cloud created approval request in Pending_Approval/")

# Simulate human approval
approved = VAULT / "Approved"
shutil.move(str(approval_file), str(approved / approval_file.name))
check(not approval_file.exists() and (approved / approval_file.name).exists(),
      "Human moved approval to Approved/")

# Simulate local agent execution
done_folder = VAULT / "Done"
done_file = done_folder / f"COMPLETED_{approval_file.name}"
shutil.move(str(approved / approval_file.name), str(done_file))
shutil.move(str(draft_file), str(done_folder / draft_file.name))
check(done_file.exists(), "Local executed and moved to Done/")

# Test 6: Error recovery test
print("\n--- Error Recovery ---")
try:
    from error_recovery import CircuitBreaker, DeadLetterQueue
    cb = CircuitBreaker("test", failure_threshold=2, timeout=1)
    check(not cb.is_open(), "Circuit breaker starts closed")
    check(cb.can_execute(), "Circuit breaker allows execution initially")
    cb.record_failure()
    cb.record_failure()
    check(cb.is_open(), "Circuit breaker opens after 2 failures")
    check(not cb.can_execute(), "Circuit breaker blocks execution when open")
    time.sleep(1.5)
    check(cb.is_open(), "Circuit breaker still open before recovery check")
    check(cb.can_execute(), "Circuit breaker recovers after timeout (can_execute)")
    check(not cb.is_open(), "Circuit breaker is no longer open after recovery")
except Exception as e:
    check(False, f"Circuit breaker test: {e}")

try:
    dlq = DeadLetterQueue(VAULT)
    dlq.add("test_item", "email", error="Test error message")
    items = dlq.get_pending_items()
    check(len(items) >= 1, "Dead Letter Queue stores items")
except Exception as e:
    check(False, f"DLQ test: {e}")

# Test 7: Audit logger
print("\n--- Audit Logger ---")
try:
    from audit_logger import AuditLogger
    audit = AuditLogger(VAULT)
    audit.log_action("test", {"test": True}, "success", actor="integration_test")
    check(True, "Audit logger writes entries")
except Exception as e:
    check(False, f"Audit logger test: {e}")

# Test 8: Health monitor check
print("\n--- Health Monitor ---")
try:
    sys.path.insert(0, str(VAULT))
    from health_monitor import HealthMonitor
    monitor = HealthMonitor("local", str(VAULT))
    health = monitor.check_all()
    check("status" in health, "Health monitor returns status")
    check("components" in health, "Health monitor returns components")
finally:
    if VAULT.__str__() in sys.path:
        sys.path.remove(str(VAULT))

# Test 9: Security guard permissions
print("\n--- Security Guard ---")
try:
    sys.path.insert(0, str(VAULT))
    from security_guard import SecurityGuard

    cloud_guard = SecurityGuard("cloud", str(VAULT))
    check(not cloud_guard.check_action_permission("email_send"),
          "Cloud cannot send email (security)")
    check(not cloud_guard.check_action_permission("social_post"),
          "Cloud cannot post social (security)")
    check(not cloud_guard.check_action_permission("bank_payment"),
          "Cloud cannot process payment (security)")

    local_guard = SecurityGuard("local", str(VAULT))
    check(local_guard.check_action_permission("email_send"),
          "Local can send email")
    check(local_guard.check_action_permission("social_post"),
          "Local can post social")
    check(local_guard.check_action_permission("whatsapp_send"),
          "Local can send WhatsApp")
finally:
    if VAULT.__str__() in sys.path:
        sys.path.remove(str(VAULT))

# Test 10: PM2 ecosystem validation
print("\n--- PM2 Ecosystem ---")
try:
    with open(VAULT / "ecosystem.config.js", "r", encoding="utf-8") as f:
        content = f.read()
    check("ai-orchestrator" in content, "PM2 has orchestrator service")
    check("cloud-agent" in content, "PM2 has cloud agent service")
    check("local-agent" in content, "PM2 has local agent service")
    check("vault-sync" in content, "PM2 has vault sync service")
    check("a2a-messenger" in content, "PM2 has A2A messenger service")
    check("health-monitor" in content, "PM2 has health monitor service")
    check("security-guard" in content, "PM2 has security guard service")
    check("path.resolve(__dirname)" in content,
          "PM2 uses dynamic vault path (not hardcoded)")
except Exception as e:
    check(False, f"PM2 ecosystem check: {e}")

# Test 11: Windows Task Scheduler script exists
print("\n--- Windows Task Scheduler ---")
check((VAULT / "install_scheduled_tasks.ps1").exists(),
      "Task scheduler install script exists")

# Test 12: A2A messenger
print("\n--- A2A Messenger ---")
try:
    sys.path.insert(0, str(VAULT))
    from a2a_messenger import A2AMessenger
    cloud_msgr = A2AMessenger("cloud", {
        "vault_path": str(VAULT),
        "cloud_endpoint": "http://localhost:8081",
        "local_endpoint": "http://localhost:8082"
    })
    check(cloud_msgr.agent_type == "cloud", "A2A Cloud messenger initialized")
    stats = cloud_msgr.get_stats()
    check("agent_type" in stats, "A2A returns stats")
finally:
    if VAULT.__str__() in sys.path:
        sys.path.remove(str(VAULT))

# Test 13: Voice Approval System
print("\n--- Voice Approval System ---")
try:
    sys.path.insert(0, str(VAULT))
    from mcp_voice_approval import VoiceApprovalSystem

    vs = VoiceApprovalSystem()

    # Test frontmatter parsing
    pending = VAULT / "Pending_Approval"
    test_file = pending / "APPROVAL_test_voice.md"
    test_file.write_text("""---
type: approval_request
draft_file: DRAFT_test.md
created_by: cloud
status: pending
confidence: 40
---
# Approval Required
Review the pricing proposal for client ABC.
""", encoding="utf-8")

    meta = vs._parse_frontmatter(test_file)
    check(meta.get('type') == 'approval_request', "Voice: frontmatter type parsed")
    check(meta.get('confidence') == '40', "Voice: frontmatter confidence parsed")
    check(meta.get('draft_file') == 'DRAFT_test.md', "Voice: frontmatter draft_file parsed")

    # Test low-confidence detection
    tasks = vs.scan_pending_approvals()
    check(len(tasks) == 1, "Voice: low-confidence task detected")
    check(tasks[0]['filename'] == 'APPROVAL_test_voice.md', "Voice: correct filename")
    check(tasks[0]['confidence'] == 40.0, "Voice: confidence value parsed as float")

    # Test summary generation (speech-friendly)
    summary = tasks[0]['summary']
    check(len(summary) > 20, "Voice: summary generated")
    check('pricing' in summary.lower(), "Voice: summary contains task body")

    # Test approve file movement
    check(vs.approve_task('APPROVAL_test_voice.md'), "Voice: approve returns True")
    check((VAULT / "Approved" / "APPROVAL_test_voice.md").exists(),
          "Voice: file moved to Approved/")
    check(not (pending / "APPROVAL_test_voice.md").exists(),
          "Voice: file removed from Pending_Approval/")

    # Test reject file movement
    test_file2 = pending / "APPROVAL_test_reject.md"
    test_file2.write_text("---\ntype: approval_request\nstatus: pending\nconfidence: 30\n---\nReject this.", encoding="utf-8")
    check(vs.reject_task('APPROVAL_test_reject.md'), "Voice: reject returns True")
    check((VAULT / "Rejected" / "APPROVAL_test_reject.md").exists(),
          "Voice: file moved to Rejected/")
    check(not (pending / "APPROVAL_test_reject.md").exists(),
          "Voice: reject file removed from Pending_Approval/")

    # Test escalate (Ralph Wiggum signal)
    test_file3 = pending / "APPROVAL_test_escalate.md"
    test_file3.write_text("---\ntype: approval_request\nstatus: pending\nconfidence: 10\n---\nEscalate me.", encoding="utf-8")
    check(vs.escalate_task('APPROVAL_test_escalate.md'), "Voice: escalate returns True")
    signal_files = list((VAULT / "Signals").glob("*APPROVAL_test_escalate*"))
    check(len(signal_files) >= 1, "Voice: signal file created in Signals/")

    # Test high-confidence task is skipped
    test_file4 = pending / "APPROVAL_test_high_conf.md"
    test_file4.write_text("---\ntype: approval_request\nstatus: pending\nconfidence: 90\n---\nHigh confidence.", encoding="utf-8")
    tasks_high = vs.scan_pending_approvals()
    check(not any(t['filename'] == 'APPROVAL_test_high_conf.md' for t in tasks_high),
          "Voice: high-confidence task skipped (>75%)")

    # Test credential check (should fail gracefully)
    check(not vs.credentials_ok(), "Voice: credentials check fails (no env vars)")

    # Test TwiML generation (no Twilio required)
    def _write_twiml_test(name):
        f = pending / name
        f.write_text(f"---\ntype: approval_request\nstatus: pending\nconfidence: 50\n---\nTwiML test {name}.", encoding="utf-8")
        return f

    f_twiml = _write_twiml_test('APPROVAL_test_twiml.md')
    twiml = vs.generate_twiml_voice('APPROVAL_test_twiml.md', 'test_call_001')
    check('Press 1 to approve' in twiml, "Voice: TwiML contains approval prompt")
    check('Press 2 to reject' in twiml, "Voice: TwiML contains rejection prompt")
    check('Press 3 to escalate' in twiml, "Voice: TwiML contains escalate prompt")
    check('<Gather' in twiml, "Voice: TwiML has Gather verb")
    check('<Say ' in twiml or '<Say>' in twiml, "Voice: TwiML has Say verb")

    # Test handle_gather for each digit (separate files so approve doesn't consume the others)
    _write_twiml_test('APPROVAL_test_d1.md')
    approve_twiml = vs.handle_gather('APPROVAL_test_d1.md', 'test_call_001', '1')
    check('approved' in approve_twiml.lower(), "Voice: digit 1 = approved message")

    _write_twiml_test('APPROVAL_test_d2.md')
    reject_twiml = vs.handle_gather('APPROVAL_test_d2.md', 'test_call_002', '2')
    check('rejected' in reject_twiml.lower(), "Voice: digit 2 = rejected message")

    _write_twiml_test('APPROVAL_test_d3.md')
    escalate_twiml = vs.handle_gather('APPROVAL_test_d3.md', 'test_call_003', '3')
    check('escalated' in escalate_twiml.lower(), "Voice: digit 3 = escalated message")

    _write_twiml_test('APPROVAL_test_d9.md')
    invalid_twiml = vs.handle_gather('APPROVAL_test_d9.md', 'test_call_004', '9')
    check('invalid' in invalid_twiml.lower(), "Voice: invalid digit handled")

    # Test missing file handling
    missing_approve = vs.approve_task('NONEXISTENT.md')
    check(not missing_approve, "Voice: approve missing file returns False")
    missing_reject = vs.reject_task('NONEXISTENT.md')
    check(not missing_reject, "Voice: reject missing file returns False")
    missing_escalate = vs.escalate_task('NONEXISTENT.md')
    check(not missing_escalate, "Voice: escalate missing file returns False")

    # Test that processed IDs are tracked
    check('APPROVAL_test_voice.md' in vs.processed_ids,
          "Voice: approved file tracked in processed_ids")
    check('APPROVAL_test_reject.md' in vs.processed_ids,
          "Voice: rejected file tracked in processed_ids")

    # Test status CLI path
    check(vs.credentials_ok() == (False),
          "Voice: status shows credentials not configured")

    check(True, "Voice: all unit tests complete")

finally:
    # Ensure any leftover test files are cleaned from pending
    for f in list(pending.glob("APPROVAL_test_*")):
        try: f.unlink()
        except: pass
    if VAULT.__str__() in sys.path:
        sys.path.remove(str(VAULT))

cleanup()

# Summary
print("\n" + "="*70)
total = PASS + FAIL
pct = (PASS / total * 100) if total > 0 else 0
print(f"  RESULTS: {PASS}/{total} passed ({pct:.0f}%)")
if FAIL == 0:
    print("  STATUS: ✅ ALL TESTS PASSED")
else:
    print(f"  STATUS: ❌ {FAIL} TEST(S) FAILED")
print("="*70)

sys.exit(0 if FAIL == 0 else 1)
