#!/usr/bin/env python3
"""
MCP Social Media Server - AI Employee Vault

Unified MCP server for posting to LinkedIn, Facebook, Instagram, and Twitter/X.
Uses Playwright for browser automation (no API keys needed for basic posting).

⚠️ SECURITY:
    - Credentials loaded from environment variables ONLY
    - NEVER hardcode credentials
    - DRY_RUN=true by default (must explicitly disable)
    - All posts require human approval before publishing

Usage:
    python mcp_social.py --action post --platform linkedin --content "Your post content"
    python mcp_social.py --action post --platform facebook --content "Your post content"
    python mcp_social.py --action draft --platform twitter --content "Your tweet"
    python mcp_social.py --status  # Check all platform statuses

Environment Variables:
    LINKEDIN_EMAIL, LINKEDIN_PASSWORD
    FACEBOOK_EMAIL, FACEBOOK_PASSWORD
    INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD
    TWITTER_USERNAME, TWITTER_PASSWORD
    DRY_RUN=true (default - safe mode)
    REQUIRE_APPROVAL=true (default - HITL safety)
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('MCPSocial')

# Check Playwright availability
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("⚠️ Playwright not installed. Run: pip install playwright && playwright install chromium")


class MCPSocialServer:
    """Unified MCP Social Media Server"""

    def __init__(self, vault_path: Optional[Path] = None):
        self.vault_path = vault_path or Path(__file__).parent
        self.drafts_folder = self.vault_path / 'Social_Drafts'
        self.drafts_folder.mkdir(parents=True, exist_ok=True)
        self.logs_folder = self.vault_path / 'Logs'
        self.logs_folder.mkdir(parents=True, exist_ok=True)

        # Safety flags
        self.dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'
        self.require_approval = os.getenv('REQUIRE_APPROVAL', 'true').lower() == 'true'

        # Credentials (from env only)
        self.linkedin_email = os.getenv('LINKEDIN_EMAIL', '')
        self.linkedin_password = os.getenv('LINKEDIN_PASSWORD', '')
        self.facebook_email = os.getenv('FACEBOOK_EMAIL', '')
        self.facebook_password = os.getenv('FACEBOOK_PASSWORD', '')
        self.instagram_username = os.getenv('INSTAGRAM_USERNAME', '')
        self.instagram_password = os.getenv('INSTAGRAM_PASSWORD', '')
        self.twitter_username = os.getenv('TWITTER_USERNAME', '')
        self.twitter_password = os.getenv('TWITTER_PASSWORD', '')

        logger.info(f"📱 MCP Social Media Server initialized")
        logger.info(f"   Dry Run: {self.dry_run}")
        logger.info(f"   Approval Required: {self.require_approval}")
        logger.info(f"   Playwright: {'✅ Available' if PLAYWRIGHT_AVAILABLE else '❌ Not installed'}")

    def post_to_linkedin(self, content: str, approved: bool = False) -> Dict:
        """Post content to LinkedIn"""
        logger.info(f"💼 Posting to LinkedIn...")

        # HITL safety check
        if self.require_approval and not approved:
            return {
                'success': False,
                'requires_approval': True,
                'platform': 'linkedin',
                'message': 'Post requires human approval. Set approved=True or REQUIRE_APPROVAL=false',
                'content_preview': content[:100]
            }

        if self.dry_run:
            logger.info(f"📝 [DRY RUN] LinkedIn post would be published")
            return self._save_draft('linkedin', content, dry_run=True)

        if not PLAYWRIGHT_AVAILABLE:
            return {'success': False, 'message': 'Playwright not installed'}

        if not self.linkedin_email or not self.linkedin_password:
            return {'success': False, 'message': 'LinkedIn credentials not set'}

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()

                # Login
                page.goto('https://www.linkedin.com/login')
                time.sleep(2)

                email_field = page.locator('#username')
                if email_field.is_visible():
                    email_field.fill(self.linkedin_email)

                password_field = page.locator('#password')
                if password_field.is_visible():
                    password_field.fill(self.linkedin_password)

                sign_in = page.locator('button[type="submit"]')
                if sign_in.is_visible():
                    sign_in.click()
                    time.sleep(3)

                # Verify login
                if 'feed' not in page.url and 'mynetwork' not in page.url:
                    browser.close()
                    return {'success': False, 'message': 'LinkedIn login failed'}

                # Create post
                page.goto('https://www.linkedin.com/feed/')
                time.sleep(2)

                textbox = page.locator('div[role="textbox"]').first
                if textbox.is_visible():
                    textbox.fill(content)
                    time.sleep(1)

                    post_button = page.locator('button:has-text("Post")').first
                    if post_button.is_visible():
                        post_button.click()
                        time.sleep(3)

                        browser.close()

                        # Log success
                        self._save_post_log('linkedin', content, status='published')

                        return {
                            'success': True,
                            'platform': 'linkedin',
                            'message': 'Post published to LinkedIn',
                            'timestamp': datetime.now().isoformat()
                        }
                    else:
                        browser.close()
                        return {'success': False, 'message': 'Post button not found'}
                else:
                    browser.close()
                    return {'success': False, 'message': 'Post input not found'}

        except Exception as e:
            logger.error(f"❌ LinkedIn post failed: {e}")
            return {'success': False, 'message': str(e)}

    def post_to_facebook(self, content: str, approved: bool = False) -> Dict:
        """Post content to Facebook"""
        logger.info(f"📘 Posting to Facebook...")

        # HITL safety check
        if self.require_approval and not approved:
            return {
                'success': False,
                'requires_approval': True,
                'platform': 'facebook',
                'message': 'Post requires human approval',
                'content_preview': content[:100]
            }

        if self.dry_run:
            logger.info(f"📝 [DRY RUN] Facebook post would be published")
            return self._save_draft('facebook', content, dry_run=True)

        if not PLAYWRIGHT_AVAILABLE:
            return {'success': False, 'message': 'Playwright not installed'}

        if not self.facebook_email or not self.facebook_password:
            return {'success': False, 'message': 'Facebook credentials not set'}

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()

                # Login
                page.goto('https://www.facebook.com/login')
                time.sleep(2)

                email_field = page.locator('#email')
                if email_field.is_visible():
                    email_field.fill(self.facebook_email)

                password_field = page.locator('#pass')
                if password_field.is_visible():
                    password_field.fill(self.facebook_password)

                login_button = page.locator('button[name="login"]')
                if login_button.is_visible():
                    login_button.click()
                    time.sleep(3)

                # Create post
                page.goto('https://www.facebook.com/')
                time.sleep(2)

                # Find post box
                post_box = page.locator('[placeholder="What\'s on your mind?"]').first
                if post_box.is_visible():
                    post_box.fill(content)
                    time.sleep(1)

                    # Click post button
                    post_button = page.locator('[aria-label="Post"]').first
                    if post_button.is_visible():
                        post_button.click()
                        time.sleep(3)

                        browser.close()

                        self._save_post_log('facebook', content, status='published')

                        return {
                            'success': True,
                            'platform': 'facebook',
                            'message': 'Post published to Facebook',
                            'timestamp': datetime.now().isoformat()
                        }
                    else:
                        browser.close()
                        return {'success': False, 'message': 'Facebook post button not found'}
                else:
                    browser.close()
                    return {'success': False, 'message': 'Facebook post box not found'}

        except Exception as e:
            logger.error(f"❌ Facebook post failed: {e}")
            return {'success': False, 'message': str(e)}

    def post_to_instagram(self, content: str, image_path: Optional[str] = None, approved: bool = False) -> Dict:
        """Post content to Instagram"""
        logger.info(f"📷 Posting to Instagram...")

        # HITL safety check
        if self.require_approval and not approved:
            return {
                'success': False,
                'requires_approval': True,
                'platform': 'instagram',
                'message': 'Post requires human approval',
                'content_preview': content[:100]
            }

        if self.dry_run:
            logger.info(f"📝 [DRY RUN] Instagram post would be published")
            return self._save_draft('instagram', content, dry_run=True)

        if not PLAYWRIGHT_AVAILABLE:
            return {'success': False, 'message': 'Playwright not installed'}

        if not self.instagram_username or not self.instagram_password:
            return {'success': False, 'message': 'Instagram credentials not set'}

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()

                # Login
                page.goto('https://www.instagram.com/accounts/login/')
                time.sleep(3)

                username_field = page.locator('input[name="username"]')
                if username_field.is_visible():
                    username_field.fill(self.instagram_username)

                password_field = page.locator('input[name="password"]')
                if password_field.is_visible():
                    password_field.fill(self.instagram_password)

                login_button = page.locator('button[type="submit"]')
                if login_button.is_visible():
                    login_button.click()
                    time.sleep(3)

                # Create post (Instagram web has limited posting capability)
                # This is a stub - Instagram web doesn't support full posting
                # For production, use Instagram Graph API

                browser.close()

                self._save_post_log('instagram', content, status='draft_web_limitation')

                return {
                    'success': True,
                    'platform': 'instagram',
                    'message': 'Instagram post saved as draft (web posting limited). Use mobile app or Graph API.',
                    'draft_saved': True,
                    'timestamp': datetime.now().isoformat()
                }

        except Exception as e:
            logger.error(f"❌ Instagram post failed: {e}")
            return {'success': False, 'message': str(e)}

    def post_to_twitter(self, content: str, approved: bool = False) -> Dict:
        """Post content to Twitter/X"""
        logger.info(f"🐦 Posting to Twitter/X...")

        # Validate tweet length
        if len(content) > 280:
            return {'success': False, 'message': f'Tweet too long: {len(content)}/280 characters'}

        # HITL safety check
        if self.require_approval and not approved:
            return {
                'success': False,
                'requires_approval': True,
                'platform': 'twitter',
                'message': 'Tweet requires human approval',
                'content_preview': content[:100]
            }

        if self.dry_run:
            logger.info(f"📝 [DRY RUN] Tweet would be published")
            return self._save_draft('twitter', content, dry_run=True)

        if not PLAYWRIGHT_AVAILABLE:
            return {'success': False, 'message': 'Playwright not installed'}

        if not self.twitter_username or not self.twitter_password:
            return {'success': False, 'message': 'Twitter credentials not set'}

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()

                # Login
                page.goto('https://twitter.com/i/flow/login')
                time.sleep(3)

                # Enter username
                username_field = page.locator('input[autocomplete="username"]')
                if username_field.is_visible():
                    username_field.fill(self.twitter_username)
                    page.locator('div[role="button"]:has-text("Next")').click()
                    time.sleep(2)

                # Enter password
                password_field = page.locator('input[name="password"]')
                if password_field.is_visible():
                    password_field.fill(self.twitter_password)
                    page.locator('div[role="button"]:has-text("Log in")').click()
                    time.sleep(3)

                # Create tweet
                page.goto('https://twitter.com/compose/tweet')
                time.sleep(2)

                tweet_box = page.locator('div[contenteditable="true"][data-testid="tweetTextarea_0"]')
                if tweet_box.is_visible():
                    tweet_box.fill(content)
                    time.sleep(1)

                    tweet_button = page.locator('div[role="button"]:has-text("Post")')
                    if tweet_button.is_visible():
                        tweet_button.click()
                        time.sleep(3)

                        browser.close()

                        self._save_post_log('twitter', content, status='published')

                        return {
                            'success': True,
                            'platform': 'twitter',
                            'message': 'Tweet published',
                            'timestamp': datetime.now().isoformat()
                        }
                    else:
                        browser.close()
                        return {'success': False, 'message': 'Tweet button not found'}
                else:
                    browser.close()
                    return {'success': False, 'message': 'Tweet box not found'}

        except Exception as e:
            logger.error(f"❌ Twitter post failed: {e}")
            return {'success': False, 'message': str(e)}

    def _save_draft(self, platform: str, content: str, dry_run: bool = True) -> Dict:
        """Save post as draft"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        draft_file = self.drafts_folder / f'{platform}_post_{timestamp}.md'

        draft_content = f"""---
type: {platform}_post
platform: {platform.title()}
created: {datetime.now().isoformat()}
status: {'draft' if dry_run else 'pending_approval'}
dry_run: {dry_run}
---

# {platform.title()} Post Draft

{content}

---
*Generated by MCP Social Media Server*
"""
        draft_file.write_text(draft_content, encoding='utf-8')

        return {
            'success': True,
            'platform': platform,
            'message': f'Draft saved for {platform.title()}',
            'draft_file': str(draft_file),
            'dry_run': dry_run
        }

    def _save_post_log(self, platform: str, content: str, status: str = 'draft') -> Path:
        """Save post log"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = self.logs_folder / f'{platform}_post_{timestamp}.md'

        log_content = f"""---
