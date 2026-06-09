# Personal AI Employee — Gold Tier

**Hackathon:** Personal AI Employee Hackathon 0  
**Stack:** Python 3.13+ / Obsidian / Claude Code / Docker  
**Vault:** `D:\Desktop4\Obsidian Vault`  
**Secrets:** `C:\Users\%USERNAME%\.ai_employee\secrets\`

---

## Architecture

```
Email ─┐
WhatsApp ─┤                  ┌─────────────┐
Social  ─┼── Watchers ─────→ │   Obsidian   │ ←── Claude Code (AI Engine)
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
             Gmail API        Odoo 17 (Docker)   LinkedIn/FB/IG/Twitter
```

**Flow:** Watchers detect events → write `.md` files to vault folders → Claude Code reads tasks → executes via MCP servers.

---

## Tier Status

| Tier | Status | Notes |
|------|--------|-------|
| Bronze | ✅ Complete | Dashboard, Handbook, folders, 1+ watcher |
| Silver | ⚠️ Partial | Code exists for all reqs, never ran DRY_RUN=false end-to-end |
| Gold | ⚠️ Partial | Odoo running via Docker, DRY_RUN=false, but no real email/social sent yet |
| Platinum | ❌ Not started | Cloud deployment not begun |

---

## Setup

### Prerequisites

- Docker Desktop (v29+)
- Python 3.13+
- Node.js v24+ (for Claude Code)
- Claude Code CLI (`npm install -g @anthropic-ai/claude-code`)
- Git

### Secrets

Credentials live **outside** the vault for security:

```
C:\Users\%USERNAME%\.ai_employee\secrets\
├── .env              # Merged config (DRY_RUN=false, Odoo creds, etc.)
├── credentials.json  # Gmail API credentials
├── token.pickle      # Gmail OAuth token
└── linkedin_session.json
```

Create `.env` in that directory:

```env
DRY_RUN=false
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USER=admin
ODOO_PASSWORD=admin
EMAIL_USER=your.email@gmail.com
EMAIL_PASSWORD=your-app-password
```

### Start Odoo

```bash
docker compose up -d
# Odoo 17 at http://localhost:8069
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
python mcp_odoo.py --action get_leads
python mcp_social.py --action status

# Batch process backlog
python batch_processor.py --count 385

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
├── Needs_Action/        # Incoming tasks (385 files)
├── Pending_Approval/    # Drafts awaiting human review (397 files)
├── Done/                # Completed tasks (49 files)
├── Drafts/              # Draft content
├── Social_Drafts/       # Social media drafts
├── Social_Summaries/    # Social media reports
├── Logs/                # Batch processing logs
├── Dead_Letter_Queue/   # Failed items
│
├── mcp_email.py         # Email MCP server
├── mcp_odoo.py          # Odoo MCP server
├── mcp_social.py        # Social media MCP server
├── orchestrator.py      # Master orchestrator
├── ralph_loop.py        # Persistent task executor
├── batch_processor.py   # Backlog processor
├── secrets_config.py    # Centralized secrets loader
├── docker-compose.yml   # Odoo 17 + PostgreSQL 15
├── STATUS.md            # Current real status
├── Dashboard.md         # Live dashboard (counts)
└── README.md            # This file
```

---

## Security

**Credentials NEVER live in the vault.** All secrets are stored at `C:\Users\%USERNAME%\.ai_employee\secrets\` and loaded via `secrets_config.py`. The vault is safe to push to public GitHub.

Files in `.gitignore`:
- `.env`, `*.pickle`, `credentials.json`, `token.json`, `linkedin_session.json`
- `__pycache__/`, `*.pyc`
- `Logs/`, `In_Progress/`

---

## Known Issues

1. **Gmail API** — OAuth token has encoding issues with Python 3.14. SMTP fallback works.
2. **LinkedIn session** — Expired, needs fresh cookie extraction from browser.
3. **No real sends** — No email/social post has ever been sent. Configure credentials and test.
4. **Odoo empty** — Needs chart of accounts, partners, and products configured.
5. **397 items in Pending_Approval** — Human review required for draft replies.

---

## Demo Video

*To be recorded.* Walkthrough should cover:
- Watchers detecting events → writing to vault
- Claude Code reading and processing tasks
- MCP servers executing actions (Odoo invoice creation, email draft)
- Batch processing backlog

---

*Last updated: June 10, 2026*
