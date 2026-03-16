# MCP Social Media Server

**Status:** ✅ **COMPLETE**
**Tier:** Gold
**Purpose:** Enable Claude Code to auto-post to social media platforms

---

## Overview

This MCP (Model Context Protocol) server provides social media automation capabilities to Claude Code:

- 💼 **post_linkedin** - Post to LinkedIn
- 📘 **post_facebook** - Post to Facebook
- 📷 **post_instagram** - Post to Instagram
- 🐦 **post_twitter** - Post to Twitter/X
- ⏰ **schedule_post** - Schedule posts for later
- 📊 **get_analytics** - Get post analytics
- 🔒 **close_browser** - Close browser sessions

**Note:** Uses Playwright browser automation (no API keys required for basic posting)

---

## Installation

### Step 1: Install Dependencies

```bash
cd mcp-social
npm install
```

### Step 2: Install Playwright Browsers

```bash
npm run install-browser
# or
npx playwright install chromium
```

### Step 3: Create Screenshots Folder

```bash
mkdir -p ../Social_Drafts/Screenshots
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
    "social": {
      "command": "node",
      "args": ["C:/Users/CC/Documents/Obsidian Vault/mcp-social/index.js"],
      "env": {
        "HEADLESS": "true",
        "BROWSER_TIMEOUT": "30000",
        "SCREENSHOTS_FOLDER": "C:/Users/CC/Documents/Obsidian Vault/Social_Drafts/Screenshots"
      }
    }
  }
}
```

---

## Usage in Claude Code

Once configured, you can use social media automation in Claude Code:

### Post to LinkedIn

```
@social Post to LinkedIn: "Excited to announce our Q1 results! Revenue up 45% with 5 new clients. #BusinessGrowth #Success"
```

### Post to Facebook

```
@social Post to Facebook: "Check out our latest product launch! Link in bio. #NewProduct #Innovation"
```

### Post to Instagram

```
@social Post to Instagram with image "post.jpg": "Behind the scenes at our office! #TeamWork #Culture"
```

### Post to Twitter

```
@social Post to Twitter: "Just hit 1000 followers! Thank you all for the support. 🎉 #Milestone"
```

### Schedule Post

```
@social Schedule a LinkedIn post for tomorrow 9 AM: "Monday motivation: Keep pushing forward! #MondayMotivation"
```

---

## API Reference

### post_linkedin

Post content to LinkedIn.

**Parameters:**
- `content` (required): Post content
- `image` (optional): Path to image file
- `add_hashtags` (optional): Auto-add hashtags (default: true)

**Example:**
```json
{
  "content": "Excited to share our Q1 results! Revenue up 45%.",
  "image": "/path/to/image.jpg",
  "add_hashtags": true
}
```

### post_facebook

Post content to Facebook.

**Parameters:**
- `content` (required): Post content
- `image` (optional): Path to image file

### post_instagram

Post content to Instagram.

**Parameters:**
- `content` (required): Caption content
- `image` (required): Path to image file
- `location` (optional): Location tag

### post_twitter

Post content to Twitter/X.

**Parameters:**
- `content` (required): Tweet content (max 280 chars)
- `image` (optional): Path to image file

### schedule_post

Schedule a post for later.

**Parameters:**
- `platform` (required): Platform name
- `content` (required): Post content
- `scheduled_time` (required): ISO 8601 datetime
- `image` (optional): Path to image file

### get_analytics

Get post analytics (mock implementation).

**Parameters:**
- `platform` (required): Platform name
- `days` (optional): Number of days (default: 7)

### close_browser

Close browser for a platform.

**Parameters:**
- `platform` (required): Platform name

---

## Authentication

### First-Time Login

The first time you use each platform:

1. **Run the post command**
2. **Browser will open** (if HEADLESS=false)
3. **Login manually** to the platform
4. **Session is saved** for future use

### Session Persistence

Sessions are stored in browser context folders:
- `sessions/linkedin/`
- `sessions/facebook/`
- `sessions/instagram/`
- `sessions/twitter/`

---

## Use Cases for AI Employee

### 1. Automated Daily Posts

```
Every day at 9 AM:
1. Generate post content from Dashboard.md
2. @social Post to LinkedIn
3. @social Post to Facebook
4. @social Post to Twitter
5. Log in Dashboard.md
```

