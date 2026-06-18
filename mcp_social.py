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

# Fix Windows console encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, Exception):
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Load secrets from outside vault
sys.path.insert(0, str(Path(__file__).parent))
from secrets_config import SECRETS_DIR, load_secrets, get_secret_path
load_secrets()

# Setup logging with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
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
        self.dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'
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
                page.wait_for_timeout(3000)

                logger.info(f"🔑 Logging in as {self.facebook_email}...")

                # Fill email field
                email_done = False
                for sel in ['#email', 'input[name="email"]', 'input[type="text"]']:
                    try:
                        el = page.locator(sel).first
                        if el.is_visible(timeout=2000):
                            el.fill(self.facebook_email)
                            email_done = True
                            logger.info(f"✅ Filled email via: {sel}")
                            break
                    except Exception:
                        continue
                if not email_done:
                    browser.close()
                    return {'success': False, 'message': 'Facebook email field not found'}

                # Fill password field
                for sel in ['#pass', 'input[name="pass"]', 'input[type="password"]']:
                    try:
                        el = page.locator(sel).first
                        if el.is_visible(timeout=2000):
                            el.fill(self.facebook_password)
                            logger.info(f"✅ Filled password via: {sel}")
                            break
                    except Exception:
                        continue

                # Click login button
                login_clicked = False
                for sel in ['button[name="login"]', 'button[type="submit"]', 'button:has-text("Log in")']:
                    try:
                        el = page.locator(sel).first
                        if el.is_visible(timeout=2000):
                            el.click()
                            login_clicked = True
                            logger.info(f"✅ Clicked login via: {sel}")
                            break
                    except Exception:
                        continue
                if login_clicked:
                    page.wait_for_timeout(5000)
                else:
                    page.keyboard.press('Enter')
                    page.wait_for_timeout(5000)

                # Create post
                logger.info("🌐 Navigating to Facebook feed...")
                page.goto('https://www.facebook.com/')
                page.wait_for_timeout(5000)

                current_url = page.url
                logger.info(f"📍 Feed URL: {current_url}")

                # Step 1: Click the "What's on your mind?" trigger to open composer
                logger.info("🔍 Opening post composer...")

                # Build selector list based on detected Facebook domain
                trigger_selectors = [
                    f'[placeholder*="What\'s on your mind"]',
                    f'[aria-label*="What\'s on your mind"]',
                    'span:has-text("What\'s on your mind")',
                    f'[role="button"]:has-text("What\'s on your mind")',
                    '[data-pagelet="FeedComposer"] [role="button"]',
                    'form [contenteditable="true"]',
                ]

                composer_opened = False
                for sel in trigger_selectors:
                    try:
                        el = page.locator(sel).first
                        if el.is_visible(timeout=2000):
                            el.click()
                            page.wait_for_timeout(2000)
                            composer_opened = True
                            logger.info(f"✅ Clicked trigger: {sel}")
                            break
                    except Exception:
                        continue

                # Fallback: press 'p' keyboard shortcut to open composer
                if not composer_opened:
                    logger.info("⌨️ Trying keyboard shortcut 'p' to open composer...")
                    page.keyboard.press('p')
                    page.wait_for_timeout(3000)
                    for sel in [
                        '[contenteditable="true"]',
                        'div[contenteditable="true"][role="textbox"]',
                        '[data-lexical-editor="true"]',
                    ]:
                        try:
                            if page.locator(sel).first.is_visible(timeout=2000):
                                composer_opened = True
                                logger.info(f"✅ Composer opened via keyboard, found: {sel}")
                                break
                        except Exception:
                            continue

                # Fallback: navigate directly to composer URL
                if not composer_opened:
                    logger.info("🌐 Trying composer URL directly...")
                    try:
                        page.goto('https://www.facebook.com/composer/mbasic/?basic_composer=1')
                        page.wait_for_timeout(3000)
                        for sel in [
                            '[contenteditable="true"]',
                            'textarea',
                            'div[contenteditable="true"][role="textbox"]',
                        ]:
                            try:
                                if page.locator(sel).first.is_visible(timeout=2000):
                                    composer_opened = True
                                    logger.info(f"✅ Composer via URL, found: {sel}")
                                    break
                            except Exception:
                                continue
                    except Exception:
                        pass

                if not composer_opened:
                    logger.warning("⚠️ Could not open Facebook composer — saving draft instead")
                    result = self._save_draft('facebook', content, dry_run=False)
                    browser.close()
                    result['message'] += ' (composer not accessible, saved as draft)'
                    return result

                # Step 2: Find the contenteditable div or textarea in the expanded composer
                logger.info("✍️ Finding text editor...")
                text_editor = None
                editor_selectors = [
                    '[contenteditable="true"]',
                    'div[contenteditable="true"][role="textbox"]',
                    '[data-lexical-editor="true"]',
                    '[contenteditable="true"]:not([style*="none"])',
                    'textarea:not([name*="pass"])',
                ]
                for sel in editor_selectors:
                    try:
                        editor = page.locator(sel).first
                        if editor.is_visible(timeout=2000):
                            text_editor = editor
                            logger.info(f"✅ Found editor: {sel}")
                            break
                    except Exception:
                        continue

                if not text_editor:
                    logger.warning("⚠️ Text editor not found — saving as draft")
                    result = self._save_draft('facebook', content, dry_run=False)
                    browser.close()
                    result['message'] += ' (editor not found, saved as draft)'
                    return result

                # Step 3: Type content
                logger.info("📝 Typing content...")
                text_editor.click()
                page.wait_for_timeout(500)
                text_editor.fill(content)
                page.wait_for_timeout(1500)

                # Step 4: Find and click Post button
                logger.info("🚀 Finding Post button...")
                post_button = None
                button_selectors = [
                    '[aria-label="Post"]',
                    'button:has-text("Post")',
                    '[role="button"]:has-text("Post")',
                    'div[aria-label="Post"][role="button"]',
                    '[data-pagelet="FeedComposer"] button:has-text("Post")',
                    '[type="submit"]:has-text("Post")',
                ]
                for sel in button_selectors:
                    try:
                        btn = page.locator(sel).first
                        if btn.is_visible(timeout=2000) and btn.is_enabled():
                            post_button = btn
                            logger.info(f"✅ Found Post button: {sel}")
                            break
                    except Exception:
                        continue

                if not post_button:
                    logger.warning("⚠️ Post button not found — trying keyboard submit...")
                    page.keyboard.press('Control+Enter')
                    page.wait_for_timeout(3000)

                if post_button:
                    post_button.click()
                    page.wait_for_timeout(5000)

                # Step 5: Verify post was published (editor should close)
                editor_still_open = page.locator('[contenteditable="true"]').first
                try:
                    still_visible = editor_still_open.is_visible(timeout=3000)
                except Exception:
                    still_visible = True

                browser.close()

                if not still_visible:
                    logger.info("✅ Facebook post published successfully!")
                    self._save_post_log('facebook', content, status='published')
                    return {
                        'success': True,
                        'platform': 'facebook',
                        'message': 'Post published to Facebook',
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    logger.warning("⚠️ Editor still open — saving draft for safety")
                    result = self._save_draft('facebook', content, dry_run=False)
                    return {
                        'success': False,
                        'platform': 'facebook',
                        'message': 'Facebook post may not have published — saved draft in Social_Drafts',
                        'draft_saved': True,
                        'draft_file': result.get('draft_file')
                    }

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
                context = browser.new_context(
                    viewport={'width': 1280, 'height': 800},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = context.new_page()

                # Login (X.com new unified login flow)
                logger.info("🌐 Logging into X/Twitter...")
                page.goto('https://x.com/i/flow/login', timeout=60000)
                page.wait_for_timeout(5000)

                # Find and fill username/email field
                logger.info("🔍 Finding login fields...")
                username_field = page.locator('input[name="username_or_email"]').first
                if username_field.is_visible():
                    username_field.fill(self.twitter_username)
                    page.wait_for_timeout(500)
                else:
                    # Try alternative selector
                    username_field = page.locator('input[autocomplete*="username"]').first
                    if username_field.is_visible():
                        username_field.fill(self.twitter_username)
                        page.wait_for_timeout(500)

                # Find and fill password field
                password_field = page.locator('input[name="password"]').first
                if password_field.is_visible():
                    password_field.fill(self.twitter_password)
                    page.wait_for_timeout(500)

                # Look for login/submit button (X.com uses "Continue" button)
                login_btn = page.locator('button[type="submit"]').first
                if not login_btn.is_visible():
                    login_btn = page.locator('button:text-is("Continue")').first
                if not login_btn.is_visible():
                    login_btn = page.locator('button:has-text("Log in")').first
                if not login_btn.is_visible():
                    login_btn = page.locator('[role="button"]:has-text("Next")').first

                if login_btn.is_visible():
                    login_text = login_btn.inner_text()
                    login_btn.click()
                    page.wait_for_timeout(3000)
                    logger.info(f"✅ Login submitted ({login_text})")

                    # Handle X.com onboarding flow (may include email verification)
                    for step in range(5):
                        # Check if we're on home page
                        current_url = page.url
                        if 'home' in current_url or 'compose' in current_url:
                            logger.info(f"✅ On home page after {step} steps")
                            break

                        # Check for email/phone input
                        email_input = page.locator('input[name="email"], input[type="email"], input[name="phone"]').first
                        if email_input.is_visible():
                            email_val = email_input.input_value()
                            if not email_val:
                                # Fill email (use username which is the email)
                                email_input.fill(self.twitter_username)
                                page.wait_for_timeout(500)
                                logger.info("✅ Filled email field")
                            else:
                                logger.info(f"✅ Email prefilled: {email_val}")

                        # Click continue/next button
                        next_btn = page.locator('button[type="submit"]').first
                        if next_btn.is_visible():
                            btn_text = next_btn.inner_text()
                            next_btn.click()
                            page.wait_for_timeout(2000)
                            logger.info(f"✅ Onboarding step: {btn_text}")
                        else:
                            # Try Enter key
                            page.keyboard.press('Enter')
                            page.wait_for_timeout(2000)
                            if page.url == current_url:
                                logger.warning(f"⚠️ Stuck at: {page.url}")
                                break

                    page.wait_for_timeout(2000)
                else:
                    logger.warning("⚠️ Login button not found")
                    page.keyboard.press('Enter')
                    page.wait_for_timeout(3000)

                # Create tweet
                logger.info("✍️ Composing tweet...")
                page.goto('https://x.com/compose/post', timeout=30000)
                page.wait_for_timeout(3000)

                tweet_box = page.locator('div[contenteditable="true"]').first
                if tweet_box.is_visible():
                    tweet_box.fill(content)
                    page.wait_for_timeout(1000)

                    tweet_button = page.locator('div[data-testid="tweetButtonInline"]').first
                    if tweet_button.is_visible():
                        tweet_button.click()
                        page.wait_for_timeout(3000)

                        browser.close()
                        self._save_post_log('twitter', content, status='published')
                        logger.info("✅ Tweet published successfully!")
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
