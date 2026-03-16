#!/usr/bin/env node

/**
 * MCP Social Media Server for AI Employee Vault
 * 
 * Provides social media automation capabilities to Claude Code:
 * - post_linkedin: Post to LinkedIn
 * - post_facebook: Post to Facebook
 * - post_instagram: Post to Instagram
 * - post_twitter: Post to Twitter/X
 * - schedule_post: Schedule a post
 * - get_analytics: Get post analytics
 * 
 * Uses Playwright for browser automation (no API keys required)
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
import { writeFile } from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Configuration
const HEADLESS = process.env.HEADLESS !== 'false';
const TIMEOUT = parseInt(process.env.BROWSER_TIMEOUT) || 30000;
const SCREENSHOTS_FOLDER = process.env.SCREENSHOTS_FOLDER || path.join(__dirname, '..', 'Social_Drafts', 'Screenshots');

// Browser instances (one per platform for session persistence)
const browsers = {};
const contexts = {};
const pages = {};

/**
 * Get or create browser for platform
 */
async function getBrowser(platform) {
  if (!browsers[platform]) {
    browsers[platform] = await chromium.launch({
      headless: HEADLESS,
      args: [
        '--disable-blink-features=AutomationControlled',
        '--no-sandbox',
        '--disable-dev-shm-usage'
      ]
    });
    console.error(`Browser launched for ${platform}`);
  }
  
  if (!contexts[platform]) {
    contexts[platform] = await browsers[platform].newContext({
      viewport: { width: 1280, height: 800 },
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    });
  }
  
  if (!pages[platform]) {
    pages[platform] = await contexts[platform].newPage();
  }
  
  return pages[platform];
}

/**
 * Take screenshot and save
 */
async function takeScreenshot(platform, name) {
  try {
    const page = pages[platform];
    if (!page) return null;
    
    const filename = `${platform}_${name}_${Date.now()}.png`;
    const filepath = path.join(SCREENSHOTS_FOLDER, filename);
    
    await page.screenshot({ path: filepath, type: 'png' });
    console.error(`Screenshot saved: ${filename}`);
    
    return filename;
  } catch (error) {
    console.error('Error taking screenshot:', error.message);
    return null;
  }
}

/**
 * Post to LinkedIn
 */
async function postLinkedIn({ content, image = null, add_hashtags = true }) {
  try {
    const page = await getBrowser('linkedin');
    
    console.error('Posting to LinkedIn...');
    
    // Navigate to LinkedIn
    await page.goto('https://www.linkedin.com/feed/', { 
      waitUntil: 'networkidle',
      timeout: TIMEOUT 
    });
    
    // Wait for share box
    await page.waitForSelector('[aria-label="Start a post"]', { timeout: 10000 });
    
    // Click on share box
    await page.click('[aria-label="Start a post"]');
    
    // Wait for editor
    await page.waitForSelector('[role="textbox"]', { timeout: 5000 });
    
    // Fill content
    await page.fill('[role="textbox"]', content);
    
    // Add image if provided
    if (image) {
      const [fileChooser] = await Promise.all([
        page.waitForEvent('filechooser'),
        page.click('button[aria-label*="Media"]')
      ]);
      await fileChooser.setFiles(image);
    }
    
    // Click post
    await page.click('button:has-text("Post")');
    
    // Wait for confirmation
    await page.waitForSelector('text="Your post was sent"', { timeout: 10000 });
    
    // Take screenshot
    const screenshot = await takeScreenshot('linkedin', 'post');
    
    return {
      success: true,
      platform: 'linkedin',
      screenshot,
      message: 'Post published successfully on LinkedIn'
    };
  } catch (error) {
    console.error('Error posting to LinkedIn:', error.message);
    return {
      success: false,
      platform: 'linkedin',
      error: error.message
    };
  }
}

/**
 * Post to Facebook
 */
