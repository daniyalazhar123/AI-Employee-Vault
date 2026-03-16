#!/usr/bin/env node

/**
 * MCP Browser Server for AI Employee Vault
 * 
 * Provides browser automation capabilities to Claude Code:
 * - navigate: Go to a URL
 * - click: Click on an element
 * - fill: Fill input fields
 * - screenshot: Take screenshots
 * - evaluate: Execute JavaScript
 * - get_text: Extract text from elements
 * 
 * Usage:
 *   node index.js
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { chromium } from 'playwright';

// Browser instance
let browser;
let currentContext;
let currentPage;

// Configuration
const HEADLESS = process.env.HEADLESS !== 'false'; // Default to headless
const TIMEOUT = parseInt(process.env.BROWSER_TIMEOUT) || 30000; // 30 seconds

/**
 * Initialize browser
 */
async function initBrowser() {
  if (!browser) {
    browser = await chromium.launch({
      headless: HEADLESS,
      args: [
        '--disable-blink-features=AutomationControlled',
        '--no-sandbox',
        '--disable-dev-shm-usage'
      ]
    });
    console.error('Browser launched');
  }
  
  if (!currentContext) {
    currentContext = await browser.newContext({
      viewport: { width: 1280, height: 800 },
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    });
    console.error('Browser context created');
  }
  
  if (!currentPage) {
    currentPage = await currentContext.newPage();
    console.error('Browser page created');
  }
  
  return { context: currentContext, page: currentPage };
}

/**
 * Navigate to a URL
 */
