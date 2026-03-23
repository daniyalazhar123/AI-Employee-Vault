# 📦 ODOO 19 INSTALLATION GUIDE

**Bhai! Yeh follow karo, Odoo install ho jayega!** 🚀

---

## ⚠️ **DOCKER NAHI CHAL RAHA!**

**Issue:** Docker Desktop run nahi ho raha hai.

**Solution:** Docker Desktop start karo ya direct install karo.

---

## 🎯 **INSTALLATION OPTIONS:**

### **Option 1: Docker Desktop Start Karo** (Easiest - 5 minutes)

**Step 1: Docker Desktop Start**
```
1. Docker Desktop application dhundo
2. Double-click karke start karo
3. Wait karo jab tak "Docker Desktop is running" na dikhe
```

**Step 2: Odoo Install**
```bash
cd "C:\Users\CC\Documents\Obsidian Vault"
docker run -d -p 8069:8069 --name odoo_community odoo:19.0
```

**Step 3: Access Odoo**
```
Browser mein kholo: http://localhost:8069
```

---

### **Option 2: Direct Download & Install** (15 minutes)

**Step 1: Odoo 19 Download**

Download link:
```
https://github.com/odoo/odoo/releases/download/19.0/odoo_19.0.latest.exe
```

**Ya phir:**
```
https://www.odoo.com/page/download
```

**Step 2: Install Odoo**

1. Downloaded file pe double-click karo
2. Next → Next → Install
3. Default settings accept karo
4. Installation complete hone do (5-7 minutes)

**Step 3: Odoo Start**

```
1. Odoo application start karo
2. Browser automatically khulega
3. Ya manually kholo: http://localhost:8069
```

---

### **Option 3: Python se Run Karo** (Advanced - 20 minutes)

**Step 1: Python Dependencies Install**
```bash
pip install odoo
```

**Step 2: PostgreSQL Install**
```
Download: https://www.postgresql.org/download/windows/
Install karo
```

**Step 3: Odoo Run**
```bash
odoo -c odoo.conf
```

---

## 🚀 **RECOMMENDED: DOCKER DESKTOP START**

### **Docker Desktop Kaise Start Karein:**

**Method 1: Start Menu**
```
1. Windows Start button click karo
2. "Docker Desktop" search karo
3. Click karke start karo
4. Wait karo (1-2 minutes)
5. Green icon dikhega "Docker Desktop is running"
```

**Method 2: Direct Path**
```
1. Yeh path pe jao:
   C:\Program Files\Docker\Docker\Docker Desktop.exe

2. Double-click karke start karo
```

**Method 3: Command Line**
```bash
"C:\Program Files\Docker\Docker\Docker Desktop.exe"
```

---

## ✅ **DOCKER START KARNE KE BAAD:**

### **Step 1: Verify Docker**
```bash
docker --version
docker ps
```

**Expected:**
```
Docker version 29.2.0
CONTAINER ID   IMAGE   COMMAND   ...
```

### **Step 2: Odoo Install**
```bash
cd "C:\Users\CC\Documents\Obsidian Vault"
docker run -d -p 8069:8069 --name odoo_community \
  -e ODOO_DATABASE=odoo \
  -e ODOO_ADMIN_PASSWORD=admin \
  odoo:19.0
```

### **Step 3: Check Status**
```bash
docker ps
docker logs odoo_community
```

### **Step 4: Access Odoo**
```
Browser: http://localhost:8069
```

---

## 📋 **ODOO SETUP STEPS:**

### **Database Creation** (5 minutes)

**Step 1: Odoo Open**
```
http://localhost:8069
```

**Step 2: Create Database**
```
1. Click "Create Database"
2. Master Password: admin
3. Database Name: odoo
4. Email: admin@example.com
5. Password: admin
6. Click "Create Database"
```

**Step 3: Wait**
```
Database creation mein 2-3 minutes lagenge
Wait karo...
```

---

### **Install Apps** (5 minutes)

**Step 1: Apps Menu**
```
1. Odoo dashboard pe jao
2. "Apps" icon click karo
```

**Step 2: Install Required Apps**
```
Search karke install karo:

1. Invoicing (Accounting)
   - Search: "Invoicing"
   - Click "Install"

2. CRM
   - Search: "CRM"
   - Click "Install"

3. Contacts
   - Search: "Contacts"
   - Click "Install"

4. Sales (Optional)
   - Search: "Sales"
   - Click "Install"
```

---

## 🔧 **ODOO MCP CONFIGURATION:**

### **Update MCP Config**

File: `config/mcp.json`

