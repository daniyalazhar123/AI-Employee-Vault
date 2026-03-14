# AI Employee Vault

An automated email and file processing system built on Obsidian Vault that uses AI to handle routine tasks like email responses, file processing, and dashboard updates.

## Description

This system acts as your AI employee, automatically:
- Monitoring Gmail for new emails and creating action items
- Watching office files for new documents to process
- Drafting professional email replies
- Updating dashboards with sales and metrics data
- Organizing processed items into appropriate folders

## Folder Structure

```
Obsidian Vault/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── gmail_watcher.py          # Gmail monitoring script
├── office_watcher.py         # Office files monitoring script
├── whatsapp_watcher.py       # WhatsApp Web monitoring script
├── linkedin_post_generator.py # LinkedIn post generator
├── facebook_instagram_post.py # Facebook & Instagram post generator
├── twitter_post.py           # Twitter post generator
├── ceo_briefing.py           # CEO weekly briefing generator
├── credentials.json          # Gmail API credentials (create your own)
├── token.pickle             # Auto-generated auth token
├── Dashboard.md              # Sales/metrics dashboard
├── Company_Handbook.md       # Tone and style guidelines
├── Business_Goals.md         # Quarterly/annual goals (optional)
├── Inbox/                    # New incoming items
├── Needs_Action/             # Pending action items (auto-created)
├── Pending_Approval/         # Drafts awaiting review
├── Approved/                 # Approved items
├── Done/                     # Completed/processed items
├── Logs/                     # Processing logs
├── Briefings/                # CEO weekly briefings
├── Office_Files/             # Office documents to process
├── Plans/                    # Future plans
├── Social_Drafts/            # Social media drafts
└── Skills/                   # AI skills documentation
    └── CORE_SKILLS.md
```

## Setup Instructions

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 1b. Install Playwright Browsers

```bash
playwright install chromium
```

This installs the Chromium browser needed for WhatsApp Web automation.

### 2. Configure Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download `credentials.json` and place it in the vault root

### 3. Configure Company Handbook

Edit `Company_Handbook.md` with your preferred tone and style guidelines.

### 4. First Run Authentication

Run the gmail_watcher.py once to authenticate:

```bash
python gmail_watcher.py
```

This will open a browser window for Google authentication. After successful auth, `token.pickle` will be created automatically.

## How to Run

### Run Gmail Watcher

Monitors Gmail for new unread emails and creates action items:

```bash
python gmail_watcher.py
```

### Run LinkedIn Post Generator

Generates professional LinkedIn posts from Dashboard data:

```bash
python linkedin_post_generator.py
```

- Reads latest metrics from `Dashboard.md`
- Generates engaging post with achievements
- Saves draft to `Social_Drafts/` folder
- Prompts for approval before posting

### Run Office Watcher

Watches `Office_Files/` folder for new documents:

```bash
python office_watcher.py
```

- Monitors `Office_Files/` folder for new files
- Creates action items in `Needs_Action/` folder
- Auto-triggers AI to process and summarize
- Updates `Dashboard.md` with relevant data

### Run WhatsApp Watcher

Monitors WhatsApp Web for messages with keywords:

```bash
python whatsapp_watcher.py
```

- Opens WhatsApp Web in persistent browser session
- Saves login to `whatsapp_session/` folder (scan QR once)
- Monitors for keywords: urgent, invoice, payment, help, price, order
- Creates action files in `Needs_Action/` folder
- Auto-triggers AI to draft responses
- Checks every 30 seconds

### Run LinkedIn Post Generator

Generates professional LinkedIn posts from Dashboard data:

```bash
python linkedin_post_generator.py
```

- Reads latest metrics from `Dashboard.md`
- Generates engaging post with achievements
- Saves draft to `Social_Drafts/` folder
- Prompts for approval before posting

### Run Facebook & Instagram Post Generator

Generates engaging Facebook and Instagram posts:

```bash
python facebook_instagram_post.py
```

- Reads Dashboard.md for business metrics
- Creates platform-specific posts (Facebook + Instagram)
- Includes emojis and hashtags
- Saves drafts to `Social_Drafts/` folder
- Prompts for approval before posting

### Run Twitter Post Generator

Generates 3 tweet options (under 280 characters):

```bash
python twitter_post.py
```

- Reads Dashboard.md for business metrics
- Creates 3 different tweet styles (revenue, client, motivational)
- Validates character count (280 limit)
- Saves drafts to `Social_Drafts/` folder
- Prompts for approval before posting

### Run CEO Weekly Briefing Generator

Generates professional CEO briefing every Monday:

```bash
python ceo_briefing.py
```

- Reads Dashboard.md, Business_Goals.md, and Done/ folder
- Creates comprehensive weekly briefing including:
  - Weekly revenue and metrics
  - Completed tasks summary
  - Bottlenecks and issues
  - Cost optimization suggestions
  - Upcoming deadlines
- Saves to `Briefings/` folder
- Prompts for approval before sending

### Run Multiple Watchers (Separate Terminals)

```bash
# Terminal 1
python gmail_watcher.py

# Terminal 2
python office_watcher.py
```

## Workflow

1. **Email arrives** → Gmail Watcher detects → Creates action file → AI drafts reply → You review → Send
2. **File added to Office_Files** → Office Watcher detects → Creates action file → AI processes → Dashboard updated → File archived
3. **WhatsApp message** → WhatsApp Watcher detects keyword → Creates action file → AI drafts response → You review → Send

## Configuration

### Gmail Watcher Settings

Edit `gmail_watcher.py` to customize:
- `maxResults`: Number of emails to fetch per check
- Check interval: Change `time.sleep(120)` for different interval

### Office Watcher Settings

Edit `office_watcher.py` to customize:
- Watch folder: Change `OFFICE_FOLDER` path
- Check interval: Adjust `time.sleep(1)` value

## Troubleshooting

### Qwen CLI Not Found
Ensure Qwen CLI is installed globally:
```bash
npm install -g @anthropic/qwen
```

### Gmail API Errors
- Delete `token.pickle` and re-authenticate
- Check Gmail API is enabled in Google Cloud Console
- Verify `credentials.json` is valid

### File Permission Errors
Run as administrator or check folder permissions.

## License

MIT License - Feel free to customize for your needs!

---
*Last updated: March 15, 2026*
