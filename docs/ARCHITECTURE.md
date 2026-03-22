# AI Employee Vault - System Architecture

**Version:** 1.0.0  
**Tier:** Gold Tier - Personal AI Employee Hackathon 0  
**Primary Engine:** Qwen CLI v0.12.6  
**Last Updated:** March 22, 2026

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Component Descriptions](#component-descriptions)
4. [Data Flow](#data-flow)
5. [Security Architecture](#security-architecture)
6. [Deployment Options](#deployment-options)
7. [Extension Guide](#extension-guide)
8. [Troubleshooting](#troubleshooting)
9. [Performance Considerations](#performance-considerations)
10. [Qwen CLI Integration](#qwen-cli-integration)

---

## System Overview

The AI Employee Vault is an autonomous automation system that manages business communications and operations 24/7. It uses a **perception-reasoning-action** architecture inspired by cognitive systems.

### Core Principles

- **Local-First:** All data stays on your machine (Obsidian vault)
- **Human-in-the-Loop:** Nothing sends without approval
- **Credential Isolation:** Secrets never touch the vault
- **Audit Trail:** Every action is logged
- **Extensible:** Easy to add new watchers and MCP servers

### Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Perception** | Python Watchers | Detect changes in external sources |
| **Reasoning** | Qwen CLI v0.12.6 | Analyze, plan, decide |
| **Action** | MCP Servers | Execute tasks (email, browser, Odoo) |
| **Memory** | Obsidian Vault | Persistent Markdown storage |
| **GUI** | Obsidian App | Human-readable dashboard |

---

## Architecture Diagram

### High-Level System View

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           EXTERNAL SOURCES                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │  Gmail   │  │ WhatsApp │  │  Odoo    │  │ Social   │  │  Office  │     │
│  │  Inbox   │  │  Web     │  │  CRM     │  │  Media   │  │  Files   │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘     │
└───────┼────────────┼────────────┼────────────┼────────────┼────────────────┘
        │            │            │            │            │
        ▼            ▼            ▼            ▼            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        WATCHERS (Perception Layer)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │    Gmail     │  │   WhatsApp   │  │     Odoo     │  │    Social    │   │
│  │   Watcher    │  │   Watcher    │  │   Watcher    │  │   Watcher    │   │
│  │  (2 min)     │  │  (30 sec)    │  │  (5 min)     │  │  (60 sec)    │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
│         │                 │                 │                 │            │
│         └────────────────┬┴────────────────┬┴────────────────┘            │
│                          │                 │                              │
│                          ▼                 ▼                              │
│               ┌──────────────────────────────────────┐                    │
│               │     office_watcher.py (1 sec)        │                    │
│               │     File system monitoring           │                    │
│               └──────────────────────────────────────┘                    │
└─────────────────────────────────────────────────────────────────────────────┘
                          │
                          │ Create Action Files
                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      OBSIDIAN VAULT (Memory / GUI)                           │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  Needs_Action/                                                      │    │
│  │  ├── EMAIL_20260322_143022.md  ← New email detected                │    │
│  │  ├── WHATSAPP_20260322_144511.md ← WhatsApp message               │    │
│  │  └── ODOO_LEAD_20260322_150000.md ← New CRM lead                  │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                          │                                                  │
│                          ▼ (processed by Qwen CLI)                         │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  Pending_Approval/                                                  │    │
│  │  ├── REPLY_EMAIL_20260322_143022.md  ← Draft reply ready          │    │
│  │  ├── POST_LINKEDIN_20260322_160000.md ← Social post draft        │    │
│  │  └── TASK_20260322_170000.md ← Task approval request              │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                          │                                                  │
│                          ▼ (after human approval)                          │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  Approved/  →  Done/                                                │    │
│  │  (Ready for execution)        (Completed + audit log)              │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                          │
                          │ Trigger MCP Actions
                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        MCP SERVERS (Action Layer)                            │
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  mcp-email   │  │ mcp-browser  │  │  mcp-odoo    │  │ mcp-social   │   │
│  │              │  │              │  │              │  │              │   │
│  │ • send_email │  │ • navigate   │  │ • create_    │  │ • post_      │   │
│  │ • draft_email│  │ • click      │  │   invoice    │  │   linkedin   │   │
│  │ • list_emails│  │ • type       │  │ • read_      │  │ • post_      │   │
│  │              │  │ • screenshot │  │   accounting │  │   twitter    │   │
│  │              │  │ • form_fill  │  │ • list_      │  │ • generate_  │   │
│  │              │  │              │  │   partners   │  │   summary    │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
└─────────┼─────────────────┼─────────────────┼─────────────────┼────────────┘
          │                 │                 │                 │
          ▼                 ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           EXTERNAL ACTIONS                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐                    │
│  │  Email   │  │  Browser │  │   Odoo   │  │  Social  │                    │
│  │  Sent    │  │  Actions │  │  Updated │  │  Posted  │                    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘                    │
└─────────────────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        RALPH LOOP (Persistence)                              │
│  • Tracks multi-step task completion                                        │
│  • Ensures no task is left incomplete                                       │
│  • Recovers from crashes/errors                                             │
│  • Maintains task state across restarts                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

```
┌─────────────┐
│   WATCHER   │  Detects new email
└──────┬──────┘
       │ 1. Creates: Needs_Action/EMAIL_*.md
       ▼
┌─────────────┐
│  OBSIDIAN   │  Markdown file stored
└──────┬──────┘
       │ 2. Qwen CLI reads file
       ▼
┌─────────────┐
│  QWEN CLI   │  Analyzes content, drafts reply
└──────┬──────┘
       │ 3. Creates: Pending_Approval/REPLY_EMAIL_*.md
       ▼
┌─────────────┐
│   HUMAN     │  Reviews and approves
└──────┬──────┘
       │ 4. Moves file to Approved/
       ▼
┌─────────────┐
│   MCP       │  Executes action (sends email)
└──────┬──────┘
       │ 5. Moves file to Done/
       ▼
┌─────────────┐
│   AUDIT     │  Logs action to Logs/Audit/
└─────────────┘
```

---

## Component Descriptions

### 1. Watchers (Sensors)

**Purpose:** Detect changes in external sources and create action files.

| Watcher | Interval | Monitors | Output |
|---------|----------|----------|--------|
| `gmail_watcher.py` | 2 min | Gmail inbox | `Needs_Action/EMAIL_*.md` |
| `whatsapp_watcher.py` | 30 sec | WhatsApp Web | `Needs_Action/WHATSAPP_*.md` |
| `office_watcher.py` | 1 sec | File system | `Needs_Action/FILE_*.md` |
| `social_watcher.py` | 60 sec | Social drafts | `Needs_Action/SOCIAL_*.md` |
| `odoo_lead_watcher.py` | 5 min | Odoo CRM | `Needs_Action/ODOO_LEAD_*.md` |

**Implementation Pattern:**

```python
# base_watcher.py pattern
class BaseWatcher:
    def __init__(self, name, interval):
        self.name = name
        self.interval = interval
    
    def watch(self):
        """Poll external source"""
        pass
    
    def create_action_file(self, data):
        """Create markdown file in Needs_Action/"""
        pass
```

### 2. Qwen CLI (Brain)

**Purpose:** Reasoning engine that analyzes action files and plans responses.

**Key Features:**
- Reads Markdown action files
- Analyzes content using LLM reasoning
- Drafts professional responses
- Calls MCP servers for actions
- Creates approval requests

**Commands:**
```bash
# Start Qwen CLI
qwen --cwd "D:\Desktop4\Obsidian Vault"

# Process action file
qwen -y "Read Needs_Action/EMAIL_*.md and draft reply"

# Check status
qwen -y "Show me pending approvals"
```

See `QWEN_CLI_GUIDE.md` for complete reference.

### 3. MCP Servers (Hands)

**Purpose:** Execute approved actions on external systems.

| Server | Functions | Rate Limit |
|--------|-----------|------------|
| `mcp-email/` | send_email, draft_email, list_emails | 10/hour |
| `mcp-browser/` | navigate, click, type, screenshot | 60/minute |
| `mcp-odoo/` | create_invoice, read_accounting, list_partners | 60/minute |
| `mcp-social/` | post_linkedin, post_twitter, generate_summary | 5/hour |

**MCP Protocol:**
- JSON-RPC 2.0 over stdio
- Compatible with Qwen CLI tool calling
- Structured responses with error handling

### 4. Obsidian Vault (Memory)

**Purpose:** Persistent storage and human-readable interface.

**Folder Structure:**

```
Obsidian Vault/
├── Needs_Action/       # New items requiring attention
├── Pending_Approval/   # Awaiting human approval
├── Approved/           # Approved and ready for execution
├── Done/               # Completed tasks
├── Logs/
│   └── Audit/          # Audit trail (JSONL format)
├── Briefings/          # CEO weekly briefings
├── Social_Drafts/      # Social media drafts
└── config/             # Configuration (credentials excluded)
```

**File Naming Convention:**
- `EMAIL_YYYYMMDD_HHMMSS.md` - Email action files
- `WHATSAPP_YYYYMMDD_HHMMSS.md` - WhatsApp action files
- `REPLY_EMAIL_YYYYMMDD_HHMMSS.md` - Reply drafts
- `POST_LINKEDIN_YYYYMMDD_HHMMSS.md` - LinkedIn posts
- `ODOO_LEAD_YYYYMMDD_HHMMSS.md` - Odoo lead files

### 5. Ralph Loop (Persistence)

**Purpose:** Ensure multi-step tasks complete even after crashes.

**Features:**
- Tracks task state in `In_Progress/` folder
- Recovers incomplete tasks on restart
- Implements retry logic with exponential backoff
- Logs all state changes

---

## Data Flow

### Example: WhatsApp Message → Approved Email

**Step 1: Message Received**

```
WhatsApp Server → WhatsApp Web → whatsapp_watcher.py detects message
```

**Step 2: Action File Created**

```markdown
---
type: whatsapp
from: +92-300-1234567
contact: Client Name
timestamp: 2026-03-22 14:30:22
priority: high
---

Message: "Hi! I need an invoice for last month's services. Can you send it?"

Intent: Invoice request
Urgency: High
```

**Step 3: Qwen CLI Processes**

```bash
qwen -y "Read WHATSAPP_*.md and determine appropriate action"
```

**Qwen Analysis:**
- Intent: Client wants invoice
- Action needed: Create invoice in Odoo, email to client
- Information required: Client ID, invoice details

**Step 4: Draft Response Created**

```markdown
---
type: approval
original: WHATSAPP_20260322_143022.md
action: create_and_send_invoice
---

## Proposed Action

1. Create invoice in Odoo for Client Name
2. Email invoice to client@example.com

## Draft Message

Hi Client Name,

Thank you for your message. I'm sending you the invoice for last month's services.

Please find the invoice attached.

Best regards,
Your Company

---
APPROVAL_REQUIRED: true
INSTRUCTIONS: Move to Approved/ to proceed, Rejected/ to cancel
```

**Step 5: Human Approval**

```bash
# User reviews in Obsidian
# Moves file: Pending_Approval/ → Approved/
```

**Step 6: MCP Executes**

```python
# mcp-odoo creates invoice
invoice_id = odoo.create_invoice(partner_id=123, lines=[...])

# mcp-email sends with attachment
mcp-email.send_email(
    to="client@example.com",
    subject="Invoice for Services",
    body="...",
    attachment=f"Invoice_{invoice_id}.pdf"
)
```

**Step 7: Completion**

```
File moved: Approved/ → Done/
Audit log entry created: Logs/Audit/2026-03-22.jsonl
Dashboard updated: Dashboard.md
```

---

## Security Architecture

### Credential Isolation

```
┌─────────────────────────────────────────────────────────────┐
│                    OBSIDIAN VAULT                            │
│  (NO CREDENTIALS STORED HERE)                                │
│                                                              │
│  ├── Needs_Action/                                           │
│  ├── Pending_Approval/                                       │
│  └── Done/                                                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    CREDENTIAL STORAGE                        │
│  (EXCLUDED FROM GIT, ENCRYPTED)                              │
│                                                              │
│  ├── .env.local          ← Environment variables            │
│  ├── config/credentials.json ← OAuth credentials           │
│  └── mcp-email/token.json ← Gmail API token               │
└─────────────────────────────────────────────────────────────┘
```

### Security Rules

1. **NEVER** commit credentials to Git
2. **ALWAYS** use environment variables
3. **NEVER** store API keys in Markdown files
4. **ALWAYS** require human approval for external actions
5. **ALWAYS** log all actions to audit trail

### `.gitignore` Patterns

```gitignore
# Credentials
.env
.env.local
.env.cloud
credentials.json
token.json
*.pem
*.key
*.session
config/secrets.json

# Logs
Logs/*.log
Logs/Audit/
Dead_Letter_Queue/

# Session Data
whatsapp_session/
*.session
*.pickle
```

### Human-in-the-Loop (HITL)

Nothing sends without explicit approval:

```
AI Drafts → Human Reviews → Human Approves → AI Executes
```

**Approval Commands:**

| Command | Action |
|---------|--------|
| `Haan, bhej do` | Send immediately |
| `Yes, send it` | Send immediately |
| `نعم، أرسله` | Send immediately |
| `Nahi, revise karo` | Redraft |
| `No, revise it` | Redraft |
| `لا، راجعه` | Redraft |
| `Edit karna hai` | I want to edit |
| `I want to edit` | I want to edit |

---

## Deployment Options

### Local-Only (Gold Tier)

**Architecture:**
```
┌──────────────────────────────────────┐
│         YOUR LOCAL MACHINE           │
│                                      │
│  ┌────────────────────────────────┐ │
│  │  Watchers + Qwen CLI + MCPs    │ │
│  └────────────────────────────────┘ │
│              │                       │
│              ▼                       │
│  ┌────────────────────────────────┐ │
│  │      Obsidian Vault            │ │
│  └────────────────────────────────┘ │
└──────────────────────────────────────┘
```

**Pros:**
- Complete privacy
- No cloud dependencies
- Full control

**Cons:**
- Requires machine to be on
- No remote access

### Cloud + Local (Platinum Tier Preview)

**Architecture:**
```
┌──────────────────────────────────────┐
│           CLOUD VM (AWS/Azure)       │
│                                      │
│  ┌────────────────────────────────┐ │
│  │  Cloud Agent + Watchers        │ │
│  └────────────────────────────────┘ │
│              │                       │
│              │ Sync via encrypted    │
│              ▼ channel               │
│  ┌────────────────────────────────┐ │
│  │      Local Obsidian Vault      │ │
│  └────────────────────────────────┘ │
│              │                       │
│              ▼                       │
└──────────────────────────────────────┘
         │
         │ Local Qwen CLI + MCPs
         ▼
┌──────────────────────────────────────┐
│         YOUR LOCAL MACHINE           │
│                                      │
│  ┌────────────────────────────────┐ │
│  │  Qwen CLI + MCP Servers        │ │
│  └────────────────────────────────┘ │
└──────────────────────────────────────┘
```

**Pros:**
- 24/7 operation
- Remote access
- Redundancy

**Cons:**
- Cloud costs
- More complex setup

---

## Extension Guide

### Adding a New Watcher

**Step 1: Create Watcher Script**

```python
# watchers/new_watcher.py
from base_watcher import BaseWatcher
from pathlib import Path
import time

class NewWatcher(BaseWatcher):
    def __init__(self):
        super().__init__("new_watcher", interval=60)
    
    def watch(self):
        """Poll your data source"""
        # Implement polling logic
        data = self.fetch_data()
        
        if data:
            self.create_action_file(data)
    
    def fetch_data(self):
        """Fetch data from source"""
        # Implement data fetching
        return data

if __name__ == "__main__":
    watcher = NewWatcher()
    while True:
        watcher.watch()
        time.sleep(watcher.interval)
```

**Step 2: Add to Orchestrator**

```python
# orchestrator.py
WATCHERS = {
    # ... existing watchers ...
    "new_watcher": {
        "script": "new_watcher.py",
        "interval": 60,
        "description": "New Data Source Monitor",
        "enabled": True,
    },
}
```

**Step 3: Add Environment Variables**

```bash
# .env.local
NEW_WATCHER_ENABLED=true
NEW_WATCHER_INTERVAL=60
```

### Adding a New MCP Server

**Step 1: Create MCP Server**

```python
# mcp-new/server.py
import json
import sys

class MCPNewServer:
    def do_something(self, param: str) -> dict:
        """Do something useful"""
        return {
            "success": True,
            "result": f"Did: {param}"
        }

def handle_request(request: dict, server: MCPNewServer) -> dict:
    method = request.get('method')
    params = request.get('params', {})
    
    if method == 'do_something':
        result = server.do_something(**params)
    else:
        return {"error": "Method not found"}
    
    return {"result": result}

if __name__ == "__main__":
    server = MCPNewServer()
    for line in sys.stdin:
        request = json.loads(line)
        response = handle_request(request, server)
        print(json.dumps(response), flush=True)
```

**Step 2: Add to MCP Config**

```json
// config/mcp.json
{
  "mcpServers": {
    "new": {
      "command": "python",
      "args": ["mcp-new/server.py"]
    }
  }
}
```

---

## Troubleshooting

### Common Issues

#### Issue 1: Watcher Not Starting

**Symptoms:**
- Watcher process exits immediately
- No action files created

**Solutions:**
```bash
# Check syntax
python -m py_compile watchers/gmail_watcher.py

# Check logs
type Logs\orchestrator.log

# Run with verbose logging
python watchers/gmail_watcher.py --verbose
```

#### Issue 2: Qwen CLI Not Found

**Symptoms:**
- `qwen: command not found`

**Solutions:**
```bash
# Install Qwen CLI
npm install -g @anthropic/qwen

# Verify installation
qwen --version

# Check PATH
echo %PATH%
```

#### Issue 3: MCP Server Won't Start

**Symptoms:**
- MCP server crashes on startup
- Connection refused errors

**Solutions:**
```bash
# Check dependencies
cd mcp-email
npm install

# Test manually
python mcp_server.py --test

# Check configuration
type config\mcp.json
```

#### Issue 4: Rate Limit Exceeded

**Symptoms:**
- "Rate limit exceeded" errors
- Actions not executing

**Solutions:**
```bash
# Check rate limit status
python mcp_server.py --rate-limit-status

# Wait for cooldown (usually 1 hour for email)
# Or increase limits in .env.local:
RATE_LIMIT=20  # emails per hour
```

#### Issue 5: Authentication Failed

**Symptoms:**
- Gmail/Odoo authentication fails
- "Invalid credentials" errors

**Solutions:**
```bash
# Re-authenticate Gmail
cd mcp-email
node authenticate.js

# Check credentials exist
dir config\credentials.json

# Verify environment variables
python -c "import os; print(os.getenv('GMAIL_CLIENT_ID', 'Not set'))"
```

---

## Performance Considerations

### Watcher Intervals

| Watcher | Default | Min | Max | Impact |
|---------|---------|-----|-----|--------|
| Gmail | 2 min | 30s | 10 min | Low |
| WhatsApp | 30 sec | 10s | 5 min | Medium |
| Office | 1 sec | 100ms | 10 sec | High (CPU) |
| Social | 60 sec | 30s | 5 min | Low |
| Odoo | 5 min | 1 min | 30 min | Low |

**Recommendations:**
- Increase intervals for high-CPU watchers (office_watcher)
- Decrease intervals for time-sensitive sources (WhatsApp)
- Balance responsiveness vs. resource usage

### Rate Limits

| Service | Default | Recommended | Notes |
|---------|---------|-------------|-------|
| Gmail | 10/hour | 10-20/hour | API quota |
| Odoo | 60/min | 60-100/min | Local instance |
| Social | 5/hour | 5-10/hour | Platform limits |

### Resource Usage

**Typical Memory:**
- Watchers: 50-100 MB total
- Qwen CLI: 200-500 MB
- MCP Servers: 100-200 MB
- **Total:** 350-800 MB

**Typical CPU:**
- Idle: <5%
- Processing: 20-50%
- Peak (multiple watchers): 50-80%

**Optimization Tips:**
1. Increase watcher intervals if CPU is high
2. Run Qwen CLI with `--model fast-model` for quick tasks
3. Use SSD for faster file operations
4. Close unused MCP servers

---

## Qwen CLI Integration

### How Qwen CLI Reads/Writes to Vault

**Reading Action Files:**

```bash
# Qwen reads markdown files
qwen -y "Read Needs_Action/EMAIL_*.md and summarize"
```

**Writing Drafts:**

```bash
# Qwen creates draft in Pending_Approval/
qwen -y "Create reply draft in Pending_Approval/REPLY_EMAIL_*.md"
```

**File Movement:**

```bash
# Qwen can move files (with user confirmation)
qwen -y "Move EMAIL_*.md from Needs_Action/ to Done/"
```

### How Qwen CLI Calls MCP Servers

**Tool Calling Format:**

```json
{
  "method": "send_email",
  "params": {
    "to": "client@example.com",
    "subject": "Invoice",
    "body": "Please find attached..."
  }
}
```

**Qwen CLI Configuration:**

```bash
# Add MCP servers to Qwen CLI config
qwen --add-mcp email mcp-email/server.py
qwen --add-mcp odoo mcp-odoo/server.py
```

**Example Interaction:**

```
User: "Send an invoice to client@example.com"

Qwen CLI:
1. Calls mcp-odoo.create_invoice()
2. Gets invoice PDF
3. Calls mcp-email.send_email() with attachment
4. Reports success
```

### Qwen CLI Commands for Vault

| Command | Purpose |
|---------|---------|
| `qwen -y "Show pending approvals"` | List Pending_Approval/ |
| `qwen -y "Process all emails"` | Process Needs_Action/EMAIL_* |
| `qwen -y "Generate weekly summary"` | Create CEO briefing |
| `qwen -y "Check system health"` | Run health checks |

---

## Appendix: File Reference

### Core Scripts

| File | Purpose | Lines |
|------|---------|-------|
| `orchestrator.py` | Master watcher orchestration | ~400 |
| `mcp_server.py` | Email MCP server | ~800 |
| `odoo_mcp.py` | Odoo MCP server | ~1000 |
| `ai_employee_orchestrator.py` | Interactive orchestrator | ~500 |
| `audit_logger.py` | Audit trail management | ~300 |
| `error_recovery.py` | Error handling & retry | ~400 |

### Watchers

| File | Monitors | Interval |
|------|----------|----------|
| `watchers/gmail_watcher.py` | Gmail API | 2 min |
| `watchers/whatsapp_watcher.py` | WhatsApp Web | 30 sec |
| `watchers/office_watcher.py` | File system | 1 sec |
| `watchers/social_watcher.py` | Social drafts | 60 sec |
| `watchers/odoo_lead_watcher.py` | Odoo CRM | 5 min |

### Documentation

| File | Purpose |
|------|---------|
| `QWEN_CLI_GUIDE.md` | Qwen CLI usage guide |
| `docs/ARCHITECTURE.md` | This file - system architecture |
| `docs/ODOO_SETUP.md` | Odoo installation guide |
| `README.md` | Getting started guide |
| `CREDENTIALS_GUIDE.md` | Credential management |

---

**Last Updated:** March 22, 2026  
**Version:** 1.0.0  
**Status:** Production Ready - Gold Tier
