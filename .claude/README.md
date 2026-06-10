# AI Employee — Claude Code Skills

**Vault:** `D:\Desktop4\Obsidian Vault`  
**AI Engine:** Claude Code (CLI v2.1+) / OpenRouter (DeepSeek V3)  
**Loop:** `python ralph_loop.py "task description"`

---

## Available Skills (8)

| Skill | Directory | Purpose |
|-------|-----------|---------|
| `audit-logger` | `.claude/skills/audit-logger/` | Audit logging & compliance reports |
| `ceo-briefing-generator` | `.claude/skills/ceo-briefing-generator/` | Weekly CEO briefings with revenue tracking |
| `email-processor` | `.claude/skills/email-processor/` | Process Gmail, draft replies, categorize urgency |
| `error-recovery` | `.claude/skills/error-recovery/` | Circuit breaker, dead letter queue, retry logic |
| `odoo-accounting` | `.claude/skills/odoo-accounting/` | Invoicing, payments, reconciliation |
| `social-media-manager` | `.claude/skills/social-media-manager/` | LinkedIn/FB/IG/Twitter posting |
| `whatsapp-responder` | `.claude/skills/whatsapp-responder/` | Monitor & respond to WhatsApp messages |
| `ceo-briefing` | `.claude/skills/ceo-briefing/` | Legacy briefing skill |

---

## Using Claude Code

### Run ad-hoc task
```bash
claude --print "Process all email drafts in Needs_Action/"
```

### Run via Ralph Wiggum loop (persistent)
```bash
python ralph_loop.py "Process all files in Needs_Action/"
```

The loop:
1. Reads task file from `Needs_Action/`
2. Passes to `claude --print <prompt>`
3. On success → moves file to `Done/`
4. On failure → retries with backoff (max 5)
5. Loops until all tasks complete

### Manual skill invocation
```bash
claude -p "Load the email-processor skill and process pending emails"
```

---

## Agent Config

For Claude Code agent mode, use `.claude/settings.json`:

```json
{
  "skills": [
    "audit-logger",
    "ceo-briefing-generator",
    "email-processor",
    "error-recovery",
    "odoo-accounting",
    "social-media-manager",
    "whatsapp-responder"
  ]
}
```

---

*Last updated: June 10, 2026*