```json
{
  "mcpServers": {
    "odoo": {
      "command": "node",
      "args": ["C:/Users/CC/Documents/Obsidian Vault/mcp-odoo/index.js"],
      "env": {
        "ODOO_URL": "http://localhost:8069",
        "ODOO_DB": "odoo",
        "ODOO_USERNAME": "admin",
        "ODOO_PASSWORD": "admin"
      }
    }
  }
}
```

### **Test Connection**
```bash
cd "C:\Users\CC\Documents\Obsidian Vault\mcp-odoo"
python test_mcp.py
```

**Expected:**
```
Odoo MCP Server running
Connected to Odoo at http://localhost:8069
User ID: 2
```

---

## 🎯 **QUICK COMMANDS:**

### **Start Odoo (Docker)**
```bash
docker start odoo_community
```

### **Stop Odoo**
```bash
docker stop odoo_community
```

### **Restart Odoo**
```bash
docker restart odoo_community
```

### **Check Logs**
```bash
docker logs odoo_community
```

### **Remove Odoo**
```bash
docker rm -f odoo_community
```

---

## 📊 **VERIFICATION CHECKLIST:**

```
Odoo Installation Checklist:
┌─────────────────────────────────────────────────────────┐
│ [ ] Docker Desktop running                              │
│ [ ] Odoo container running                              │
│ [ ] http://localhost:8069 accessible                    │
│ [ ] Database created (odoo)                             │
│ [ ] Apps installed (Invoicing, CRM, Contacts)           │
│ [ ] MCP server connected                                │
│ [ ] Test lead created                                   │
│ [ ] Test invoice created                                │
└─────────────────────────────────────────────────────────┘
```

---

## 🚨 **TROUBLESHOOTING:**

### **Issue: Docker Desktop Start Nahi Ho Raha**

**Solution:**
```
1. Computer restart karo
2. BIOS mein virtualization enable check karo
3. Docker Desktop reinstall karo
```

### **Issue: Port 8069 Already in Use**

**Solution:**
```bash
# Different port use karo
docker run -d -p 8070:8069 --name odoo_community odoo:19.0

# Access: http://localhost:8070
```

### **Issue: Database Creation Failed**

**Solution:**
```
1. Browser cache clear karo
2. Incognito mode try karo
3. Docker container restart karo
```

### **Issue: MCP Connection Failed**

**Solution:**
```bash
# Check Odoo is running
docker ps

# Check credentials
type config\mcp.json

# Test manually
curl http://localhost:8069
```

---

## 🎉 **POST-INSTALLATION:**

### **Test Odoo MCP**

```bash
cd "C:\Users\CC\Documents\Obsidian Vault"
python ai_employee_orchestrator.py
```

**Choice 4 select karo:**
```
4. Process specific platform
   → Odoo (choice 7)
```

### **Create Test Lead**

Odoo mein jao:
```
1. CRM → Leads → New
2. Name: Test Lead
3. Email: test@example.com
4. Phone: +92-300-1234567
5. Save
```

### **Test with AI Employee**

```bash
python ai_employee_orchestrator.py
# Choice 2: Run demo
```

---

## 📞 **NEXT STEPS:**

### **Immediate:**
1. ✅ Docker Desktop start karo
2. ⚪ Odoo install karo
3. ⚪ Database create karo
4. ⚪ Apps install karo
5. ⚪ MCP test karo

### **After Installation:**
6. ⚪ Test lead create karo
7. ⚪ Test invoice create karo
8. ⚪ AI Employee se process karwao

---

## 🎯 **DOCKER DESKTOP DOWNLOAD:**

Agar Docker Desktop install nahi hai:

**Download Link:**
```
https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe
```

**Installation:**
```
1. Downloaded file run karo
2. "Use WSL 2" select karo
3. Install click karo
4. Restart computer
5. Docker Desktop start karo
```

---

## 📊 **EXPECTED RESULTS:**

### **After Installation:**
```
✅ Odoo running on http://localhost:8069
✅ Database: odoo
✅ Username: admin
✅ Password: admin
✅ Apps: Invoicing, CRM, Contacts
✅ MCP Server: Connected
✅ AI Employee: Ready to process leads
```

---

## 🎉 **BHAI! READY HAI?**

**Ab bas yeh karo:**

1. **Docker Desktop start karo**
2. **Yeh command run karo:**
   ```bash
   docker run -d -p 8069:8069 --name odoo_community odoo:19.0
   ```
3. **Browser mein kholo:** http://localhost:8069
4. **Database create karo**
5. **Apps install karo**

**Done!** ✅

---

**Status:** ⚪ **Installation Guide Ready**  
**Next:** Docker Desktop start karo  
**Time:** 15 minutes  

---

*Bhai! Docker Desktop start karo, phir main Odoo install karwa dunga!* 🚀
