---
title: STATUS — AI Employee Vault (Honest Baseline)
last_updated: 2026-08-22
supersedes: prior STATUS.md dated 2026-07-25 (which overstated completion — see "Correction Notice")
basis: Independent code audit (7 parallel sub-audits), source read + py_compile + live pm2 logs + git tracking + grep sweeps
grading: "✅ VERIFIED = confirmed by code/logs/git · ⚠️ PARTIAL = exists but incomplete/flawed/unverified · ❌ NOT MET = missing or not-as-specified · 🕓 PLANNED = scripted but not deployed/run"
---

# STATUS — AI Employee Vault

> **This is the honest single source of truth.** It intentionally replaces the earlier optimistic status. Where an earlier claim could not be reproduced from the code, it is marked **UNVERIFIED** rather than PASS — that is a fairness stance, not an accusation.

---

## Correction Notice (why this file changed)

The previous `STATUS.md` (and `FINAL_HACKATHON_REPORT.md`) reported **Gold 14/14 (100%)**, **Platinum 21/21**, **overall 47/52 (90%) "Gold-Ready"**, and **"554/554 tests 100%"**. An independent audit found several of those PASS entries are **not defensible**:

1. **"MCP servers" are not MCP servers.** `mcp_email.py`, `mcp_odoo.py`, `mcp_social.py`, `mcp_browser.py` are ordinary Python **argparse CLI scripts**. None import the MCP SDK, open an `stdio_server`, or register tools. They perform real actions — but not over the MCP protocol.
2. **Odoo "payment #1 via JSON-RPC" is false.** `mcp_odoo.py` uses **XML-RPC, not JSON-RPC** (the "JSON-RPC" label remains wrong). The `record_payment` no-op stub is ✅ **RESOLVED 2026-08-22** — it is now a real `account.payment.register` wizard call (`create` → `action_create_payments`) **gated by the security matrix** (see "What Genuinely Works"). *(The live XML-RPC round-trip against a running Odoo remains **UNVERIFIED** — no Odoo server available; the gate logic + code path are proven in dry-run.)*
3. **CEO-briefing revenue "Rs. 113,000" is hand-typed static text** (`Dashboard.md`, `Business_Goals.md`, echoed into `Briefings/`). It is never queried from Odoo.
4. **Audit logging is not wired.** `audit_logger.log_action()` is called **0 times** by any action script — real sends leave no structured audit record. ✅ **RESOLVED 2026-08-21** — now wired + verified at the `local_agent` execution chokepoint; see "What Genuinely Works".
5. **The Platinum demo is a mock.** `platinum_demo.py` auto-approves and writes a log file instead of calling the real send path. The "minimum passing gate" is narrated, not executed.
6. **"554/554 tests (100%)" is misleading.** `integration_test.py` is dominated by file-existence and `py_compile` checks (and does **not** exclude `.venv`, so third-party library files are compiled and counted). Its end-to-end "handoff" test performs the `shutil.move` steps **itself** rather than driving the real agents, and its Platinum-demo assertion passes precisely **because the demo is a mock**. It does not evidence a working live system.
7. **`DRY_RUN=false` was listed as an achievement.** It is actually a **safety defect** (fail-open real sends by default).

None of this erases the genuinely working parts (below). It re-grades the overstated ones.

---

## Honest Tier Assessment

