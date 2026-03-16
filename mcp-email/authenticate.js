#!/usr/bin/env node

/**
 * Gmail OAuth2 Authentication Script
 * 
 * Run this first to authenticate with Gmail API
 * Creates token.json file for MCP Email Server
 * 
 * Usage:
 *   node authenticate.js
 */

import { google } from 'google-auth-library';
import { readFile, writeFile } from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import http from 'http';
import url from 'url';
import { open } from 'fs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Configuration
const CREDENTIALS_PATH = process.env.GMAIL_CREDENTIALS || path.join(__dirname, '..', 'credentials.json');
const TOKEN_PATH = process.env.GMAIL_TOKEN || path.join(__dirname, 'token.json');
const SCOPES = ['https://www.googleapis.com/auth/gmail.modify'];
const PORT = 3000;

/**
 * Get stored credentials
 */
async function getCredentials() {
  try {
    const content = await readFile(CREDENTIALS_PATH, 'utf-8');
    return JSON.parse(content);
  } catch (error) {
    console.error('Error reading credentials:', error.message);
    console.error(`Expected credentials at: ${CREDENTIALS_PATH}`);
    console.error('\nPlease download credentials.json from Google Cloud Console:');
    console.error('1. Go to https://console.cloud.google.com/');
    console.error('2. Create/select a project');
    console.error('3. Enable Gmail API');
    console.error('4. Create OAuth 2.0 credentials (Desktop app)');
    console.error('5. Download credentials.json');
    console.error(`6. Place it in: ${CREDENTIALS_PATH}`);
    process.exit(1);
  }
}

/**
 * Save token to file
 */
async function saveToken(token) {
  await writeFile(TOKEN_PATH, JSON.stringify(token, null, 2));
  console.log(`\n✅ Token saved to: ${TOKEN_PATH}`);
  console.log('You can now use the MCP Email Server!');
}

/**
 * Start local server to receive OAuth callback
 */
function startOAuthServer(oauth2Client) {
  return new Promise((resolve, reject) => {
    const server = http.createServer((req, res) => {
      try {
        const parsedUrl = url.parse(req.url, true);
        
        if (parsedUrl.pathname === '/callback' && parsedUrl.query.code) {
          const { code } = parsedUrl.query;
          
          res.writeHead(200, { 'Content-Type': 'text/html' });
          res.end(`
            <html>
              <head><title>Authentication Successful</title></head>
              <body>
                <h1>✅ Authentication Successful!</h1>
                <p>You can close this window and return to the terminal.</p>
                <script>setTimeout(() => window.close(), 3000);</script>
              </body>
            </html>
          `);
          
          oauth2Client.getToken(code, async (err, token) => {
            if (err) {
              reject(err);
              server.close();
              return;
            }
            
            oauth2Client.setCredentials(token);
            await saveToken(token);
            
            resolve();
            server.close();
          });
        } else {
          res.writeHead(404);
          res.end('Not found');
        }
      } catch (error) {
        reject(error);
        server.close();
      }
    });
    
    server.listen(PORT, () => {
      console.log(`\n🌐 Local server listening on http://localhost:${PORT}/callback`);
    });
  });
}

/**
 * Main authentication flow
 */
async function authenticate() {
  console.log('🔐 Gmail OAuth2 Authentication\n');
  console.log('This will authenticate with Gmail API and create a token file.\n');
  
  // Get credentials
  const credentials = await getCredentials();
  
  // Create OAuth2 client
  const oauth2Client = new google.auth.OAuth2(
    credentials.client_id,
    credentials.client_secret,
    credentials.redirect_uris[0]
  );
  
  // Generate auth URL
  const authUrl = oauth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: SCOPES,
    redirect_uri: credentials.redirect_uris[0]
  });
  
  console.log('📋 Step 1: Open this URL in your browser:\n');
  console.log(authUrl);
  console.log('\n📋 Step 2: Sign in with your Google account');
  console.log('📋 Step 3: Grant permissions when prompted');
  console.log('📋 Step 4: You will be redirected to localhost');
  console.log('\n⏳ Waiting for authentication...\n');
  
  // Start server and wait for callback
  try {
    await startOAuthServer(oauth2Client);
    console.log('\n✅ Authentication complete!\n');
  } catch (error) {
    console.error('\n❌ Authentication failed:', error.message);
    process.exit(1);
  }
}

// Run authentication
authenticate().catch(console.error);
