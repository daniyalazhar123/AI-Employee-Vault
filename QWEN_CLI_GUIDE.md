# Qwen CLI Guide - AI Employee Primary Engine

**Version:** Qwen CLI v0.12.6  
**Status:** Production Ready  
**Tier:** Gold Tier Submission - Personal AI Employee Hackathon 0

---

## 🎯 Overview

This guide explains how to use **Qwen CLI v0.12.6** as the primary reasoning engine for your AI Employee Vault. Qwen CLI is a **free alternative to Claude Code** with no subscription required.

---

## 🏗️ Architecture Overview

### The Complete Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                       EXTERNAL SOURCES                           │
│   Gmail │ WhatsApp │ Social Media │ Odoo CRM │ Office Files     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        WATCHERS (Perception)                     │
│   gmail_watcher │ whatsapp_watcher │ office_watcher │ ...       │
│   • Poll external sources every 30s-5min                        │
│   • Detect changes, new messages, updates                       │
│   • Create action files in Needs_Action/                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OBSIDIAN VAULT (Memory)                       │
│   Needs_Action/ │ Pending_Approval/ │ Done/ │ Logs/Audit/       │
│   • Markdown files as data persistence                          │
│   • Human-readable action requests                              │
│   • Full audit trail                                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   QWEN CLI (Reasoning Engine)                    │
│   • Reads action files from vault                               │
│   • Analyzes, reasons, plans responses                          │
│   • Calls MCP servers for actions                               │
│   • Creates approval requests                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MCP SERVERS (Action Layer)                    │
│   mcp-email │ mcp-browser │ mcp-odoo │ mcp-social               │
│   • Send emails via Gmail API                                   │
│   • Browser automation via Playwright                           │
│   • Odoo ERP operations                                         │
│   • Social media posting                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL ACTIONS                              │
│   Emails sent │ Posts published │ CRM updated │ Reports generated│
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RALPH LOOP (Persistence)                      │
│   • Tracks multi-step task completion                           │
│   • Ensures no task is left incomplete                          │
│   • Recovers from crashes/errors                                │
└─────────────────────────────────────────────────────────────────┘
```

### Component Roles

| Component | Role | Analogy |
|-----------|------|---------|
| **Watchers** | Perception | Eyes and ears - detect changes |
| **Obsidian Vault** | Memory | Brain storage - holds all data |
| **Qwen CLI** | Reasoning | Brain - thinks and decides |
| **MCP Servers** | Action | Hands - execute tasks |
| **Ralph Loop** | Persistence | Conscience - ensures completion |

---

## 📁 Folder Structure Reference

```
D:\Desktop4\Obsidian Vault\
├── Needs_Action/          # New items requiring attention
│   ├── EMAIL_*.md         # Email action files
│   ├── WHATSAPP_*.md      # WhatsApp action files
│   ├── SOCIAL_*.md        # Social media action files
│   └── ODOO_*.md          # Odoo CRM action files
│
├── Pending_Approval/      # Awaiting your approval
│   ├── REPLY_EMAIL_*.md   # Draft email replies
│   ├── POST_SOCIAL_*.md   # Draft social posts
│   └── TASK_*.md          # Task approval requests
│
├── Approved/              # Approved and executing
│   └── *.md               # Files ready for execution
│
├── Done/                  # Completed tasks
│   └── *.md               # Historical record
│
├── Logs/
│   ├── Audit/             # Audit trail (JSONL)
│   ├── orchestrator.log   # Orchestrator logs
│   └── watcher_*.log      # Watcher logs
│
├── Briefings/             # CEO briefings
│   └── CEO_Briefing_*.md  # Weekly reports
│
├── watchers/              # Watcher scripts
│   ├── gmail_watcher.py
│   ├── whatsapp_watcher.py
│   ├── office_watcher.py
│   ├── social_watcher.py
│   └── odoo_lead_watcher.py
│
├── mcp-email/             # Email MCP server
├── mcp-browser/           # Browser MCP server
├── mcp-odoo/              # Odoo MCP server
└── mcp-social/            # Social MCP server
```

---

## 🚀 Getting Started with Qwen CLI

### Installation

```bash
# Install Qwen CLI globally
npm install -g @anthropic/qwen

# Verify installation
qwen --version
# Expected: 0.12.6
```

### Authentication

```bash
# Authenticate with Qwen (first time only)
qwen --auth
```

**What happens:**
1. Browser opens automatically
2. Sign in with your Qwen account
3. Grant permissions
4. Token saved to `~/.qwen/` directory

### Starting Qwen CLI

```bash
# Basic start (uses current directory)
qwen

