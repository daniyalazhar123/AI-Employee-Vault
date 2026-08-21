---
title: Independent Automation Audit — Personal AI Employee
auditor: Claude Code (adversarial / evidence-based)
date: 2026-08-21
method: 7 parallel sub-audits, code read + compile-checked + cross-checked against live pm2 logs and git tracking
verdict_scope: Audited against "Personal AI Employee Hackathon 0" official document (Bronze/Silver/Gold/Platinum tiers)
---

# Independent Automation Audit — Personal AI Employee

> **Executive summary (Roman Urdu):**
> Engineering scaffolding **genuinely bana hua hai** aur bohat kuch **actually chal raha hai** — Gmail watcher live proven hai, error-recovery real hai, HITL file-flow wired hai, secrets hygiene strong hai. Lekin spec ke **teen define-karne wale pillars** poore nahi hue: (1) koi **real MCP server nahi** — sab CLI scripts hain, (2) **Odoo JSON-RPC + posted payment** claim jhoot hai (XML-RPC + stub), (3) **audit logging aur payment approval-gate wired nahi**. Upar se **documentation overclaim** karti hai (false "PASS"). Honest reality: **strong Bronze, shaky Silver, Gold/Platinum spec ke mutabiq NOT MET.**

---

## 1. Bottom Line

| Layer | What the doc wanted | What actually exists | Verdict |
|---|---|---|---|
| Watchers (Perception) | 2+ real, running watchers | Gmail (live-proven) + Office + Social + Odoo | ✅ **REAL** |
| MCP Servers (Action) | ≥1 real MCP server (Gold: multiple) | 5 argparse CLI scripts named `mcp_*.py` — zero MCP protocol | ❌ **NOT MCP** |
| Agent Skills | All AI logic as Agent Skills | 8 thin doc-shells; logic lives in standalone `.py` | ⚠️ **PARTIAL** |
| Orchestration / Ralph | Stop-hook Ralph loop | Python polling loop, no Stop hook, invalid CLI flag | ⚠️ **IMITATED** |
| HITL Approval | Approve-by-move → real action | Real via `local_agent.py`; stub twin also runs | ✅ **WIRED** (with caveats) |
| Odoo / Accounting | Odoo 19 via **MCP + JSON-RPC** | XML-RPC CLI, `record_payment` **stubbed**, installer empty | ❌ **PARTIAL / OVERCLAIMED** |
| CEO Briefing | Real revenue/audit from data | Revenue **hand-typed static text**, health block hardcoded | ⚠️ **FAKE DATA** |
| Security / Privacy | Rate limits, payment gate, audit log | Secrets clean ✅; but gate/limits/logging **not wired** | ⚠️ **PARTIAL / theater** |
| Error Recovery | Circuit breaker, DLQ, retry | Genuinely implemented and used | ✅ **REAL** |
| Cloud / Platinum | Always-on VM, HTTPS Odoo, real demo | No running VM, HTTP-only, demo is **mock** | ❌ **NOT MET** |

---

## 2. Tier-by-Tier Scorecard (against the official document)

### 🥉 Bronze — Foundation → **MET (with caveats)**
- ✅ Obsidian vault + `Dashboard.md` present; folder structure (`Needs_Action`, `Done`, etc.) present.
- ✅ One working watcher: **Gmail watcher is live-proven** (pm2 log 2026-08-13: "Processed 5 email(s)", "Saved 44 processed IDs").
- ✅ Reading/writing the vault works.
- ⚠️ "All AI functionality as Agent Skills" — **PARTIAL**: skills exist but are thin docs that shell out to `.py`; logic is not *in* the skills.
- ⚠️ Reasoning engine is **not Claude** at runtime — `settings.local.json` routes to OpenRouter `minimax/minimax-m2.5:free`. (Doc allows non-Claude LLM via router, so this is a *note*, not a fail — see §7.)

