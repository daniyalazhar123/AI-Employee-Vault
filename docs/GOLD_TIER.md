# Gold Tier — Personal AI Employee

## Requirements

- Odoo 19 running via Docker
- mcp_odoo.py authenticated with invoice creation
- DRY_RUN=false in all MCP servers
- Real email sent via Gmail API
- LinkedIn session saved with li_at cookie
- Facebook/Instagram/Twitter code ready
- CEO Briefing generation
- Error recovery with circuit breaker
- Audit logging
- Ralph Wiggum loop (Claude Code only — no Qwen)
- All AI as Agent Skills

## What Is Complete

| Requirement | Status | Details |
|-------------|--------|---------|
| Odoo 19 via Docker | ✅ Complete | `docker compose up -d`, running at http://localhost:8069 |
| mcp_odoo.py authenticated | ✅ Complete | Invoice #1 and #2 created via JSON-RPC |
| DRY_RUN=false all MCPs | ✅ Complete | `mcp_email.py`, `mcp_social.py`, `mcp_odoo.py` all set to real mode |
| Real email via Gmail API | ✅ Complete | Message ID: `19eaf0416b78f363`, sent to smartydaniyazhar234@gmail.com |
| LinkedIn session saved | ✅ Complete | `li_at` cookie present, 11 cookies saved |
| Facebook/IG/Twitter code | ✅ Complete | `mcp_social.py` with all platforms |
| CEO Briefing generation | ✅ Complete | `ceo-briefing-generator` skill installed |
| Error recovery | ✅ Complete | Circuit breaker, retry, dead letter queue in `error-recovery` skill |
| Audit logging | ✅ Complete | `audit-logger` skill with timestamp/actor/params/results |
| Ralph Wiggum loop | ✅ Complete | Claude Code only — `RALPH_ENGINE=claude` in `.env` |
| All AI as Agent Skills | ✅ Complete | 8 skills in `.claude/skills/` |
| Gmail API fresh token | ✅ Complete | OAuth completed June 10, 2026 (token.pickle valid) |
| Secrets outside vault | ✅ Complete | `C:\Users\%USERNAME%\.ai_employee\secrets\` |
| .gitignore correct | ✅ Complete | No credentials in repo |
| GitHub pushed | ✅ Complete | Latest commit: `96763d6` — Gold Tier verified |

## Setup Instructions (Gold)

1. Complete Bronze and Silver requirements
2. Install Docker Desktop (v29+)
3. Run \`docker compose up -d\` to start Odoo 19 + PostgreSQL 15
4. Configure `C:\Users\%USERNAME%\.ai_employee\secrets\.env`:
   ```env
   DRY_RUN=false
   REQUIRE_APPROVAL=false
   ODOO_URL=http://localhost:8069
   ODOO_DB=odoo
   ODOO_USERNAME=admin
   ODOO_PASSWORD=admin
   ```
5. Run `python mcp_odoo.py --action get_partners` to verify Odoo connection
6. Run `python mcp_email.py --action list` to verify email
7. Run `python orchestrator.py` to start all systems

## Verification Commands

```bash
# Check Odoo
curl http://localhost:8069/web | head -5

# Test email
python mcp_email.py --action list

# Check Gmail token
python -c "import pickle; f=open(r'C:\Users\CC\.ai_employee\secrets\token.pickle','rb'); c=pickle.load(f); print('Valid:', c.valid)"

# Check LinkedIn session
python -c "import json; f=open(r'C:\Users\CC\.ai_employee\secrets\linkedin_session.json'); d=json.load(f); print('li_at:', bool(d.get('li_at') or any(c.get('name')=='li_at' for c in d.get('cookies',[]))))"

# Run orchestrator
python orchestrator.py
```

## Status

**✅ VERIFIED COMPLETE** — June 10, 2026. All Gold Tier objectives achieved and verified.
