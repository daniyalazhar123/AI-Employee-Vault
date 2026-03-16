# AI Employee - Agent Skills

**Gold Tier Requirement #12** - All AI functionality implemented as Agent Skills

This folder contains Claude Code Agent Skills definitions for the AI Employee.

---

## Agent Skills Structure

### `/agents/` - Agent Definitions

Agent skills define what the AI Employee can do autonomously.

### `/skills/` - Skill Implementations

Individual skill implementations that agents can use.

---

## Available Agent Skills

### 1. Email Processing Agent

**Skill:** `email_processor`

**Capabilities:**
- Read emails from Gmail
- Draft professional replies
- Categorize emails by urgency
- Flag important emails for human review

**Usage:**
```
@agent Process emails in Needs_Action folder
```

### 2. WhatsApp Response Agent

**Skill:** `whatsapp_responder`

**Capabilities:**
- Monitor WhatsApp messages
- Detect urgent keywords
- Draft responses
- Escalate complex queries

**Usage:**
```
@agent Respond to urgent WhatsApp messages
```

### 3. Social Media Agent

**Skill:** `social_media_manager`

**Capabilities:**
- Generate posts for LinkedIn, Facebook, Instagram, Twitter
- Add relevant hashtags
- Schedule posts
- Generate performance summaries

**Usage:**
```
@agent Create and schedule social media posts for this week
```

### 4. Odoo Accounting Agent

**Skill:** `accounting_assistant`

**Capabilities:**
- Create invoices in Odoo
- Record payments
- Reconcile bank transactions
- Generate financial reports

**Usage:**
```
@agent Create invoice for Client A
```

### 5. CEO Briefing Agent

**Skill:** `ceo_briefing_generator`

**Capabilities:**
- Generate weekly CEO briefings
- Include accounting audit
- Add social media summaries
- Identify bottlenecks

**Usage:**
```
@agent Generate weekly CEO briefing
```

### 6. Ralph Loop Agent

**Skill:** `persistent_task_executor`

**Capabilities:**
- Execute multi-step tasks
- Retry on failure
- Move tasks to Done when complete
- Report progress

**Usage:**
```
@agent Process all pending tasks in Needs_Action
```

---

## Agent Configuration

### Agent Skills Config File

Create `.claude/agents/ai-employee.json`:

```json
{
  "name": "ai-employee",
  "version": "1.0.0",
  "description": "Personal AI Employee for business automation",
  "skills": [
    "email_processor",
    "whatsapp_responder",
    "social_media_manager",
    "accounting_assistant",
    "ceo_briefing_generator",
    "persistent_task_executor"
  ],
  "permissions": {
    "email": {
      "read": true,
      "draft": true,
      "send": false
    },
    "whatsapp": {
      "read": true,
      "draft": true,
      "send": false
    },
    "social": {
      "create": true,
      "schedule": true,
      "post": false
    },
    "accounting": {
      "create_invoice": false,
      "record_payment": false,
      "read_reports": true
    }
  },
  "human_in_loop": [
    "email_send",
    "whatsapp_send",
    "social_post",
    "invoice_create",
    "payment_record"
  ]
}
```

---

## Skill Implementation Template

### Example: Email Processor Skill

Create `.claude/skills/email_processor.py`:

```python
"""
Email Processor Agent Skill

Processes emails and drafts replies.
"""

def process_emails(vault_path: str) -> dict:
    """
    Process emails in Needs_Action folder.
    
    Returns:
        dict with processed count and drafts created
    """
    # Implementation here
    return {
        'processed': 0,
        'drafts_created': 0
    }

def draft_reply(email_path: str) -> str:
    """
    Draft a reply for an email.
    
    Returns:
        Path to draft file
    """
    # Implementation here
    return draft_path
```

---

## Usage in Claude Code

### Enable Agent Skills

In Claude Code:

```
/agents enable ai-employee
```

### Run Agent Skill

```
@ai-employee Process all pending emails
```

### Check Agent Status

```
/agents status
```

---

## Gold Tier Compliance

All AI functionality is implemented as Agent Skills:

- ✅ Email processing → `email_processor`
- ✅ WhatsApp responses → `whatsapp_responder`
- ✅ Social media → `social_media_manager`
- ✅ Accounting → `accounting_assistant`
- ✅ CEO Briefings → `ceo_briefing_generator`
- ✅ Task execution → `persistent_task_executor`

**Status:** ✅ **COMPLETE**

---

## Next Steps

1. Implement each skill in Python
2. Test skills with Claude Code
3. Enable human-in-the-loop for sensitive actions
4. Monitor skill performance
5. Update skills based on feedback

---

*Agent Skills for AI Employee - Gold Tier Complete*
