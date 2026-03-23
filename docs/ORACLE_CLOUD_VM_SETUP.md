# ☁️ ORACLE CLOUD FREE VM - COMPLETE SETUP GUIDE

**Personal AI Employee Hackathon 0**
**Platinum Tier - Cloud VM Deployment**
**Created:** March 23, 2026

---

## 🎯 OVERVIEW

This guide provides step-by-step instructions to create a **free Oracle Cloud VM** for hosting your AI Employee 24/7.

### **Free Tier Specifications**

```
Shape: VM.Standard.A1.Flex (ARM-based)
OCPUs: 4 cores
Memory: 24 GB RAM
Storage: 200 GB block volume
OS: Ubuntu 22.04 LTS
Cost: FREE (Always Free tier)
```

---

## 📋 PREREQUISITES

### **What You Need**

1. **Oracle Cloud Account**
   - Sign up: https://www.oracle.com/cloud/free/
   - Credit/debit card required (for verification, no charges)
   - Phone number for SMS verification

2. **SSH Key Pair**
   - We'll generate this in Step 2
   - Used for secure VM access

3. **Email Address**
   - For Oracle Cloud notifications

---

## 🚀 STEP-BY-STEP SETUP

### **Step 1: Sign Up for Oracle Cloud**

#### 1.1: Create Account

1. Go to: https://www.oracle.com/cloud/free/
2. Click **"Start for free"** button
3. Fill in registration form:
   ```
   - First Name
   - Last Name
   - Email Address
   - Password (min 12 chars, uppercase, lowercase, number, special char)
   - Country/Region
   - Mobile Phone Number
   ```

#### 1.2: Verify Email

1. Check your email inbox
2. Click verification link from Oracle
3. Set security questions

#### 1.3: Verify Phone

1. Enter SMS code sent to your phone
2. Complete CAPTCHA verification

#### 1.4: Add Payment Method

1. Enter credit/debit card details
2. **Note:** Card will NOT be charged (only verification)
3. Complete verification

#### 1.5: Account Activation

1. Wait for account approval (usually instant, max 24 hours)
2. You'll receive email: "Your Oracle Cloud account is ready"

---

### **Step 2: Generate SSH Key Pair**

#### 2.1: Generate SSH Key (Windows)

**Option A: Using PowerShell**

```powershell
# Open PowerShell as Administrator
cd C:\Users\YourUsername\.ssh

# Generate SSH key (RSA 4096-bit)
ssh-keygen -t rsa -b 4096 -f oracle_cloud_key -C "oracle_cloud"

# You'll be prompted for passphrase (optional, press Enter to skip)
```

**Option B: Using PuTTYgen**

1. Download PuTTYgen: https://www.puttygen.com/
2. Open PuTTYgen
3. Select: **RSA** → **4096 bits**
4. Click **"Generate"**
5. Move mouse randomly to generate entropy
6. Save private key: `oracle_cloud_key.ppk`
7. Copy public key text (for later use)

#### 2.2: Generate SSH Key (Mac/Linux)

```bash
# Open Terminal
cd ~/.ssh

# Generate SSH key
ssh-keygen -t rsa -b 4096 -f oracle_cloud_key -C "oracle_cloud"

# Press Enter twice (no passphrase)
```

#### 2.3: Verify Key Files

You should have:
- **Private Key:** `oracle_cloud_key` (or `.ppk` for PuTTY)
- **Public Key:** `oracle_cloud_key.pub`

**IMPORTANT:** Keep private key secure! Never share it.

---

### **Step 3: Create VM Instance**

#### 3.1: Login to Oracle Cloud Console

1. Go to: https://cloud.oracle.com/
2. Enter credentials
3. Click **"Sign In"**

#### 3.2: Navigate to Compute

1. Click **Hamburger Menu** (☰) top-left
2. Go to: **Compute** → **Instances**

#### 3.3: Create Instance

1. Click **"Create instance"** button

#### 3.4: Configure Instance

**Section 1: Name and Placement**
```
Name: ai-employee-cloud
Compartment: Select your compartment (usually your email)
Availability Domain: Select any (AD-1, AD-2, or AD-3)
```

**Section 2: Image and Shape**
```
Image: 
  - Click "Change Image"
  - Select: Ubuntu 22.04 LTS (aarch64)
  
Shape:
  - Click "Change Shape"
  - Select: VM.Standard.A1.Flex
  - OCPUs: 4
  - Memory: 24 GB
```

**Section 3: Networking**
```
Virtual cloud network: Create new VCN
Subnet: Use default (public)
Assign public IPv4 address: ✓ Checked
Hostname: ai-employee-cloud
```

**Section 4: Add SSH Keys** ⭐ **CRITICAL**

```
Select public key source: Generate a key pair for me
   OR
Select public key source: Paste public keys

If pasting:
1. Open your public key file: oracle_cloud_key.pub
2. Copy entire content
3. Paste in the box
```

**Section 5: Boot Volume**
```
Specify a custom boot volume size: ✓ Checked
Size: 200 GB
```

