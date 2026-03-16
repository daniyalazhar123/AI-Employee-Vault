# QWEM: Quick Worker Employee Manual

**Your Personal AI Employee - Quick Start Guide**

> **Tagline:** *Life and business on autopilot. Local-first, agent-driven, human-in-the-loop.*

---

## **What is QWEM?**

QWEM (Quick Worker Employee Manual) is your streamlined reference for building an **Autonomous AI FTE** (Full-Time Equivalent) that works 24/7 managing your personal and business affairs.

---

## **Architecture at a Glance**

```
┌─────────────────────────────────────────────────────────┐
│                    OBSIDIAN VAULT                        │
│              (Memory / GUI / Dashboard)                  │
└─────────────────────────────────────────────────────────┘
           ▲                    │                    ▲
           │                    │                    │
    ┌──────┴──────┐      ┌──────┴──────┐      ┌──────┴──────┐
    │   WATCHERS   │      │ CLAUDE CODE  │      │    MCPs     │
    │  (Senses)    │─────▶│   (Brain)    │─────▶│   (Hands)   │
    │ - Gmail      │      │  (Reasoning) │      │ - Email     │
    │ - WhatsApp   │      │  (Planning)  │      │ - Browser   │
    │ - FileSystem │      │  (Ralph Loop)│      │ - Payments  │
    └──────────────┘      └──────────────┘      └──────────────┘
```

---

## **Core Components**

### **1. The Brain: Claude Code**
- Runs in terminal, pointed at Obsidian vault
- Uses **Ralph Wiggum Loop** (Stop hook) for autonomous multi-step tasks
- Reads tasks, creates plans, executes via MCPs

### **2. The Memory: Obsidian**
- **Dashboard.md** - Real-time status (bank balance, pending messages, projects)
- **Company_Handbook.md** - Your rules of engagement
- Folder structure: `/Inbox`, `/Needs_Action`, `/Done`

### **3. The Senses: Watchers (Python Scripts)**
Lightweight scripts that monitor and trigger Claude:

| Watcher | Monitors | Trigger |
|---------|----------|---------|
| Gmail | Unread important emails | New urgent email |
| WhatsApp | Keywords (urgent, invoice, payment) | Urgent message |
| FileSystem | Drop folder | New file added |

### **4. The Hands: MCP Servers**
Model Context Protocol servers for external actions:

| MCP | Capability | Use Case |
|-----|------------|----------|
| filesystem | Read/write files | Vault operations |
| email-mcp | Send/draft emails | Gmail integration |
| browser-mcp | Navigate web | Payment portals |
| odoo-mcp | Accounting | Invoices/payments |

---

## **Quick Start (Bronze Tier - 8-12 hours)**

### **Prerequisites**
```bash
# Install these first
- Claude Code (Pro subscription or use free tier)
- Obsidian v1.10.6+
- Python 3.13+
- Node.js v24+
- GitHub Desktop
```

### **Step 1: Create Vault Structure**
```
AI_Employee_Vault/
├── Dashboard.md
├── Company_Handbook.md
├── Business_Goals.md
├── Inbox/
├── Needs_Action/
├── Done/
├── Pending_Approval/
└── Plans/
```

### **Step 2: Create Dashboard.md**
```markdown
# Dashboard - Last Updated: {{date}}

## Bank Balance: $____
## Pending Messages: __
## Active Projects: __

## Today's Priorities
- [ ] 

## Alerts
```

### **Step 3: Create Company_Handbook.md**
```markdown
# Company Handbook

## Rules of Engagement
1. Always be polite on WhatsApp
2. Flag any payment over $500 for approval
3. Respond to client emails within 24 hours
4. Never send payments without human approval

## Approval Workflow
- Payments > $500 → Requires approval
- Email replies → Draft only, human sends
- Social posts → Schedule, human approves
```

