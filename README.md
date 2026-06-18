# Personal AI Employee — Hackathon Project

**Hackathon:** Personal AI Employee Hackathon 0  
**Stack:** Python 3.13+ / Obsidian / OpenCode + DeepSeek V4 Flash / Docker  
**Vault:** `D:\Desktop4\Obsidian Vault`  
**Secrets:** `C:\Users\%USERNAME%\.ai_employee\secrets\`  
**GitHub:** https://github.com/daniyalazhar123/AI-Employee-Vault

---

## Quick Status

| Tier | Status | Verified |
|------|--------|---------|
| 🥉 Bronze | ✅ Complete | Yes |
| 🥈 Silver | ✅ Complete | Yes |
| 🥇 Gold | ✅ Complete (11/14 PASS) | June 18, 2026 |
| 💎 Platinum | ❌ Not Started | — |

---

## What This Does

- Monitors Gmail, WhatsApp, LinkedIn, Odoo automatically
- Processes tasks using OpenCode + DeepSeek V4 Flash as AI engine
- Creates invoices in Odoo 19 (Docker)
- Sends real emails via Gmail API
- Posts to LinkedIn / Facebook / Instagram / Twitter
- Human-in-the-loop approval for sensitive actions
- Ralph Wiggum loop for autonomous task completion
- Error recovery with circuit breaker and dead letter queue
- Audit logging for all actions

## Architecture

```
Email ─┐
WhatsApp ─┤                  ┌─────────────┐
Social  ─┼── Watchers ─────→ │   Obsidian   │ ←── OpenCode + DeepSeek (AI Engine)
Odoo   ─┘        │           │   Vault      │       │
                  │           │ (File System)│       │
                  │           └─────────────┘       │
                  │                │                │
                  ▼                ▼                ▼
            ┌──────────┐    ┌──────────┐    ┌──────────┐
            │ mcp_email │    │ mcp_odoo │    │mcp_social│
            └──────────┘    └──────────┘    └──────────┘
                  │                │                │
                  ▼                ▼                ▼
             Gmail API        Odoo 19 (Docker)   LinkedIn/FB/IG/Twitter
```

**Flow:** Watchers detect events → write `.md` files to vault folders → OpenCode + DeepSeek reads tasks → executes via MCP servers.

---

## Screenshots

*Coming soon — see demo video for live demonstration*

---

### Prerequisites

- Docker Desktop (v29+)
- Python 3.13+
- Node.js v24+ (for Claude Code)
- Claude Code CLI (`npm install -g @anthropic-ai/claude-code`) / OpenRouter (DeepSeek V3)
- Git

### Secrets Setup

All credentials stored **outside** vault at `C:\Users\%USERNAME%\.ai_employee\secrets\`:

```env
DRY_RUN=false
REQUIRE_APPROVAL=false
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=admin
ODOO_PASSWORD=admin
```

Files in secrets directory:
- `.env` — Merged configuration
- `credentials.json` — Gmail API OAuth credentials
- `token.pickle` — Gmail OAuth token
- `linkedin_session.json` — LinkedIn session cookies

### Start Odoo

```bash
docker compose up -d
# Odoo 19 at http://localhost:8069
# PostgreSQL 15 at localhost:5432
# Default: admin / admin
```

### Run

```bash
# Start all watchers
python orchestrator.py

# Or individual watchers
python watchers/gmail_watcher.py
python watchers/whatsapp_watcher.py
python watchers/social_watcher.py
python watchers/odoo_lead_watcher.py

# MCP servers (manual)
python mcp_email.py --action list
python mcp_odoo.py --action get_partners
python mcp_social.py --action status

# Ralph Wiggum loop (persistent task execution)
python ralph_loop.py "Process all files in Needs_Action"
```

---

## Vault Structure

```
Obsidian Vault/
├── .claude/
│   ├── skills/          # 8 agent skills
│   └── README.md
│
├── watchers/            # Perception layer (5 watchers)
│   ├── gmail_watcher.py
│   ├── whatsapp_watcher.py
│   ├── social_watcher.py
│   ├── office_watcher.py
│   └── odoo_lead_watcher.py
│
├── Needs_Action/        # Incoming tasks
├── Pending_Approval/    # Drafts awaiting human review
├── Done/                # Completed tasks
├── Drafts/              # Draft content
├── Social_Drafts/       # Social media drafts
├── Social_Summaries/    # Social media reports
├── Logs/                # Batch processing logs
├── Dead_Letter_Queue/   # Failed items
├── Approved/            # Approved action files
│
├── mcp_email.py         # Email MCP server
├── mcp_odoo.py          # Odoo MCP server
├── mcp_social.py        # Social media MCP server
├── orchestrator.py      # Master orchestrator
├── ralph_loop.py        # Persistent task executor
├── batch_processor.py   # Backlog processor
├── secrets_config.py    # Centralized secrets loader
├── docker-compose.yml   # Odoo 19 + PostgreSQL 15
├── STATUS.md            # Current real status
├── Dashboard.md         # Live dashboard (counts)
└── README.md            # This file
```

---

## Tier Documentation

| Tier | Document | Status |
|------|----------|--------|
| 🥉 Bronze | [docs/BRONZE_TIER.md](docs/BRONZE_TIER.md) | ✅ Complete |
| 🥈 Silver | [docs/SILVER_TIER.md](docs/SILVER_TIER.md) | ✅ Complete |
| 🥇 Gold | [docs/GOLD_TIER.md](docs/GOLD_TIER.md) | ✅ Verified June 18-19, 2026 |
| 💎 Platinum | [docs/PLATINUM_TIER.md](docs/PLATINUM_TIER.md) | ❌ Not Started |

## Security

**Zero credentials in the vault.** All secrets are stored at `C:\Users\%USERNAME%\.ai_employee\secrets\` and loaded via `secrets_config.py`. The vault is safe to push to public GitHub.

Files excluded via `.gitignore`:
- `.env`, `*.pickle`, `credentials.json`, `token.json`, `linkedin_session.json`
- `__pycache__/`, `*.pyc`
- `Logs/`, `In_Progress/`
- `linkedin_browser_data/`, `linkedin_browser_profile/`

---

## GitHub

https://github.com/daniyalazhar123/AI-Employee-Vault

---

*Last updated: June 19, 2026 — Gold Tier Live Tested*
