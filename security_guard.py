#!/usr/bin/env python3
"""
🔒 SECURITY GUARD - Platinum Tier
Enforces Platinum security rules
Personal AI Employee Hackathon 0 - Platinum Tier

Security Rules:
1. Cloud Agent cannot send (draft only)
2. Local Agent requires approval
3. Secrets never sync
4. WhatsApp/Banking local only
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('security_guard.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('SecurityGuard')


class SecurityLevel(Enum):
    """Security clearance levels"""
    CLOUD_DRAFT_ONLY = "cloud_draft"
    LOCAL_EXECUTE = "local_execute"
    HUMAN_APPROVAL = "human_approval"
    LOCAL_ONLY = "local_only"


class SecurityGuard:
    """
    Security Guard for Platinum Tier
    
    Enforces:
    - Action permissions (cloud vs local)
    - Credential validation
    - Secret sync prevention
    - Audit logging
    """
    
    def __init__(self, agent_type: str, vault_path: str):
        self.agent_type = agent_type  # 'cloud' or 'local'
        self.vault = Path(vault_path)
        self.logs = self.vault / 'Logs'
        
        # Ensure logs folder exists
        self.logs.mkdir(parents=True, exist_ok=True)
        
        # Define action permissions
        self.action_permissions = {
            # Cloud-only actions (draft)
            'email_draft': SecurityLevel.CLOUD_DRAFT_ONLY,
            'social_draft': SecurityLevel.CLOUD_DRAFT_ONLY,
            'odoo_draft': SecurityLevel.CLOUD_DRAFT_ONLY,
            'whatsapp_draft': SecurityLevel.CLOUD_DRAFT_ONLY,
            
            # Local-only actions (execute)
            'email_send': SecurityLevel.LOCAL_EXECUTE,
            'social_post': SecurityLevel.LOCAL_EXECUTE,
            'odoo_post': SecurityLevel.LOCAL_EXECUTE,
            'odoo_payment': SecurityLevel.LOCAL_EXECUTE,
            'whatsapp_send': SecurityLevel.LOCAL_ONLY,
            'bank_payment': SecurityLevel.LOCAL_ONLY,
            'bank_transfer': SecurityLevel.LOCAL_ONLY,
            
            # Always require human approval
            'bulk_email': SecurityLevel.HUMAN_APPROVAL,
            'large_payment': SecurityLevel.HUMAN_APPROVAL,
            'contract_sign': SecurityLevel.HUMAN_APPROVAL,
            'refund': SecurityLevel.HUMAN_APPROVAL,
            'credit_note': SecurityLevel.HUMAN_APPROVAL,
        }
        
        # Forbidden files for git sync
        self.forbidden_files = [
            '.env',
            '.env.local',
            '.env.cloud',
            'credentials.json',
            'token.json',
            'token.pickle',
            'whatsapp_session',
            '*.session',
            '*.pickle',
            '*.pem',
            '*.key',
            '*.crt',
        ]
        
        # Load environment
        self._load_env()
        
        logger.info(f"🔒 Security Guard initialized ({agent_type})")
    
    def _load_env(self):
        """Load environment variables"""
        if self.agent_type == 'cloud':
            env_file = self.vault / '.env.cloud'
        else:
            env_file = self.vault / '.env.local'
        
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value
            logger.info(f"✅ Loaded environment from {env_file}")
        else:
            logger.warning(f"⚠️ Environment file not found: {env_file}")
    
    def check_action_permission(self, action_type: str) -> bool:
        """
        Check if agent can perform action
        
        Returns True if allowed, False otherwise
        """
        if action_type not in self.action_permissions:
            logger.warning(f"⚠️ Unknown action type: {action_type}")
            # Unknown actions require approval by default
            return False
        
        required_level = self.action_permissions[action_type]
        
        # Cloud restrictions
        if self.agent_type == 'cloud':
            if required_level in [
                SecurityLevel.LOCAL_EXECUTE,
                SecurityLevel.LOCAL_ONLY,
                SecurityLevel.HUMAN_APPROVAL
            ]:
                logger.warning(f"🔒 SECURITY: Cloud Agent cannot perform {action_type}")
                self._audit_action(action_type, False, 'permission_denied')
                return False
        
        # Human approval required
        if required_level == SecurityLevel.HUMAN_APPROVAL:
            logger.info(f"🔒 SECURITY: {action_type} requires human approval")
            self._audit_action(action_type, False, 'requires_approval')
            return False
        
        self._audit_action(action_type, True, 'permission_granted')
        return True
    
    def validate_credentials(self, credential_type: str) -> bool:
        """
        Validate that required credentials exist
        
        Returns True if credentials are present
        """
        required_vars = {
            'email': ['GMAIL_CLIENT_ID', 'GMAIL_CLIENT_SECRET', 'GMAIL_REFRESH_TOKEN'],
            'whatsapp': ['WHATSAPP_SESSION_PATH'],
            'banking': ['BANK_API_URL', 'BANK_API_KEY'],
            'odoo': ['ODOO_URL', 'ODOO_DB', 'ODOO_USERNAME', 'ODOO_API_KEY'],
            'social': ['LINKEDIN_ACCESS_TOKEN', 'FACEBOOK_ACCESS_TOKEN'],
            'twitter': ['TWITTER_BEARER_TOKEN'],
            'instagram': ['INSTAGRAM_ACCESS_TOKEN']
        }
        
        if credential_type not in required_vars:
            logger.warning(f"⚠️ Unknown credential type: {credential_type}")
            return False
        
        missing = []
        for var in required_vars[credential_type]:
            if var not in os.environ:
                missing.append(var)
        
        if missing:
            logger.error(f"🔒 SECURITY: Missing credentials: {', '.join(missing)}")
            self._audit_action(f'credential_check_{credential_type}', False, f'missing: {missing}')
            return False
        
        logger.info(f"✅ Credentials validated for {credential_type}")
        self._audit_action(f'credential_check_{credential_type}', True, 'validated')
        return True
    
    def check_secrets_sync(self) -> bool:
        """
        Check that no secrets are in git sync
        
        Returns True if secure, False if issues found
        """
        issues = []
        
        for pattern in self.forbidden_files:
            # Check if file exists and is tracked by git
            try:
                result = subprocess.run(
                    ['git', 'ls-files', '--error-unmatch', pattern],
                    cwd=self.vault,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    issues.append(f"Secret file in git: {pattern}")
            except:
                pass
        
        # Also check .gitignore
        gitignore_file = self.vault / '.gitignore'
        if gitignore_file.exists():
            gitignore_content = gitignore_file.read_text()
            for pattern in self.forbidden_files:
                if pattern not in gitignore_content:
                    issues.append(f"Pattern not in .gitignore: {pattern}")
        
        if issues:
            logger.error("🔒 SECURITY WARNING - Secrets may sync:")
            for issue in issues:
                logger.error(f"  - {issue}")
            return False
        
        logger.info("✅ No secrets in git sync")
        return True
    
    def _audit_action(self, action_type: str, success: bool, details: str):
        """Log action for security audit"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'agent_type': self.agent_type,
            'action_type': action_type,
            'success': success,
            'details': details
        }
        
        log_file = self.logs / 'Audit' / f"security_{datetime.now().strftime('%Y%m%d')}.jsonl"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def get_security_report(self) -> Dict:
        """Generate security report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'agent_type': self.agent_type,
            'vault_path': str(self.vault),
            'checks': {}
        }
        
        # Check credentials
        for cred_type in ['email', 'odoo', 'social']:
            report['checks'][f'credentials_{cred_type}'] = self.validate_credentials(cred_type)
        
        # Check secrets sync
        report['checks']['secrets_sync'] = self.check_secrets_sync()
        
        # Check .gitignore
        gitignore_file = self.vault / '.gitignore'
        report['checks']['gitignore_exists'] = gitignore_file.exists()
        
        # Overall status
        all_passed = all(report['checks'].values())
        report['overall_status'] = 'secure' if all_passed else 'issues_found'
        
        return report
    
    def run_security_check(self) -> bool:
        """Run comprehensive security check"""
        logger.info("="*60)
        logger.info("🔒 SECURITY CHECK STARTING")
        logger.info(f"🎯 Agent Type: {self.agent_type}")
        logger.info(f"📂 Vault: {self.vault}")
        logger.info("="*60)
        
        all_passed = True
        
        # Check 1: Secrets sync
        if not self.check_secrets_sync():
            all_passed = False
        
        # Check 2: Credentials
        for cred_type in ['email', 'odoo', 'social']:
            if not self.validate_credentials(cred_type):
                all_passed = False
        
        # Check 3: Action permissions
        logger.info("\n📋 Action Permission Matrix:")
        for action, level in self.action_permissions.items():
            can_do = self.check_action_permission(action)
            status = "✅" if can_do else "❌"
            logger.info(f"  {status} {action}: {level.value}")
        
        # Generate report
        report = self.get_security_report()
        
        # Save report
        report_file = self.logs / f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"\n📊 Security Report saved to: {report_file}")
        
        if all_passed:
            logger.info("✅ ALL SECURITY CHECKS PASSED")
        else:
            logger.error("❌ SECURITY ISSUES FOUND - Review report")
        
        return all_passed


def main():
    """Main entry point"""
    print("="*60)
    print("🔒 PLATINUM TIER - SECURITY GUARD")
    print("="*60)
    
    # Get agent type from argument
    agent_type = sys.argv[1] if len(sys.argv) > 1 else 'cloud'
    if agent_type not in ['cloud', 'local']:
        print("Usage: python security_guard.py [cloud|local] [vault_path]")
        sys.exit(1)
    
    # Get vault path
    vault_path = sys.argv[2] if len(sys.argv) > 2 else 'C:/Users/CC/Documents/Obsidian Vault'
    
    print(f"🎯 Agent Type: {agent_type}")
    print(f"📂 Vault Path: {vault_path}")
    print("\n🚀 Running security check...\n")
    
    guard = SecurityGuard(agent_type, vault_path)
    
    success = guard.run_security_check()
    
    if success:
        print("\n✅ All security checks passed!")
        sys.exit(0)
    else:
        print("\n❌ Security issues found - review logs")
        sys.exit(1)


if __name__ == '__main__':
    main()
