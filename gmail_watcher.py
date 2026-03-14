import os
import time
import pickle
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import subprocess

# Paths
VAULT_PATH = Path(__file__).parent
NEEDS_ACTION = VAULT_PATH / "Needs_Action"
PENDING_APPROVAL = VAULT_PATH / "Pending_Approval"
CREDENTIALS_FILE = VAULT_PATH / "credentials.json"
TOKEN_FILE = VAULT_PATH / "token.pickle"

# Gmail scope (modify for draft creation)
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def get_gmail_service():
    creds = None
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)

def check_emails(service, processed_ids):
    results = service.users().messages().list(
        userId='me',
        q='is:unread',
        maxResults=5
    ).execute()
   
    messages = results.get('messages', [])
    new_messages = []
   
    for msg in messages:
        if msg['id'] not in processed_ids:
            new_messages.append(msg)
   
    return new_messages

def create_action_file(service, message):
    msg = service.users().messages().get(
        userId='me',
        id=message['id'],
        format='metadata',
        metadataHeaders=['From', 'Subject', 'Date']
    ).execute()
   
    headers = {}
    for h in msg['payload']['headers']:
        headers[h['name']] = h['value']
   
    snippet = msg.get('snippet', '')
   
    from_email = headers.get('From', 'Unknown')
    subject = headers.get('Subject', 'No Subject')
    date = headers.get('Date', '')
   
    # Safe file name banaye
    safe_subject = subject[:40].replace(' ', '_').replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_')
    action_file = NEEDS_ACTION / f"EMAIL_{safe_subject}_{message['id'][:8]}.md"
   
    content = f"""---
type: email
from: {from_email}
subject: {subject}
date: {date}
message_id: {message['id']}
status: pending
---
## Email Preview
{snippet}

## Suggested Actions
- [ ] Draft professional reply
- [ ] Forward if needed
- [ ] Archive after processing
"""

    action_file.write_text(content, encoding='utf-8')
    print(f"Email action file created: {action_file.name}")

    # Trigger Qwen to draft reply
    try:
        qwen_prompt = f"Read the email action file: {action_file.name} in Needs_Action folder. Draft a professional reply following Company_Handbook rules. Save the reply draft in Pending_Approval folder as REPLY_{action_file.stem}.md"
        result = subprocess.run(
            ["qwen", "-y", qwen_prompt],
            check=False,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd=str(VAULT_PATH),
            shell=True,
            timeout=120
        )
        print("Qwen reply draft triggered")
        print("Qwen stdout:", result.stdout.strip())
        print("Qwen stderr:", result.stderr.strip())
        print("Exit code:", result.returncode)
    except subprocess.TimeoutExpired:
        print("Qwen timeout – reply draft may be long")
    except FileNotFoundError:
        print("Qwen CLI not found – check npm global install or path")
    except subprocess.CalledProcessError as e:
        print(f"Qwen failed with exit code {e.returncode}")
        print("Qwen error:", e.stderr.strip() if e.stderr else "No detailed error")
    except Exception as e:
        print(f"Qwen call error: {e}")

def main():
    print("=" * 50)
    print("AI Employee - Gmail Watcher Started!")
    print("=" * 50)
   
    service = get_gmail_service()
    print("Gmail connected successfully!")
   
    processed_ids = set()
   
    processed_file = VAULT_PATH / "processed_emails.txt"
    if processed_file.exists():
        processed_ids = set(processed_file.read_text(encoding='utf-8').splitlines())
   
    print("Checking emails every 2 minutes...")
   
    while True:
        try:
            new_emails = check_emails(service, processed_ids)
           
            if new_emails:
                print(f"Found {len(new_emails)} new email(s)!")
                for msg in new_emails:
                    create_action_file(service, msg)
                    processed_ids.add(msg['id'])
               
                processed_file.write_text('\n'.join(processed_ids), encoding='utf-8')
            else:
                print(f"No new emails - {time.strftime('%H:%M:%S')}")
               
        except Exception as e:
            print(f"Error: {e}")
       
        time.sleep(120)

if __name__ == "__main__":
    main()