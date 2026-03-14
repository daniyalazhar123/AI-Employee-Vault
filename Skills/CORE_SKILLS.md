# Core Skills - AI Employee

This document defines the core skills and capabilities of the AI Employee system for processing emails, files, and updating dashboards.

---

## Skill 1: Email Processing

### Purpose
Process incoming emails efficiently and draft professional responses.

### Capabilities

#### 1.1 Email Classification
- **Informational**: No reply needed (notifications, newsletters, confirmations)
- **Action Required**: Needs response or follow-up
- **Forward**: Content to be shared with others
- **Urgent**: Requires immediate attention

#### 1.2 Response Drafting
- Follow Company_Handbook tone guidelines
- Professional and concise language
- Context-aware responses
- Clear call-to-action when needed

#### 1.3 Email Metadata Extraction
```yaml
From: Sender name and email
Subject: Email subject line
Date: Received timestamp
Message-ID: Unique identifier
Snippet: Email preview/summary
```

#### 1.4 Processing Workflow
1. Read email action file in `Needs_Action/`
2. Extract sender, subject, and content preview
3. Classify email type
4. Draft appropriate response
5. Save draft to `Pending_Approval/`
6. Move processed file to `Done/`

#### 1.5 Response Templates

**Acknowledgment:**
```
Dear [Name],

Thank you for your email. I have received your message and will review it shortly.

Best regards
```

**Informational (No Reply):**
```
[Note: Informational email - no response required]
Action: Archive after reading
```

**Forward Request:**
```
FYI - Please review the forwarded content below.
Let me know if you need any clarification.
```

---

## Skill 2: File Processing

### Purpose
Analyze and process office documents, extracting key information for records and reporting.

### Capabilities

#### 2.1 File Type Handling
- **Markdown (.md)**: Reports, notes, documentation
- **Text files**: Data exports, logs
- **Spreadsheets**: Sales data, metrics (via text extraction)

#### 2.2 Content Analysis
- Extract key metrics and data points
- Identify document type and purpose
- Summarize main content
- Flag action items or decisions needed

#### 2.3 Data Extraction Patterns

**Sales Data:**
```yaml
Revenue: [amount]
Period: [month/quarter/year]
Products: [list]
Growth: [percentage if applicable]
```

**Reports:**
```yaml
Type: [report category]
Period: [time range]
Key Findings: [summary]
Recommendations: [if any]
```

#### 2.4 Processing Workflow
1. Detect new file in `Office_Files/`
2. Read and analyze content
3. Extract relevant data/metrics
4. Create summary in `Done/` folder
5. Update Dashboard.md if applicable
6. Archive original file

#### 2.5 File Naming Convention
- Use descriptive names: `YYYY-MM-DD_description.md`
- Avoid special characters: `/ \ : * ? " < > |`
- No double extensions: `.md.md` ❌ → `.md` ✅

---

## Skill 3: Dashboard Updating

### Purpose
Maintain accurate and up-to-date dashboards with processed data and metrics.

### Capabilities

#### 3.1 Dashboard Sections
- **Sales Summary**: Revenue, clients, invoices
- **Monthly Breakdown**: Period-by-period performance
- **Key Highlights**: Achievements and milestones
- **Recent Activity**: Latest processed items
- **Status**: Current state overview

#### 3.2 Data Integration
- Aggregate data from processed files
- Calculate totals and averages
- Track trends (growth/decline)
- Update timestamps

#### 3.3 Update Triggers
- New sales data processed
- Monthly/quarterly reports completed
- Client acquisition updates
- Financial transactions recorded

#### 3.4 Dashboard Format
```markdown
# Dashboard

## Sales Summary - [Period]

**Overview:** [Brief description]

### Monthly Breakdown
| Month | Revenue | Notes |
|-------|---------|-------|
| [Month] | [Amount] | [Details] |

### Key Highlights
- [Achievement 1]
- [Achievement 2]

### Recent Activity
- ✅ [Completed task]
- 📋 [Pending item]

**Status:** [Overall status]

---
*Last updated: [Date]*
```

#### 3.5 Update Workflow
1. Process new data file
2. Extract metrics and KPIs
3. Compare with existing dashboard data
4. Update tables and summaries
5. Add new highlights if applicable
6. Update "Last updated" timestamp
7. Log changes in `Logs/` folder

---

## Skill 4: Communication & Tone

### Purpose
Maintain consistent, professional communication aligned with company guidelines.

### Guidelines

#### 4.1 Tone Settings
- **Professional**: Formal business communication
- **Friendly**: Warm but professional
- **Concise**: Clear and to the point
- **Helpful**: Solution-oriented

#### 4.2 Language Rules
- Use proper grammar and spelling
- Avoid slang in professional contexts
- Be respectful and courteous
- Use active voice when possible

#### 4.3 Email Signatures
```
Best regards
[Name/Team]

Thank you
[Name/Team]

Regards
[Name/Team]
```

---

## Skill 5: Organization & Filing

### Purpose
Maintain clean, organized folder structure for easy retrieval and tracking.

### Folder Usage

| Folder | Purpose | Auto-Cleanup |
|--------|---------|--------------|
| `Inbox/` | New incoming items | Manual review |
| `Needs_Action/` | Pending tasks | Auto-processed |
| `Pending_Approval/` | Drafts for review | Manual approval |
| `Approved/` | Approved items | Archive |
| `Done/` | Completed items | Weekly cleanup |
| `Office_Files/` | Source documents | Monthly archive |
| `Logs/` | Processing logs | Monthly rotation |

### Filing Rules
1. Every processed item must have a destination
2. Action files deleted after processing
3. Logs maintained for audit trail
4. Duplicates avoided

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-15 | Initial core skills definition |

---
*Core Skills Document - AI Employee System*