#### 3.5: Launch Instance

1. Review all settings
2. Click **"Create"** button
3. Wait 2-5 minutes for instance creation
4. Instance status changes to **"RUNNING"**

---

### **Step 4: Configure Security List**

#### 4.1: Navigate to Security Lists

1. Click **Hamburger Menu** (☰)
2. Go to: **Networking** → **Virtual cloud networks**
3. Click your VCN (usually `VCN-ai-employee-cloud`)
4. Under **Resources**, click **"Security lists"**
5. Click **"Default Security List for VCN-..."**

#### 4.2: Add Ingress Rules

Click **"Add Ingress Rules"**

**Rule 1: SSH (Port 22)**
```
Source CIDR: 0.0.0.0/0
Destination Port Range: 22
Description: SSH Access
```

**Rule 2: HTTP (Port 80)**
```
Source CIDR: 0.0.0.0/0
Destination Port Range: 80
Description: HTTP Access
```

**Rule 3: HTTPS (Port 443)**
```
Source CIDR: 0.0.0.0/0
Destination Port Range: 443
Description: HTTPS Access
```

**Rule 4: Odoo (Port 8069)**
```
Source CIDR: 0.0.0.0/0
Destination Port Range: 8069
Description: Odoo ERP Access
```

**Rule 5: Health Check (Port 8080)**
```
Source CIDR: 0.0.0.0/0
Destination Port Range: 8080
Description: Health Monitor
```

**Rule 6: Agent Communication (Port 8081-8082)**
```
Source CIDR: 0.0.0.0/0
Destination Port Range: 8081-8082
Description: Cloud/Local Agent Communication
```

#### 4.3: Save Rules

1. Click **"Add Ingress Rules"**
2. Verify all rules added
3. Click **"Save Changes"**

---

### **Step 5: Get Public IP Address**

#### 5.1: Find VM Public IP

1. Go to: **Compute** → **Instances**
2. Click your instance: `ai-employee-cloud`
3. Under **Instance Access**, find:
   ```
   Public IP Address: XXX.XXX.XXX.XXX
   Private IP Address: 10.XXX.XXX.XXX
   ```

#### 5.2: Note Down Information

Save this information:
```
VM Name: ai-employee-cloud
Public IP: XXX.XXX.XXX.XXX
Private IP: 10.XXX.XXX.XXX
SSH Key: oracle_cloud_key
Username: ubuntu
```

---

### **Step 6: Test SSH Connection**

#### 6.1: SSH from Windows (PowerShell)

```powershell
# Navigate to SSH key folder
cd C:\Users\YourUsername\.ssh

# Test SSH connection
ssh -i oracle_cloud_key ubuntu@XXX.XXX.XXX.XXX

# First time: Type "yes" to accept fingerprint
```

#### 6.2: SSH from Mac/Linux

```bash
# Navigate to SSH key folder
cd ~/.ssh

# Test SSH connection
ssh -i oracle_cloud_key ubuntu@XXX.XXX.XXX.XXX

# First time: Type "yes" to accept fingerprint
```

#### 6.3: Successful Connection

You should see:
```
Welcome to Ubuntu 22.04 LTS (GNU/Linux ...)

System information as of [date]

Usage of /:   X% of 196GB
Memory usage: X%
Processes:    XXX
```

**Type:** `exit` to disconnect

---

## 🔧 POST-INSTALLATION SETUP

### **Step 7: Initial VM Configuration**

#### 7.1: SSH into VM

```bash
ssh -i oracle_cloud_key ubuntu@XXX.XXX.XXX.XXX
```

#### 7.2: Update System

```bash
sudo apt update && sudo apt upgrade -y
```

#### 7.3: Install Required Packages

```bash
# Install essential tools
sudo apt install -y git curl wget vim htop net-tools

# Install Python
sudo apt install -y python3 python3-pip python3-venv

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install Docker
sudo apt install -y docker.io
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Qwen CLI
sudo npm install -g @anthropic/qwen

# Install PM2
sudo npm install -g pm2
```

#### 7.4: Verify Installations

```bash
python3 --version    # Should show Python 3.10+
node --version       # Should show v18.x
npm --version        # Should show 9.x
git --version        # Should show 2.34+
docker --version     # Should show 24.x
docker-compose --version  # Should show 2.x
qwen --version       # Should show latest
pm2 --version        # Should show 5.x
```

---

## 📊 VERIFICATION CHECKLIST

### **Oracle Cloud Account**
- [ ] Account created and activated
- [ ] Email verified
- [ ] Phone verified
- [ ] Payment method added

### **SSH Keys**
- [ ] SSH key pair generated
- [ ] Public key uploaded to Oracle
- [ ] Private key saved securely
- [ ] SSH connection tested

### **VM Instance**
- [ ] Instance created (VM.Standard.A1.Flex)
- [ ] Ubuntu 22.04 LTS selected
- [ ] 4 OCPUs, 24GB RAM configured
- [ ] 200GB boot volume configured
- [ ] Public IP assigned
- [ ] Instance status: RUNNING

