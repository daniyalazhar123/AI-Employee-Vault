#!/usr/bin/env python3
"""
🔗 LinkedIn OAuth2 Agent
Professional Cloud Architecture Portfolio Module

Implements OAuth2 authentication flow for LinkedIn API.
Supports token generation, refresh, and posting status updates.

Setup:
    1. Add to .env.local:
       LINKEDIN_CLIENT_ID=your_client_id
       LINKEDIN_CLIENT_SECRET=your_client_secret
       LINKEDIN_REDIRECT_URI=http://localhost:8080/callback
    
    2. Run: python linkedin_oauth_agent.py
    3. Authorize in browser
    4. Token saved automatically

Usage:
    from linkedin_oauth_agent import LinkedInOAuthAgent
    
    agent = LinkedInOAuthAgent()
    agent.post_status_update("Hello from AI Agent! 🚀")
"""

import os
import json
import logging
import webbrowser
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

import requests
from dotenv import load_dotenv
from requests_oauthlib import OAuth2Session

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('linkedin_oauth_agent.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('LinkedInOAuthAgent')


class LinkedInOAuthAgent:
    """
    LinkedIn OAuth2 Agent
    
    Implements OAuth2 authentication flow for LinkedIn API.
    Manages token generation, refresh, and API operations.
    
    Attributes:
        client_id (str): LinkedIn app client ID
        client_secret (str): LinkedIn app client secret
        redirect_uri (str): OAuth redirect URI
        token_file (str): Path to store token
        oauth (OAuth2Session): OAuth2 session instance
    """

    AUTHORIZATION_BASE_URL = "https://www.linkedin.com/oauth/v2/authorization"
    TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
    API_BASE_URL = "https://api.linkedin.com/v2"
    PROFILE_ENDPOINT = f"{API_BASE_URL}/me"
    POST_ENDPOINT = f"{API_BASE_URL}/ugcPosts"
    
    # LinkedIn OAuth2 scopes (matching app configuration)
    SCOPES = [
        'openid',           # Use your name and photo
        'profile',          # Use your name and photo
        'email',            # Use the primary email address
        'w_member_social'   # Create, modify, and delete posts
    ]

    def __init__(
        self,
        token_file: str = "linkedin_token.json",
        env_file: str = ".env.local"
    ):
        """
        Initialize LinkedIn OAuth2 Agent
        
        Args:
            token_file: Path to store/load OAuth2 token
            env_file: Path to environment file
        """
        self.token_file = Path(token_file)
        self.env_file = Path(env_file)
        
        # Load environment
        self._load_environment()
        
        # OAuth2 credentials
        self.client_id = os.getenv("LINKEDIN_CLIENT_ID")
        self.client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
        self.redirect_uri = os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:8080/callback")
        
        # Validate credentials
        self._validate_credentials()
        
        # OAuth2 session
        self.oauth: Optional[OAuth2Session] = None
        self.token: Optional[Dict[str, Any]] = None
        
        # Load existing token if available
        self._load_token()
        
        logger.info("✅ LinkedIn OAuth2 Agent initialized")
        logger.info(f"🔑 Client ID: {self.client_id[:10]}...")

    def _load_environment(self):
        """Load environment variables from .env file"""
        env_paths = [
            Path.cwd() / '.env.local',
            Path.cwd() / '.env',
            self.env_file,
            Path.home() / '.env',
        ]
        
        for env_path in env_paths:
            if env_path.exists():
                load_dotenv(env_path, override=True)
                logger.debug(f"📄 Loaded env from: {env_path}")
        
        logger.info("🔐 Environment variables loaded")

    def _validate_credentials(self):
        """Validate OAuth2 credentials exist"""
        if not self.client_id:
            raise ValueError(
                "❌ LINKEDIN_CLIENT_ID not found in environment.\n"
                "Add to .env.local:\n"
                "  LINKEDIN_CLIENT_ID=your_client_id"
            )
        
        if not self.client_secret:
            raise ValueError(
                "❌ LINKEDIN_CLIENT_SECRET not found in environment.\n"
                "Add to .env.local:\n"
                "  LINKEDIN_CLIENT_SECRET=your_client_secret"
            )
        
        logger.info("✅ OAuth2 credentials validated")

    def _load_token(self) -> bool:
        """
        Load OAuth2 token from file
        
        Returns:
            bool: True if token loaded and still valid
        """
        if not self.token_file.exists():
            logger.info("ℹ️ No saved token found")
            return False
        
        try:
            with open(self.token_file, 'r') as f:
                self.token = json.load(f)
            
            # Check if token is expired
            if self._is_token_expired():
                logger.info("⚠️ Token expired, attempting refresh...")
                if self._refresh_token():
                    logger.info("✅ Token refreshed successfully")
                    return True
                else:
                    logger.warning("⚠️ Token refresh failed, need re-authorization")
                    return False
            
            logger.info("✅ Token loaded from file")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load token: {e}")
            return False

    def _save_token(self):
        """Save OAuth2 token to file"""
        try:
            with open(self.token_file, 'w') as f:
                json.dump(self.token, f, indent=2)
            
            logger.info(f"💾 Token saved to: {self.token_file}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save token: {e}")

    def _is_token_expired(self) -> bool:
        """
        Check if token is expired
        
        Returns:
            bool: True if token is expired
        """
        if not self.token:
            return True
        
        # Check expires_at timestamp
        expires_at = self.token.get('expires_at', 0)
        if expires_at and datetime.now().timestamp() > expires_at:
            return True
        
        # Check access_token exists
        if not self.token.get('access_token'):
            return True
        
        return False

    def _refresh_token(self) -> bool:
        """
        Refresh expired OAuth2 token
        
        Returns:
            bool: True if refresh successful
        """
        try:
            refresh_token = self.token.get('refresh_token')
            if not refresh_token:
                logger.warning("⚠️ No refresh token available")
                return False
            
            # Create OAuth2 session for refresh
            from oauthlib.oauth2 import LegacyApplicationClient
            client = OAuth2Session(
                self.client_id,
                client=self,
                token=self.token
            )
            
            # Refresh token
            self.token = client.refresh_token(
                self.TOKEN_URL,
                auth=requests.auth.HTTPBasicAuth(
                    self.client_id,
                    self.client_secret
                )
            )
            
            # Add expires_at timestamp
            if 'expires_in' in self.token:
                self.token['expires_at'] = datetime.now().timestamp() + self.token['expires_in']
            
            self._save_token()
            return True
            
        except Exception as e:
            logger.error(f"❌ Token refresh failed: {e}")
            return False

    def get_authorization_url(self) -> str:
        """
        Generate LinkedIn OAuth2 authorization URL
        
        Returns:
            str: Authorization URL to open in browser
        """
        self.oauth = OAuth2Session(
            self.client_id,
            redirect_uri=self.redirect_uri,
            scope=self.SCOPES
        )
        
        authorization_url, _ = self.oauth.authorization_url(
            self.AUTHORIZATION_BASE_URL,
            state="linkedin_oauth_agent_state"
        )
        
        logger.info("🔗 Authorization URL generated")
        return authorization_url

    def _start_callback_server(self) -> str:
        """
        Start local HTTP server to capture OAuth2 callback
        
        Returns:
            str: Authorization code from callback
        """
        authorization_code = None
        server = None
        
        class CallbackHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                nonlocal authorization_code, server
                
                # Parse authorization code from URL
                # Support both /callback and root path
                if '/callback' in self.path or self.path == '/':
                    from urllib.parse import urlparse, parse_qs
                    
                    parsed = urlparse(self.path)
                    params = parse_qs(parsed.query)
                    
                    if 'code' in params:
                        authorization_code = params['code'][0]
                        
                        # Send success response
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        html_success = """
                            <html>
                            <body style="font-family: Arial; text-align: center; padding: 50px;">
                                <h2>LinkedIn Authorization Successful!</h2>
                                <p>You can close this window and return to the application.</p>
                            </body>
                            </html>
                        """
                        self.wfile.write(html_success.encode('utf-8'))
                        
                        # Shutdown server
                        threading.Thread(target=server.shutdown).start()
                    else:
                        # Error in authorization
                        self.send_response(400)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        html_error = """
                            <html>
                            <body style="font-family: Arial; text-align: center; padding: 50px;">
                                <h2>Authorization Failed</h2>
                                <p>No authorization code received. Please try again.</p>
                            </body>
                            </html>
                        """
                        self.wfile.write(html_error.encode('utf-8'))
                        threading.Thread(target=server.shutdown).start()
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def log_message(self, format, *args):
                # Suppress default logging
                pass
        
        # Start server
        server = HTTPServer(('localhost', 8080), CallbackHandler)
        
        logger.info("🌐 Starting callback server on http://localhost:8080")
        server.serve_forever()
        
        return authorization_code

    def fetch_token(self, authorization_code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token
        
        Args:
            authorization_code: OAuth2 authorization code
            
        Returns:
            dict: OAuth2 token data
        """
        try:
            self.oauth = OAuth2Session(
                self.client_id,
                redirect_uri=self.redirect_uri
            )
            
            # Fetch token
            self.token = self.oauth.fetch_token(
                self.TOKEN_URL,
                code=authorization_code,
                client_secret=self.client_secret,
                include_client_id=True
            )
            
            # Add expires_at timestamp
            if 'expires_in' in self.token:
                self.token['expires_at'] = datetime.now().timestamp() + self.token['expires_in']
            
            # Save token
            self._save_token()
            
            logger.info("✅ Access token obtained successfully")
            return self.token
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch token: {e}")
            raise

    def authorize(self):
        """
        Complete OAuth2 authorization flow
        
        Opens browser for authorization and waits for callback.
        """
        print("\n" + "="*60)
        print("🔗 LINKEDIN OAUTH2 AUTHORIZATION")
        print("="*60)
        
        # Check if we already have a valid token
        if self.token and not self._is_token_expired():
            print("\n✅ Valid token already exists!")
            return
        
        # Generate authorization URL
        auth_url = self.get_authorization_url()
        
        print("\n📋 Step 1: Opening browser for authorization...")
        print(f"🔗 URL: {auth_url}")
        
        # Open browser
        webbrowser.open(auth_url)
        
        print("\n⏳ Step 2: Please authorize the application in your browser...")
        print("   (The app will automatically continue after authorization)")
        
        # Start callback server and wait for code
        authorization_code = self._start_callback_server()
        
        if not authorization_code:
            raise Exception("❌ No authorization code received")
        
        print("\n✅ Step 3: Authorization code received!")
        
        # Exchange code for token
        print("⏳ Step 4: Exchanging code for access token...")
        self.fetch_token(authorization_code)
        
        print("\n✅ Authorization complete! Token saved to file.")
        print("   You can now use post_status_update() to post to LinkedIn.")

    def _ensure_token(self):
        """Ensure we have a valid token, refresh if needed"""
        if not self.token or self._is_token_expired():
            if self.token and self.token.get('refresh_token'):
                if not self._refresh_token():
                    raise Exception(
                        "❌ Token expired and refresh failed.\n"
                        "   Please run authorize() again."
                    )
            else:
                raise Exception(
                    "❌ No valid token available.\n"
                    "   Please run authorize() first."
                )

    def _get_oauth_session(self) -> OAuth2Session:
        """
        Get authenticated OAuth2 session
        
        Returns:
            OAuth2Session: Authenticated session
        """
        if not self.token or not self.token.get('access_token'):
            raise Exception("❌ No access token available. Run authorize() first.")
        
        # Refresh token if expired
        if self._is_token_expired():
            self._refresh_token()
        
        # Create OAuth2 session
        return OAuth2Session(
            self.client_id,
            token=self.token
        )

    def get_profile(self) -> Optional[Dict[str, Any]]:
        """
        Fetch authenticated user's LinkedIn profile
        
        Returns:
            dict: Profile data or None if failed
        """
        try:
            self._ensure_token()
            oauth = self._get_oauth_session()
            
            logger.info("👤 Fetching LinkedIn profile...")
            
            response = oauth.get(self.PROFILE_ENDPOINT)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract profile information
                profile = {
                    'id': data.get('id', ''),
                    'first_name': data.get('localizedFirstName', ''),
                    'last_name': data.get('localizedLastName', ''),
                    'profile_url': f"https://www.linkedin.com/in/{data.get('vanityName', '')}",
                    'headline': data.get('headline', '')
                }
                
                full_name = f"{profile['first_name']} {profile['last_name']}"
                logger.info(f"✅ Profile fetched: {full_name}")
                return profile
            
            elif response.status_code == 401:
                raise Exception("❌ Token expired or invalid")
            
            else:
                raise Exception(f"❌ Profile fetch failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"❌ Failed to get profile: {e}")
            raise

    def post_status_update(
        self,
        text: str,
        visibility: str = "PUBLIC",
        author_person_urn: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Post a status update to LinkedIn
        
        Args:
            text: Post content (max 3000 characters)
            visibility: Post visibility (PUBLIC, CONNECTIONS, LOGGED_IN)
            author_person_urn: LinkedIn URN for author (auto-detected if None)
            
        Returns:
            dict: Result with success status and post ID
        """
        try:
            # Validate input
            if len(text) > 3000:
                raise ValueError("Post content exceeds 3000 character limit")
            if len(text.strip()) < 10:
                raise ValueError("Post content too short (minimum 10 characters)")
            
            self._ensure_token()
            
            # Get author URN if not provided
            if not author_person_urn:
                profile = self.get_profile()
                author_person_urn = f"urn:li:person:{profile['id']}"
            
            logger.info(f"📝 Posting status update ({len(text)} chars)...")
            
            # Construct post payload
            payload = {
                "author": author_person_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": visibility
                }
            }
            
            # Create OAuth2 session
            oauth = self._get_oauth_session()
            
            # Make POST request
            headers = {
                'X-Restli-Protocol-Version': '2.0.0',
                'Content-Type': 'application/json'
            }
            
            response = oauth.post(
                self.POST_ENDPOINT,
                json=payload,
                headers=headers
            )
            
            if response.status_code == 201:
                result = {
                    'success': True,
                    'post_id': response.json().get('id', ''),
                    'text': text[:100] + '...' if len(text) > 100 else text,
                    'visibility': visibility,
                    'timestamp': datetime.now().isoformat()
                }
                
                logger.info("✅ Status update posted successfully")
                return result
            
            elif response.status_code == 401:
                raise Exception("❌ Token expired or invalid")
            
            elif response.status_code == 403:
                raise Exception("❌ Permission denied. Check OAuth2 scopes.")
            
            else:
                raise Exception(f"❌ Post failed: {response.status_code} - {response.text[:500]}")
                
        except Exception as e:
            logger.error(f"❌ Failed to post status update: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def post_with_image(
        self,
        text: str,
        image_url: str,
        image_description: str = "Image description",
        title: str = "Post Title",
        visibility: str = "PUBLIC"
    ) -> Dict[str, Any]:
        """
        Post a status update with an image to LinkedIn
        
        Args:
            text: Post text
            image_url: URL of the image
            image_description: Alt text for image
            title: Title for the shared content
            visibility: Post visibility
            
        Returns:
            dict: Result with success status
        """
        try:
            self._ensure_token()
            
            profile = self.get_profile()
            author_person_urn = f"urn:li:person:{profile['id']}"
            
            logger.info(f"📝 Posting status update with image...")
            
            # Construct post payload with media
            payload = {
                "author": author_person_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text
                        },
                        "shareMediaCategory": "IMAGE",
                        "media": [
                            {
                                "status": "READY",
                                "description": {
                                    "text": image_description
                                },
                                "originalUrl": image_url,
                                "title": {
                                    "text": title
                                }
                            }
                        ]
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": visibility
                }
            }
            
            oauth = self._get_oauth_session()
            
            response = oauth.post(
                self.POST_ENDPOINT,
                json=payload,
                headers={
                    'X-Restli-Protocol-Version': '2.0.0',
                    'Content-Type': 'application/json'
                }
            )
            
            if response.status_code == 201:
                return {
                    'success': True,
                    'post_id': response.json().get('id', ''),
                    'text': text[:100] + '...',
                    'image_url': image_url,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                raise Exception(f"❌ Post failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"❌ Failed to post with image: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def revoke_token(self) -> bool:
        """
        Revoke current OAuth2 token
        
        Returns:
            bool: True if successful
        """
        try:
            if not self.token:
                return False
            
            oauth = self._get_oauth_session()
            
            # Revoke token
            response = oauth.post(
                "https://www.linkedin.com/oauth/v2/revoke",
                data={'token': self.token.get('access_token', '')}
            )
            
            if response.status_code == 200:
                # Clear saved token
                if self.token_file.exists():
                    self.token_file.unlink()
                
                self.token = None
                logger.info("✅ Token revoked successfully")
                return True
            
            else:
                raise Exception(f"❌ Revoke failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Failed to revoke token: {e}")
            return False

    def get_token_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about current token
        
        Returns:
            dict: Token metadata
        """
        if not self.token:
            return None
        
        expires_at = self.token.get('expires_at', 0)
        expires_in = max(0, expires_at - datetime.now().timestamp())
        
        return {
            'has_token': bool(self.token.get('access_token')),
            'expires_at': datetime.fromtimestamp(expires_at).isoformat() if expires_at else 'N/A',
            'expires_in_seconds': int(expires_in),
            'expires_in_human': f"{int(expires_in / 3600)}h {int((expires_in % 3600) / 60)}m",
            'scopes': self.token.get('scope', '').split(' '),
            'token_file': str(self.token_file)
        }

    def close(self):
        """Cleanup"""
        logger.info("🔒 LinkedIn OAuth2 Agent closed")


# ============================================
# MAIN - Test/Example Usage
# ============================================
def main():
    """Test LinkedIn OAuth2 Agent"""
    
    print("="*60)
    print("🔗 LINKEDIN OAUTH2 AUTOMATION AGENT")
    print("="*60)
    
    try:
        agent = LinkedInOAuthAgent()
        
        # Show token info
        print("\n🔑 Token Information:")
        token_info = agent.get_token_info()
        if token_info:
            print(f"   Has Token: {token_info['has_token']}")
            print(f"   Expires: {token_info['expires_in_human']}")
            print(f"   Scopes: {', '.join(token_info['scopes'])}")
        else:
            print("   No token found")
        
        # Check if we need to authorize
        if not token_info or not token_info['has_token'] or token_info['expires_in_seconds'] == 0:
            print("\n🔐 No valid token found. Starting authorization flow...")
            agent.authorize()
        
        # Get profile
        print("\n👤 Fetching profile...")
        profile = agent.get_profile()
        if profile:
            print(f"   Name: {profile['first_name']} {profile['last_name']}")
            print(f"   Profile URL: {profile['profile_url']}")
            print(f"   Headline: {profile['headline']}")
        
        # Example: Post status update
        print("\n📝 Ready to post!")
        print("\nTo post a status update, uncomment the following lines:")
        print("""
        result = agent.post_status_update(
            text="🚀 Testing LinkedIn OAuth2 Agent for Cloud Architecture portfolio! #AI #Automation",
            visibility="PUBLIC"
        )
        
        if result['success']:
            print(f"✅ Posted successfully! Post ID: {result['post_id']}")
        else:
            print(f"❌ Post failed: {result['error']}")
        """)
        
        # Example: Post with image
        print("\nTo post with an image, uncomment:")
        print("""
        result = agent.post_with_image(
            text="Check out my latest project! 🎨",
            image_url="https://example.com/image.jpg",
            image_description="Project screenshot",
            title="My Amazing Project"
        )
        """)
        
        print("\n✅ Agent ready for use!")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")


if __name__ == '__main__':
    main()