### **Step 4: Create First Watcher (Gmail)**
```python
# gmail_watcher.py
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from pathlib import Path
from datetime import datetime

class GmailWatcher:
    def __init__(self, vault_path: str, credentials_path: str):
        self.vault_path = Path(vault_path)
        self.creds = Credentials.from_authorized_user_file(credentials_path)
        self.service = build('gmail', 'v1', credentials=self.creds)
        self.processed_ids = set()
    
    def check_for_updates(self):
        results = self.service.users().messages().list(
            userId='me', q='is:unread is:important'
        ).execute()
        return [m for m in results.get('messages', []) 
                if m['id'] not in self.processed_ids]
    
    def create_action_file(self, message):
        msg = self.service.users().messages().get(
            userId='me', id=message['id']
        ).execute()
        
        content = f'''---
type: email
from: {msg['payload']['headers'][0]['value']}
subject: {msg['snippet'][:50]}
received: {datetime.now().isoformat()}
priority: high
status: pending
---

## Email Content
{msg.get('snippet', '')}

## Suggested Actions
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing
'''
        filepath = self.vault_path / 'Needs_Action' / f'EMAIL_{message["id"]}.md'
        filepath.write_text(content)
        self.processed_ids.add(message['id'])
```

### **Step 5: Run Claude Code**
```bash
# Point Claude at your vault
cd /path/to/vault
claude

# Prompt: "Check /Needs_Action folder and process any pending items"
```

---

## **Ralph Wiggum Loop (Persistence Pattern)**

Keep Claude working autonomously until task completion:

```bash
# Start a Ralph loop
/ralph-loop "Process all files in /Needs_Action, move to /Done when complete" \
  --completion-promise "TASK_COMPLETE" \
  --max-iterations 10
```

**How it works:**
1. Claude works on task
2. Claude tries to exit
3. Stop hook checks: Is task in `/Done`?
4. NO → Block exit, re-inject prompt (loop continues)
5. YES → Allow exit (complete)

---

## **Human-in-the-Loop Pattern**

For sensitive actions, Claude creates approval requests:

```markdown
---
type: approval_request
action: payment
amount: 500.00
recipient: Client A
reason: Invoice #1234 payment
created: 2026-01-07T10:30:00Z
status: pending
---

## Payment Details
- Amount: $500.00
- To: Client A (Bank: XXXX1234)
- Reference: Invoice #1234

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder.
```

---

## **Tiered Deliverables**

| Tier | Time | Deliverables |
|------|------|--------------|
| **Bronze** | 8-12h | Vault + 1 Watcher + Claude reading/writing |
| **Silver** | 20-30h | 2+ Watchers + MCP + Approval workflow + Scheduling |
| **Gold** | 40+h | Full integration + Odoo + Social media + CEO Briefing |
| **Platinum** | 60+h | Cloud deployment + 24/7 watchers + Domain specialization |

---

## **Monday Morning CEO Briefing**

**The Standout Feature:** Autonomous weekly business audit

**Trigger:** Scheduled task every Sunday night

**Output:** `Briefings/YYYY-MM-DD_Monday_Briefing.md`

**Contents:**
- **Revenue:** Total earned this week
- **Bottlenecks:** Tasks that took too long
- **Proactive Suggestions:** "I noticed we spent $200 on unused software; shall I cancel?"

---

## **Digital FTE Economics**

| Metric | Human FTE | Digital FTE |
|--------|-----------|-------------|
| Availability | 40 hrs/week | 168 hrs/week (24/7) |
| Monthly Cost | $4,000–$8,000+ | $500–$2,000 |
| Ramp-up Time | 3–6 months | Instant |
| Consistency | 85–95% | 99%+ |
| Annual Hours | ~2,000 | ~8,760 |
| Cost per Task | ~$5.00 | ~$0.50 |

**The 'Aha!' Moment:** 85–90% cost savings = CEO approval threshold

---

## **Pre-Hackathon Checklist**

- [ ] Install all required software
- [ ] Create Obsidian vault "AI_Employee_Vault"
- [ ] Verify Claude Code: `claude --version`
- [ ] Set up UV Python project
- [ ] Join Wednesday Research Meeting (Zoom: 871 8870 7642, Passcode: 744832)

---

## **Resources**

- **Ralph Wiggum Plugin:** https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum
- **MCP Servers:** https://github.com/modelcontextprotocol/servers
- **Odoo MCP:** https://github.com/AlanOgic/mcp-odoo-adv
- **Wednesday Meetings:** Wed 10:00 PM PKT on Zoom/YouTube @panaversity

---

## **Next Steps**

1. Start with **Bronze Tier** (get foundation working)
2. Add one Watcher at a time
3. Implement approval workflow before automating sensitive actions
4. Build up to **Gold Tier** with Odoo + Social Media integration
5. Deploy to cloud for **Platinum Tier** (24/7 operation)

---

**Remember:** This is "agent engineering," not just "prompt engineering." You're building a senior employee who figures out how to solve problems autonomously.

*Built with Claude Code + Obsidian + Python + MCP*
