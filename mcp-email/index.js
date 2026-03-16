#!/usr/bin/env node

/**
 * MCP Email Server for AI Employee Vault
 * 
 * Provides email capabilities to Claude Code:
 * - send_email: Send emails via Gmail
 * - create_draft: Create email drafts
 * - search_emails: Search and read emails
 * - mark_read: Mark emails as read
 * 
 * Usage:
 *   node index.js
 * 
 * Configuration:
 *   Set GMAIL_CREDENTIALS environment variable to path of credentials.json
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { readFile } from 'fs/promises';
import { google } from 'googleapis';
import path from 'path';
import { fileURLToPath } from 'url';

// Get directory name in ES modules
const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Configuration
const CREDENTIALS_PATH = process.env.GMAIL_CREDENTIALS || path.join(__dirname, '..', 'credentials.json');
const TOKEN_PATH = process.env.GMAIL_TOKEN || path.join(__dirname, 'token.json');
const SCOPES = ['https://www.googleapis.com/auth/gmail.modify'];

// Gmail API client
let oauth2Client;
let gmail;

/**
 * Load or refresh OAuth2 credentials
 */
async function getAuthClient() {
  try {
    // Read credentials
    const credentialsContent = await readFile(CREDENTIALS_PATH, 'utf-8');
    const credentials = JSON.parse(credentialsContent);
    
    // Create OAuth2 client
    oauth2Client = new google.auth.OAuth2(
      credentials.client_id,
      credentials.client_secret,
      credentials.redirect_uris[0]
    );
    
    // Try to load existing token
    try {
      const tokenContent = await readFile(TOKEN_PATH, 'utf-8');
      const token = JSON.parse(tokenContent);
      oauth2Client.setCredentials(token);
      
      // Refresh if expired
      if (oauth2Client.credentials.expiry_date) {
        const expiry = new Date(oauth2Client.credentials.expiry_date);
        const now = new Date();
        if (expiry <= now) {
          await oauth2Client.refreshAccessToken();
          await saveToken(oauth2Client.credentials);
        }
      }
    } catch (err) {
      // No token exists, need to authenticate
      console.error('No token found. Please authenticate first.');
      console.error('Run: node authenticate.js');
      throw new Error('Authentication required');
    }
    
    return oauth2Client;
  } catch (error) {
    console.error('Error loading credentials:', error.message);
    throw error;
  }
}

/**
 * Save token to file
 */
async function saveToken(credentials) {
  const fs = await import('fs/promises');
  await fs.writeFile(TOKEN_PATH, JSON.stringify(credentials, null, 2));
  console.log('Token saved to', TOKEN_PATH);
}

/**
 * Initialize Gmail API client
 */
async function initGmail() {
  const auth = await getAuthClient();
  gmail = google.gmail({ version: 'v1', auth });
  return gmail;
}

/**
 * Send an email
 */
