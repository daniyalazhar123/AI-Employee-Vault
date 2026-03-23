#!/bin/bash
# ============================================
# ☁️ PLATINUM TIER - ORACLE CLOUD VM SETUP
# Complete Automated Setup Script
# ============================================
# Run this script on Oracle Cloud VM after SSH
# Creates complete AI Employee Cloud environment

set -e

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║  ☁️  PLATINUM TIER - ORACLE CLOUD VM SETUP            ║"
echo "║     AI Employee Cloud Agent Deployment                ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Configuration
VAULT_PATH="$HOME/ai-employee-vault"
PYTHON_VERSION="3.10"
NODE_VERSION="18"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_step() {
    echo -e "${BLUE}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Step 1: System Update
print_step "Step 1/12: Updating system packages..."
sudo apt update
sudo apt upgrade -y
print_success "System updated"

# Step 2: Install Python
print_step "Step 2/12: Installing Python $PYTHON_VERSION..."
sudo apt install -y python$PYTHON_VERSION python$PYTHON_VERSION-venv python$PYTHON_VERSION-dev python3-pip
print_success "Python installed: $(python$PYTHON_VERSION --version)"

# Step 3: Install Node.js
print_step "Step 3/12: Installing Node.js $NODE_VERSION..."
curl -fsSL https://deb.nodesource.com/setup_$NODE_VERSION.x | sudo -E bash -
sudo apt install -y nodejs
print_success "Node.js installed: $(node --version)"

# Step 4: Install Git
print_step "Step 4/12: Installing Git..."
sudo apt install -y git
print_success "Git installed: $(git --version)"

# Step 5: Install Docker
print_step "Step 5/12: Installing Docker..."
sudo apt install -y docker.io
sudo usermod -aG docker $USER
sudo systemctl start docker
sudo systemctl enable docker
print_success "Docker installed: $(docker --version)"

# Step 6: Install Docker Compose
print_step "Step 6/12: Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
print_success "Docker Compose installed: $(docker-compose --version)"

# Step 7: Install Qwen CLI
print_step "Step 7/12: Installing Qwen CLI..."
sudo npm install -g @anthropic/qwen
print_success "Qwen CLI installed: $(qwen --version)"

# Step 8: Install PM2
print_step "Step 8/12: Installing PM2 (Process Manager)..."
sudo npm install -g pm2
pm2 update
print_success "PM2 installed: $(pm2 --version)"

# Step 9: Install Python Dependencies
print_step "Step 9/12: Installing global Python dependencies..."
sudo pip3 install requests watchdog python-dotenv playwright
print_success "Python dependencies installed"

# Step 10: Setup Vault Directory
print_step "Step 10/12: Setting up vault directory..."

# Clone vault (user needs to replace with their repo)
echo ""
print_warning "Enter your Git repository URL (or press Enter to skip):"
read -r GIT_REPO

if [ -n "$GIT_REPO" ]; then
    git clone "$GIT_REPO" "$VAULT_PATH"
    cd "$VAULT_PATH"
    print_success "Vault cloned to: $VAULT_PATH"
else
    mkdir -p "$VAULT_PATH"
    cd "$VAULT_PATH"
    git init
    print_warning "Initialize Git repository manually"
fi

# Create required folders
mkdir -p cloud local
mkdir -p Needs_Action/{cloud,local}
mkdir -p In_Progress/{cloud,local}
mkdir -p Drafts/{email,social,odoo}
mkdir -p Updates Signals Pending_Approval Approved Rejected Done
mkdir -p Logs/Audit Dead_Letter_Queue

print_success "Vault directory structure created"

# Step 11: Create Environment Files
print_step "Step 11/12: Creating environment files..."

# Create .env.example
cat > .env.example << 'EOF'
# Cloud Environment Variables
# NEVER commit actual .env file!

# Odoo Configuration
ODOO_URL=http://localhost:8069
ODOO_DB=odoo_production
ODOO_USERNAME=admin
ODOO_API_KEY=your_api_key_here

# Gmail API (Read-only for Cloud)
GMAIL_CLIENT_ID=your_client_id
GMAIL_CLIENT_SECRET=your_client_secret
GMAIL_REDIRECT_URI=http://localhost:8080/callback

# Social Media (Read-only for Cloud)
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret

# Cloud Agent Configuration
CLOUD_AGENT_PORT=8081
HEALTH_CHECK_PORT=8080
VAULT_PATH=/home/ubuntu/ai-employee-vault

# Git Configuration
GIT_REPO_URL=your_git_repo_url
GIT_SYNC_INTERVAL=300
EOF

# Create cloud/.env.cloud
cat > cloud/.env.cloud << 'EOF'
# Cloud Agent Environment
AGENT_TYPE=draft_only
CLOUD_MODE=true

# Permissions (Cloud is DRAFT-ONLY)
EMAIL_SEND=false
WHATSAPP_SEND=false
SOCIAL_POST=false
PAYMENT_EXECUTE=false

# Odoo (Draft-only for Cloud)
ODOO_CREATE_INVOICE=false
ODOO_RECORD_PAYMENT=false
ODOO_READ_REPORTS=true

# Endpoints
LOCAL_AGENT_URL=http://localhost:8082
HEALTH_CHECK_URL=http://localhost:8080/health
EOF

print_success "Environment files created"

# Step 12: Create Startup Scripts
print_step "Step 12/12: Creating startup scripts..."

# Create cloud agent startup script
cat > cloud/start_cloud_agent.sh << 'EOF'
#!/bin/bash
# Start Cloud Agent with PM2

cd "$(dirname "$0")"

# Load environment
if [ -f .env.cloud ]; then
    export $(cat .env.cloud | grep -v '^#' | xargs)
fi

# Install dependencies
pip3 install -r requirements.txt 2>/dev/null || true

# Start with PM2
pm2 start cloud_agent.py \
  --name cloud-agent \
  --interpreter python3 \
  --watch \
  --log-date-format="YYYY-MM-DD HH:mm:ss" \
  --max-memory-restart 500M

# Auto-start on reboot
pm2 save
pm2 startup | tail -1 | bash 2>/dev/null || true

echo ""
echo "✓ Cloud Agent started with PM2"
echo "  Status: pm2 status"
echo "  Logs: pm2 logs cloud-agent"
EOF

chmod +x cloud/start_cloud_agent.sh

# Create health monitor startup script
cat > cloud/start_health_monitor.sh << 'EOF'
#!/bin/bash
# Start Health Monitor with PM2

cd "$(dirname "$0")"

# Start with PM2
pm2 start health_monitor.py \
  --name health-monitor \
  --interpreter python3 \
  --watch \
  --log-date-format="YYYY-MM-DD HH:mm:ss"

echo ""
echo "✓ Health Monitor started with PM2"
EOF

chmod +x cloud/start_health_monitor.sh

# Create Git sync script
cat > cloud/sync_vault.sh << 'EOF'
#!/bin/bash
# Sync vault with Git every 5 minutes

VAULT_PATH="/home/ubuntu/ai-employee-vault"
LOG_FILE="$VAULT_PATH/Logs/git_sync.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

cd "$VAULT_PATH"

# Pull latest changes
echo "[$TIMESTAMP] Pulling latest changes..." >> "$LOG_FILE"
git pull origin main >> "$LOG_FILE" 2>&1

# Add cloud-generated files
echo "[$TIMESTAMP] Adding cloud files..." >> "$LOG_FILE"
git add Drafts/ Updates/ Signals/ In_Progress/cloud/ >> "$LOG_FILE" 2>&1

# Commit cloud changes (only if there are changes)
if ! git diff --cached --quiet; then
    echo "[$TIMESTAMP] Committing cloud changes..." >> "$LOG_FILE"
    git commit -m "Cloud agent updates $TIMESTAMP" >> "$LOG_FILE" 2>&1
    
    # Push to remote
    echo "[$TIMESTAMP] Pushing to remote..." >> "$LOG_FILE"
    git push origin main >> "$LOG_FILE" 2>&1
    echo "[$TIMESTAMP] Sync completed with push" >> "$LOG_FILE"
else
    echo "[$TIMESTAMP] No changes to commit" >> "$LOG_FILE"
fi

echo "[$TIMESTAMP] Sync cycle complete" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
EOF

chmod +x cloud/sync_vault.sh

# Create Odoo docker-compose wrapper
cat > odoo/start_odoo.sh << 'EOF'
#!/bin/bash
# Start Odoo on Cloud VM

cd "$(dirname "$0")"

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "Please edit .env with your credentials"
    exit 1
fi

# Start Odoo
docker-compose up -d

echo ""
echo "✓ Odoo started"
echo "  Access: http://$(curl -s http://169.254.169.254/opc/v1/instance/metadata/oci_compute_public_ip 2>/dev/null || echo 'localhost'):8069"
echo "  Status: docker-compose ps"
echo "  Logs: docker-compose logs -f"
EOF

chmod +x odoo/start_odoo.sh

print_success "Startup scripts created"

# Final Setup
echo ""
print_success "Installing Playwright browsers..."
python3 -m playwright install --with-deps chromium 2>/dev/null || print_warning "Playwright installation skipped"

# Setup cron job for Git sync
print_step "Setting up automatic Git sync..."
(crontab -l 2>/dev/null; echo "*/5 * * * * $VAULT_PATH/cloud/sync_vault.sh") | crontab -
print_success "Git sync scheduled (every 5 minutes)"

# Summary
echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║  ☁️  CLOUD VM SETUP COMPLETE!                         ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "📂 Vault Path: $VAULT_PATH"
echo ""
echo "🚀 Next Steps:"
echo ""
echo "1. Configure environment:"
echo "   cd $VAULT_PATH"
echo "   nano .env"
echo "   nano cloud/.env.cloud"
echo ""
echo "2. Start Cloud Agent:"
echo "   cd $VAULT_PATH/cloud"
echo "   ./start_cloud_agent.sh"
echo ""
echo "3. Start Health Monitor:"
echo "   cd $VAULT_PATH/cloud"
echo "   ./start_health_monitor.sh"
echo ""
echo "4. Start Odoo (optional):"
echo "   cd $VAULT_PATH/odoo"
echo "   ./start_odoo.sh"
echo ""
echo "5. Check status:"
echo "   pm2 status"
echo "   docker-compose ps"
echo ""
echo "📝 Important Files:"
echo "   - .env (main configuration)"
echo "   - cloud/.env.cloud (cloud-specific settings)"
echo "   - cloud/sync_vault.sh (Git sync script)"
echo ""
echo "🔒 Security Reminder:"
echo "   - NEVER commit .env files"
echo "   - NEVER commit credentials"
echo "   - Keep WhatsApp session on Local only"
echo ""
print_success "Cloud VM ready for Platinum Tier!"
echo ""