# Start with specific working directory
qwen --cwd "D:\Desktop4\Obsidian Vault"

# Start in debug mode
qwen --debug
```

---

## 📚 Qwen CLI Commands Reference

### Core Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/auth` | Authenticate with Qwen OAuth | `/auth` |
| `/model` | Switch between models | `/model coder-model` |
| `/insight` | Generate insights from chat history | `/insight last 7 days` |
| `/help` | Show available commands | `/help` |
| `/clear` | Clear conversation context | `/clear` |
| `/exit` | Exit Qwen CLI | `/exit` |

### Model Options

```bash
# Switch to coder model (best for code tasks)
/model coder-model

# Switch to general model (best for reasoning)
/model general-model

# Switch to fast model (best for quick tasks)
/model fast-model
```

### Using Insights

```bash
# Generate insights from last 7 days
/insight last 7 days

# Generate insights for specific topic
/insight about email responses

# Export insights to file
/insight export to Briefings/insights.md
```

---

## 🔧 Running Watchers

### Individual Watchers

```bash
# Gmail Watcher (checks every 2 minutes)
python watchers/gmail_watcher.py

# WhatsApp Watcher (checks every 30 seconds)
python watchers/whatsapp_watcher.py

# Office Files Watcher (checks every 1 second)
python watchers/office_watcher.py

# Social Media Watcher (checks every 60 seconds)
python watchers/social_watcher.py

# Odoo Lead Watcher (checks every 5 minutes)
python watchers/odoo_lead_watcher.py
```

### All Watchers via Orchestrator

```bash
# Start all watchers with auto-restart
python orchestrator.py

# Dry run (test without starting)
python orchestrator.py --dry-run

# Check health status
python orchestrator.py --health
```

### Watcher Configuration

Environment variables (set in `.env.local`):

```bash
# Watcher intervals (seconds)
GMAIL_WATCHER_INTERVAL=120
WHATSAPP_WATCHER_INTERVAL=30
OFFICE_WATCHER_INTERVAL=1
SOCIAL_WATCHER_INTERVAL=60
ODOO_WATCHER_INTERVAL=300

# Logging
LOG_LEVEL=INFO
LOG_FILE=Logs/orchestrator.log
```

---

## 🤖 How Qwen CLI Processes Actions

### Step-by-Step Flow

**1. Watcher Detects Change**

```python
# gmail_watcher.py detects new email
# Creates: Needs_Action/EMAIL_20260322_143022.md
```

**2. Action File Created**

```markdown
---
type: email
from: client@example.com
subject: Pricing Inquiry
received: 2026-03-22 14:30:22
priority: normal
---

Hi,

Can you send me your pricing details?

Thanks,
Client
```

**3. Qwen CLI Reads and Processes**

```bash
qwen -y "Read Needs_Action/EMAIL_20260322_143022.md and draft professional reply"
```

**4. Draft Reply Created**

```markdown
---
type: reply_approval
original_email: EMAIL_20260322_143022.md
to: client@example.com
subject: Re: Pricing Inquiry
---

Dear Client,

Thank you for your inquiry. Here are our pricing details:

[Professional response with pricing]

Best regards,
Your Company

---
APPROVAL_REQUIRED: true
ACTION: Move to Approved/ to send, Rejected/ to discard
```

**5. You Review and Approve**

```bash
# Review pending approvals
dir Pending_Approval\

# Read the draft
type Pending_Approval\REPLY_EMAIL_*.md

# Approve (move to Approved folder)
move Pending_Approval\REPLY_EMAIL_*.md Approved\
```

**6. MCP Server Executes**

```bash
# Email MCP sends the email
# File moves to Done/
# Audit log entry created
```

---

## 🔐 Security Best Practices

### Credential Management

**⚠️ CRITICAL RULES:**

1. **NEVER** commit credentials to version control
2. **ALWAYS** use environment variables
3. **NEVER** store API keys in Markdown files
4. **ALWAYS** use `.env.local` for local secrets

### Secure File Patterns

```gitignore
# NEVER commit these to Git
.env
.env.local
.env.cloud
credentials.json
token.json
*.pem
*.key
*.session
config/secrets.json
```

### Environment Variables Pattern

