r"""
Secrets Configuration for AI Employee Vault

ALL sensitive files now live OUTSIDE the vault:
    C:\Users\%USERNAME%\.ai_employee\secrets\

This module provides a consistent way to load secrets
across all Python files. Import and call load_secrets() early.

Usage:
    from secrets_config import SECRETS_DIR, load_secrets, get_secret_path
    load_secrets()
    creds_path = get_secret_path('credentials.json')
"""

import os
from pathlib import Path

# Singleton: compute once
_SECRETS_DIR = Path(os.environ.get(
    'SECRETS_DIR',
    Path.home() / '.ai_employee' / 'secrets'
))

SECRETS_DIR = _SECRETS_DIR


def load_secrets():
    """Load all .env files from secrets directory into os.environ."""
    if not SECRETS_DIR.exists():
        print(f"[SECRETS] WARNING: Secrets directory not found: {SECRETS_DIR}")
        return

    # Load the merged .env first, then any specific ones
    for env_file in ['.env', '.env.local', '.env.cloud', '.env.linkedin']:
        path = SECRETS_DIR / env_file
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#') or '=' not in line:
                        continue
                    key, _, value = line.partition('=')
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key and key not in os.environ:
                        os.environ[key] = value

    # Also register convenience env vars for paths
    os.environ.setdefault('SECRETS_DIR', str(SECRETS_DIR))
    os.environ.setdefault('DRY_RUN', 'true')
    os.environ.setdefault('REQUIRE_APPROVAL', 'true')

    print(f"[SECRETS] Loaded from {SECRETS_DIR}")


def get_secret_path(filename: str) -> Path:
    """Return the full path to a secret file inside the secrets directory.

    Respects explicit env vars named after the file, e.g.:
        GMAIL_CREDENTIALS_PATH
        GMAIL_TOKEN_PATH
        LINKEDIN_SESSION_PATH
    """
    env_key = filename.upper().replace('.', '_').replace('-', '_') + '_PATH'
    override = os.environ.get(env_key)
    if override:
        return Path(override)
    return SECRETS_DIR / filename


# Auto-load on import (callable explicitly too)
if not os.environ.get('SECRETS_LOADED'):
    load_secrets()
    os.environ['SECRETS_LOADED'] = '1'
