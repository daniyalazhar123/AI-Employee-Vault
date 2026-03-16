# MCP Browser Server

**Status:** ✅ **COMPLETE**
**Tier:** Silver/Gold
**Purpose:** Enable Claude Code to automate web browsers via Playwright

---

## Overview

This MCP (Model Context Protocol) server provides browser automation capabilities to Claude Code:

- 🌐 **navigate** - Go to any URL
- 👆 **click** - Click on elements
- ⌨️ **fill/type** - Fill input fields
- 📸 **screenshot** - Take screenshots
- 📖 **get_text/get_html** - Extract content
- 🔧 **evaluate** - Execute JavaScript
- ⏱️ **wait_for** - Wait for elements
- ⌨️ **press** - Press keyboard keys
- 📜 **scroll** - Scroll page

---

## Installation

### Step 1: Install Dependencies

```bash
cd mcp-browser
npm install
```

### Step 2: Install Playwright Browsers

```bash
npm run install-browser
# or
npx playwright install chromium
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
    "browser": {
      "command": "node",
      "args": ["C:/Users/CC/Documents/Obsidian Vault/mcp-browser/index.js"],
      "env": {
        "HEADLESS": "true",
        "BROWSER_TIMEOUT": "30000"
      }
    }
  }
}
```

---

## Usage in Claude Code

Once configured, you can use browser automation in Claude Code:

### Navigate to Website

```
@browser Navigate to https://www.linkedin.com
```

### Click Elements

```
@browser Click on the "Sign In" button
```

### Fill Forms

```
@browser Fill the email field with "user@example.com"
@browser Fill the password field with "mypassword"
```

### Take Screenshots

```
@browser Take a screenshot of the current page
```

### Extract Content

```
@browser Get the text from the main content area
@browser Find all job postings on the page
```

### Execute JavaScript

```
@browser Run JavaScript to get all links on the page
```

---

## API Reference

### navigate

Navigate to a URL.

**Parameters:**
- `url` (required): URL to navigate to
- `waitUntil` (optional): When to consider navigation complete
  - `load` - Wait for load event
  - `domcontentloaded` - Wait for DOMContentLoaded
  - `networkidle` - Wait for network to be idle (default)
  - `commit` - Wait for network response

**Example:**
```json
{
  "url": "https://www.example.com",
  "waitUntil": "networkidle"
}
```

### click

Click on an element.

**Parameters:**
- `selector` (required): CSS selector
- `timeout` (optional): Timeout in ms (default: 5000)

**Example:**
```json
{
  "selector": "button[type='submit']"
}
```

### fill

Fill an input field.

**Parameters:**
- `selector` (required): CSS selector
- `value` (required): Text to fill
- `timeout` (optional): Timeout in ms (default: 5000)

**Example:**
```json
{
  "selector": "input[name='email']",
  "value": "user@example.com"
}
```

### type

Type text with delays (like real typing).

**Parameters:**
- `selector` (required): CSS selector
- `value` (required): Text to type
- `delay` (optional): Delay between keystrokes in ms (default: 50)

### screenshot

Take a screenshot.

**Parameters:**
- `name` (optional): Filename (default: 'screenshot')
- `fullPage` (optional): Capture full scroll (default: false)

### get_text

Get text content from element.

**Parameters:**
- `selector` (required): CSS selector

### get_html

Get HTML content from element.

**Parameters:**
- `selector` (optional): CSS selector (default: 'body')

### evaluate

Execute JavaScript on page.

**Parameters:**
- `script` (required): JavaScript code

**Example:**
```json
{
  "script": "document.querySelectorAll('a').length"
}
```

### wait_for

Wait for element to appear.

**Parameters:**
- `selector` (required): CSS selector
- `state` (optional): visible, hidden, attached, detached (default: visible)
- `timeout` (optional): Timeout in ms (default: 5000)

### press

Press keyboard key.

**Parameters:**
- `key` (required): Key name (Enter, Tab, ArrowDown, etc.)

### scroll

Scroll page.

**Parameters:**
- `x` (optional): Horizontal position (default: 0)
- `y` (optional): Vertical position (default: 0)

### get_page_info

Get current page information.

**Parameters:** None

### find_elements

Find elements matching selector.

**Parameters:**
- `selector` (required): CSS selector

