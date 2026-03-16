@echo off
REM ============================================
REM AI Employee - MCP Servers Installation
REM ============================================
REM This script installs all MCP servers and dependencies

echo ============================================
echo AI Employee - MCP Servers Installation
echo ============================================
echo.

cd /d "%~dp0"

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found!
    echo Please install Node.js 18+ from https://nodejs.org/
    echo.
    pause
    exit /b 1
)

echo Node.js found!
echo.

REM Install Email MCP
echo [1/4] Installing Email MCP...
cd mcp-email
call npm install
if errorlevel 1 (
    echo Failed to install Email MCP
    cd ..
    pause
    exit /b 1
)
cd ..
echo Email MCP installed!
echo.

REM Install Browser MCP
echo [2/4] Installing Browser MCP...
cd mcp-browser
call npm install
if errorlevel 1 (
    echo Failed to install Browser MCP
    cd ..
    pause
    exit /b 1
)
echo Installing Playwright Chromium browser...
call npx playwright install chromium
if errorlevel 1 (
    echo Warning: Playwright browser installation failed
)
cd ..
echo Browser MCP installed!
echo.

REM Install Odoo MCP
echo [3/4] Installing Odoo MCP...
cd mcp-odoo
call npm install
if errorlevel 1 (
    echo Failed to install Odoo MCP
    cd ..
    pause
    exit /b 1
)
cd ..
echo Odoo MCP installed!
echo.

REM Install Social MCP
echo [4/4] Installing Social MCP...
cd mcp-social
call npm install
if errorlevel 1 (
    echo Failed to install Social MCP
    cd ..
    pause
    exit /b 1
)
echo Installing Playwright Chromium browser...
call npx playwright install chromium
if errorlevel 1 (
    echo Warning: Playwright browser installation failed
)
cd ..
echo Social MCP installed!
echo.

REM Create Screenshots folder
if not exist "Social_Drafts\Screenshots" (
    mkdir "Social_Drafts\Screenshots"
    echo Screenshots folder created!
)

echo ============================================
echo ✅ All MCP Servers Installed Successfully!
echo ============================================
echo.
echo Next Steps:
echo 1. Authenticate Gmail:
echo    cd mcp-email
echo    node authenticate.js
echo.
echo 2. Configure Claude Code:
echo    Copy config\mcp.json to:
echo    %%APPDATA%%\claude-code\mcp.json
echo.
echo 3. Test MCP servers:
echo    cd mcp-email
echo    npm start
echo.
echo ============================================
echo.

pause