### 🥈 Silver — Functional Assistant → **PARTIAL (core criterion fails)**
- ✅ 2+ watchers (well past requirement).
- ✅ HITL approval workflow — real.
- ✅ Basic scheduling (Task Scheduler + PM2).
- ❌ **"One working MCP server"** — **NOT MET.** None of the `mcp_*.py` speak MCP protocol.
- ❌ **Auto-post to LinkedIn** — LinkedIn path is **broken/unimplemented** (`save_linkedin_session.py.md` fails to compile; no LinkedIn watcher).
- ⚠️ Plan.md reasoning loop — partial.

### 🥇 Gold — Autonomous Employee → **NOT MET (as specified)**
- ❌ **Odoo via MCP using JSON-RPC (Odoo 19+)** — it's **XML-RPC**, **not MCP**, and `record_payment` is a **stub**.
- ❌ **Multiple MCP servers** — zero are MCP.
- ⚠️ Facebook/Instagram/Twitter posting — real code exists (Playwright/XAgent). ✅ partial credit.
- ⚠️ **Weekly audit + CEO Briefing** — briefing exists & is scheduled, but numbers are **fabricated** (see §5).
- ✅ **Error recovery & graceful degradation** — genuinely strong.
- ❌/⚠️ **Comprehensive audit logging** — logger is capable but **`log_action()` is called 0 times** by any action script → real sends emit no audit record.
- ⚠️ **Ralph Wiggum loop** — imitated via subprocess polling, **not a Stop hook**; uses invalid `claude --yes` flag that would fail on a live run.
- ⚠️ Documentation exists but **overclaims** (false PASS entries — §6).

### 🏆 Platinum — Always-On Cloud + Local → **NOT MET**
- ✅ Work-zone split (Cloud draft-only / Local executes) — clean, verified.
- ✅ Single-writer Dashboard + Updates merge pattern — correct (folders currently empty).
- ✅ **Secrets-never-sync** — PASS (thorough `.gitignore`, no tracked secrets).
- ⚠️ **Claim-by-move** — implemented but **BROKEN across sync**: `In_Progress/` is gitignored, so claim state never propagates between VMs.
- ❌ **Cloud 24/7** — no evidence of a running always-on VM; deploy scripts are stubs (placeholder OCIDs, nonexistent `mcp-email` npm dirs, `@anthropic/qwen`).
- ❌ **Odoo HTTPS + backups** — HTTP-only compose, no TLS/reverse-proxy, no backup job.
- ❌ **Platinum demo passing gate** — `platinum_demo.py` is **theater**: auto-approves and "send" just writes a log file instead of calling MCP.

---

## 3. Layer-by-Layer Detail (with evidence)

### 3.1 Watchers / Perception — ✅ REAL (best part of the project)
- **gmail_watcher.py — REAL & WORKING.** Google OAuth, frontmatter action files, dedupe, run-loop with try/except. Live proof in pm2 logs. Minor flaws: queries `is:unread` only (spec said unread/important); `MAX_RESULTS=5` hardcoded; mark-as-read disabled.
- **whatsapp_watcher.py — REAL BUT FLAWED.** Genuine Playwright persistent context. **Two real bugs:** (1) keyword filter is dead — flags **all** unread regardless of `KEYWORDS`; (2) dedupe key embeds current `HH:MM`, so a lingering unread chat spawns a **new action file every minute** → duplicate flooding.
- **office_watcher.py / social_watcher.py — REAL & WORKING** (watchdog-based).
- **odoo_lead_watcher.py — REAL BUT FLAWED.** Real XML-RPC. Flaws: hardcoded `admin/admin` (lines 39–44); `run()` is **single-shot, no loop** — contradicts the persistent run-loop pattern.
- **base_watcher.py — helper, NOT the doc's ABC.** No `abc`/`@abstractmethod`/`check_for_updates`; the doc's "Core Watcher Pattern" is imitated, not enforced.
- **save_linkedin_session.py.md — BROKEN** (syntax error, one-lined). LinkedIn advertised but unimplemented.