async function navigate({ url, waitUntil = 'networkidle' }) {
  try {
    const { page } = await initBrowser();
    
    console.error(`Navigating to: ${url}`);
    
    await page.goto(url, { 
      waitUntil,
      timeout: TIMEOUT 
    });
    
    return {
      success: true,
      url: page.url(),
      title: await page.title(),
      message: `Navigated to ${url}`
    };
  } catch (error) {
    console.error('Error navigating:', error.message);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Click on an element
 */
async function click({ selector, timeout = 5000 }) {
  try {
    const { page } = await initBrowser();
    
    console.error(`Clicking: ${selector}`);
    
    await page.click(selector, { timeout });
    
    return {
      success: true,
      message: `Clicked ${selector}`
    };
  } catch (error) {
    console.error('Error clicking:', error.message);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Fill input field
 */
async function fill({ selector, value, timeout = 5000 }) {
  try {
    const { page } = await initBrowser();
    
    console.error(`Filling ${selector} with: ${value.substring(0, 50)}...`);
    
    await page.fill(selector, value, { timeout });
    
    return {
      success: true,
      message: `Filled ${selector}`
    };
  } catch (error) {
    console.error('Error filling:', error.message);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Type text (like fill but with delays)
 */
async function type({ selector, value, delay = 50 }) {
  try {
    const { page } = await initBrowser();
    
    console.error(`Typing into ${selector}`);
    
    await page.type(selector, value, { delay });
    
    return {
      success: true,
      message: `Typed into ${selector}`
    };
  } catch (error) {
    console.error('Error typing:', error.message);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Take a screenshot
 */
async function screenshot({ name = 'screenshot', fullPage = false }) {
  try {
    const { page } = await initBrowser();
    
    console.error(`Taking screenshot: ${name}`);
    
    const screenshot = await page.screenshot({ 
      fullPage,
      type: 'png'
    });
    
    // Convert to base64 for display
    const base64 = screenshot.toString('base64');
    
    return {
      success: true,
      name: `${name}.png`,
      base64: base64.substring(0, 100) + '...', // Truncate for response
      message: `Screenshot saved as ${name}.png`
    };
  } catch (error) {
    console.error('Error taking screenshot:', error.message);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Get text content from element
 */
async function getText({ selector }) {
  try {
    const { page } = await initBrowser();
    
    console.error(`Getting text from: ${selector}`);
    
    const text = await page.textContent(selector);
    
    return {
      success: true,
      selector,
      text: text.substring(0, 500), // Limit response length
      message: `Retrieved text from ${selector}`
    };
  } catch (error) {
    console.error('Error getting text:', error.message);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Get HTML content from element
 */
async function getHTML({ selector = 'body' }) {
  try {
    const { page } = await initBrowser();
    
    console.error(`Getting HTML from: ${selector}`);
    
    const html = await page.innerHTML(selector);
    
    return {
      success: true,
      selector,
      html: html.substring(0, 1000), // Limit response length
      message: `Retrieved HTML from ${selector}`
    };
  } catch (error) {
    console.error('Error getting HTML:', error.message);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Execute JavaScript on page
 */
async function evaluate({ script }) {
  try {
    const { page } = await initBrowser();
    
    console.error(`Evaluating script: ${script.substring(0, 100)}...`);
    
    const result = await page.evaluate(script);
    
    return {
      success: true,
      result: typeof result === 'object' ? JSON.stringify(result) : result,
      message: 'Script executed successfully'
    };
  } catch (error) {
    console.error('Error evaluating script:', error.message);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Wait for element
 */
async function waitFor({ selector, state = 'visible', timeout = 5000 }) {
  try {
    const { page } = await initBrowser();
    
    console.error(`Waiting for ${selector} (${state})`);
    
    await page.waitForSelector(selector, { state, timeout });
    
    return {
      success: true,
      message: `Element ${selector} is ${state}`
    };
  } catch (error) {
    console.error('Error waiting:', error.message);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Wait for navigation
 */
async function waitForNavigation({ timeout = 30000, waitUntil = 'networkidle' }) {
  try {
    const { page } = await initBrowser();
    
    console.error('Waiting for navigation');
    
    await page.waitForNavigation({ timeout, waitUntil });
    
    return {
      success: true,
      url: page.url(),
      title: await page.title(),
      message: 'Navigation complete'
    };
  } catch (error) {
    console.error('Error waiting for navigation:', error.message);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Press keyboard key
 */
async function press({ key }) {
  try {
    const { page } = await initBrowser();
    
    console.error(`Pressing key: ${key}`);
    
    await page.keyboard.press(key);
    
    return {
      success: true,
      message: `Pressed ${key}`
    };
  } catch (error) {
    console.error('Error pressing key:', error.message);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Scroll page
 */
async function scroll({ x = 0, y = 0 }) {
  try {
    const { page } = await initBrowser();
    
    console.error(`Scrolling to ${x}, ${y}`);
    
    await page.evaluate((scrollX, scrollY) => {
      window.scrollTo(scrollX, scrollY);
    }, x, y);
    
    return {
      success: true,
      message: `Scrolled to ${x}, ${y}`
    };
  } catch (error) {
    console.error('Error scrolling:', error.message);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Get page info
 */
async function getPageInfo() {
  try {
    const { page } = await initBrowser();
    
    const info = await page.evaluate(() => {
      return {
        url: window.location.href,
        title: document.title,
        width: window.innerWidth,
        height: window.innerHeight
      };
    });
    
    return {
      success: true,
      info,
      message: 'Page info retrieved'
    };
  } catch (error) {
    console.error('Error getting page info:', error.message);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Find elements
 */
async function findElements({ selector }) {
  try {
    const { page } = await initBrowser();
    
    console.error(`Finding elements: ${selector}`);
    
    const elements = await page.$$(selector);
    
    return {
      success: true,
      count: elements.length,
      message: `Found ${elements.length} elements matching ${selector}`
    };
  } catch (error) {
    console.error('Error finding elements:', error.message);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Close browser
 */
async function closeBrowser() {
  try {
    if (currentPage) {
      await currentPage.close();
      currentPage = null;
    }
    if (currentContext) {
      await currentContext.close();
      currentContext = null;
    }
    if (browser) {
      await browser.close();
      browser = null;
    }
    
    return {
      success: true,
      message: 'Browser closed'
    };
  } catch (error) {
    console.error('Error closing browser:', error.message);
    return {
      success: false,
      error: error.message
    };
  }
}

// Create MCP Server
const server = new Server(
  {
    name: 'mcp-browser-server',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'navigate',
        description: 'Navigate to a URL in the browser',
        inputSchema: {
          type: 'object',
          properties: {
            url: {
              type: 'string',
              description: 'URL to navigate to'
            },
            waitUntil: {
              type: 'string',
              description: 'When to consider navigation complete (load, domcontentloaded, networkidle, commit)',
              default: 'networkidle'
            }
          },
          required: ['url']
        }
      },
      {
        name: 'click',
        description: 'Click on an element',
        inputSchema: {
          type: 'object',
          properties: {
            selector: {
              type: 'string',
              description: 'CSS selector for element to click'
            },
            timeout: {
              type: 'number',
              description: 'Timeout in milliseconds',
              default: 5000
            }
          },
          required: ['selector']
        }
      },
      {
        name: 'fill',
        description: 'Fill an input field with text',
        inputSchema: {
          type: 'object',
          properties: {
            selector: {
              type: 'string',
              description: 'CSS selector for input field'
            },
            value: {
              type: 'string',
              description: 'Text to fill'
            },
            timeout: {
              type: 'number',
              description: 'Timeout in milliseconds',
              default: 5000
            }
          },
          required: ['selector', 'value']
        }
      },
      {
        name: 'type',
        description: 'Type text into an input field (with delays)',
        inputSchema: {
          type: 'object',
          properties: {
            selector: {
              type: 'string',
              description: 'CSS selector for input field'
            },
            value: {
              type: 'string',
              description: 'Text to type'
            },
            delay: {
              type: 'number',
              description: 'Delay between keystrokes in ms',
              default: 50
            }
          },
          required: ['selector', 'value']
        }
      },
      {
        name: 'screenshot',
        description: 'Take a screenshot of the current page',
        inputSchema: {
          type: 'object',
          properties: {
            name: {
              type: 'string',
              description: 'Filename for screenshot',
              default: 'screenshot'
            },
            fullPage: {
              type: 'boolean',
              description: 'Capture full page scroll',
              default: false
            }
          }
        }
      },
      {
        name: 'get_text',
        description: 'Get text content from an element',
        inputSchema: {
          type: 'object',
          properties: {
            selector: {
              type: 'string',
              description: 'CSS selector for element'
            }
          },
          required: ['selector']
        }
      },
      {
        name: 'get_html',
        description: 'Get HTML content from an element',
        inputSchema: {
          type: 'object',
          properties: {
            selector: {
              type: 'string',
              description: 'CSS selector for element',
              default: 'body'
            }
          }
        }
      },
      {
        name: 'evaluate',
        description: 'Execute JavaScript on the page',
        inputSchema: {
          type: 'object',
          properties: {
            script: {
              type: 'string',
              description: 'JavaScript code to execute'
            }
          },
          required: ['script']
        }
      },
      {
        name: 'wait_for',
        description: 'Wait for an element to appear',
        inputSchema: {
          type: 'object',
          properties: {
            selector: {
              type: 'string',
              description: 'CSS selector to wait for'
            },
            state: {
              type: 'string',
              description: 'Element state (visible, hidden, attached, detached)',
              default: 'visible'
            },
            timeout: {
              type: 'number',
              description: 'Timeout in milliseconds',
              default: 5000
            }
          },
          required: ['selector']
        }
      },
      {
        name: 'press',
        description: 'Press a keyboard key',
        inputSchema: {
          type: 'object',
          properties: {
            key: {
              type: 'string',
              description: 'Key to press (e.g., "Enter", "Tab", "ArrowDown")'
            }
          },
          required: ['key']
        }
      },
      {
        name: 'scroll',
        description: 'Scroll the page',
        inputSchema: {
          type: 'object',
          properties: {
            x: {
              type: 'number',
              description: 'Horizontal scroll position',
              default: 0
            },
            y: {
              type: 'number',
              description: 'Vertical scroll position',
              default: 0
            }
          }
        }
      },
      {
        name: 'get_page_info',
        description: 'Get current page information (URL, title, dimensions)',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },
      {
        name: 'find_elements',
        description: 'Find elements matching a CSS selector',
        inputSchema: {
          type: 'object',
          properties: {
            selector: {
              type: 'string',
              description: 'CSS selector to match'
            }
          },
          required: ['selector']
        }
      },
      {
        name: 'close',
        description: 'Close the browser',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      }
    ]
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  
  try {
    switch (name) {
      case 'navigate':
        return { content: [{ type: 'text', text: JSON.stringify(await navigate(args), null, 2) }] };
      case 'click':
        return { content: [{ type: 'text', text: JSON.stringify(await click(args), null, 2) }] };
      case 'fill':
        return { content: [{ type: 'text', text: JSON.stringify(await fill(args), null, 2) }] };
      case 'type':
        return { content: [{ type: 'text', text: JSON.stringify(await type(args), null, 2) }] };
      case 'screenshot':
        return { content: [{ type: 'text', text: JSON.stringify(await screenshot(args), null, 2) }] };
      case 'get_text':
        return { content: [{ type: 'text', text: JSON.stringify(await getText(args), null, 2) }] };
      case 'get_html':
        return { content: [{ type: 'text', text: JSON.stringify(await getHTML(args), null, 2) }] };
      case 'evaluate':
        return { content: [{ type: 'text', text: JSON.stringify(await evaluate(args), null, 2) }] };
      case 'wait_for':
        return { content: [{ type: 'text', text: JSON.stringify(await waitFor(args), null, 2) }] };
      case 'press':
        return { content: [{ type: 'text', text: JSON.stringify(await press(args), null, 2) }] };
      case 'scroll':
        return { content: [{ type: 'text', text: JSON.stringify(await scroll(args), null, 2) }] };
      case 'get_page_info':
        return { content: [{ type: 'text', text: JSON.stringify(await getPageInfo(), null, 2) }] };
      case 'find_elements':
        return { content: [{ type: 'text', text: JSON.stringify(await findElements(args), null, 2) }] };
      case 'close':
        return { content: [{ type: 'text', text: JSON.stringify(await closeBrowser(), null, 2) }] };
      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    return {
      content: [{ type: 'text', text: JSON.stringify({ success: false, error: error.message }, null, 2) }],
      isError: true
    };
  }
});

// Handle graceful shutdown
process.on('SIGINT', async () => {
  console.error('Shutting down browser...');
  await closeBrowser();
  process.exit(0);
});

// Start server
async function main() {
  console.error('MCP Browser Server starting...');
  console.error(`Headless: ${HEADLESS}`);
  console.error(`Timeout: ${TIMEOUT}ms`);
  
  try {
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error('MCP Browser Server running on stdio');
    
    // Pre-initialize browser
    await initBrowser();
    console.error('Browser pre-initialized');
  } catch (error) {
    console.error('Error starting server:', error);
    process.exit(1);
  }
}

main();
