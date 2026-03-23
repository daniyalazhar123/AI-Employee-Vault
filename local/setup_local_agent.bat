@echo off
REM ============================================
REM 🏠 PLATINUM TIER - LOCAL AGENT SETUP
REM Windows Local Machine Setup Script
REM ============================================
REM Run this script on your local Windows machine
REM Sets up Local Agent with full execute permissions

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║  🏠  PLATINUM TIER - LOCAL AGENT SETUP                ║
echo ║     AI Employee Local Agent (Approval + Execute)      ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Step 1: Check Python
echo [Step 1/8] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.10+
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✓ Python installed: %PYTHON_VERSION%

REM Step 2: Check Node.js
echo [Step 2/8] Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found! Please install Node.js 18+
    echo Download from: https://nodejs.org/
    pause
    exit /b 1
)
echo ✓ Node.js installed

REM Step 3: Check Git
echo [Step 3/8] Checking Git installation...
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git not found! Please install Git
    echo Download from: https://git-scm.com/download/win
    pause
    exit /b 1
)
echo ✓ Git installed

REM Step 4: Install Python Dependencies
echo [Step 4/8] Installing Python dependencies...
pip install requests watchdog python-dotenv playwright
if errorlevel 1 (
    echo WARNING: Some dependencies failed to install
)
echo ✓ Dependencies installed

REM Step 5: Install Playwright
echo [Step 5/8] Installing Playwright browsers...
python -m playwright install chromium
if errorlevel 1 (
    echo WARNING: Playwright installation failed
)
echo ✓ Playwright installed

REM Step 6: Setup Folders
echo [Step 6/8] Creating folder structure...
if not exist "cloud" mkdir cloud
if not exist "local" mkdir local
if not exist "Needs_Action\cloud" mkdir Needs_Action\cloud
if not exist "Needs_Action\local" mkdir Needs_Action\local
if not exist "In_Progress\cloud" mkdir In_Progress\cloud
if not exist "In_Progress\local" mkdir In_Progress\local
if not exist "Drafts\email" mkdir Drafts\email
if not exist "Drafts\social" mkdir Drafts\social
if not exist "Drafts\odoo" mkdir Drafts\odoo
if not exist "Updates" mkdir Updates
if not exist "Signals" mkdir Signals
if not exist "Pending_Approval" mkdir Pending_Approval
if not exist "Approved" mkdir Approved
if not exist "Rejected" mkdir Rejected
if not exist "Done" mkdir Done
if not exist "Logs\Audit" mkdir Logs\Audit
if not exist "Dead_Letter_Queue" mkdir Dead_Letter_Queue
echo ✓ Folder structure created

REM Step 7: Create Environment Files
echo [Step 7/8] Creating environment files...

REM Create .env.example
(
echo # Local Environment Variables
echo # SECURITY: This file contains secrets - NEVER commit!
echo.
echo # Agent Configuration
echo AGENT_TYPE=execute
echo LOCAL_MODE=true
echo.
echo # Full Permissions for Local Agent
echo EMAIL_SEND=true
echo WHATSAPP_SEND=true
echo SOCIAL_POST=true
echo PAYMENT_EXECUTE=true
echo.
echo # Odoo (Full access for Local)
echo ODOO_CREATE_INVOICE=true
echo ODOO_RECORD_PAYMENT=true
echo ODOO_READ_REPORTS=true
echo.
echo # Paths
echo VAULT_PATH=%CD%
echo WHATSAPP_SESSION=%APPDATA%\WhatsApp\Web
echo.
echo # MCP Credentials (Local only - NEVER sync!)
echo GMAIL_CREDENTIALS=%CD%\mcp-email\credentials.json
echo BANKING_CREDENTIALS=%CD%\local\.env.local
) > .env.example

REM Create local\.env.local
(
echo # Local Agent Secrets
echo # SECURITY: NEVER commit this file!
echo.
echo # Email Send Credentials
echo GMAIL_SEND_USER=your_email@gmail.com
echo GMAIL_SEND_PASSWORD=your_app_password
echo.
echo # WhatsApp Session (stored locally)
echo WHATSAPP_SESSION_PATH=%APPDATA%\WhatsApp\Web
echo.
echo # Banking Credentials
echo BANKING_API_KEY=your_banking_api_key
echo BANKING_ACCOUNT_ID=your_account_id
echo.
echo # Social Media Posting
echo LINKEDIN_ACCESS_TOKEN=your_linkedin_token
echo TWITTER_ACCESS_TOKEN=your_twitter_token
echo FACEBOOK_ACCESS_TOKEN=your_facebook_token
echo INSTAGRAM_ACCESS_TOKEN=your_instagram_token
) > local\.env.local.example

echo ✓ Environment files created

REM Step 8: Create Startup Scripts
echo [Step 8/8] Creating startup scripts...

REM Create local agent startup
(
echo @echo off
echo REM Start Local Agent
echo.
echo cd /d "%%~dp0"
echo.
echo REM Load environment
echo if exist ..\local\.env.local ^(
echo     for /f "delims=" %%%%a in ('type ..\local\.env.local ^| findstr /v "^#" ^| findstr /v "^$"') do set "%%%%a"
echo ^)
echo.
echo REM Install dependencies
echo pip install -r requirements.txt 2^>nul
echo.
echo REM Start Local Agent
echo echo Starting Local Agent...
echo python local_agent.py
echo.
echo if errorlevel 1 ^(
echo     echo Local Agent crashed!
echo     pause
echo ^)
) > local\start_local_agent.bat

REM Create approval watcher
(
echo @echo off
echo REM Watch for approvals and execute
echo.
echo cd /d "%%~dp0.."
echo.
echo echo Starting Approval Watcher...
echo python local\approval_watcher.py
) > local\start_approval_watcher.bat

echo ✓ Startup scripts created

REM Setup Git (if not already done)
echo.
echo [Git Setup] Checking Git repository...
if not exist ".git" (
    echo Initializing Git repository...
    git init
    echo.
    echo ⚠ IMPORTANT: Configure .gitignore before committing!
    echo The script created .gitignore.example - rename it to .gitignore
) else (
    echo ✓ Git repository already initialized
)

REM Final summary
echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║  🏠  LOCAL AGENT SETUP COMPLETE!                      ║
echo ╚════════════════════════════════════════════════════════╝
echo.
echo 📂 Vault Path: %CD%
echo.
echo 🔒 SECURITY CRITICAL:
echo    - Review .gitignore.example
echo    - NEVER commit .env files
echo    - NEVER commit credentials
echo    - WhatsApp session stays local only
echo.
echo 🚀 Next Steps:
echo.
echo 1. Configure environment:
echo    notepad local\.env.local
echo.
echo 2. Review .gitignore:
echo    copy .gitignore.example .gitignore
echo.
echo 3. Start Local Agent:
echo    cd local
echo    start_local_agent.bat
echo.
echo 4. Start Approval Watcher:
echo    cd local
echo    start_approval_watcher.bat
echo.
echo 5. Test Platinum Demo:
echo    cd ..
echo    python platinum_demo.py
echo.
echo 📝 Important Files:
echo    - local\.env.local (secrets - NEVER commit!)
echo    - local\start_local_agent.bat
echo    - local\approval_watcher.py
echo.
echo ✓ Local Agent ready for Platinum Tier!
echo.
pause
