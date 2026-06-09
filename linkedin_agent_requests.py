#!/usr/bin/env python3
"""
🔗 LinkedIn Automation Agent (Requests-based)
Professional Cloud Architecture Portfolio Module

A lightweight agent class for LinkedIn automation using the Voyager API.
Fetches profile data and latest posts with proper error handling.

Usage:
    from linkedin_agent_requests import LinkedInAgent
    
    agent = LinkedInAgent()
    profile = agent.get_profile_name()
    posts = agent.get_latest_posts(count=5)
"""

import os
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

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
    LinkedIn Automation Agent (Requests-based)
    
    A lightweight agent for LinkedIn automation using the Voyager REST API.
    Supports profile fetching, feed reading, and posting capabilities.
    
    Attributes:
        session (requests.Session): HTTP session with LinkedIn cookies
        base_url (str): LinkedIn Voyager API base URL
        headers (dict): Common headers for API requests
    """

    VOYAGER_BASE_URL = "https://www.linkedin.com/voyager/api"
    PROFILE_ENDPOINT = f"{VOYAGER_BASE_URL}/identity/profiles/me"
    FEED_ENDPOINT = f"{VOYAGER_BASE_URL}/feed/updates"
    NETWORK_BASE = "https://www.linkedin.com/voyager/api/network"

    def __init__(self, cookie_env_var: str = "LINKEDIN_COOKIE"):
        """
        Initialize LinkedIn Agent
        
        Args:
            cookie_env_var: Environment variable name for cookie (default: LINKEDIN_COOKIE)
        """
        self.cookie_env_var = cookie_env_var
        self.session = requests.Session()
        
        # Load environment and setup
        self._load_environment()
        self._setup_session()
        
        logger.info("✅ LinkedIn Agent initialized (Requests-based)")
        logger.info(f"🔗 Using Voyager API: {self.VOYAGER_BASE_URL}")

    def _load_environment(self):
        """Load environment variables from .env files"""
        # Try multiple locations
        import pathlib
        env_paths = [
            pathlib.Path.cwd() / '.env',
            pathlib.Path.cwd() / '.env.local',
            pathlib.Path.home() / '.env',
        ]
        
        for env_path in env_paths:
            if env_path.exists():
                load_dotenv(env_path, override=True)
                logger.debug(f"📄 Loaded env from: {env_path}")
        
        logger.info("🔐 Environment variables loaded")

    def _setup_session(self):
        """Setup requests session with LinkedIn authentication"""
        cookie = os.getenv(self.cookie_env_var)
        
        if not cookie:
            raise ValueError(
                f"❌ LinkedIn cookie not found in '{self.cookie_env_var}' environment variable.\n"
                f"Please add to your .env.local file:\n"
                f"  {self.cookie_env_var}=your_li_at_cookie_here"
            )
        
        # Set common headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json',
            'x-restli-protocol-version': '2.0.0',
            'x-li-lang': 'en_US',
            'x-li-page-instance': 'urn:li:page:d_flagship3_feed',
            'x-li-track': json.dumps({
                "clientVersion": "1.12.*",
                "mpVersion": "1.12.*",
                "os": "web",
                "timestamp": int(datetime.now().timestamp() * 1000),
                "timezone": "Asia/Karachi",
                "deviceFormFactor": "DESKTOP"
            })
        })
        
        # Set cookies
        self.session.cookies.set('li_at', cookie, domain='.linkedin.com', path='/')
        
        logger.info("✅ Session configured with LinkedIn authentication")

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle API response and check for errors
        
        Args:
            response: requests Response object
            
        Returns:
            dict: Parsed JSON response
            
        Raises:
            Exception: If session expired or request failed
        """
        status_code = response.status_code
        
        if status_code == 200:
            return response.json()
        
        elif status_code == 401:
            raise Exception(
                "❌ LinkedIn session has expired (401 Unauthorized).\n"
                "Please update your LINKEDIN_COOKIE in .env.local file."
            )
        
        elif status_code == 403:
            raise Exception(
                "❌ Access forbidden (403 Forbidden).\n"
                "Your session may have restrictions or needs verification."
            )
        
        elif status_code == 404:
            raise Exception(
                "❌ Resource not found (404 Not Found).\n"
                "The endpoint may have changed or be unavailable."
            )
        
        elif status_code == 429:
            raise Exception(
                "❌ Rate limited (429 Too Many Requests).\n"
                "Please wait before making more requests."
            )
        
        else:
            raise Exception(
                f"❌ Request failed with status {status_code}: {response.text[:200]}"
            )

    def get_profile_name(self) -> Optional[str]:
        """
        Fetch the authenticated user's profile name
        
        Returns:
            str: Full name or None if failed
        """
        try:
            logger.info("👤 Fetching profile name...")
            
            response = self.session.get(
                self.PROFILE_ENDPOINT,
                headers={
                    'csrf-token': self._get_csrf_token(),
                },
                timeout=30
            )
            
            data = self._handle_response(response)
            
            # Extract name from profile data
            first_name = data.get('firstName', {}).get('localized', {}).get('en_US', '')
            last_name = data.get('lastName', {}).get('localized', {}).get('en_US', '')
            
            full_name = f"{first_name} {last_name}".strip()
            
            if full_name:
                logger.info(f"✅ Profile name: {full_name}")
                return full_name
            else:
                logger.warning("⚠️ Name not found in profile data")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to fetch profile name: {e}")
            return None

    def get_profile_full(self) -> Optional[Dict[str, Any]]:
        """
        Fetch complete profile information
        
        Returns:
            dict: Full profile data or None if failed
        """
        try:
            logger.info("👤 Fetching full profile...")
            
            response = self.session.get(
                self.PROFILE_ENDPOINT,
                headers={
                    'csrf-token': self._get_csrf_token(),
                },
                timeout=30
            )
            
            data = self._handle_response(response)
            
            profile = {
                'first_name': data.get('firstName', {}).get('localized', {}).get('en_US', ''),
                'last_name': data.get('lastName', {}).get('localized', {}).get('en_US', ''),
                'headline': data.get('headline', ''),
                'summary': data.get('summary', ''),
                'location': data.get('locationName', ''),
                'industry': data.get('industry', ''),
                'profile_url': data.get('publicIdentifier', ''),
                'profile_urn': data.get('entityUrn', '')
            }
            
            logger.info(f"✅ Full profile fetched: {profile['first_name']} {profile['last_name']}")
            return profile
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch full profile: {e}")
            return None

    def get_latest_posts(self, count: int = 5) -> List[Dict[str, Any]]:
        """
        Fetch latest posts from LinkedIn feed
        
        Args:
            count: Number of posts to fetch (default: 5)
            
        Returns:
            list: List of post dictionaries
        """
        try:
            logger.info(f"📰 Fetching {count} latest posts...")
            
            params = {
                'count': count,
                'q': 'memberShareFeed',
                'start': 0
            }
            
            response = self.session.get(
                self.FEED_ENDPOINT,
                params=params,
                headers={
                    'csrf-token': self._get_csrf_token(),
                },
                timeout=30
            )
            
            data = self._handle_response(response)
            
            posts = []
            elements = data.get('elements', [])
            
            for element in elements:
                post = self._parse_post(element)
                if post:
                    posts.append(post)
            
            logger.info(f"✅ Fetched {len(posts)} posts")
            return posts
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch posts: {e}")
            return []

    def _parse_post(self, element: Dict) -> Optional[Dict[str, Any]]:
        """
        Parse a single post element from the feed
        
        Args:
            element: Raw post data from API
            
        Returns:
            dict: Parsed post data or None
        """
        try:
            # Extract content
            content = element.get('content', {})
            text = content.get('contentEntities', [{}])[0].get('description', {}).get('text', '')
            
            # Extract author
            author = element.get('actor', {}).get('name', 'Unknown')
            
            # Extract engagement metrics
            social_detail = element.get('socialDetail', {})
            likes = social_detail.get('totalShareCount', 0)
            comments = social_detail.get('commentCount', 0)
            
            # Extract timestamp
            timestamp = element.get('created', {}).get('time', 0)
            timestamp_str = datetime.fromtimestamp(timestamp / 1000).isoformat() if timestamp else ''
            
            # Extract post URN
            post_urn = element.get('urn', '')
            
            return {
                'author': author,
                'content': text[:500],  # Limit content length
                'timestamp': timestamp_str,
                'likes': likes,
                'comments': comments,
                'urn': post_urn
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to parse post: {e}")
            return None

    def post_status_update(self, text: str, visibility: str = "PUBLIC") -> Dict[str, Any]:
        """
        Post a status update to LinkedIn
        
        Args:
            text: Post content (max 3000 characters)
            visibility: Visibility level (PUBLIC, CONNECTIONS, LOGGED_IN)
            
        Returns:
            dict: Result with success status
        """
        try:
            # Validate input
            if len(text) > 3000:
                raise ValueError("Post content exceeds 3000 character limit")
            if len(text.strip()) < 10:
                raise ValueError("Post content too short (minimum 10 characters)")
            
            logger.info(f"📝 Posting status update ({len(text)} chars)...")
            
            # Get current user's profile URN
            profile = self.get_profile_full()
            if not profile:
                raise Exception("Could not fetch profile URN for posting")
            
            actor_urn = f"urn:li:member:{profile.get('profile_urn', '')}"
            
            # Construct post payload
            payload = {
                'content': {
                    'contentEntities': [{
                        'entityLocation': {
                            'url': f"https://www.linkedin.com/feed/"
                        },
                        'thumbnails': []
                    }],
                    'title': text
                },
                'distribution': {
                    'feedDistribution': visibility,
                    'targetEntities': [],
                    'thirdPartyDistributionChannels': []
                },
                'owner': actor_urn,
                'subject': text,
                'visibility': visibility
            }
            
            response = self.session.post(
                self.FEED_ENDPOINT,
                json=payload,
                headers={
                    'csrf-token': self._get_csrf_token(),
                    'x-li-edit-mode': 'CREATION'
                },
                timeout=30
            )
            
            data = self._handle_response(response)
            
            result = {
                'success': True,
                'response': data,
                'text': text[:100] + '...' if len(text) > 100 else text,
                'visibility': visibility,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info("✅ Status update posted successfully")
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to post status update: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _get_csrf_token(self) -> str:
        """
        Get CSRF token from LinkedIn session
        
        Returns:
            str: CSRF token or empty string
        """
        # Try to get from cookies
        csrf = self.session.cookies.get('JSESSIONID', '').strip('"')
        
        if csrf:
            return csrf
        
        # Fallback: make a request to get the token
        try:
            response = self.session.get('https://www.linkedin.com/feed/', timeout=10)
            
            # Try to extract from response cookies
            csrf = response.cookies.get('JSESSIONID', '').strip('"')
            
            if csrf:
                return csrf
            
        except Exception as e:
            logger.warning(f"⚠️ Could not fetch CSRF token: {e}")
        
        return ''

    def is_session_valid(self) -> bool:
        """
        Check if LinkedIn session is still valid
        
        Returns:
            bool: True if session is valid
        """
        try:
            logger.info("🔍 Checking session validity...")
            
            response = self.session.get(
                self.PROFILE_ENDPOINT,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info("✅ Session is valid")
                return True
            
            elif response.status_code == 401:
                logger.error("❌ Session has expired (401 Unauthorized)")
                return False
            
            else:
                logger.error(f"❌ Session check failed with status {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Session check request failed: {e}")
            return False

    def close(self):
        """Close the session"""
        self.session.close()
        logger.info("🔒 Session closed")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
        return False


# ============================================
# MAIN - Test/Example Usage
# ============================================
def main():
    """Test LinkedIn Agent functionality"""
    
    print("="*60)
    print("🔗 LINKEDIN AUTOMATION AGENT (Requests-based)")
    print("="*60)
    
    # Check if cookie is set
    if not os.getenv("LINKEDIN_COOKIE"):
        print("\n❌ LINKEDIN_COOKIE not found in .env file")
        print("\n📋 Setup Instructions:")
        print("1. Add to your .env.local file:")
        print("   LINKEDIN_COOKIE=your_li_at_cookie_value_here")
        print("\n2. How to get LinkedIn cookie:")
        print("   - Login to LinkedIn in Chrome")
        print("   - Open DevTools (F12)")
        print("   - Go to Application > Cookies > linkedin.com")
        print("   - Copy the 'li_at' cookie value")
        return
    
    # Test the agent
    try:
        with LinkedInAgent() as agent:
            
            # Check session validity
            print("\n🔍 Checking session validity...")
            if not agent.is_session_valid():
                print("❌ Session has expired! Please update your LinkedIn cookie.")
                return
            print("✅ Session is valid!")
            
            # Get profile name
            print("\n👤 Fetching profile name...")
            name = agent.get_profile_name()
            if name:
                print(f"   Name: {name}")
            
            # Get full profile
            print("\n📋 Fetching full profile...")
            profile = agent.get_profile_full()
            if profile:
                print(f"   Name: {profile['first_name']} {profile['last_name']}")
                print(f"   Headline: {profile['headline']}")
                print(f"   Location: {profile['location']}")
            
            # Get latest posts
            print("\n📰 Fetching latest posts...")
            posts = agent.get_latest_posts(count=3)
            if posts:
                for i, post in enumerate(posts, 1):
                    print(f"\n   Post {i}:")
                    print(f"   Author: {post['author']}")
                    print(f"   Content: {post['content'][:100]}...")
                    print(f"   Likes: {post['likes']}, Comments: {post['comments']}")
            else:
                print("   No posts found")
            
            # Example: Post status update (commented out for safety)
            # print("\n📝 Posting status update...")
            # result = agent.post_status_update(
            #     text="🚀 Testing LinkedIn Automation Agent! #CloudArchitecture #Automation",
            #     visibility="PUBLIC"
            # )
            # if result['success']:
            #     print("✅ Post published successfully!")
            # else:
            #     print(f"❌ Post failed: {result['error']}")
            
            print("\n✅ All tests completed!")
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")


if __name__ == '__main__':
    main()