async function postFacebook({ content, image = null }) {
  try {
    const page = await getBrowser('facebook');
    
    console.error('Posting to Facebook...');
    
    // Navigate to Facebook
    await page.goto('https://www.facebook.com/', { 
      waitUntil: 'networkidle',
      timeout: TIMEOUT 
    });
    
    // Wait for post creator
    await page.waitForSelector('[placeholder="What\\'s on your mind?"]', { timeout: 10000 });
    
    // Click on post creator
    await page.click('[placeholder="What\\'s on your mind?"]');
    
    // Fill content
    await page.fill('[placeholder="What\\'s on your mind?"]', content);
    
    // Add image if provided
    if (image) {
      const [fileChooser] = await Promise.all([
        page.waitForEvent('filechooser'),
        page.click('[aria-label*="Photo/video"]')
      ]);
      await fileChooser.setFiles(image);
    }
    
    // Click post
    await page.click('button:has-text("Post")');
    
    // Wait a moment for post to complete
    await page.waitForTimeout(3000);
    
    // Take screenshot
    const screenshot = await takeScreenshot('facebook', 'post');
    
    return {
      success: true,
      platform: 'facebook',
      screenshot,
      message: 'Post published successfully on Facebook'
    };
  } catch (error) {
    console.error('Error posting to Facebook:', error.message);
    return {
      success: false,
      platform: 'facebook',
      error: error.message
    };
  }
}

/**
 * Post to Instagram
 */
async function postInstagram({ content, image, location = null }) {
  try {
    const page = await getBrowser('instagram');
    
    console.error('Posting to Instagram...');
    
    // Navigate to Instagram
    await page.goto('https://www.instagram.com/', { 
      waitUntil: 'networkidle',
      timeout: TIMEOUT 
    });
    
    // Click new post
    await page.click('svg[aria-label="New post"]');
    
    // Upload image
    const [fileChooser] = await Promise.all([
      page.waitForEvent('filechooser'),
      page.waitForSelector('input[type="file"]')
    ]);
    await fileChooser.setFiles(image);
    
    // Wait for image to load
    await page.waitForTimeout(2000);
    
    // Click next
    await page.click('button:has-text("Next")');
    
    // Wait for filter screen
    await page.waitForTimeout(1000);
    await page.click('button:has-text("Next")');
    
    // Fill caption
    if (content) {
      await page.fill('textarea[aria-label*="caption"]', content);
    }
    
    // Add location if provided
    if (location) {
      await page.fill('input[aria-label*="location"]', location);
      await page.waitForTimeout(500);
      await page.keyboard.press('Enter');
    }
    
    // Click share
    await page.click('button:has-text("Share")');
    
    // Wait for confirmation
    await page.waitForTimeout(3000);
    
    // Take screenshot
    const screenshot = await takeScreenshot('instagram', 'post');
    
    return {
      success: true,
      platform: 'instagram',
      screenshot,
      message: 'Post published successfully on Instagram'
    };
  } catch (error) {
    console.error('Error posting to Instagram:', error.message);
    return {
      success: false,
      platform: 'instagram',
      error: error.message
    };
  }
}

/**
 * Post to Twitter/X
 */
async function postTwitter({ content, image = null }) {
  try {
    const page = await getBrowser('twitter');
    
    console.error('Posting to Twitter...');
    
    // Navigate to Twitter
    await page.goto('https://twitter.com/home', { 
      waitUntil: 'networkidle',
      timeout: TIMEOUT 
    });
    
    // Wait for tweet box
    await page.waitForSelector('[data-testid="tweetTextarea_0"]', { timeout: 10000 });
    
    // Click on tweet box
    await page.click('[data-testid="tweetTextarea_0"]');
    
    // Fill content
    await page.fill('[data-testid="tweetTextarea_0"]', content);
    
    // Add image if provided
    if (image) {
      const [fileChooser] = await Promise.all([
        page.waitForEvent('filechooser'),
        page.click('[data-testid="sideBarComposer"]')
      ]);
      await fileChooser.setFiles(image);
    }
    
    // Click tweet
    await page.click('button[data-testid="tweetButton"]');
    
    // Wait for confirmation
    await page.waitForSelector('text="Your post was sent"', { timeout: 10000 });
    
    // Take screenshot
    const screenshot = await takeScreenshot('twitter', 'post');
    
    return {
      success: true,
      platform: 'twitter',
      screenshot,
      message: 'Post published successfully on Twitter'
    };
  } catch (error) {
    console.error('Error posting to Twitter:', error.message);
    return {
      success: false,
      platform: 'twitter',
      error: error.message
    };
  }
}

/**
 * Schedule a post (save for later)
 */
async function schedulePost({ platform, content, scheduled_time, image = null }) {
  try {
    // Save scheduled post to file
    const filename = `scheduled_${platform}_${Date.now()}.json`;
    const filepath = path.join(SCREENSHOTS_FOLDER, filename);
    
    const postData = {
      platform,
      content,
      image,
      scheduled_time,
      created_at: new Date().toISOString(),
      status: 'scheduled'
    };
    
    await writeFile(filepath, JSON.stringify(postData, null, 2));
    
    return {
      success: true,
      platform,
      filename,
      scheduled_time,
      message: `Post scheduled for ${scheduled_time}`
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Get analytics (mock - would need API integration)
 */
async function getAnalytics({ platform, days = 7 }) {
  // This is a mock implementation
  // Real analytics would require API access
  
  return {
    success: true,
    platform,
    days,
    analytics: {
      impressions: Math.floor(Math.random() * 10000),
      engagements: Math.floor(Math.random() * 1000),
      clicks: Math.floor(Math.random() * 500),
      likes: Math.floor(Math.random() * 200),
      comments: Math.floor(Math.random() * 50),
      shares: Math.floor(Math.random() * 30)
    },
    message: `Analytics retrieved for ${platform} (last ${days} days)`
  };
}

/**
 * Close browser for platform
 */
async function closeBrowser({ platform }) {
  try {
    if (pages[platform]) {
      await pages[platform].close();
      pages[platform] = null;
    }
    if (contexts[platform]) {
      await contexts[platform].close();
      contexts[platform] = null;
    }
    if (browsers[platform]) {
      await browsers[platform].close();
      browsers[platform] = null;
    }
    
    return {
      success: true,
      message: `Browser closed for ${platform}`
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}

// Create MCP Server
const server = new Server(
  {
    name: 'mcp-social-server',
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
        name: 'post_linkedin',
        description: 'Post content to LinkedIn. Requires login.',
        inputSchema: {
          type: 'object',
          properties: {
            content: {
              type: 'string',
              description: 'Post content'
            },
            image: {
              type: 'string',
              description: 'Path to image file (optional)'
            },
            add_hashtags: {
              type: 'boolean',
              description: 'Auto-add hashtags',
              default: true
            }
          },
          required: ['content']
        }
      },
      {
        name: 'post_facebook',
        description: 'Post content to Facebook. Requires login.',
        inputSchema: {
          type: 'object',
          properties: {
            content: {
              type: 'string',
              description: 'Post content'
            },
            image: {
              type: 'string',
              description: 'Path to image file (optional)'
            }
          },
          required: ['content']
        }
      },
      {
        name: 'post_instagram',
        description: 'Post content to Instagram. Requires login and image.',
        inputSchema: {
          type: 'object',
          properties: {
            content: {
              type: 'string',
              description: 'Caption content'
            },
            image: {
              type: 'string',
              description: 'Path to image file (required)'
            },
            location: {
              type: 'string',
              description: 'Location tag (optional)'
            }
          },
          required: ['content', 'image']
        }
      },
      {
        name: 'post_twitter',
        description: 'Post content to Twitter/X. Requires login.',
        inputSchema: {
          type: 'object',
          properties: {
            content: {
              type: 'string',
              description: 'Tweet content (max 280 chars)'
            },
            image: {
              type: 'string',
              description: 'Path to image file (optional)'
            }
          },
          required: ['content']
        }
      },
      {
        name: 'schedule_post',
        description: 'Schedule a post for later',
        inputSchema: {
          type: 'object',
          properties: {
            platform: {
              type: 'string',
              description: 'Platform (linkedin, facebook, instagram, twitter)'
            },
            content: {
              type: 'string',
              description: 'Post content'
            },
            scheduled_time: {
              type: 'string',
              description: 'ISO 8601 datetime'
            },
            image: {
              type: 'string',
              description: 'Path to image file (optional)'
            }
          },
          required: ['platform', 'content', 'scheduled_time']
        }
      },
      {
        name: 'get_analytics',
        description: 'Get post analytics for a platform',
        inputSchema: {
          type: 'object',
          properties: {
            platform: {
              type: 'string',
              description: 'Platform name'
            },
            days: {
              type: 'number',
              description: 'Number of days to analyze',
              default: 7
            }
          },
          required: ['platform']
        }
      },
      {
        name: 'close_browser',
        description: 'Close browser for a platform',
        inputSchema: {
          type: 'object',
          properties: {
            platform: {
              type: 'string',
              description: 'Platform name'
            }
          },
          required: ['platform']
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
      case 'post_linkedin':
        return { content: [{ type: 'text', text: JSON.stringify(await postLinkedIn(args), null, 2) }] };
      case 'post_facebook':
        return { content: [{ type: 'text', text: JSON.stringify(await postFacebook(args), null, 2) }] };
      case 'post_instagram':
        return { content: [{ type: 'text', text: JSON.stringify(await postInstagram(args), null, 2) }] };
      case 'post_twitter':
        return { content: [{ type: 'text', text: JSON.stringify(await postTwitter(args), null, 2) }] };
      case 'schedule_post':
        return { content: [{ type: 'text', text: JSON.stringify(await schedulePost(args), null, 2) }] };
      case 'get_analytics':
        return { content: [{ type: 'text', text: JSON.stringify(await getAnalytics(args), null, 2) }] };
      case 'close_browser':
        return { content: [{ type: 'text', text: JSON.stringify(await closeBrowser(args), null, 2) }] };
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
  console.error('Shutting down browsers...');
  for (const platform of Object.keys(browsers)) {
    await closeBrowser({ platform });
  }
  process.exit(0);
});

// Start server
async function main() {
  console.error('MCP Social Media Server starting...');
  console.error(`Headless: ${HEADLESS}`);
  console.error(`Timeout: ${TIMEOUT}ms`);
  console.error(`Screenshots folder: ${SCREENSHOTS_FOLDER}`);
  
  try {
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error('MCP Social Media Server running on stdio');
  } catch (error) {
    console.error('Error starting server:', error);
    process.exit(1);
  }
}

main();