### close

Close the browser.

---

## Example Workflows

### Login to Website

```
1. @browser Navigate to https://example.com/login
2. @browser Fill "#email" with "user@example.com"
3. @browser Fill "#password" with "password123"
4. @browser Click "button[type='submit']"
5. @browser Wait for ".dashboard"
6. @browser Take screenshot name="logged_in"
```

### Extract Data

```
1. @browser Navigate to https://example.com/products
2. @browser Get text from ".product-list"
3. @browser Find elements ".product-item"
4. @browser Evaluate "document.querySelectorAll('.product-item').length"
```

### Fill Form

```
1. @browser Navigate to https://example.com/contact
2. @browser Fill "#name" with "John Doe"
3. @browser Fill "#email" with "john@example.com"
4. @browser Fill "#message" with "Hello..."
5. @browser Click "button[type='submit']"
6. @browser Wait for ".success-message"
```

---

## Use Cases for AI Employee

### 1. LinkedIn Automation
- Navigate to LinkedIn
- Post updates
- Connect with people
- Extract job postings

### 2. Payment Portals
- Login to banking website
- Check transactions
- Initiate payments (with approval)
- Download statements

### 3. Social Media Posting
- Navigate to Facebook/Twitter
- Fill post content
- Click post button
- Verify posting

### 4. Data Extraction
- Scrape product prices
- Extract job listings
- Get competitor info
- Monitor websites

### 5. Form Automation
- Fill lengthy forms
- Submit applications
- Register for events
- Update profiles

---

## Troubleshooting

### Error: "Browser not found"

**Solution:** Install Playwright browsers
```bash
npx playwright install chromium
```

### Error: "Timeout exceeded"

**Solution:** 
- Increase timeout in configuration
- Check if selector is correct
- Wait for element before interacting

### Error: "Element not found"

**Solution:**
- Verify CSS selector
- Wait for element to load
- Check if page is fully loaded

### Error: "Navigation failed"

**Solution:**
- Check URL is valid
- Increase timeout
- Check network connectivity

---

## Security Considerations

1. **Never automate sensitive operations** without approval
2. **Use headless mode** for production (HEADLESS=true)
3. **Implement rate limiting** to avoid bans
4. **Respect robots.txt** and terms of service
5. **Don't store credentials** in scripts
6. **Log all actions** for audit trail

---

## Performance Tips

1. **Reuse browser instance** - Don't close after every action
2. **Use appropriate waitUntil** - networkidle is safest
3. **Batch operations** - Minimize round trips
4. **Cache screenshots** - Don't take unnecessary screenshots
5. **Close browser** when done for extended periods

---

## Files

```
mcp-browser/
├── package.json          # Dependencies
├── index.js             # Main MCP server
├── README.md            # This file
└── .gitignore          # Git ignore rules
```

---

## Development

### Run in Development

```bash
npm start
```

### Debug Mode

```bash
HEADLESS=false npm start
```

This shows the browser window for debugging.

### View Logs

Logs are sent to stderr:
```bash
npm start 2> logs.txt
```

---

## Integration with AI Employee

This MCP server integrates with the AI Employee Vault:

1. **Payment Portals** - Login and process payments
2. **Social Media** - Auto-post to LinkedIn, Facebook, Twitter
3. **Data Extraction** - Scrape websites for leads
4. **Form Filling** - Automate repetitive forms

### Example: LinkedIn Post

```
1. @browser Navigate to https://www.linkedin.com
2. @browser Click ".share-box-button"
3. @browser Fill ".share-box-feed-editor" with post content
4. @browser Click "button[aria-label*='Post']"
5. @browser Wait for ".update-post-confirmation"
6. @browser Take screenshot name="linkedin_post"
```

---

## Next Steps

After Browser MCP is working:

1. ✅ Test with Claude Code
2. ✅ Create automation workflows
3. ✅ Integrate with watchers
4. ⏭️ Build Odoo MCP
5. ⏭️ Build Social MCP

---

## References

- [MCP SDK Documentation](https://modelcontextprotocol.io/)
- [Playwright Documentation](https://playwright.dev/)
- [Official MCP Examples](https://github.com/modelcontextprotocol/servers)

---

**Status:** ✅ **Silver Tier - COMPLETE**

*Created: March 16, 2026*
