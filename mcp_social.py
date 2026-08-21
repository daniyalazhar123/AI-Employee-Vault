#!/usr/bin/env python3
"""
MCP Social Media Server - AI Employee Vault

Unified MCP server for posting to LinkedIn, Facebook, Instagram, and Twitter/X.
Uses Playwright for browser automation (no API keys needed for basic posting).

⚠️ SECURITY:
    - Credentials loaded from environment variables ONLY
    - NEVER hardcode credentials
    - DRY_RUN=true by default (MUST explicitly set DRY_RUN=false to post for real)
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
    DRY_RUN=true (default - safe mode; set DRY_RUN=false to post for real)
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

# Fix Windows console encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, Exception):
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# --- MCP stdio mode detection (must precede logging-configuring imports) ---
# MCP-over-stdio uses stdout for the JSON-RPC channel; any log line written to
# stdout corrupts the protocol. When this file is launched as an MCP server
# (no CLI args, or an explicit --mcp flag), route ALL logging to stderr BEFORE
# importing secrets_config / audit_logger, both of which emit log lines at
# import time. When imported as a module (local_agent), __name__ != '__main__'
# so nothing changes.
_MCP_MODE = __name__ == '__main__' and (len(sys.argv) == 1 or '--mcp' in sys.argv)
if _MCP_MODE:
    os.environ['AI_EMPLOYEE_LOG_STREAM'] = 'stderr'

# Load secrets from outside vault
sys.path.insert(0, str(Path(__file__).parent))
from secrets_config import SECRETS_DIR, load_secrets, get_secret_path
load_secrets()

from audit_logger import setup_logging
logger = setup_logging('MCPSocial')

# Check Playwright availability
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("⚠️ Playwright not installed. Run: pip install playwright && playwright install chromium")

# Session-cookie-based social agents
from x_agent import XAgent
from facebook_instagram_post import FacebookPoster, InstagramPoster


class MCPSocialServer:
    """Unified MCP Social Media Server"""

    def __init__(self, vault_path: Optional[Path] = None):
        self.vault_path = vault_path or Path(__file__).parent
        self.drafts_folder = self.vault_path / 'Social_Drafts'
        self.drafts_folder.mkdir(parents=True, exist_ok=True)
        self.logs_folder = self.vault_path / 'Logs'
        self.logs_folder.mkdir(parents=True, exist_ok=True)

        # Safety flags
        # Fail-safe: dry-run is ON unless DRY_RUN is explicitly set to "false".
        # A missing var or a typo (e.g. "flase") keeps posts simulated, never real.
        self.dry_run = os.getenv('DRY_RUN', 'true').strip().lower() != 'false'
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
        self.twitter_email = os.getenv('TWITTER_EMAIL', '')

        logger.info(f"📱 MCP Social Media Server initialized")
        logger.info(f"   Dry Run: {self.dry_run}")
        logger.info(f"   Approval Required: {self.require_approval}")
        logger.info(f"   Playwright: {'✅ Available' if PLAYWRIGHT_AVAILABLE else '❌ Not installed'}")

    def post_to_linkedin(self, content: str, approved: bool = False) -> Dict:
        """Post content to LinkedIn using session cookies"""
        logger.info(f"💼 Posting to LinkedIn...")

        # HITL safety check
        if self.require_approval and not approved:
            logger.warning(f"⚠️ [HITL BLOCKED] Approval required for LinkedIn post")
            return {
                'success': False,
                'requires_approval': True,
                'platform': 'linkedin',
                'message': 'Post requires human approval. Set approved=True or REQUIRE_APPROVAL=false',
                'content_preview': content[:100]
            }

        if self.dry_run:
            logger.info("=" * 70)
            logger.info("📝 [DRY RUN MODE] LinkedIn post would be published (NO ACTUAL POST)")
            logger.info(f"📝 [DRY RUN] Content: {content[:100]}...")
            logger.info("=" * 70)
            return self._save_draft('linkedin', content, dry_run=True)

        # REAL POST - DRY_RUN=false
        if not PLAYWRIGHT_AVAILABLE:
            return {'success': False, 'message': 'Playwright not installed. Run: pip install playwright && playwright install chromium'}

        # Check for session cookies (now in secrets dir)
        session_file = get_secret_path('linkedin_session.json')
        if not session_file.exists():
            logger.warning("⚠️ No LinkedIn session file found. Session cookies required.")
            return {
                'success': False,
                'message': f'LinkedIn session file not found. Place valid linkedin_session.json in {SECRETS_DIR}.',
                'session_file_path': str(session_file)
            }

        logger.info("=" * 70)
        logger.info("🚀 [REAL SEND EXECUTED] Actually posting to LinkedIn...")
        logger.info(f"🚀 [REAL SEND] Content: {content[:100]}...")
        logger.info(f"🔑 [REAL SEND] Using session cookies from {session_file}")
        logger.info("=" * 70)

        return self._post_linkedin_with_cookies(content, session_file)

    def _post_linkedin_with_cookies(self, content: str, session_file: Path) -> Dict:
        """Post to LinkedIn using saved session cookies"""
        try:
            # Load session cookies
            with open(session_file, 'r') as f:
                session_data = json.load(f)

            cookies = session_data.get('cookies', [])

            with sync_playwright() as p:
                # Launch browser with persistent context to accept cookies
                user_data_dir = self.vault_path / 'linkedin_browser_data'
                user_data_dir.mkdir(exist_ok=True)

                context = p.chromium.launch_persistent_context(
                    user_data_dir=str(user_data_dir),
                    headless=True,
                    accept_downloads=True
                )

                page = context.pages[0] if context.pages else context.new_page()

                # Inject cookies
                logger.info(f"🍪 Injecting {len(cookies)} cookies")
                context.add_cookies(cookies)

                # Navigate to LinkedIn feed
                logger.info("🌐 Navigating to LinkedIn feed...")
                page.goto('https://www.linkedin.com/feed/', wait_until='load', timeout=60000)
                page.wait_for_timeout(3000)

                # Verify we're logged in by checking for feed elements
                current_url = page.url
                if 'login' in current_url.lower() or 'signin' in current_url.lower():
                    context.close()
                    logger.error("❌ LinkedIn session expired. Need fresh session cookies.")
                    return {
                        'success': False,
                        'message': 'LinkedIn session expired. Please refresh session cookies.',
                        'platform': 'linkedin'
                    }

                # Create post
                logger.info("📝 Creating LinkedIn post...")

                # Step 1: Click "Start a post" button using text matching
                logger.info("🔍 Looking for 'Start a post' button...")
                start_post = page.get_by_text('Start a post', exact=True).first
                if start_post.count() > 0 and start_post.is_visible():
                    start_post.click()
                    logger.info("✅ Clicked 'Start a post'")
                else:
                    context.close()
                    return {'success': False, 'message': 'Could not find "Start a post" button on LinkedIn feed'}

                page.wait_for_timeout(2000)

                # Step 2: Find the text input (try multiple selectors with increasing waits)
                logger.info("🔍 Looking for share box text editor...")
                textbox = page.locator('[contenteditable="true"]').first
                for attempt in range(5):
                    if textbox.count() > 0:
                        break
                    page.wait_for_timeout(1500)
                    textbox = page.locator('[contenteditable="true"]').first

                if textbox.count() == 0:
                    context.close()
                    return {'success': False, 'message': 'Post textbox not found after clicking Start a post'}

                # Step 3: Type content character by character (triggers React events)
                logger.info("📝 Typing content into editor...")
                textbox.click()
                page.wait_for_timeout(500)
                textbox.type(content, delay=20)
                logger.info("✅ Content typed in post editor")
                page.wait_for_timeout(2000)

                # Step 4: Find and click Post button inside the Shadow DOM
                logger.info("🚀 Looking for Post button in Shadow DOM...")
                page.wait_for_timeout(1000)

                result = textbox.evaluate("""
                (el) => {
                    const root = el.getRootNode();
                    if (!(root instanceof ShadowRoot)) return 'not_in_shadow';
                    const btns = root.querySelectorAll('button');
                    for (const b of btns) {
                        const text = (b.innerText || '').trim();
                        if (text === 'Post') {
                            if (b.disabled) {
                                return 'post_button_disabled';
                            }
                            b.click();
                            return 'clicked_post';
                        }
                    }
                    return 'no_post_button';
                }
                """)

                logger.info(f"📋 Shadow DOM result: {result}")

                if result == 'post_button_disabled':
                    logger.info("⚠️ Post button is disabled - waiting and retrying...")
                    page.wait_for_timeout(3000)
                    # Check again after waiting
                    result = textbox.evaluate("""
                    (el) => {
                        const root = el.getRootNode();
                        if (!(root instanceof ShadowRoot)) return 'not_in_shadow';
                        const btns = root.querySelectorAll('button');
                        for (const b of btns) {
                            if ((b.innerText || '').trim() === 'Post') {
                                if (b.disabled) return 'post_button_disabled';
                                b.click();
                                return 'clicked_post';
                            }
                        }
                        return 'no_post_button';
                    }
                    """)
                    logger.info(f"📋 Retry result: {result}")

                    if result == 'post_button_disabled':
                        # Try forcing click on disabled button anyway
                        logger.info("⚠️ Trying force-click on disabled Post button...")
                        textbox.evaluate("""
                        (el) => {
                            const root = el.getRootNode();
                            const btns = root.querySelectorAll('button');
                            for (const b of btns) {
                                if ((b.innerText || '').trim() === 'Post') {
                                    // Dispatch click with bubbles:true to simulate user click
                                    b.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));
                                    b.dispatchEvent(new PointerEvent('pointerdown', {bubbles: true}));
                                    b.dispatchEvent(new PointerEvent('pointerup', {bubbles: true}));
                                    return 'force_clicked';
                                }
                            }
                            return 'no_button';
                        }
                        """)
                        page.wait_for_timeout(3000)

                elif result == 'clicked_post':
                    logger.info("✅ Post button clicked!")
                    page.wait_for_timeout(3000)
                elif result == 'not_in_shadow':
                    logger.error("❌ Contenteditable not in Shadow DOM - unexpected")
                elif result == 'no_post_button':
                    logger.error("❌ No Post button found in Shadow DOM")

                # If JS methods didn't work, try pressing Enter key
                ce_after = page.locator('[contenteditable="true"]').first
                if ce_after.count() > 0 and ce_after.is_visible():
                    logger.info("⌨️ Trying keyboard submit methods...")
                    for key_combo in ['Control+Enter', 'Meta+Enter', 'Enter']:
                        if ce_after.count() == 0:
                            break
                        ce_after.focus()
                        page.keyboard.press(key_combo)
                        page.wait_for_timeout(2000)
                        ce_after = page.locator('[contenteditable="true"]').first
                        if ce_after.count() == 0:
                            logger.info(f"✅ {key_combo} submitted the post!")
                            break

                # Final verification
                ce_final = page.locator('[contenteditable="true"]').first
                still_open = ce_final.count() > 0

                if not still_open:
                    logger.info("=" * 70)
                    logger.info("✅ [REAL SEND EXECUTED] LinkedIn post published successfully!")
                    logger.info("=" * 70)
                    context.close()
                    self._save_post_log('linkedin', content, status='published')
                    return {
                        'success': True,
                        'platform': 'linkedin',
                        'message': '[REAL SEND] Post published to LinkedIn',
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    context.close()
                    return {'success': False, 'message': 'Could not post to LinkedIn - share box still open after all methods'}

        except Exception as e:
            logger.error(f"❌ LinkedIn post failed: {e}")
            return {'success': False, 'message': str(e)}

    def post_to_facebook(self, content: str, approved: bool = False) -> Dict:
        """Post content to Facebook using saved session cookies (no password login)."""
        logger.info(f"Posting to Facebook...")

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
            logger.info(f"[DRY RUN] Facebook post would be published")
            return self._save_draft('facebook', content, dry_run=True)

        if not PLAYWRIGHT_AVAILABLE:
            return {'success': False, 'platform': 'facebook', 'message': 'Playwright not installed'}

        session_file = get_secret_path('facebook_session.json')
        if not session_file.exists():
            return {
                'success': False,
                'platform': 'facebook',
                'message': f'Facebook session not found at {session_file}. Save cookies first.',
                'session_file': str(session_file)
            }

        poster = FacebookPoster()
        result = poster.post(content)
        if result['success']:
            self._save_post_log('facebook', content, status='published')
        return result

    def post_to_instagram(self, content: str, image_path: Optional[str] = None, approved: bool = False) -> Dict:
        """Post content to Instagram using saved session cookies."""
        logger.info(f"Posting to Instagram...")

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
            logger.info(f"[DRY RUN] Instagram post would be published")
            return self._save_draft('instagram', content, dry_run=True)

        if not PLAYWRIGHT_AVAILABLE:
            return {'success': False, 'platform': 'instagram', 'message': 'Playwright not installed'}

        session_file = get_secret_path('instagram_session.json')
        if not session_file.exists():
            return {
                'success': False,
                'platform': 'instagram',
                'message': f'Instagram session not found at {session_file}. Save cookies first.',
                'session_file': str(session_file)
            }

        poster = InstagramPoster()
        result = poster.post(content, image_path=image_path)
        if result.get('success'):
            self._save_post_log('instagram', content, status='published')
        return result

    def post_to_twitter(self, content: str, approved: bool = False) -> Dict:
        """Post content to Twitter/X using saved session cookies (no password login)."""
        logger.info(f"Posting to Twitter/X...")

        # Validate tweet length
        if len(content) > 280:
            return {'success': False, 'platform': 'twitter', 'message': f'Tweet too long: {len(content)}/280 characters'}

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
            logger.info(f"[DRY RUN] Tweet would be published")
            return self._save_draft('twitter', content, dry_run=True)

        if not PLAYWRIGHT_AVAILABLE:
            return {'success': False, 'platform': 'twitter', 'message': 'Playwright not installed'}

        session_file = get_secret_path('twitter_session.json')
        if not session_file.exists():
            return {
                'success': False,
                'platform': 'twitter',
                'message': f'Twitter session not found at {session_file}. Save cookies first.',
                'session_file': str(session_file)
            }

        xagent = XAgent()
        result = xagent.post(content)
        if result['success']:
            self._save_post_log('twitter', content, status='published')
        return result

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
        """Get status of all platforms (session-cookie based)"""
        linkedin_session = get_secret_path('linkedin_session.json').exists()
        twitter_session = get_secret_path('twitter_session.json').exists()
        facebook_session = get_secret_path('facebook_session.json').exists()
        instagram_session = get_secret_path('instagram_session.json').exists()
        return {
            'linkedin': {
                'configured': linkedin_session,
                'auth_method': 'session_cookies' if linkedin_session else 'none',
                'dry_run': self.dry_run,
                'approval_required': self.require_approval
            },
            'facebook': {
                'configured': facebook_session,
                'auth_method': 'session_cookies' if facebook_session else 'none',
                'dry_run': self.dry_run,
                'approval_required': self.require_approval
            },
            'instagram': {
                'configured': instagram_session,
                'auth_method': 'session_cookies' if instagram_session else 'none',
                'dry_run': self.dry_run,
                'approval_required': self.require_approval
            },
            'twitter': {
                'configured': twitter_session,
                'auth_method': 'session_cookies' if twitter_session else 'none',
                'dry_run': self.dry_run,
                'approval_required': self.require_approval
            },
            'playwright_available': PLAYWRIGHT_AVAILABLE
        }


# CLI Interface
if __name__ == '__main__':
    if _MCP_MODE:
        # ---- Real MCP protocol server over stdio (Silver #5 / Gold #3, #6) ----
        # Speaks JSON-RPC over stdin/stdout via the official `mcp` SDK. The
        # MCPSocialServer logic class is reused unchanged; mcp_server_base wraps
        # each method as an advertised tool.
        from mcp_server_base import ToolSpec, run_mcp_server

        server = MCPSocialServer()

        def _post_social(a):
            platform = (a.get('platform') or '').lower()
            content = a.get('content', '')
            approved = bool(a.get('approved', False))
            if platform == 'linkedin':
                return server.post_to_linkedin(content, approved=approved)
            if platform == 'facebook':
                return server.post_to_facebook(content, approved=approved)
            if platform == 'instagram':
                return server.post_to_instagram(content, image_path=a.get('image_path'), approved=approved)
            if platform == 'twitter':
                return server.post_to_twitter(content, approved=approved)
            return {'success': False, 'message': f'Unknown platform: {platform!r}'}

        tools = [
            ToolSpec(
                name='post_social',
                description=('Publish a post to a social platform (linkedin/facebook/'
                             'instagram/twitter). Honors DRY_RUN and the human-approval '
                             'gate; pass approved=true to publish for real.'),
                input_schema={
                    'type': 'object',
                    'properties': {
                        'platform': {'type': 'string', 'enum': ['linkedin', 'facebook', 'instagram', 'twitter']},
                        'content': {'type': 'string'},
                        'image_path': {'type': 'string', 'description': 'Optional image path (instagram)'},
                        'approved': {'type': 'boolean', 'default': False},
                    },
                    'required': ['platform', 'content'],
                },
                handler=_post_social,
            ),
            ToolSpec(
                name='draft_social',
                description='Save a social post as a local draft (never publishes).',
                input_schema={
                    'type': 'object',
                    'properties': {
                        'platform': {'type': 'string', 'enum': ['linkedin', 'facebook', 'instagram', 'twitter']},
                        'content': {'type': 'string'},
                    },
                    'required': ['platform', 'content'],
                },
                handler=lambda a: server._save_draft(a['platform'], a.get('content', ''), dry_run=True),
            ),
            ToolSpec(
                name='get_platform_status',
                description='Report configured/available status for each social platform.',
                input_schema={'type': 'object', 'properties': {}},
                handler=lambda a: server.get_platform_status(),
            ),
        ]

        run_mcp_server('ai-employee-social', tools)
    else:
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
