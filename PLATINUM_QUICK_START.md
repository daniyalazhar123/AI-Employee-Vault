# 💿 PLATINUM TIER - QUICK START GUIDE

**Your Fast-Track to Platinum Tier Completion**

---

## 🎯 **PLATINUM TIER IN ONE PAGE**

### **What You're Building:**

```
┌─────────────────────────────────────────┐
│  ☁️ CLOUD AGENT (24/7 VM)              │
│  - Email triage & draft replies        │
│  - Social post drafts                  │
│  - Odoo draft invoices                 │
│  - ❌ NO final send permissions        │
└──────────────┬──────────────────────────┘
               │ Git Sync (every 5 min)
┌──────────────┴──────────────────────────┐
│  🏠 LOCAL AGENT (Your Machine)         │
│  - Human approvals                     │
│  - WhatsApp (session local)            │
│  - Final email send                    │
│  - Final social post                   │
│  - Banking/payments                    │
└─────────────────────────────────────────┘
```

### **7 Platinum Requirements:**

1. ✅ Cloud VM running 24/7
2. ✅ Cloud vs Local work zones
3. ✅ Git-based vault sync
4. ✅ Secrets never sync
5. ✅ Odoo on cloud VM
6. ✅ (Optional) A2A messaging
7. ✅ Demo: Email→Cloud draft→Local send

---

## ⚡ **30-MINUTE SETUP**

### **Step 1: Create Oracle Cloud Account** (15 min)

1. Go to: https://www.oracle.com/cloud/free/
2. Click "Start for free"
3. Fill in registration
4. Add credit card (verification, not charged)
5. Wait for approval email

