#!/usr/bin/env python3
"""
🔗 LinkedIn AI Agent (Cookie-based)
Professional Cloud Architecture Portfolio Module

Uses LinkedIn session cookie (li_at) with Voyager API.
No OAuth2 required - direct session-based authentication.

Setup:
    1. Get li_at cookie from browser
    2. Add to .env.local: LINKEDIN_COOKIE=your_li_at_value
    3. Run: python linkedin_cookie_agent.py

Usage:
    from linkedin_cookie_agent import LinkedInAgent
    
    agent = LinkedInAgent()
    agent.post_status_update("Hello from AI Agent! 🚀")
"""

import os
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('linkedin_agent.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('LinkedInAgent')


class LinkedInAgent:
    """
    LinkedIn AI Agent (Cookie-based)
    
    Uses LinkedIn session cookie for authentication via Voyager API.
    Supports profile reading and status updates.
    
    Attributes:
        session (requests.Session): HTTP session with LinkedIn cookies
        voyager_base (str): Voyager API base URL
    """

    VOYAGER_BASE = "https://www.linkedin.com/voyager/api"
    PROFILE_ENDPOINT = f"{VOYAGER_BASE}/me"
    POST_ENDPOINT = f"{VOYAGER_BASE}/ugcPosts"

    def __init__(self, cookie_env_var: str = "LINKEDIN_COOKIE"):
        """
        Initialize LinkedIn Agent
        
        Args:
            cookie_env_var: Environment variable name for cookie
        """
        self.cookie_env_var = cookie_env_var
        self.session = requests.Session()
        
        # Load and setup
        self._load_environment()
        self._setup_session()
        
        logger.info("✅ LinkedIn AI Agent initialized (Cookie-based)")

    def _load_environment(self):
        """Load environment from .env files"""
        env_paths = [
            Path.cwd() / '.env.local',
            Path.cwd() / '.env',
            Path.home() / '.env',
        ]
        
        for env_path in env_paths:
            if env_path.exists():
                load_dotenv(env_path, override=True)
                logger.debug(f"📄 Loaded env from: {env_path}")

    def _setup_session(self):
        """Setup session with LinkedIn cookie"""
        cookie = os.getenv(self.cookie_env_var)
        
        if not cookie:
            raise ValueError(
                f"❌ LinkedIn cookie not found in '{self.cookie_env_var}'.\n"
                f"Add to .env.local:\n"
                f"  {self.cookie_env_var}=your_li_at_cookie"
            )
        
        # Set headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/vnd.linkedin.normalized+json+2.1',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json',
            'x-restli-protocol-version': '2.0.0',
            'x-li-lang': 'en_US',
            'x-li-page-instance': 'urn:li:page:d_flagship3_feed',
            'csrf-token': '',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Origin': 'https://www.linkedin.com',
            'Referer': 'https://www.linkedin.com/feed/'
        })
        
        # Set cookie with proper attributes
        self.session.cookies.set('li_at', cookie, domain='.linkedin.com', path='/', secure=True)
        
        # Try to get JSESSIONID by making initial request
        try:
            logger.info("🔄 Initializing session...")
            init_response = self.session.get(
                'https://www.linkedin.com/feed/',
                timeout=15,
                allow_redirects=False
            )
            
            # Extract JSESSIONID from cookies
            jsession = self.session.cookies.get('JSESSIONID', '')
            if jsession:
                self.session.headers['csrf-token'] = jsession.strip('"')
                logger.info("✅ CSRF token extracted")
            
            # Check if we're being redirected to login
            if init_response.status_code in [301, 302, 303, 307, 308]:
                location = init_response.headers.get('Location', '')
                if 'login' in location.lower() or 'checkpoint' in location.lower():
                    logger.warning("⚠️ Session redirecting to login - cookie may be expired")
            
        except Exception as e:
            logger.debug(f"Session init warning: {e}")
        
        logger.info("✅ Session configured with LinkedIn cookie")

    def _check_session(self) -> bool:
        """
        Check if session is valid
        
        Returns:
            bool: True if session is valid
        """
        try:
            response = self.session.get(self.PROFILE_ENDPOINT, timeout=15)
            
            if response.status_code == 200:
                return True
            elif response.status_code == 401 or response.status_code == 403:
                logger.error("❌ Session expired or invalid (401/403)")
                return False
            else:
                logger.error(f"❌ Session check failed: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Session check error: {e}")
            return False

    def get_profile(self) -> Optional[Dict[str, Any]]:
        """
        Get current user's profile
        
        Returns:
            dict: Profile data or None if failed
        """
        try:
            # Check session first
            if not self._check_session():
                raise Exception("Session expired. Please update your li_at cookie.")
            
            logger.info("👤 Fetching profile...")
            
            response = self.session.get(
                self.PROFILE_ENDPOINT,
                timeout=15
            )
            
            if response.status_code != 200:
                raise Exception(f"Profile fetch failed: {response.status_code}")
            
            data = response.json()
            
            # Debug: Log raw response
            logger.debug(f"Raw profile response: {json.dumps(data, indent=2)[:500]}")
            
            # Try different response formats
            # Format 1: Standard Voyager API
            first_name = (data.get('firstName', {}) or {}).get('localized', {}).get('en_US', '')
            last_name = (data.get('lastName', {}) or {}).get('localized', {}).get('en_US', '')
            
            # Format 2: Flat structure
            if not first_name:
                first_name = data.get('firstName', '')
                last_name = data.get('lastName', '')
            
            # Format 3: Check nested profile data
            if not first_name and 'profile' in data:
                profile_data = data['profile']
                first_name = profile_data.get('firstName', '')
                last_name = profile_data.get('lastName', '')
            
            profile = {
                'id': data.get('id', ''),
                'first_name': first_name,
                'last_name': last_name,
                'headline': data.get('headline', ''),
                'location': data.get('locationName', ''),
                'profile_url': f"https://www.linkedin.com/in/{data.get('publicIdentifier', '')}"
            }
            
            if profile['first_name'] or profile['last_name']:
                logger.info(f"✅ Profile: {profile['first_name']} {profile['last_name']}")
            else:
                logger.warning("⚠️ Profile data incomplete, but session is valid")
            
            return profile
            
        except Exception as e:
            logger.error(f"❌ Failed to get profile: {e}")
            raise

    def post_status_update(self, text: str, visibility: str = "PUBLIC") -> Dict[str, Any]:
        """
        Post a status update to LinkedIn
        
        Args:
            text: Post content (max 3000 chars)
            visibility: PUBLIC, CONNECTIONS, or LOGGED_IN
            
        Returns:
            dict: Result with success status
        """
        try:
            # Validate
            if len(text) > 3000:
                raise ValueError("Post exceeds 3000 character limit")
            if len(text.strip()) < 10:
                raise ValueError("Post too short (minimum 10 characters)")
            
            # Check session
            if not self._check_session():
                raise Exception("Session expired. Please update your li_at cookie.")
            
            logger.info(f"📝 Posting status update ({len(text)} chars)...")
            
            # Get profile ID for author URN
            profile = self.get_profile()
            author_urn = f"urn:li:fsd_profile:{profile['id']}"
            
            # Build payload
            payload = {
                "author": author_urn,
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
            
            # Post
            response = self.session.post(
                self.POST_ENDPOINT,
                json=payload,
                timeout=30
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
            
            elif response.status_code == 401 or response.status_code == 403:
                raise Exception("Session expired. Please update your li_at cookie.")
            
            else:
                raise Exception(f"Post failed: {response.status_code} - {response.text[:300]}")
                
        except Exception as e:
            logger.error(f"❌ Failed to post: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def get_feed_posts(self, count: int = 5) -> List[Dict[str, Any]]:
        """
        Get posts from feed
        
        Args:
            count: Number of posts to fetch
            
        Returns:
            list: Posts data
        """
        try:
            if not self._check_session():
                raise Exception("Session expired. Please update your li_at cookie.")
            
            logger.info(f"📰 Fetching {count} feed posts...")
            
            params = {
                'count': count,
                'q': 'memberShareFeed',
                'start': 0
            }
            
            response = self.session.get(
                f"{self.VOYAGER_BASE}/feed/updates",
                params=params,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                posts = []
                
                for element in data.get('elements', []):
                    content = element.get('content', {})
                    text = content.get('contentEntities', [{}])[0].get('description', {}).get('text', '')
                    author = element.get('actor', {}).get('name', 'Unknown')
                    
                    posts.append({
                        'author': author,
                        'content': text[:300],
                        'timestamp': element.get('created', {}).get('time', 0)
                    })
                
                logger.info(f"✅ Fetched {len(posts)} posts")
                return posts
            
            else:
                raise Exception(f"Feed fetch failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Failed to get feed: {e}")
            return []

    def close(self):
        """Close session"""
        self.session.close()
        logger.info("🔒 Session closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False


def main():
    """Test LinkedIn Agent"""
    print("="*60)
    print("🔗 LINKEDIN AI AGENT (Cookie-based)")
    print("="*60)
    
    try:
        with LinkedInAgent() as agent:
            
            # Get profile
            print("\n👤 Profile:")
            profile = agent.get_profile()
            if profile:
                print(f"   Name: {profile['first_name']} {profile['last_name']}")
                print(f"   Headline: {profile['headline']}")
                print(f"   Profile: {profile['profile_url']}")
                print(f"   ID: {profile['id']}")
            
            # Post status update
            print("\n📝 Posting test status update...")
            result = agent.post_status_update(
                text="🚀 Testing AI Agent for Cloud Architecture! #AI #Automation #CloudComputing",
                visibility="PUBLIC"
            )
            print(f"Result: {result}")
            
            print("\n✅ Test complete!")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == '__main__':
    main()