### **Security Configuration**
- [ ] Security list accessed
- [ ] Port 22 (SSH) added
- [ ] Port 80 (HTTP) added
- [ ] Port 443 (HTTPS) added
- [ ] Port 8069 (Odoo) added
- [ ] Port 8080 (Health) added
- [ ] Port 8081-8082 (Agents) added

### **VM Setup**
- [ ] SSH connection successful
- [ ] System updated
- [ ] Python installed
- [ ] Node.js installed
- [ ] Docker installed
- [ ] Qwen CLI installed
- [ ] PM2 installed

---

## 🎯 NEXT STEPS

### **After VM is Ready**

1. **Clone Your Vault**
   ```bash
   cd ~
   git clone <your-repo-url> ai-employee-vault
   cd ai-employee-vault
   ```

2. **Run Setup Script**
   ```bash
   bash cloud/setup_oracle_cloud_vm.sh
   ```

3. **Configure Environment**
   ```bash
   nano .env
   nano cloud/.env.cloud
   ```

4. **Start Cloud Agent**
   ```bash
   cd cloud
   bash start_cloud_agent.sh
   ```

5. **Verify Running**
   ```bash
   pm2 status
   docker-compose ps
   ```

---

## 🐛 TROUBLESHOOTING

### **Problem: SSH Connection Refused**

**Solution:**
```bash
# Check security list has port 22
# Verify public IP is correct
# Check instance is RUNNING
ssh -v -i oracle_cloud_key ubuntu@XXX.XXX.XXX.XXX
```

### **Problem: Can't Access Odoo (Port 8069)**

**Solution:**
```bash
# Check security list has port 8069
# Verify Odoo is running
docker-compose ps
# Check Odoo logs
docker-compose logs odoo
```

### **Problem: VM Not Starting**

**Solution:**
```bash
# Check instance status in Oracle Console
# Try: Stop → Start (not restart)
# Check boot volume size (200GB)
# Verify shape is VM.Standard.A1.Flex
```

### **Problem: Out of Resources**

**Solution:**
```bash
# Check resource usage
free -h
df -h
top

# Clean up if needed
sudo apt clean
docker system prune -a
```

---

## 💰 COST ESTIMATE

### **Always Free Resources**

| Resource | Specification | Cost |
|----------|--------------|------|
| **Compute VM** | VM.Standard.A1.Flex (4 OCPUs, 24GB) | FREE |
| **Boot Volume** | 200 GB block volume | FREE |
| **Public IP** | 1 ephemeral IP | FREE |
| **Network** | 10 TB/month egress | FREE |

**Total Monthly Cost:** **$0.00** ✅

### **Potential Charges (If Exceeded)**

- Additional storage: $0.0255/GB/month
- Additional network: $0.0085/GB over 10TB
- Larger VM shapes: Varies

---

## 📞 SUPPORT RESOURCES

### **Oracle Cloud Documentation**
- Compute: https://docs.oracle.com/en-us/iaas/Content/Compute/Concepts/computeoverview.htm
- Networking: https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/overview.htm
- Security Lists: https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/securitylists.htm

### **Hackathon Resources**
- `PLATINUM_TIER_COMPLETE_IMPLEMENTATION.md`
- `PLATINUM_TIER_STATUS.md`
- `cloud/setup_oracle_cloud_vm.sh`

### **Community Support**
- Oracle Cloud Free Tier Forum: https://forums.oracle.com/ords/apexds/forum/152
- Hackathon Zoom: Wednesdays 10:00 PM
- YouTube: https://www.youtube.com/@panaversity

---

## ✅ QUICK REFERENCE

### **Important Commands**

```bash
# SSH into VM
ssh -i oracle_cloud_key ubuntu@<public-ip>

# Check instance status
sudo systemctl status cloud-init

# Check running processes
pm2 status

# Check Docker containers
docker-compose ps

# Check disk usage
df -h

# Check memory usage
free -h

# Check network connections
netstat -tulpn
```

### **Important URLs**

- Oracle Cloud Console: https://cloud.oracle.com/
- Oracle Free Tier: https://www.oracle.com/cloud/free/
- OCI Documentation: https://docs.oracle.com/en-us/iaas/

---

## 🎉 CONCLUSION

**Congratulations!** You now have a **free Oracle Cloud VM** running 24/7 for your AI Employee!

### **What You've Accomplished:**

✅ Created Oracle Cloud account
✅ Generated SSH key pair
✅ Launched VM (4 OCPUs, 24GB RAM)
✅ Configured security lists
✅ Assigned public IP
✅ Installed all prerequisites
✅ Ready for AI Employee deployment

### **Next Step:**

Run the deployment script:
```bash
bash ~/setup_oracle_cloud_vm.sh
```

---

**Created:** March 23, 2026
**Personal AI Employee Hackathon 0**
**Platinum Tier - Oracle Cloud VM Setup**

**Status:** ✅ **READY FOR DEPLOYMENT**