**Alternative:** AWS Free Tier (https://aws.amazon.com/free/)

### **Step 2: Create VM Instance** (15 min)

**Oracle Cloud:**

```
1. Login to Oracle Cloud Console
2. Go to Compute → Instances
3. Click "Create Instance"
4. Configuration:
   - Name: ai-employee-cloud
   - Image: Ubuntu 22.04 or 24.04 LTS
   - Shape: VM.Standard.A1.Flex (ARM)
   - OCPUs: 2
   - Memory: 12 GB
   - Boot Volume: 200 GB
5. Networking:
   - Select your VCN (or create new)
   - Assign public IPv4: YES
   - Allow SSH port 22: YES
6. Add SSH key (generate new or upload existing)
7. Click "Create"
8. Note the public IP address
```

**You now have:** A cloud VM running 24/7 for free!

---

## 🚀 **2-HOUR DEPLOYMENT**

### **Step 1: SSH into VM**

```bash
# Replace with your VM's public IP
ssh -i ~/.ssh/your_key ubuntu@YOUR_VM_IP
```

### **Step 2: Install Dependencies**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python, Node.js, Git
sudo apt install -y python3 python3-pip python3-venv git curl wget

# Install Node.js 24
curl -fsSL https://deb.nodesource.com/setup_24.x | sudo -E bash -
sudo apt install -y nodejs

# Install PM2 (process manager)
sudo npm install -g pm2

# Create app directory
mkdir -p /home/ubuntu/ai-employee-vault
cd /home/ubuntu/ai-employee-vault
```

### **Step 3: Clone Your Vault**

```bash
# On your LOCAL machine, initialize git first
cd "C:\Users\CC\Documents\Obsidian Vault"
git init

# Create .gitignore (CRITICAL!)
cat > .gitignore << 'EOF'
# NEVER SYNC THESE
.env
.env.local
.env.cloud
*.env
credentials.json
token.json
whatsapp_session/
*.session
node_modules/
Logs/
Dead_Letter_Queue/
__pycache__/
*.pyc
EOF

git add .
git commit -m "Platinum-ready vault"
# Create GitHub repo and push
git remote add origin https://github.com/yourusername/ai-employee-vault.git
git push -u origin main
```

```bash
# On CLOUD VM, clone
git clone https://github.com/yourusername/ai-employee-vault.git
cd ai-employee-vault

# Install Python dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install Node dependencies
python mcp_email.py --action list
python mcp_browser.py --action navigate
python mcp_odoo.py --action get_leads
python mcp_social.py --action linkedin
cd ..
```

### **Step 4: Create Cloud Credentials**

```bash
# On CLOUD VM only
cat > .env.cloud << 'EOF'
# CLOUD AGENT - DRAFT ONLY
# These credentials should have DRAFT-ONLY permissions

# Email (read/draft only)
GMAIL_CLIENT_ID=your_cloud_client_id
GMAIL_CLIENT_SECRET=your_cloud_client_secret

# Odoo (draft only)
ODOO_URL=http://localhost:8069
ODOO_DB=odoo_production
ODOO_USERNAME=cloud_user
ODOO_API_KEY=cloud_draft_key
EOF

# NEVER commit this file!
echo ".env.cloud" >> .gitignore
```

### **Step 5: Setup Git Sync**

```bash
# Create sync script
cat > sync_vault.sh << 'EOF'
#!/bin/bash
cd /home/ubuntu/ai-employee-vault
git pull origin main
git add .
git diff --cached --quiet || (git commit -m "Cloud updates $(date)" && git push origin main)
EOF

chmod +x sync_vault.sh

# Test sync
./sync_vault.sh
```

```bash
# Setup cron for auto-sync (every 5 min)
crontab -e

# Add this line:
*/5 * * * * /home/ubuntu/ai-employee-vault/sync_vault.sh >> /home/ubuntu/sync.log 2>&1
```

---

## 🔒 **SECURITY CHECKLIST (15 MIN)**

### **Critical Security Rules:**

```bash
# ✅ 1. Never sync secrets
cat >> .gitignore << 'EOF'
.env
.env.local
.env.cloud
credentials.json
token.json
whatsapp_session/
*.session
Logs/
EOF

# ✅ 2. Separate credentials
# Cloud VM: .env.cloud (draft-only access)
# Local: .env.local (full access)

# ✅ 3. SSH key security
chmod 600 ~/.ssh/your_key

# ✅ 4. Firewall (only necessary ports)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 443/tcp   # HTTPS (for Odoo)
sudo ufw allow 8069/tcp  # Odoo
sudo ufw enable

# ✅ 5. Regular updates
sudo apt update && sudo apt upgrade -y
```

---

## 📦 **ODOO CLOUD DEPLOYMENT (1 HOUR)**

### **Quick Odoo Install:**

```bash
# On CLOUD VM
cd /tmp

# Download Odoo
wget https://nightly.odoo.com/17.0/nightly/src/odoo_17.0.latest.zip
unzip odoo_17.0.latest.zip
sudo mv odoo-17.0-latest /opt/odoo

# Install dependencies
cd /opt/odoo
sudo pip3 install -r requirements.txt

# Create Odoo user
sudo useradd -m -d /opt/odoo -s /bin/bash odoo
sudo chown -R odoo:odoo /opt/odoo

# Create systemd service
sudo cat > /etc/systemd/system/odoo.service << 'EOF'
[Unit]
Description=Odoo ERP
After=network.target

[Service]
Type=simple
User=odoo
ExecStart=/opt/odoo/odoo-bin --config=/etc/odoo/odoo.conf
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Create config
sudo mkdir -p /etc/odoo
sudo cat > /etc/odoo/odoo.conf << 'EOF'
[options]
admin_passwd = CHANGE_THIS_PASSWORD
db_host = localhost
db_port = 5432
db_user = odoo
db_password = odoo_db_password
db_name = odoo_production
addons_path = /opt/odoo/addons
proxy_mode = True
EOF

# Start Odoo
sudo systemctl daemon-reload
sudo systemctl enable odoo
sudo systemctl start odoo
sudo systemctl status odoo

# Access at: http://YOUR_VM_IP:8069
```

---

## 🧪 **PLATINUM DEMO (5 MIN)**

### **Run the Demo:**

```bash
# On your LOCAL machine
cd "C:\Users\CC\Documents\Obsidian Vault"
python platinum_demo.py
```

**What it demonstrates:**
1. ✅ Email arrives (Local offline)
2. ✅ Cloud drafts reply
3. ✅ Local approves
4. ✅ Local executes send
5. ✅ Logged to /Done/

---

## 📊 **PLATINUM PROGRESS TRACKER**

### **Checklist:**

#### **Phase 1: Cloud Setup** (2 hours)
- [ ] Oracle Cloud account created
- [ ] VM instance running
- [ ] SSH access working
- [ ] Dependencies installed
- [ ] Git repo initialized
- [ ] Vault cloned on VM

#### **Phase 2: Work Zones** (2 hours)
- [ ] .env.cloud created (draft-only)
- [ ] .env.local exists (full access)
- [ ] Git sync working (manual test)
- [ ] Cron sync setup (auto every 5 min)
- [ ] Cloud Agent script ready
- [ ] Local Agent script ready

#### **Phase 3: Security** (30 min)
- [ ] .gitignore complete
- [ ] Secrets separated
- [ ] Firewall configured
- [ ] SSH secured
- [ ] Security checklist done

#### **Phase 4: Odoo** (1 hour)
- [ ] Odoo installed on VM
- [ ] Odoo accessible via browser
- [ ] Odoo MCP configured
- [ ] Backups setup

#### **Phase 5: Demo** (30 min)
- [ ] Health monitor running
- [ ] Platinum demo script ready
- [ ] Demo runs successfully
- [ ] All steps documented

---

## 🎯 **MINIMUM PASSING GATE**

**To pass Platinum Tier, demonstrate:**

```
✅ Email arrives while Local offline
✅ Cloud Agent drafts reply (cannot send)
✅ Git syncs draft to Local
✅ Human approves (moves to /Approved)
✅ Local executes send via MCP
✅ Action logged to /Done
✅ Dashboard updated
✅ Git syncs back to Cloud
```

**Run demo:**
```bash
python platinum_demo.py
```

**Success output:**
```
✅ PLATINUM DEMO COMPLETE!
💿 PLATINUM TIER MINIMUM PASSING GATE: PASSED!
```

---

## 🚨 **COMMON ISSUES & FIXES**

### **Git Sync Fails:**

```bash
# Check Git status
git status

# Force pull (discard local changes)
git fetch --all
git reset --hard origin/main

# Re-push
git add .
git commit -m "Fix sync"
git push origin main
```

### **Cloud Agent Not Running:**

```bash
# Check if running
ps aux | grep cloud_agent

# Restart
cd /home/ubuntu/ai-employee-vault
source venv/bin/activate
python cloud_agent.py &

# Or use PM2
pm2 start cloud_agent.py --interpreter python3
pm2 save
pm2 startup
```

### **Odoo Not Accessible:**

```bash
# Check status
sudo systemctl status odoo

# Restart
sudo systemctl restart odoo

# Check logs
sudo tail -f /var/log/odoo/odoo.log
```

### **Vault Sync Conflicts:**

```bash
# On LOCAL machine
cd "C:\Users\CC\Documents\Obsidian Vault"

# See conflicts
git status

# Accept remote changes
git fetch origin
git reset --hard origin/main

# Or keep local and force push
git add .
git commit -m "Resolve conflict"
git push origin main --force
```

---

## 📞 **NEXT STEPS**

### **After Quick Start:**

1. **Read Full Roadmap:** `PLATINUM_TIER_ROADMAP.md`
2. **Implement Cloud Agent:** `cloud_agent.py`
3. **Implement Local Agent:** `local_agent.py`
4. **Setup Health Monitoring:** `health_monitor.py`
5. **Run Platinum Demo:** `platinum_demo.py`
6. **Document Everything:** Create `PLATINUM_TIER_COMPLETE.md`

### **Time Estimates:**

- **Quick Start:** 4 hours
- **Full Implementation:** 60+ hours
- **Testing & Demo:** 5 hours
- **Documentation:** 5 hours

**Total:** ~74 hours

---

## 🏆 **PLATINUM BENEFITS**

### **What You Get:**

✅ **24/7 Operation** - AI Employee never sleeps  
✅ **Production-Grade** - Real cloud deployment  
✅ **Security** - Proper credential separation  
✅ **Scalability** - Easy to add more agents  
✅ **Reliability** - Health monitoring + alerts  
✅ **Portfolio Piece** - Impressive demo for employers  

### **Business Value:**

- **Cost:** Free (Oracle Cloud Free Tier)
- **Availability:** 168 hours/week (vs 40 hours human)
- **Response Time:** < 2 minutes (vs 24 hours human)
- **Consistency:** 99%+ (vs 85-95% human)

---

## 🎓 **LEARNING RESOURCES**

### **Oracle Cloud:**
- Docs: https://docs.oracle.com/en-us/iaas/
- Free Tier Guide: https://www.oracle.com/cloud/free/

### **Odoo:**
- Documentation: https://www.odoo.com/documentation
- Odoo 19 API: https://www.odoo.com/documentation/19.0/developer/reference/external_api.html

### **Git Sync:**
- Git Basics: https://git-scm.com/book
- Git Workflows: https://www.atlassian.com/git/tutorials/comparing-workflows

### **Security:**
- OWASP: https://owasp.org/
- Cloud Security: https://www.cloudsecurityalliance.org/

---

## 📝 **SUBMISSION CHECKLIST**

### **For Hackathon Submission:**

- [ ] Platinum Tier Demo recorded (5-10 min video)
- [ ] `PLATINUM_TIER_COMPLETE.md` created
- [ ] All 7 requirements verified
- [ ] Security checklist complete
- [ ] Architecture documented
- [ ] Demo script runs successfully
- [ ] Submit form: https://forms.gle/JR9T1SJq5rmQyGkGA

---

**Ready to go Platinum? Let's build! 🚀**

*💿 PLATINUM TIER QUICK START - Version 1.0*  
*Created: March 21, 2026*
