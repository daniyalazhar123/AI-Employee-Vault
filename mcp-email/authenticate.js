#!/usr/bin/env node

import { OAuth2Client } from 'google-auth-library';
import { readFile, writeFile } from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import http from 'http';
import { URL } from 'url';
import { exec } from 'child_process';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const CREDENTIALS_PATH = path.join(__dirname, '..', 'credentials.json');
const TOKEN_PATH = path.join(__dirname, 'token.json');
const SCOPES = ['https://www.googleapis.com/auth/gmail.modify'];
const PORT = 3000;

async function authenticate() {
  const credContent = await readFile(CREDENTIALS_PATH, 'utf8');
  const creds = JSON.parse(credContent);
  const { client_id, client_secret } = creds.installed;

  const oAuth2Client = new OAuth2Client(
    client_id,
    client_secret,
    `http://localhost:${PORT}/callback`
  );

  const authUrl = oAuth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: SCOPES,
  });

  console.log('Browser khul raha hai...');

  return new Promise((resolve, reject) => {
    const server = http.createServer(async (req, res) => {
      const parsedUrl = new URL(req.url, `http://localhost:${PORT}`);
      const code = parsedUrl.searchParams.get('code');

      if (code) {
        res.end('Authentication successful! Window band kar sakte ho.');
        server.close();
        const { tokens } = await oAuth2Client.getToken(code);
        await writeFile(TOKEN_PATH, JSON.stringify(tokens, null, 2));
        console.log('✅ Token save ho gaya:', TOKEN_PATH);
        resolve(tokens);
      }
    });

    server.listen(PORT, () => {
      exec(`start "" "${authUrl}"`);
      console.log('Browser mein Google account select karo...');
    });
  });
}

authenticate().catch(console.error);