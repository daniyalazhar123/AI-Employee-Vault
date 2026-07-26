import sys, os, json, pickle
sys.path.insert(0, r'D:\Desktop4\Obsidian Vault')

secrets_dir = os.path.join(os.environ['USERPROFILE'], '.ai_employee', 'secrets')
token_file = os.path.join(secrets_dir, 'token.pickle')
creds_file = os.path.join(secrets_dir, 'credentials.json')

print('=== GMAIL INTEGRATION ===')
print(f'Token file: {os.path.exists(token_file)}')
print(f'Creds file: {os.path.exists(creds_file)}')

if os.path.exists(token_file):
    with open(token_file, 'rb') as f:
        creds = pickle.load(f)
    print(f'Token valid: {creds.valid}, expired: {creds.expired}, has refresh: {bool(creds.refresh_token)}')
    if creds.valid:
        from googleapiclient.discovery import build
        service = build('gmail', 'v1', credentials=creds)
        profile = service.users().getProfile(userId='me').execute()
        print(f'Gmail account: {profile["emailAddress"]}')
        print(f'Total messages: {profile.get("messagesTotal", "?")}')
        results = service.users().messages().list(userId='me', q='is:unread', maxResults=3).execute()
        msgs = results.get('messages', [])
        print(f'Unread messages: {len(msgs)}')
        for msg in msgs[:3]:
            m = service.users().messages().get(userId='me', id=msg['id'], format='metadata').execute()
            headers = {h['name']: h['value'] for h in m['payload']['headers']}
            print(f'  From: {headers.get("From","?")} | Subject: {headers.get("Subject","?")}')
        print('GMAIL: VERIFIED')
    else:
        print(f'GMAIL: TOKEN EXPIRED - needs re-auth (refresh failed in earlier attempt)')
else:
    print('GMAIL: NO TOKEN - needs first-time auth')
