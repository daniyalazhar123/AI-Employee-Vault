module.exports = {
  apps: [
    {
      name: 'ai-orchestrator',
      script: './ai_employee_orchestrator.py',
      interpreter: 'python',
      cwd: 'C:/Users/CC/Documents/Obsidian Vault',
      watch: false,
      max_memory_restart: '2G',
      env: {
        PYTHONUNBUFFERED: '1',
        VAULT_PATH: 'C:/Users/CC/Documents/Obsidian Vault'
      },
      error_file: './Logs/pm2-orchestrator-error.log',
      out_file: './Logs/pm2-orchestrator-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss'
    },
    {
      name: 'cloud-agent',
      script: './cloud_agent.py',
      interpreter: 'python',
      cwd: 'C:/Users/CC/Documents/Obsidian Vault',
      watch: false,
      max_memory_restart: '1G',
      env: {
        PYTHONUNBUFFERED: '1'
      },
      error_file: './Logs/pm2-cloud-agent-error.log',
      out_file: './Logs/pm2-cloud-agent-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss'
    },
    {
      name: 'local-agent',
      script: './local_agent.py',
      interpreter: 'python',
      cwd: 'C:/Users/CC/Documents/Obsidian Vault',
      watch: false,
      max_memory_restart: '1G',
      env: {
        PYTHONUNBUFFERED: '1'
      },
      error_file: './Logs/pm2-local-agent-error.log',
      out_file: './Logs/pm2-local-agent-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss'
    },
    {
      name: 'health-monitor',
      script: './health_monitor.py',
      interpreter: 'python',
      args: 'local',
      cwd: 'C:/Users/CC/Documents/Obsidian Vault',
      watch: false,
      max_memory_restart: '500M',
      env: {
        PYTHONUNBUFFERED: '1'
      },
      error_file: './Logs/pm2-health-monitor-error.log',
      out_file: './Logs/pm2-health-monitor-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss'
    },
    {
      name: 'security-guard',
      script: './security_guard.py',
      interpreter: 'python',
      args: 'local',
      cwd: 'C:/Users/CC/Documents/Obsidian Vault',
      watch: false,
      max_memory_restart: '500M',
      env: {
        PYTHONUNBUFFERED: '1'
      },
      error_file: './Logs/pm2-security-guard-error.log',
      out_file: './Logs/pm2-security-guard-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss'
    },
    {
      name: 'multi-language-agent',
      script: './multi_language_agent.py',
      interpreter: 'python',
      cwd: 'C:/Users/CC/Documents/Obsidian Vault',
      watch: false,
      max_memory_restart: '1G',
      env: {
        PYTHONUNBUFFERED: '1'
      },
      error_file: './Logs/pm2-multi-language-agent-error.log',
      out_file: './Logs/pm2-multi-language-agent-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      instances: 1,
      exec_mode: 'fork'
    },
    {
      name: 'gmail-watcher',
      script: './watchers/gmail_watcher.py',
      interpreter: 'python',
      cwd: 'C:/Users/CC/Documents/Obsidian Vault',
      watch: false,
      max_memory_restart: '500M',
      env: {
        PYTHONUNBUFFERED: '1'
      },
      error_file: './Logs/pm2-gmail-watcher-error.log',
      out_file: './Logs/pm2-gmail-watcher-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss'
    },
    {
      name: 'whatsapp-watcher',
      script: './watchers/whatsapp_watcher.py',
      interpreter: 'python',
      cwd: 'C:/Users/CC/Documents/Obsidian Vault',
      watch: false,
      max_memory_restart: '500M',
      env: {
        PYTHONUNBUFFERED: '1'
      },
      error_file: './Logs/pm2-whatsapp-watcher-error.log',
      out_file: './Logs/pm2-whatsapp-watcher-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss'
    },
    {
      name: 'office-watcher',
      script: './watchers/office_watcher.py',
      interpreter: 'python',
      cwd: 'C:/Users/CC/Documents/Obsidian Vault',
      watch: false,
      max_memory_restart: '500M',
      env: {
        PYTHONUNBUFFERED: '1'
      },
      error_file: './Logs/pm2-office-watcher-error.log',
      out_file: './Logs/pm2-office-watcher-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss'
    },
    {
      name: 'social-watcher',
      script: './watchers/social_watcher.py',
      interpreter: 'python',
      cwd: 'C:/Users/CC/Documents/Obsidian Vault',
      watch: false,
      max_memory_restart: '500M',
      env: {
        PYTHONUNBUFFERED: '1'
      },
      error_file: './Logs/pm2-social-watcher-error.log',
      out_file: './Logs/pm2-social-watcher-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss'
    },
    {
      name: 'odoo-lead-watcher',
      script: './watchers/odoo_lead_watcher.py',
      interpreter: 'python',
      cwd: 'C:/Users/CC/Documents/Obsidian Vault',
      watch: false,
      max_memory_restart: '500M',
      env: {
        PYTHONUNBUFFERED: '1'
      },
      error_file: './Logs/pm2-odoo-lead-watcher-error.log',
      out_file: './Logs/pm2-odoo-lead-watcher-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss'
    }
  ]
};
