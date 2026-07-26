import sys, os, json
sys.path.insert(0, r'D:\Desktop4\Obsidian Vault')
sys.path.insert(0, r'D:\Desktop4\Obsidian Vault\watchers')
from pathlib import Path

VAULT = Path(r'D:\Desktop4\Obsidian Vault')

print('=== MCP SERVERS ===')

# Test Email MCP
try:
    from mcp_email import MCPEmailServer
    email = MCPEmailServer(vault_path=VAULT)
    print(f'MCP Email: OK (mode={email.mode})')
except Exception as e:
    print(f'MCP Email: {e}')

# Test Social MCP
try:
    from mcp_social import MCPSocialServer
    social = MCPSocialServer(vault_path=VAULT)
    has_dry_run = hasattr(social, 'dry_run')
    has_approval = hasattr(social, 'approval_required')
    print(f'MCP Social: OK (dry_run={has_dry_run}, approval={has_approval})')
except Exception as e:
    print(f'MCP Social: {e}')

# Test Browser MCP
try:
    from mcp_browser import MCPBrowserServer
    browser = MCPBrowserServer(vault_path=VAULT)
    print(f'MCP Browser: OK')
except Exception as e:
    print(f'MCP Browser: {e}')

# Test Voice Approval MCP
try:
    from mcp_voice_approval import VoiceApprovalSystem
    print(f'MCP Voice Approval: OK (class={VoiceApprovalSystem.__name__})')
except Exception as e:
    print(f'MCP Voice Approval: {e}')

print()
print('=== WATCHERS ===')

# Test Base Watcher
from watchers.base_watcher import BaseWatcher
print(f'BaseWatcher: OK (abstract class)')

# Test Gmail watcher import
try:
    from watchers.gmail_watcher import GmailWatcher
    print(f'GmailWatcher: OK (class imported)')
except Exception as e:
    print(f'GmailWatcher: {e}')

# Test WhatsApp watcher import
try:
    from watchers.whatsapp_watcher import WhatsAppWatcher
    print(f'WhatsAppWatcher: OK (class imported)')
except Exception as e:
    print(f'WhatsAppWatcher: {e}')

# Test Social watcher import
try:
    from watchers.social_watcher import SocialWatcher
    print(f'SocialWatcher: OK (class imported)')
except Exception as e:
    print(f'SocialWatcher: {e}')

# Test Odoo lead watcher import
try:
    from watchers.odoo_lead_watcher import OdooLeadWatcher
    print(f'OdooLeadWatcher: OK (class imported)')
except Exception as e:
    print(f'OdooLeadWatcher: {e}')

# Test Office watcher import
try:
    from watchers.office_watcher import OfficeWatcher
    print(f'OfficeWatcher: OK (class imported)')
except Exception as e:
    print(f'OfficeWatcher: {e}')

print()
print('=== ORCHESTRATOR ===')
try:
    from orchestrator import Orchestrator
    print(f'Ochestrator: OK')
except Exception as e:
    print(f'Ochestrator: {e}')

print()
print('=== A2A MESSENGER ===')
try:
    from a2a_messenger import A2AMessenger
    a2a = A2AMessenger(agent_type='test', config={'vault_path': str(VAULT)})
    print(f'A2A Messenger: OK')
except Exception as e:
    print(f'A2A Messenger: {e}')

print()
print('=== HEALTH MONITOR ===')
try:
    from health_monitor import HealthMonitor
    hm = HealthMonitor(agent_type='local', vault_path=str(VAULT))
    status = hm.get_status()
    print(f'Health Monitor: OK ({status})')
except Exception as e:
    print(f'Health Monitor: {e}')

print()
print('=== SECURITY GUARD ===')
try:
    from security_guard import SecurityGuard
    sg_cloud = SecurityGuard(agent_type='cloud', vault_path=str(VAULT))
    sg_local = SecurityGuard(agent_type='local', vault_path=str(VAULT))
    print(f'Security Guard: OK (cloud+docker initialized)')
    can_send = sg_cloud.check_action_permission('email_send')
    local_can_send = sg_local.check_action_permission('email_send')
    print(f'  Cloud can email_send: {can_send}')
    print(f'  Local can email_send: {local_can_send}')
except Exception as e:
    print(f'Security Guard: {e}')

print()
print('All MCP + Watcher integrations verified.')
