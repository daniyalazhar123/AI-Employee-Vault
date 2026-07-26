"""
X Agent - Persistent Twitter/X Automation with Saved Session Cookies

Uses Playwright with pre-saved browser cookies (not password login) to
bypass X.com bot detection and rate limiting. Same approach as LinkedIn
session cookie flow.

Session file (created once manually, reused forever):
    C:/Users/<USER>/.ai_employee/secrets/twitter_session.json

How to save session:
    1. python -c "from playwright.sync_api import sync_playwright; p=sync_playwright().start(); b=p.chromium.launch(headless=False); ctx=b.new_context(); ctx.new_page().goto('https://x.com/i/flow/login'); input('Login manually, then press Enter...'); ctx.storage_state(path=r'C:/Users/%USERNAME%/.ai_employee/secrets/twitter_session.json'); b.close(); p.stop()"
    2. Delete the file and repeat when cookies expire (typically 6-12 months)

Usage:
    from x_agent import XAgent
    agent = XAgent()
    result = agent.post("Hello from AI Employee!")
"""

import json
import logging
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict

logger = logging.getLogger('XAgent')

PLAYWRIGHT_AVAILABLE = False
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    pass

sys.path.insert(0, str(Path(__file__).parent))
from secrets_config import SECRETS_DIR, get_secret_path


SESSION_FILE = 'twitter_session.json'


class XAgent:
    """Persistent Twitter/X poster using saved session cookies."""

    def __init__(self, secrets_dir: Optional[Path] = None):
        self.secrets_dir = Path(secrets_dir) if secrets_dir else SECRETS_DIR
        self.session_path = self.secrets_dir / SESSION_FILE
        self.drafts_folder = Path(__file__).parent / 'Social_Drafts'
        self.drafts_folder.mkdir(parents=True, exist_ok=True)

    def post(self, content: str) -> Dict:
        """Post a tweet. Returns dict with success/message."""
        if not PLAYWRIGHT_AVAILABLE:
            return {'success': False, 'platform': 'twitter', 'message': 'Playwright not installed'}

        if len(content) > 280:
            return {'success': False, 'platform': 'twitter', 'message': f'Tweet too long: {len(content)}/280'}

        if not self.session_path.exists():
            return {
                'success': False,
                'platform': 'twitter',
                'message': f'Twitter session not found at {self.session_path}. Save cookies first.',
                'session_file': str(self.session_path)
            }

        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)
                context = browser.new_context(
                    viewport={'width': 1280, 'height': 800},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = context.new_page()

                with open(self.session_path, 'r') as f:
                    state = json.load(f)
                cookies = state.get('cookies', [])
                context.add_cookies(cookies)

                logger.info(f"Loaded {len(cookies)} session cookies")

                page.goto('https://x.com/home', wait_until='load', timeout=60000)
                page.wait_for_timeout(3000)

                if not self._is_logged_in(page):
                    browser.close()
                    return {
                        'success': False,
                        'platform': 'twitter',
                        'message': 'Twitter session expired. Save fresh cookies.',
                        'session_file': str(self.session_path)
                    }

                result = self._compose_and_post(page, content)
                browser.close()

                if result['success']:
                    self._save_post_log(content)

                return result

        except Exception as e:
            logger.error(f"Twitter post failed: {e}")
            return {'success': False, 'platform': 'twitter', 'message': str(e)}

    def _is_logged_in(self, page) -> bool:
        current_url = page.url.lower()
        if 'login' in current_url or 'flow' in current_url:
            logger.warning("Redirected to login page — session expired")
            return False
        try:
            page.wait_for_selector('[data-testid="SideNav_NewTweet_Button"]', timeout=10000)
            return True
        except Exception:
            pass
        try:
            page.wait_for_selector('[aria-label="Tweet"]', timeout=5000)
            return True
        except Exception:
            pass
        try:
            compose_link = page.locator('a[href="/compose/post"]')
            if compose_link.count() > 0:
                return True
        except Exception:
            pass
        return False

    def _compose_and_post(self, page, content: str) -> Dict:
        logger.info("Composing tweet...")
        page.goto('https://x.com/compose/post', wait_until='load', timeout=30000)
        page.wait_for_timeout(3000)

        tweet_box = page.locator('[data-testid="tweetTextarea_0"]').first
        if tweet_box.count() == 0:
            tweet_box = page.locator('div[contenteditable="true"][role="textbox"]').first
        if tweet_box.count() == 0:
            tweet_box = page.locator('[data-testid="tweetTextarea"]').first
        if tweet_box.count() == 0:
            return {'success': False, 'platform': 'twitter', 'message': 'Tweet textarea not found'}

        tweet_box.click()
        page.wait_for_timeout(300)
        tweet_box.fill(content)
        page.wait_for_timeout(1500)

        post_btn = page.locator('[data-testid="tweetButtonInline"]').first
        if post_btn.count() == 0:
            post_btn = page.locator('[data-testid="tweetButton"]').first
        if post_btn.count() == 0:
            post_btn = page.locator('button:has-text("Post")').first

        if post_btn.count() > 0 and post_btn.is_visible():
            post_btn.click()
            page.wait_for_timeout(4000)
            logger.info("Tweet published successfully!")
            return {
                'success': True,
                'platform': 'twitter',
                'message': 'Tweet published to X/Twitter',
                'timestamp': datetime.now().isoformat()
            }

        page.keyboard.press('Control+Enter')
        page.wait_for_timeout(3000)
        current_url = page.url.lower()
        if 'compose' not in current_url and 'home' in current_url:
            logger.info("Tweet submitted via Ctrl+Enter")
            return {
                'success': True,
                'platform': 'twitter',
                'message': 'Tweet published to X/Twitter',
                'timestamp': datetime.now().isoformat()
            }

        return {'success': False, 'platform': 'twitter', 'message': 'Could not find post button'}

    def _save_post_log(self, content: str):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = Path(__file__).parent / 'Logs' / f'twitter_post_{timestamp}.md'
        log_file.parent.mkdir(parents=True, exist_ok=True)
        log_file.write_text(
            f"---\ntype: twitter_post_log\nplatform: Twitter\n"
            f"posted: {datetime.now().isoformat()}\nstatus: published\n---\n\n"
            f"# Tweet\n\n{content}\n\n---\n*Posted via XAgent*\n",
            encoding='utf-8'
        )

    @staticmethod
    def save_session_guide() -> str:
        return (
            "Run this in Python (headless=False browser will open):\n\n"
            "from playwright.sync_api import sync_playwright\n"
            "import json\n"
            "secrets_dir = r'C:\\Users\\<USER>\\.ai_employee\\secrets'\n"
            "with sync_playwright() as p:\n"
            "    b = p.chromium.launch(headless=False)\n"
            "    ctx = b.new_context(viewport={'width': 1280, 'height': 800})\n"
            "    page = ctx.new_page()\n"
            "    page.goto('https://x.com/i/flow/login')\n"
            "    input('Login manually, then press Enter...')\n"
            "    state = ctx.storage_state()\n"
            f"    with open(f'{{secrets_dir}}\\\\{SESSION_FILE}', 'w') as f:\n"
            "        json.dump(state, f, indent=2)\n"
            "    b.close()\n"
        )


if __name__ == '__main__':
    from audit_logger import setup_logging
    setup_logging('XAgent')
    content = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else 'Hello from AI Employee XAgent!'
    agent = XAgent()
    result = agent.post(content)
    print(json.dumps(result, indent=2))