```python
# ✅ CORRECT - Use environment variables
import os
gmail_api_key = os.getenv('GMAIL_API_KEY')
odoo_password = os.getenv('ODOO_PASSWORD')

# ❌ WRONG - Never hardcode credentials
gmail_api_key = "sk-1234567890abcdef"
odoo_password = "supersecret123"
```

### Security Warnings in Code

```python
# ⚠️ NEVER commit this file to version control
# See CREDENTIALS_GUIDE.md for secure setup instructions
import os
credentials = os.getenv('CREDENTIALS_PATH')
```

---

## 🛠️ Troubleshooting

### Common Issues

#### Issue 1: Qwen CLI Not Found

**Error:** `'qwen' is not recognized as an internal or external command`

**Solution:**
```bash
# Install Qwen CLI
npm install -g @anthropic/qwen

# Verify PATH includes npm global folder
npm config get prefix

# Add to PATH if needed
setx PATH "%PATH%;C:\Users\CC\AppData\Roaming\npm"
```

---

#### Issue 2: Authentication Failed

**Error:** `Authentication failed. Please try again.`

**Solution:**
```bash
# Clear existing auth
rm ~/.qwen/token.json

# Re-authenticate
qwen --auth

# Check network connection
ping api.qwen.ai
```

---

#### Issue 3: Watcher Crashes

**Error:** `Watcher script crashed with exit code 1`

**Solution:**
```bash
# Check syntax
python -m py_compile watchers/gmail_watcher.py

# Check logs
type Logs\watcher_gmail.log

# Run with verbose logging
python watchers/gmail_watcher.py --verbose 2>&1 | tee Logs/gmail_debug.log

# Check dependencies
pip install -r requirements.txt
```

---

#### Issue 4: MCP Server Won't Start

**Error:** `Error: Cannot find module '@modelcontextprotocol/server'`

**Solution:**
```bash
# Install MCP server dependencies
cd mcp-email
npm install

# Check Node.js version
node --version  # Should be 18+

# Reinstall if needed
npm ci
```

---

#### Issue 5: Rate Limit Exceeded

**Error:** `Rate limit exceeded. Try again in 60 seconds.`

**Solution:**
```bash
# Check rate limit settings
# Email: max 10 emails/hour
# Social: max 5 posts/hour
# Odoo: max 100 requests/minute

# Wait for cooldown or reduce frequency
# Adjust watcher intervals in .env.local
```

---

## 📊 Monitoring and Health Checks

### Check Watcher Status

```bash
# Via orchestrator health endpoint
python orchestrator.py --health

# Expected output:
{
  "gmail_watcher": "running",
  "whatsapp_watcher": "running",
  "office_watcher": "running",
  "social_watcher": "running",
  "odoo_watcher": "running"
}
```

### Check Audit Logs

```bash
# View recent audit entries
python audit_logger.py

# View last 24 hours
python audit_logger.py --hours 24

# Export to JSON
python audit_logger.py --export audit_export.json
```

### Check System Health

```bash
# Run health monitor
python health_monitor.py

# Check all components
python orchestrator.py --health --verbose
```

---

## 🎓 Tips for Effective Use

### Daily Workflow

**Morning (5 minutes):**
```bash
# 1. Check overnight activity
type Dashboard.md

# 2. Review pending approvals
dir Pending_Approval\

# 3. Approve items
move Pending_Approval\*.md Approved\
```

**Evening (5 minutes):**
```bash
# 1. Check completed tasks
dir Done\

# 2. Review audit log
python audit_logger.py

# 3. Plan tomorrow's priorities
```

### Weekly Workflow

**Monday Morning (15 minutes):**
```bash
# Generate CEO briefing
python ceo_briefing_enhanced.py

# Review weekly summary
type Briefings\CEO_Briefing_*.md

# Set weekly goals in Business_Goals.md
```

---

## 📝 Note

**Qwen CLI is a free alternative to Claude Code - no subscription required.**

All features in this guide work with Qwen CLI v0.12.6. For the latest updates, check:
- GitHub: https://github.com/anthropics/qwen-cli
- Documentation: https://docs.qwen.ai

---

## 📞 Support

For issues specific to AI Employee Vault:
- Check `CREDENTIALS_GUIDE.md` for credential setup
- Check `docs/ARCHITECTURE.md` for system design
- Check `README.md` for general setup

For Qwen CLI issues:
- Use `/help` command
- Check official Qwen CLI documentation

---

**Last Updated:** March 22, 2026  
**Version:** 1.0  
**Status:** Production Ready