### 3.2 MCP Servers / Action — ❌ NONE ARE REAL MCP
**All five `mcp_*.py` are ordinary Python classes with argparse CLIs.** None import the MCP SDK, none open `stdio_server`, none register tools (`@mcp.tool` / `list_tools` / `call_tool`), none run JSON-RPC.
- `config/mcp.json` references email/odoo/social — but launching `python mcp_email.py` with no `--action` exits code 2 (argparse error), **not** a JSON-RPC handshake. Schema is also non-standard (`servers[]` array vs Claude Code's `mcpServers` object).
- `install_mcp_servers.bat` installs **Node** servers in `mcp-email/`, `mcp-browser/`, `mcp-odoo/`, `mcp-social/` — **all four directories are MISSING.**
- `mcp_email.py` **does** really send via Gmail/SMTP; `mcp_social.py` really posts; `mcp_browser.py` (not wired) does real Playwright. So the *actions* are real — they're just **not exposed as MCP.**
- `mcp_voice_approval.py` is actually a **FastAPI/Twilio webhook**, not MCP.

> **Silver "1 MCP server": NOT MET. Gold "multiple MCP servers": NOT MET.** The `mcp_*` naming is misleading.

### 3.3 Agent Skills — ⚠️ PARTIAL (logic isn't in the skills)
- All 8 skill folders contain **only `SKILL.md`** — zero bundled scripts.
- **5 of 8 have corrupted frontmatter**: closing `---` fused to the H1 (`---# WhatsApp Responder…`) with newline-stripped bodies → this already knocks `social-media-manager` and `whatsapp-responder` out of the live Skill listing. (Commit `d1ea782` re-added keys but left the fence jammed.)
- **Dead references:** `linkedin_post_generator.py`, `twitter_post.py`, `mcp-odoo/` — all missing.
- `.claude/agents/auto-reply-agent.md` — **INVALID** (no YAML frontmatter at all → not a loadable subagent).

### 3.4 Orchestration / Ralph / HITL / Scheduling
- **Ralph — LOOP-BUT-NOT-STOP-HOOK.** No Claude Code Stop hook registered anywhere (repo-wide grep = zero). `ralph_loop.py` is a plain subprocess polling loop. Bug: `claude --yes` is not a valid flag (should be `--dangerously-skip-permissions`) → would error live.
- **HITL — FULLY WIRED** via `local_agent.py`: `Approved/*.md` → route by filename → real MCP calls → move to `Done/`; failures → `Dead_Letter_Queue`. Caveats: `local_orchestrator.py` is a **parallel STUB** ("would be sent") that **also runs under PM2**; `/Rejected` is created but **never consumed**; `cloud_orchestrator.py` names approvals `APPROVAL_DRAFT_*` which miss the local router and fall through to a stub.
- **Orchestrator — REAL process supervisor** (5 watchers, auto-restart, health endpoint :8765, `--dry-run`). But `--stop` is a stub, and it only wires `odoo_lead_watcher` — bank-recon & briefings are not orchestrated.
- **Scheduling — REAL** (Task Scheduler + `schtasks` + PM2 ecosystem; weekly Mon 08:00 CEO briefing).

### 3.5 Odoo / Accounting / CEO Briefing
- `mcp_odoo.py` — **XML-RPC, not JSON-RPC; not MCP; `record_payment` is a no-op stub** (lines 249–257: "Actual payment recording would go here"). Hardcoded `admin/admin`.
- `odoo-accounting/SKILL.md` is **fictional** — documents a Node.js `mcp-odoo/index.js` with "8 MCP commands … FULLY FUNCTIONAL … 98%+ success". **That directory does not exist**; only 4 of 8 commands exist in Python.
- `odoo_installer/` is **EMPTY**. But `docker-compose.yml` pulls `odoo:19.0` → **deployable**, though **not proven running**.
- `odoo_bank_reconciliation.py` — **genuinely real** matching logic (proper `account.payment.register` wizard, 3-tier matcher, DLQ). But **not wired into orchestrator**; needs a live Odoo.
- `.reset_odoo.py` / `.fix_odoo_modules.py` / `.fix_odoo_invoice.py` — raw psycopg2 DB surgery + force-install retries → signals a **fragile, manually-nursed** Odoo install.

### 3.6 Security & Privacy
- ✅ **No real secrets committed.** Grep for `sk-`, `sk-ant-`, `ya29.`, `AIza`, `xox*`, `ghp_`, `AKIA` = **zero** hits. Session dirs untracked. Secrets live outside the vault in `~/.ai_employee/secrets/`.
- ⚠️ **Committed default DB password** — `odoo/odoo.config:16` (`odoo_secure_..._123`) + docker-compose fallbacks (`admin_password_change_me`). Tracked, not `.example`.
- ❌ **DEV_MODE flag absent.** **`DRY_RUN` defaults to `false`** (fail-open) in email/odoo/social → real sends by default unless the secrets dir exists.
- ❌ **Rate limiting NOT implemented** — `EMAIL_RATE_LIMIT`/`MAX_PAYMENT_AMOUNT` declared in `.env.example` but **no counter/throttle in code**. Theater.
- ❌ **Payment approval boundary NOT enforced** — `record_payment` checks only `dry_run`; no `>$100`, no new-payee, no approval gate. `security_guard.py`'s permission matrix exists but is **never invoked**.
- ❌ **Audit logger not wired** — `log_action()` called **0 times**; schema also deviates (`status` vs `approval_status`, no `approved_by`; retention 30 not 90 days; wrong path/format).
- ✅ **Error recovery — PASS** (real CircuitBreaker, DLQ, exponential backoff; actually used in watchers & bank-recon).

### 3.7 Cloud / Platinum
- ✅ Work-zone split verified (Cloud writes only to `Drafts/`+`Pending_Approval/`; Local executes real MCP).
- ✅ Secrets-never-sync PASS. Minor privacy smell: `processed_whatsapp.txt` (chat/group titles) **is tracked**.
- ⚠️ Claim-by-move broken across sync (`In_Progress/` gitignored).
- ❌ `platinum_demo.py` is **mock** — `local_approve()` auto-moves with "Human approves" log; `local_execute_send()` writes `Demo_Send_Log.md` instead of calling MCP. The passing gate is **narrated, not executed.**
- ❌ Deploy/K8s stubs: placeholder OCIDs, `cd mcp-email && npm install` (dir doesn't exist), `@anthropic/qwen`, `/health:8080` probe with no server behind it → pod crash-loop.
- The stray **`--help/` folder** is an `argv[1]` parse bug in `platinum_demo.py` (run once with `--help`).

---

## 4. Top Issues (ranked, all layers)

1. **No real MCP protocol anywhere** — the spec's core "MCP server" requirement (Silver #5, Gold #6, Gold #3) is unmet despite `mcp_*` naming. These are CLI action scripts.
2. **Documentation overclaims / false PASS** — `FINAL_HACKATHON_REPORT.md` claims JSON-RPC + a posted MCP payment the code does not support (§6). This is the single biggest credibility risk.
3. **Payment path has no approval / amount / new-payee gate** — only dry-run. Directly violates the doc's central safety rule.
4. **Audit logger not invoked by any action script** — "EVERY action logged" is unmet; real sends leave no structured trail.
5. **Rate limiting entirely unimplemented + DEV_MODE absent; `DRY_RUN` fail-open** — safety layer is declarative, not wired.
6. **Ralph is not a Stop hook** and its live invocation would fail (`claude --yes`).
7. **WhatsApp watcher bugs** — dead keyword filter + time-based dedupe → duplicate action-file flooding every minute.
8. **Broken/fictional wiring** — missing `mcp-email/`/`mcp-odoo/` dirs, empty `odoo_installer/`, corrupted SKILL.md frontmatter, invalid `auto-reply-agent.md`.
9. **Odoo integration fragile** — stub payment, `admin/admin`, DB-surgery `.fix_*` scripts, not orchestrated.
10. **Platinum is aspirational** — mock demo, stub deploy scripts, no proven always-on VM, no HTTPS/backups.

---

## 5. Fabricated / Static "Data" (integrity)

The CEO briefing presents numbers as if computed, but they are hand-typed:
- **Revenue "Rs. 113,000"** is static text in `Dashboard.md:18` and `Business_Goals.md:19`, echoed into `Briefings/CEO_Briefing_2026-06-18.md:21`. **Never queried from Odoo `account.move`.**
- `ceo_briefing_auto.py:72-76` **hardcodes** the "AI Employee Health" block ("Odoo: Running", "DRY_RUN: false (real mode)") — printed identically every time, no real check.
- `ceo_briefing_enhanced.py:232-241` hardcodes a "Gold Tier Status" table = all "✅ Complete".
- **Subscription-cancellation audit** exists only as prose in `Business_Goals.md:170-193` — **zero code** (grep for `subscription|cancel|unused` in briefing scripts = 0). No `Bank_Transactions.md` exists.
- Real parts: folder/file counts and audit-log JSONL metrics *do* vary across outputs.

---

## 6. Documentation vs Reality (false "PASS" claims)

From the project's own `FINAL_HACKATHON_REPORT.md`:
- **Line 38** — *"MCP Odoo server | mcp_odoo.py … (JSON-RPC + XML-RPC) | ✅ PASS"* → **No JSON-RPC exists; not an MCP server.**
- **Line 53** — *"payment #1 via JSON-RPC … ✅ PASS"* → **`record_payment` is a stub; no payment is posted.**
- Honest entries (good): `:52` "Odoo … server currently off ⚠️ PARTIAL"; `:91` bank-recon PASS justified only by "File exists".

> A verifiable false PASS is what an auditor/judge penalizes hardest — it puts every other green checkmark in doubt. Fixing this is the highest-leverage cleanup.

---

## 7. On the "OpenAI Agents SDK mandatory / free LLM allowed" point

You noted the requirement is: **OpenAI Agents SDK framework mandatory, but any free LLM on the back end is fine** (and Claude Code / any CLI/LLM permitted, since this doc predates that rule).

Two independent facts from the audit:
- The runtime engine is currently **OpenRouter `minimax/minimax-m2.5:free`** (via `settings.local.json`) — consistent with "free LLM on the back end." ✅ compatible with your rule.
- **BUT**: a repo-wide check found the `mcp` package only as a *transitive dependency of `openai-agents`* — it is **not in `requirements.txt`, not imported anywhere**, and **no `openai-agents` Runner/Agent code path is wired** into the watchers/actions. So if "OpenAI Agents SDK mandatory" is the governing rule, **that framework is effectively not used** in the live code paths — same category of gap as the MCP one: the dependency is present, the *usage* is not.

If you confirm the SDK is truly mandatory, that becomes a **must-fix** and I'll produce the migration plan.

---

## 8. What's genuinely good (credit where due)

- **Gmail watcher**: real, running, deduped — live-proven.
- **Error recovery**: real circuit breaker + DLQ + exponential backoff, actually wired into watchers and bank-recon.
- **Secrets hygiene**: no leaked secrets, thorough `.gitignore`, secrets outside the vault.
- **HITL file-flow** (`local_agent.py`): approve-by-move → real action → Done, with dead-letter fallback.
- **Bank reconciliation logic**: genuinely implemented (proper payment-register wizard, 3-tier matcher) — just unwired and needs a live Odoo.
- **Work-zone split & secrets-never-sync**: the two Platinum ideas that are actually correct.

---

## 9. Recommended next steps (my advice)

1. **Honesty pass first** — rewrite `FINAL_HACKATHON_REPORT.md` to remove false PASS claims; add a truthful `STATUS.md` (real vs planned). *Lowest effort, highest credibility gain.*
2. **Wire the safety layer** — call `log_action()` on every real send; enforce payment approval/amount/new-payee gate; flip `DRY_RUN` default to `true`; add a real rate limiter.
3. **Decide the framework question** — if OpenAI Agents SDK is mandatory, wire it (or one real MCP server) so the core criterion is genuinely met.
4. **Fix the cheap bugs** — WhatsApp dedupe key (drop `HH:MM`) + keyword filter; corrupted SKILL.md frontmatter; `ralph_loop.py` invalid flag.
5. **Only then** claim tiers — Bronze truthfully; Silver once ≥1 real MCP server + LinkedIn or honest scope; Gold/Platinum reframed as "in progress".

---

*Generated by an independent code audit — 7 parallel sub-audits, evidence read from source, cross-checked against live pm2 logs and git tracking. All file:line references verified at audit time (2026-08-21).*
