#!/bin/bash
# ============================================
# ☁️ PLATINUM TIER - DEPLOY CLOUD AGENT
# Run this script on Oracle Cloud VM
# ============================================

set -e

echo "============================================"
echo "☁️  PLATINUM TIER - DEPLOY CLOUD AGENT"
echo "============================================"

VAULT_DIR="/home/ubuntu/ai-employee-vault"

echo ""
echo "Step 1: Update System"
echo "----------------------------------------"
sudo apt update && sudo apt upgrade -y

echo ""
echo "Step 2: Install Dependencies"
echo "----------------------------------------"
sudo apt install -y python3 python3-pip python3-venv git curl wget nodejs npm

echo ""
echo "Step 3: Install PM2"
echo "----------------------------------------"
sudo npm install -g pm2

echo ""
echo "Step 4: Clone Vault"
echo "----------------------------------------"
cd /home/ubuntu
git clone <YOUR_GIT_REPO_URL> $VAULT_DIR
cd $VAULT_DIR

echo ""
echo "Step 5: Setup Python Environment"
echo "----------------------------------------"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo ""
echo "Step 6: Install Node Dependencies"
echo "----------------------------------------"
cd mcp-email && npm install
cd ../mcp-browser && npm install
cd ../mcp-odoo && npm install
cd ../mcp-social && npm install
cd ..

echo ""
echo "Step 7: Create .env.cloud"
echo "----------------------------------------"
cp .env.cloud.template .env.cloud
echo "⚠️  Edit .env.cloud with your cloud credentials!"
echo "   nano .env.cloud"

echo ""
echo "Step 8: Setup Git Sync"
echo "----------------------------------------"
cp sync_vault.sh /home/ubuntu/sync_vault.sh
chmod +x /home/ubuntu/sync_vault.sh
chmod +x sync_vault.sh

# Setup cron for auto-sync (every 5 minutes)
(crontab -l 2>/dev/null; echo "*/5 * * * * /home/ubuntu/sync_vault.sh") | crontab -

echo ""
echo "Step 9: Start Cloud Agent with PM2"
echo "----------------------------------------"
pm2 start cloud_agent.py --name cloud-agent --interpreter python3
pm2 start health_monitor.py --name health-monitor --interpreter python3 -- cloud
pm2 save
pm2 startup

echo ""
echo "Step 10: Verify Deployment"
echo "----------------------------------------"
pm2 status

echo ""
echo "============================================"
echo "✅ CLOUD AGENT DEPLOYMENT COMPLETE"
echo "============================================"
echo ""
echo "Cloud Agent is now running 24/7!"
echo ""
echo "Commands:"
echo "  pm2 status          - Check status"
echo "  pm2 logs            - View logs"
echo "  pm2 restart all     - Restart all"
echo "  pm2 monit           - Monitor"
echo ""
echo "Git sync runs every 5 minutes via cron"
echo ""