async function sendEmail({ to, subject, body, cc = null, bcc = null, attachments = [] }) {
  try {
    const auth = await getAuthClient();
    const gmailClient = google.gmail({ version: 'v1', auth });
    
    // Create email message
    const message = [
      `To: ${to}`,
      cc ? `Cc: ${cc}` : '',
      bcc ? `Bcc: ${bcc}` : '',
      `Subject: ${subject}`,
      'MIME-Version: 1.0',
      'Content-Type: text/plain; charset="utf-8"',
      '',
      body
    ].filter(line => line).join('\n');
    
    // Encode message
    const encodedMessage = Buffer.from(message)
      .toString('base64')
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=+$/, '');
    
    // Send email
    const response = await gmailClient.users.messages.send({
      userId: 'me',
      requestBody: {
        raw: encodedMessage
      }
    });
    
    return {
      success: true,
      messageId: response.data.id,
      threadId: response.data.threadId,
      message: `Email sent successfully to ${to}`
    };
  } catch (error) {
    console.error('Error sending email:', error.message);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Create an email draft
 */
async function createDraft({ to, subject, body, cc = null }) {
  try {
    const auth = await getAuthClient();
    const gmailClient = google.gmail({ version: 'v1', auth });
    
    // Create email message
    const message = [
      `To: ${to}`,
      cc ? `Cc: ${cc}` : '',
      `Subject: ${subject}`,
      'MIME-Version: 1.0',
      'Content-Type: text/plain; charset="utf-8"',
      '',
      body
    ].filter(line => line).join('\n');
    
    // Encode message
    const encodedMessage = Buffer.from(message)
      .toString('base64')
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=+$/, '');
    
    // Create draft
    const response = await gmailClient.users.drafts.create({
      userId: 'me',
      requestBody: {
        message: {
          raw: encodedMessage
        }
      }
    });
    
    return {
      success: true,
      draftId: response.data.id,
      messageId: response.data.message.id,
      message: `Draft created successfully`
    };
  } catch (error) {
    console.error('Error creating draft:', error.message);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Search and read emails
 */
async function searchEmails({ query = '', maxResults = 10 }) {
  try {
    const auth = await getAuthClient();
    const gmailClient = google.gmail({ version: 'v1', auth });
    
    // Search emails
    const response = await gmailClient.users.messages.list({
      userId: 'me',
      q: query,
      maxResults: maxResults
    });
    
    const messages = response.data.messages || [];
    
    if (messages.length === 0) {
      return {
        success: true,
        count: 0,
        emails: [],
        message: 'No emails found'
      };
    }
    
    // Get full message details
    const emails = [];
    for (const msg of messages.slice(0, 5)) { // Limit to 5 full messages
      const fullMessage = await gmailClient.users.messages.get({
        userId: 'me',
        id: msg.id,
        format: 'metadata',
        metadataHeaders: ['From', 'To', 'Subject', 'Date']
      });
      
      const headers = fullMessage.data.payload.headers;
      const email = {
        id: msg.id,
        threadId: fullMessage.data.threadId,
        from: headers.find(h => h.name === 'From')?.value || 'Unknown',
        to: headers.find(h => h.name === 'To')?.value || 'Unknown',
        subject: headers.find(h => h.name === 'Subject')?.value || 'No Subject',
        date: headers.find(h => h.name === 'Date')?.value || 'Unknown',
        snippet: fullMessage.data.snippet
      };
      
      emails.push(email);
    }
    
    return {
      success: true,
      count: messages.length,
      emails: emails,
      message: `Found ${messages.length} emails`
    };
  } catch (error) {
    console.error('Error searching emails:', error.message);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Mark email as read
 */
async function markAsRead({ messageId }) {
  try {
    const auth = await getAuthClient();
    const gmailClient = google.gmail({ version: 'v1', auth });
    
    // Remove UNREAD label
    await gmailClient.users.messages.modify({
      userId: 'me',
      id: messageId,
      requestBody: {
        removeLabelIds: ['UNREAD']
      }
    });
    
    return {
      success: true,
      message: `Message ${messageId} marked as read`
    };
  } catch (error) {
    console.error('Error marking as read:', error.message);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Get email content
 */
async function getEmailContent({ messageId }) {
  try {
    const auth = await getAuthClient();
    const gmailClient = google.gmail({ version: 'v1', auth });
    
    const response = await gmailClient.users.messages.get({
      userId: 'me',
      id: messageId,
      format: 'full'
    });
    
    // Extract body
    let body = '';
    if (response.data.payload.parts) {
      for (const part of response.data.payload.parts) {
        if (part.mimeType === 'text/plain' && part.body.data) {
          body = Buffer.from(part.body.data, 'base64').toString('utf-8');
          break;
        }
      }
    } else if (response.data.payload.body.data) {
      body = Buffer.from(response.data.payload.body.data, 'base64').toString('utf-8');
    }
    
    // Extract headers
    const headers = response.data.payload.headers;
    
    return {
      success: true,
      email: {
        id: response.data.id,
        threadId: response.data.threadId,
        from: headers.find(h => h.name === 'From')?.value || 'Unknown',
        to: headers.find(h => h.name === 'To')?.value || 'Unknown',
        subject: headers.find(h => h.name === 'Subject')?.value || 'No Subject',
        date: headers.find(h => h.name === 'Date')?.value || 'Unknown',
        body: body,
        snippet: response.data.snippet
      }
    };
  } catch (error) {
    console.error('Error getting email content:', error.message);
    return {
      success: false,
      error: error.message
    };
  }
}

// Create MCP Server
const server = new Server(
  {
    name: 'mcp-email-server',
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
        name: 'send_email',
        description: 'Send an email via Gmail. Requires authentication.',
        inputSchema: {
          type: 'object',
          properties: {
            to: {
              type: 'string',
              description: 'Recipient email address'
            },
            subject: {
              type: 'string',
              description: 'Email subject'
            },
            body: {
              type: 'string',
              description: 'Email body text'
            },
            cc: {
              type: 'string',
              description: 'CC email address (optional)'
            },
            bcc: {
              type: 'string',
              description: 'BCC email address (optional)'
            }
          },
          required: ['to', 'subject', 'body']
        }
      },
      {
        name: 'create_draft',
        description: 'Create an email draft in Gmail. Does not send immediately.',
        inputSchema: {
          type: 'object',
          properties: {
            to: {
              type: 'string',
              description: 'Recipient email address'
            },
            subject: {
              type: 'string',
              description: 'Email subject'
            },
            body: {
              type: 'string',
              description: 'Email body text'
            },
            cc: {
              type: 'string',
              description: 'CC email address (optional)'
            }
          },
          required: ['to', 'subject', 'body']
        }
      },
      {
        name: 'search_emails',
        description: 'Search and retrieve emails from Gmail',
        inputSchema: {
          type: 'object',
          properties: {
            query: {
              type: 'string',
              description: 'Gmail search query (e.g., "is:unread", "from:john", "subject:invoice")'
            },
            maxResults: {
              type: 'number',
              description: 'Maximum number of results (default: 10)'
            }
          },
          required: ['query']
        }
      },
      {
        name: 'get_email',
        description: 'Get full content of a specific email by ID',
        inputSchema: {
          type: 'object',
          properties: {
            messageId: {
              type: 'string',
              description: 'Gmail message ID'
            }
          },
          required: ['messageId']
        }
      },
      {
        name: 'mark_read',
        description: 'Mark an email as read',
        inputSchema: {
          type: 'object',
          properties: {
            messageId: {
              type: 'string',
              description: 'Gmail message ID'
            }
          },
          required: ['messageId']
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
      case 'send_email':
        return { content: [{ type: 'text', text: JSON.stringify(await sendEmail(args), null, 2) }] };
      
      case 'create_draft':
        return { content: [{ type: 'text', text: JSON.stringify(await createDraft(args), null, 2) }] };
      
      case 'search_emails':
        return { content: [{ type: 'text', text: JSON.stringify(await searchEmails(args), null, 2) }] };
      
      case 'get_email':
        return { content: [{ type: 'text', text: JSON.stringify(await getEmailContent(args), null, 2) }] };
      
      case 'mark_read':
        return { content: [{ type: 'text', text: JSON.stringify(await markAsRead(args), null, 2) }] };
      
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

// Start server
async function main() {
  console.error('MCP Email Server starting...');
  console.error(`Credentials path: ${CREDENTIALS_PATH}`);
  console.error(`Token path: ${TOKEN_PATH}`);
  
  try {
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error('MCP Email Server running on stdio');
  } catch (error) {
    console.error('Error starting server:', error);
    process.exit(1);
  }
}

main();
