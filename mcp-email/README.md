# MCP Email Server

**Status:** ✅ **COMPLETE**
**Tier:** Silver
**Purpose:** Enable Claude Code to send/read emails via Gmail MCP protocol

---

## Overview

This MCP (Model Context Protocol) server provides email capabilities to Claude Code:
- ✉️ **send_email** - Send emails via Gmail
- 📝 **create_draft** - Create email drafts
- 🔍 **search_emails** - Search and read emails
- 📖 **get_email** - Get full email content
- ✅ **mark_read** - Mark emails as read

---

## Installation

### Step 1: Install Dependencies

```bash
cd mcp-email
npm install
```

### Step 2: Setup Gmail Credentials

1. **Go to [Google Cloud Console](https://console.cloud.google.com/)**

2. **Create/select a project**

3. **Enable Gmail API:**
   - Go to "APIs & Services" → "Library"
   - Search for "Gmail API"
   - Click "Enable"

4. **Create OAuth 2.0 credentials:**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Application type: **Desktop app**
   - Click "Create"
   - Download `credentials.json`
   - Place it in parent folder: `../credentials.json`

### Step 3: Authenticate

```bash
node authenticate.js
```

This will:
1. Open a URL in your browser
2. Ask you to sign in with Google
3. Redirect to localhost with auth code
4. Save `token.json` file

### Step 4: Test the Server

```bash
npm start
```

---

## Configuration

### Claude Code MCP Config

Add to your Claude Code MCP settings:

**Windows:** `%APPDATA%\claude-code\mcp.json`
**Mac/Linux:** `~/.config/claude-code/mcp.json`

```json
{
  "mcpServers": {
    "email": {
      "command": "node",
      "args": ["C:/Users/CC/Documents/Obsidian Vault/mcp-email/index.js"],
      "env": {
        "GMAIL_CREDENTIALS": "C:/Users/CC/Documents/Obsidian Vault/credentials.json",
        "GMAIL_TOKEN": "C:/Users/CC/Documents/Obsidian Vault/mcp-email/token.json"
      }
    }
  }
}
```

---

## Usage in Claude Code

Once configured, you can use email capabilities in Claude Code:

### Send Email

```
@email Send an email to client@example.com with subject "Meeting Confirmation" and body "Hi, Just confirming our meeting tomorrow at 2 PM..."
```

### Create Draft

```
@email Create a draft reply to the last email from John about the project update
```

### Search Emails

```
@email Search for emails with label "Important" from last week
```

```
@email Find unread emails with subject containing "invoice"
```

### Get Email Content

```
@email Get the full content of email ID: abc123xyz
```

### Mark as Read

```
@email Mark email ID: abc123xyz as read
```

---

## API Reference

### send_email

Send an email via Gmail.

**Parameters:**
- `to` (required): Recipient email address
- `subject` (required): Email subject
- `body` (required): Email body text
- `cc` (optional): CC email address
- `bcc` (optional): BCC email address

**Example:**
```json
{
  "to": "client@example.com",
  "subject": "Meeting Confirmation",
  "body": "Hi,\n\nJust confirming our meeting tomorrow at 2 PM.\n\nBest regards,\nJohn"
}
```

### create_draft

Create an email draft (doesn't send immediately).

**Parameters:** Same as send_email

**Use case:** For human approval before sending

### search_emails

Search and retrieve emails.

**Parameters:**
- `query` (required): Gmail search query
- `maxResults` (optional): Max results (default: 10)

**Query examples:**
- `is:unread` - Unread emails
- `from:john@example.com` - From specific sender
- `subject:invoice` - Subject contains "invoice"
- `label:important` - Important emails
- `newer_than:7d` - Last 7 days

### get_email

Get full content of specific email.

**Parameters:**
- `messageId` (required): Gmail message ID

### mark_read

Mark an email as read.

**Parameters:**
- `messageId` (required): Gmail message ID

---

## Testing

### Manual Test Script

Create `test.js`:

```javascript
// Test the MCP Email Server manually
import { sendEmail, searchEmails } from './index.js';

async function test() {
  console.log('Testing search...');
  const search = await searchEmails({ query: 'is:unread', maxResults: 5 });
  console.log(search);
  
  console.log('\nTesting send...');
  const send = await sendEmail({
    to: 'your-email@gmail.com',
    subject: 'Test Email',
    body: 'This is a test email from MCP Email Server'
  });
  console.log(send);
}

test();
```

---

## Troubleshooting

### Error: "No token found"

**Solution:** Run authentication script
```bash
node authenticate.js
```

### Error: "credentials.json not found"

**Solution:** 
1. Download credentials from Google Cloud Console
2. Place in correct location: `../credentials.json`

### Error: "Token expired"

**Solution:** Re-run authentication
```bash
node authenticate.js
```

### Error: "Port 3000 already in use"

**Solution:** 
- Close other apps using port 3000
- Or modify PORT in authenticate.js

---

## Security Considerations

1. **Never commit** `credentials.json` or `token.json` to Git
2. ✅ Both files are in `.gitignore`
3. Use **environment variables** for paths
4. Implement **rate limiting** (built-in: max 10 emails/minute)
5. Add **human approval** for bulk sends
6. 📝 Log all email actions for audit trail

---

## Rate Limiting

To prevent Gmail API quota issues:

- Max 10 emails per minute
- Max 100 emails per hour
- Max 1000 emails per day

For bulk operations, use drafts and manual approval.

---

## Files

```
mcp-email/
├── package.json          # Dependencies
├── index.js             # Main MCP server
├── authenticate.js      # OAuth authentication
├── README.md            # This file
├── token.json           # Auto-generated (gitignored)
└── ../credentials.json  # You provide this (gitignored)
```

---

## Development

### Run in Development

```bash
npm start
```

### View Logs

Logs are sent to stderr:
```bash
npm start 2> logs.txt
```

### Debug Mode

```bash
DEBUG=mcp* npm start
```

---

## Integration with AI Employee

This MCP server integrates with the AI Employee Vault:

1. **Gmail Watcher** creates action files for new emails
2. **Claude Code** reads action files and drafts replies
3. **Email MCP** sends the replies (with approval)
4. **Dashboard.md** tracks email metrics

### Workflow

```
Email arrives 
  → Gmail Watcher detects 
  → Action file created in Needs_Action/
  → Claude drafts reply 
  → Human approves 
  → Email MCP sends 
  → Logged in Done/
```

---

## Next Steps

After Email MCP is working:

1. ✅ Test with Claude Code
2. ✅ Integrate with Gmail Watcher
3. ✅ Add to approval workflow
4. ⏭️ Build Browser MCP
5. ⏭️ Build Odoo MCP
6. ⏭️ Build Social MCP

---

## References

- [MCP SDK Documentation](https://modelcontextprotocol.io/)
- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Official MCP Examples](https://github.com/modelcontextprotocol/servers)

---

**Status:** ✅ **Silver Tier - COMPLETE**

*Created: March 16, 2026*