### 2. Product Launch Campaign

```
Launch day:
1. @social Post to all platforms simultaneously
2. Include product images
3. Add relevant hashtags
4. Take screenshots for records
```

### 3. Weekly Summary Post

```
Every Friday:
1. Read completed tasks from Done/
2. Generate weekly summary
3. @social Post to LinkedIn
4. Schedule for Monday morning
```

### 4. Event Promotion

```
Before event:
1. Create event posts
2. @social Schedule posts (daily countdown)
3. Track engagement
4. Post live updates during event
```

---

## Integration with AI Employee

### Workflow: Social Media Automation

```
Dashboard updated with achievements
  → Social Watcher detects
  → Draft posts created in Social_Drafts/
  → Human approves drafts
  → Social MCP posts to platforms
  → Screenshots saved
  → Logged in Done/
```

### Example: LinkedIn Post from Dashboard

```
1. Read Dashboard.md for latest metrics
2. Generate LinkedIn post
3. Save draft in Social_Drafts/Polished/
4. Human reviews and approves
5. @social Post to LinkedIn
6. Screenshot saved in Social_Drafts/Screenshots/
7. Move draft to Done/
```

---

## Troubleshooting

### Error: "Browser not found"

**Solution:** Install Playwright browsers
```bash
npx playwright install chromium
```

### Error: "Login required"

**Solution:**
- Run with HEADLESS=false first time
- Manually login to each platform
- Session will be saved

### Error: "Post failed"

**Solution:**
- Check if logged in
- Verify selectors haven't changed
- Increase timeout

### Error: "Image not found"

**Solution:**
- Verify image path is absolute
- Check file exists
- Use supported formats (jpg, png)

---

## Security Considerations

1. **Never post sensitive information**
2. **Use approval workflow** - Human reviews before posting
3. **Rate limit posts** - Don't spam
4. **Respect platform ToS** - No automation abuse
5. **Log all posts** - Audit trail maintained
6. **Backup sessions** - Save browser sessions

---

## Best Practices

### Content Guidelines

1. **LinkedIn:** Professional, business-focused
2. **Facebook:** Friendly, engaging
3. **Instagram:** Visual, lifestyle
4. **Twitter:** Concise, timely

### Posting Schedule

- **LinkedIn:** Tue-Thu, 9-11 AM
- **Facebook:** Wed-Fri, 1-3 PM
- **Instagram:** Daily, 6-9 PM
- **Twitter:** Daily, multiple times

### Hashtag Strategy

- **LinkedIn:** 3-5 professional hashtags
- **Facebook:** 1-3 hashtags
- **Instagram:** 10-15 hashtags
- **Twitter:** 1-2 hashtags

---

## Files

```
mcp-social/
├── package.json          # Dependencies
├── index.js             # Main MCP server
├── README.md            # This file
└── ../Social_Drafts/
    └── Screenshots/     # Post screenshots
```

---

## Development

### Run in Development

```bash
HEADLESS=false npm start
```

This shows browser windows for debugging.

### Debug Mode

```bash
DEBUG=mcp* npm start
```

---

## Platform-Specific Notes

### LinkedIn

- Professional network
- Longer posts perform well
- Use 3-5 hashtags
- Best for B2B content

### Facebook

- Personal/professional mix
- Images increase engagement
- Use 1-3 hashtags
- Good for community building

### Instagram

- Visual-first platform
- High-quality images required
- Use 10-15 hashtags
- Stories + Posts

### Twitter/X

- Short-form content (280 chars)
- Real-time updates
- Use 1-2 hashtags
- Good for news/announcements

---

## Next Steps

After Social MCP is working:

1. ✅ Test with Claude Code
2. ✅ Create posting workflows
3. ✅ Integrate with Social Watcher
4. ✅ Setup scheduled posts
5. ⏭️ Add analytics tracking

---

## References

- [MCP SDK Documentation](https://modelcontextprotocol.io/)
- [Playwright Documentation](https://playwright.dev/)
- [Official MCP Examples](https://github.com/modelcontextprotocol/servers)

---

**Status:** ✅ **Gold Tier - COMPLETE**

*Created: March 16, 2026*
