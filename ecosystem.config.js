const path = require('path');

const VAULT_PATH = path.resolve(__dirname);

module.exports = {
  apps: [
    {
      name: 'ai-orchestrator',
      script: path.join(VAULT_PATH, 'orchestrator.py'),
      interpreter: 'python',
      cwd: VAULT_PATH,
      watch: false,
      max_memory_restart: '2G',
      env: {
        PYTHONUNBUFFERED: '1',
        PYTHONIOENCODING: 'utf-8',
        VAULT_PATH: VAULT_PATH
      },
      error_file: path.join(VAULT_PATH, 'Logs', 'pm2-orchestrator-error.log'),
      out_file: path.join(VAULT_PATH, 'Logs', 'pm2-orchestrator-out.log'),
      log_date_format: 'YYYY-MM-DD HH:mm:ss'
    },
    {
      name: 'cloud-agent',
      script: path.join(VAULT_PATH, 'cloud_agent.py'),
      interpreter: 'python',
      cwd: VAULT_PATH,
      watch: false,
      max_memory_restart: '1G',
      env: {
        PYTHONUNBUFFERED: '1',
        PYTHONIOENCODING: 'utf-8',
        VAULT_PATH: VAULT_PATH
      },
      error_file: path.join(VAULT_PATH, 'Logs', 'pm2-cloud-agent-error.log'),
      out_file: path.join(VAULT_PATH, 'Logs', 'pm2-cloud-agent-out.log'),
      log_date_format: 'YYYY-MM-DD HH:mm:ss'
    },
    {
      name: 'local-agent',
      script: path.join(VAULT_PATH, 'local_agent.py'),
      interpreter: 'python',
      cwd: VAULT_PATH,
      watch: false,
      max_memory_restart: '1G',
      env: {
        PYTHONUNBUFFERED: '1',
        PYTHONIOENCODING: 'utf-8',
        VAULT_PATH: VAULT_PATH
      },
      error_file: path.join(VAULT_PATH, 'Logs', 'pm2-local-agent-error.log'),
      out_file: path.join(VAULT_PATH, 'Logs', 'pm2-local-agent-out.log'),
      log_date_format: 'YYYY-MM-DD HH:mm:ss'
    },
    {
      name: 'cloud-orchestrator',
      script: path.join(VAULT_PATH, 'cloud_orchestrator.py'),
      interpreter: 'python',
      cwd: VAULT_PATH,
      watch: false,
      max_memory_restart: '1G',
      env: {
        PYTHONUNBUFFERED: '1',
        PYTHONIOENCODING: 'utf-8',
        VAULT_PATH: VAULT_PATH
      },
      error_file: path.join(VAULT_PATH, 'Logs', 'pm2-cloud-orch-error.log'),
      out_file: path.join(VAULT_PATH, 'Logs', 'pm2-cloud-orch-out.log'),
      log_date_format: 'YYYY-MM-DD HH:mm:ss'
    },
    {
      name: 'local-orchestrator',
      script: path.join(VAULT_PATH, 'local_orchestrator.py'),
      interpreter: 'python',
      cwd: VAULT_PATH,
      watch: false,
      max_memory_restart: '1G',
      env: {
        PYTHONUNBUFFERED: '1',
        PYTHONIOENCODING: 'utf-8',
        VAULT_PATH: VAULT_PATH
      },
      error_file: path.join(VAULT_PATH, 'Logs', 'pm2-local-orch-error.log'),
      out_file: path.join(VAULT_PATH, 'Logs', 'pm2-local-orch-out.log'),
      log_date_format: 'YYYY-MM-DD HH:mm:ss'
    },
    {
      name: 'vault-sync',
      script: path.join(VAULT_PATH, 'vault_sync.py'),
      interpreter: 'python',
      cwd: VAULT_PATH,
      watch: false,
      max_memory_restart: '500M',
      env: {
        PYTHONUNBUFFERED: '1',
        PYTHONIOENCODING: 'utf-8',
        VAULT_PATH: VAULT_PATH
      },
      error_file: path.join(VAULT_PATH, 'Logs', 'pm2-vault-sync-error.log'),
      out_file: path.join(VAULT_PATH, 'Logs', 'pm2-vault-sync-out.log'),
      log_date_format: 'YYYY-MM-DD HH:mm:ss'
    },
    {
      name: 'a2a-messenger',
      script: path.join(VAULT_PATH, 'a2a_messenger.py'),
      interpreter: 'python',
      cwd: VAULT_PATH,
      args: ['local', '8082', VAULT_PATH],
      watch: false,
      max_memory_restart: '500M',
      env: {
        PYTHONUNBUFFERED: '1',
        PYTHONIOENCODING: 'utf-8',
        VAULT_PATH: VAULT_PATH
      },
      error_file: path.join(VAULT_PATH, 'Logs', 'pm2-a2a-error.log'),
      out_file: path.join(VAULT_PATH, 'Logs', 'pm2-a2a-out.log'),
      log_date_format: 'YYYY-MM-DD HH:mm:ss'
    },
    {
      name: 'health-monitor',
      script: path.join(VAULT_PATH, 'health_monitor.py'),
      interpreter: 'python',
      cwd: VAULT_PATH,
      args: ['local', VAULT_PATH],
      watch: false,
      max_memory_restart: '500M',
      env: {
        PYTHONUNBUFFERED: '1',
        PYTHONIOENCODING: 'utf-8',
        VAULT_PATH: VAULT_PATH
      },
      error_file: path.join(VAULT_PATH, 'Logs', 'pm2-health-monitor-error.log'),
      out_file: path.join(VAULT_PATH, 'Logs', 'pm2-health-monitor-out.log'),
      log_date_format: 'YYYY-MM-DD HH:mm:ss'
    },
    {
      name: 'security-guard',
      script: path.join(VAULT_PATH, 'security_guard.py'),
      interpreter: 'python',
      cwd: VAULT_PATH,
      args: ['local', VAULT_PATH],
      watch: false,
      max_memory_restart: '500M',
      env: {
        PYTHONUNBUFFERED: '1',
        PYTHONIOENCODING: 'utf-8',
        VAULT_PATH: VAULT_PATH
      },
      error_file: path.join(VAULT_PATH, 'Logs', 'pm2-security-guard-error.log'),
      out_file: path.join(VAULT_PATH, 'Logs', 'pm2-security-guard-out.log'),
      log_date_format: 'YYYY-MM-DD HH:mm:ss'
    },
    {
      name: 'multi-language-agent',
      script: path.join(VAULT_PATH, 'multi_language_agent.py'),
      interpreter: 'python',
      cwd: VAULT_PATH,
      watch: false,
      max_memory_restart: '1G',
      env: {
        PYTHONUNBUFFERED: '1',
        PYTHONIOENCODING: 'utf-8',
        VAULT_PATH: VAULT_PATH
      },
      error_file: path.join(VAULT_PATH, 'Logs', 'pm2-multi-lang-error.log'),
      out_file: path.join(VAULT_PATH, 'Logs', 'pm2-multi-lang-out.log'),
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      instances: 1,
      exec_mode: 'fork'
    },
    {
      name: 'gmail-watcher',
      script: path.join(VAULT_PATH, 'watchers', 'gmail_watcher.py'),
      interpreter: 'python',
      cwd: VAULT_PATH,
      watch: false,
      max_memory_restart: '500M',
      env: {
        PYTHONUNBUFFERED: '1',
        PYTHONIOENCODING: 'utf-8',
        VAULT_PATH: VAULT_PATH
      },
      error_file: path.join(VAULT_PATH, 'Logs', 'pm2-gmail-watcher-error.log'),
      out_file: path.join(VAULT_PATH, 'Logs', 'pm2-gmail-watcher-out.log'),
      log_date_format: 'YYYY-MM-DD HH:mm:ss'
    },
    {
      name: 'whatsapp-watcher',
      script: path.join(VAULT_PATH, 'watchers', 'whatsapp_watcher.py'),
      interpreter: 'python',
      cwd: VAULT_PATH,
      watch: false,
      max_memory_restart: '500M',
      env: {
        PYTHONUNBUFFERED: '1',
        PYTHONIOENCODING: 'utf-8',
        VAULT_PATH: VAULT_PATH
      },
      error_file: path.join(VAULT_PATH, 'Logs', 'pm2-whatsapp-watcher-error.log'),
      out_file: path.join(VAULT_PATH, 'Logs', 'pm2-whatsapp-watcher-out.log'),
      log_date_format: 'YYYY-MM-DD HH:mm:ss'
    },
    {
      name: 'office-watcher',
      script: path.join(VAULT_PATH, 'watchers', 'office_watcher.py'),
      interpreter: 'python',
      cwd: VAULT_PATH,
      watch: false,
      max_memory_restart: '500M',
      env: {
        PYTHONUNBUFFERED: '1',
        PYTHONIOENCODING: 'utf-8',
        VAULT_PATH: VAULT_PATH
      },
      error_file: path.join(VAULT_PATH, 'Logs', 'pm2-office-watcher-error.log'),
      out_file: path.join(VAULT_PATH, 'Logs', 'pm2-office-watcher-out.log'),
      log_date_format: 'YYYY-MM-DD HH:mm:ss'
    },
    {
      name: 'social-watcher',
      script: path.join(VAULT_PATH, 'watchers', 'social_watcher.py'),
      interpreter: 'python',
      cwd: VAULT_PATH,
      watch: false,
      max_memory_restart: '500M',
      env: {
        PYTHONUNBUFFERED: '1',
        PYTHONIOENCODING: 'utf-8',
        VAULT_PATH: VAULT_PATH
      },
      error_file: path.join(VAULT_PATH, 'Logs', 'pm2-social-watcher-error.log'),
      out_file: path.join(VAULT_PATH, 'Logs', 'pm2-social-watcher-out.log'),
      log_date_format: 'YYYY-MM-DD HH:mm:ss'
    },
    {
      name: 'odoo-lead-watcher',
      script: path.join(VAULT_PATH, 'watchers', 'odoo_lead_watcher.py'),
      interpreter: 'python',
      cwd: VAULT_PATH,
      watch: false,
      max_memory_restart: '500M',
      env: {
        PYTHONUNBUFFERED: '1',
        PYTHONIOENCODING: 'utf-8',
        VAULT_PATH: VAULT_PATH
      },
      error_file: path.join(VAULT_PATH, 'Logs', 'pm2-odoo-lead-watcher-error.log'),
      out_file: path.join(VAULT_PATH, 'Logs', 'pm2-odoo-lead-watcher-out.log'),
      log_date_format: 'YYYY-MM-DD HH:mm:ss'
    }
  ]
};