| Tier | Honest Status | One-line reason |
|------|---------------|-----------------|
| 🥉 **Bronze** | ✅ **MET** (~95%) | Vault, folders, Gmail watcher (live-proven), secrets hygiene all real. Skills present but 5/8 have corrupted frontmatter. |
| 🥈 **Silver** | ⚠️ **PARTIAL** | Watchers + HITL + scheduling real; but **"one working MCP server" not met** (none are MCP) and **LinkedIn auto-post broken**. |
| 🥇 **Gold** | ❌ **NOT MET (as specified)** | Strong error-recovery, **and audit logging now wired + verified (Gold #9)**; but Odoo-via-MCP/JSON-RPC and multiple MCP servers still fail. |
| 💎 **Platinum** | ❌ **NOT MET** | Work-zone split + secrets-never-sync correct; but no running cloud, HTTP-only Odoo (no TLS/backups), and the passing-gate demo is a mock. |

---

## What Genuinely Works Today (✅ VERIFIED)

- **Gmail watcher** — real Google OAuth, dedupe, frontmatter action files, run-loop. Live proof in pm2 logs (2026-08-13: "Processed 5 email(s)", "Saved 44 processed IDs"). `watchers/gmail_watcher.py`
- **Error recovery** — real `CircuitBreaker` + `DeadLetterQueue` + exponential-backoff `RetryHandler`, actually wired into `watchers/base_watcher.py:138`, gmail/odoo watchers, and `odoo_bank_reconciliation.py`. `error_recovery.py`
- **HITL file-flow (execution)** — `local_agent.py` run loop reads `Approved/*.md`, routes by filename to real actions, moves to `Done/`, sends failures to `Dead_Letter_Queue/`.
- **Secrets hygiene** — no secrets committed (grep for `sk-`, `ya29.`, `AIza`, `ghp_`, `AKIA` = 0 hits); secrets loaded from `~/.ai_employee/secrets/` outside the vault; thorough `.gitignore`.
- **Work-zone split** — Cloud layer is draft-only (writes to `Drafts/`+`Pending_Approval/`, zero send/post); Local executes. `cloud_agent.py` / `local_agent.py`
- **Vault sync (git)** — `vault_sync.py` commits on an interval; real commit history present.
- **Health monitor** — `health_monitor.py` runs real checks (git/disk/logs/pending) and wrote alerts (`health_monitor.log`).
- **Orchestrator** — real process supervisor: spawns watchers, auto-restarts on crash, health endpoint :8765, `--dry-run`.
- **Scheduling** — Task Scheduler + `schtasks` + PM2 `ecosystem.config.js` all real (weekly Mon 08:00 briefing task).
- **Bank reconciliation logic** — genuinely implemented (proper `account.payment.register` wizard, 3-tier matcher, CSV/PDF parse). *(Not wired into orchestrator; needs a live Odoo.)*
- **Wired audit logging (Gold #9)** — every executed action at the HITL chokepoint now writes a structured row to `Logs/Audit/audit_YYYYMMDD.jsonl` via `AuditLogger.log_action()`. Success path: `_log_action` → `self.audit.log_action(...)` at `local_agent.py:575`; failure path (before DLQ) at `local_agent.py:213`. **Verified 2026-08-21** by `verify_audit_wiring.py`: a dry-run approved email produced `{action_type:email_send, actor:local_agent, status:success}` and a recipient-less file produced `{…status:failed, error:"Could not extract recipient…"}` — both rows confirmed on disk in `Logs/Audit/audit_20260821.jsonl`; the same run logged `email_mcp.dry_run=True` (no real send). *(Scope: the `local_agent` execution path only. Direct-CLI runs of `mcp_*.py` still don't call `log_action()` — tracked separately.)*
- **Payment approval gate (Safety Gap #1)** — `record_payment` is no longer a stub: it is a real `account.payment.register` wizard call (`mcp_odoo.py:293` create → `mcp_odoo.py:298` `action_create_payments`) **gated by the security matrix before any write**. `SecurityGuard.evaluate_payment()` (`security_guard.py:149`) maps a payment `> PAYMENT_APPROVAL_THRESHOLD` (default $100) **or** a new/unknown payee to `large_payment` (HUMAN_APPROVAL → refused unless `approved=True`); an ordinary payment to a known payee maps to `odoo_payment` (auto-allowed). The gate is invoked on the real path at `mcp_odoo.py:275` and runs **before** the dry-run branch, so it is enforced in every mode. New-payee detection is a best-effort Odoo `account.payment` history lookup (`_payee_has_history`, `mcp_odoo.py:230`) that fails safe to "new" when offline. **Verified 2026-08-22** by `verify_payment_gate.py` (dry-run, no real payment): $50/known → allowed; $5000/known → blocked; $50/new-payee → blocked; $5000/known+approved → allowed. Proof on disk: 4 `mcp_odoo_record_payment` rows in `Logs/Audit/audit_20260822.jsonl` (2 `requires_approval` + 2 `success`) and 4 `payment_gate` rows in `Logs/Audit/security_20260822.jsonl`. *(The live XML-RPC round-trip against a running Odoo is still **UNVERIFIED** — no server; the gate decision + code path are what's proven.)*

## What's Partial or Flawed (⚠️)

- **WhatsApp watcher** — real Playwright, but (1) keyword filter is dead (flags all unread), (2) dedupe key embeds `HH:MM` → duplicate action files every minute.
- **Odoo lead watcher** — real XML-RPC, but hardcoded `admin/admin` and single-shot (no run-loop).
- **Agent Skills** — 8 exist but are thin docs; 5/8 have corrupted frontmatter (closing `---` fused to H1) → 2 drop from the live listing; several dead file references.
- **Ralph loop** — subprocess polling loop, **not** a Claude Code Stop hook; uses invalid flag `claude --yes` → would fail on a live run.
- **CEO briefings** — files exist and some metrics are real (folder/file counts, log JSONL), but revenue is static placeholder and there is no subscription/accounting-audit code.
- **Social (FB/IG/Twitter)** — real posting code exists (Playwright/XAgent); runtime not reproduced in audit; not exposed as MCP.
- **Claim-by-move** — atomic move code is correct, but `In_Progress/` is gitignored → claim state does **not** sync between VMs.

## What's Not Met / Not Real Yet (❌)

- **Any MCP-protocol server** — the `mcp_*.py` are CLIs, not MCP servers. (Blocks Silver #5, Gold #3, Gold #6.)
- **Odoo payment via JSON-RPC (as-specified)** — the transport is **XML-RPC, not JSON-RPC**, so the literal spec wording is still not met. But `record_payment` is no longer stubbed: it's a real, security-gated `account.payment.register` call (see "What Genuinely Works" / Correction Notice #2). Live posting to a real Odoo remains **UNVERIFIED** (no server).
- **Platinum passing-gate demo** — `platinum_demo.py` is a mock (auto-approve + log file, no real send).
- **Always-on cloud** — no provisioned VM; deploy scripts are stubs (placeholder OCIDs, `cd mcp-email && npm install` on a nonexistent dir, `@anthropic/qwen`); K8s `/health:8080` probe targets a server that doesn't exist → crash-loop.
- **Odoo HTTPS + backups** — HTTP-only compose; no TLS/reverse-proxy; no `pg_dump`/backup job.
- **LinkedIn auto-post (automated)** — `save_linkedin_session.py.md` is broken; no LinkedIn watcher (the referenced one is a filesystem watcher). A one-time manual post may have occurred but is **UNVERIFIED** from code.

## Unverified Historical Claims (need live re-demonstration to claim)

- "Real email sent, Message ID `19eaf0416b78f363`" — send capability is real (`mcp_email.py`), but this specific historical send is not reproducible from the audit.
- "LinkedIn real post published Jun 18 05:10 AM" — automation path is broken in code; treat as a manual/one-off unless re-demonstrated.
- "Facebook 8 cookies / Instagram 11 cookies / Twitter session" — session files may exist (gitignored), but working automated posting is unverified.

---

## Safety Gaps to Fix Before Any Unattended Run (priority order)

1. ~~**Payment gate** — `record_payment` (`mcp_odoo.py`) has no `>$100`/new-payee/approval check; `security_guard.py`'s matrix exists but is never invoked by the payment path.~~ ✅ **DONE 2026-08-22** — `SecurityGuard.evaluate_payment()` (`security_guard.py:149`) is now invoked inside `record_payment` (`mcp_odoo.py:275`) **before** any write; payments `>$100` or to a new/unknown payee are refused unless `approved=True`. Verified by `verify_payment_gate.py` (4/4 cases; proof rows in `audit_20260822.jsonl` + `security_20260822.jsonl`).
2. ~~**`DRY_RUN` default** — flip to `true` (currently fail-open `false`).~~ ✅ **DONE 2026-08-21** — all four action servers now default dry-run ON unless `DRY_RUN` is explicitly `false` (`os.getenv('DRY_RUN','true').strip().lower() != 'false'`): `mcp_email.py:69`, `mcp_odoo.py:51`, `mcp_social.py:82`, `mcp_browser.py:43`. The audit-logging verification run above confirmed `email_mcp.dry_run=True` at runtime (no real send).
3. ~~**Wire `log_action()`** — call it on every real send/post/payment.~~ ✅ **DONE 2026-08-21** at the `local_agent` execution chokepoint (success + failure), verified via `verify_audit_wiring.py`. *(Remaining: direct-CLI `mcp_*.py` invocations.)*
4. **Rate limiting** — declared in `.env.example` but not implemented; add real counters.
5. **WhatsApp dedupe** — remove `HH:MM` from the key; fix the keyword filter.
6. **Committed default DB password** — `odoo/odoo.config:16` + docker-compose fallbacks; move to secrets.

---

## Preserved Implementation Notes (real engineering, kept for reference)

- **SafeConsoleFormatter** (`audit_logger.py`) — emoji-safe centralized logging; auto-strips emoji on cp1252/latin-1 streams; supports `PRODUCTION_JSON_LOGS=1`. `setup_logging()` is genuinely imported across many modules. *(This is real and useful — separate from the `log_action()` wiring, which is now done and verified; see above.)*
- **dependency_fallback_guard.py** — `importlib.util` proxies for twilio/fastapi/uvicorn/PyPDF2 with typed fallbacks. Real structural code.
- **LinkedIn Shadow DOM technique (Jun 18 notes)** — share box uses open Shadow DOM; fix used `getRootNode()` + `textbox.type()` (not `.fill()`) to trigger React and enable the Post button. Valid technique; the *automated watcher* around it is still missing/broken.

---

## Engine

Reasoning engine is a **free non-Claude LLM** (report says "OpenCode + DeepSeek V4 Flash Free"; current `settings.local.json` routes to OpenRouter `minimax/minimax-m2.5:free`). This is **permitted** — the hackathon allows any LLM/CLI on the back end. Just disclose it plainly in the submission; reconcile the two engine names so the report matches the live config.

---

*Honest baseline established 2026-08-21 from an independent, evidence-based audit. Update this file as items move from ⚠️/❌ to ✅ — with the file:line or log proof that justifies the change.*