type: {platform}_post_log
platform: {platform.title()}
posted: {datetime.now().isoformat()}
status: {status}
---

# {platform.title()} Post

{content}

---
*Posted via MCP Social Media Server*
"""
        log_file.write_text(log_content, encoding='utf-8')
        return log_file

    def get_platform_status(self) -> Dict:
        """Get status of all platforms"""
        return {
            'linkedin': {
                'configured': bool(self.linkedin_email and self.linkedin_password),
                'dry_run': self.dry_run,
                'approval_required': self.require_approval
            },
            'facebook': {
                'configured': bool(self.facebook_email and self.facebook_password),
                'dry_run': self.dry_run,
                'approval_required': self.require_approval
            },
            'instagram': {
                'configured': bool(self.instagram_username and self.instagram_password),
                'dry_run': self.dry_run,
                'approval_required': self.require_approval
            },
            'twitter': {
                'configured': bool(self.twitter_username and self.twitter_password),
                'dry_run': self.dry_run,
                'approval_required': self.require_approval
            },
            'playwright_available': PLAYWRIGHT_AVAILABLE
        }


# CLI Interface
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='MCP Social Media Server')
    parser.add_argument('--action', choices=['post', 'draft', 'status'], required=True,
                        help='Action: post (publish), draft (save draft), status (check platforms)')
    parser.add_argument('--platform', choices=['linkedin', 'facebook', 'instagram', 'twitter'],
                        help='Platform to post/draft')
    parser.add_argument('--content', help='Post content')
    parser.add_argument('--approved', action='store_true', help='Mark as human-approved')
    parser.add_argument('--vault', help='Vault path')

    args = parser.parse_args()

    server = MCPSocialServer(Path(args.vault) if args.vault else None)

    if args.action == 'status':
        result = server.get_platform_status()
    elif args.action == 'post' and args.platform and args.content:
        if args.platform == 'linkedin':
            result = server.post_to_linkedin(args.content, approved=args.approved)
        elif args.platform == 'facebook':
            result = server.post_to_facebook(args.content, approved=args.approved)
        elif args.platform == 'instagram':
            result = server.post_to_instagram(args.content, approved=args.approved)
        elif args.platform == 'twitter':
            result = server.post_to_twitter(args.content, approved=args.approved)
        else:
            parser.print_help()
            sys.exit(1)
    elif args.action == 'draft' and args.platform and args.content:
        result = server._save_draft(args.platform, args.content, dry_run=True)
    else:
        parser.print_help()
        sys.exit(1)

    print(json.dumps(result, indent=2))
