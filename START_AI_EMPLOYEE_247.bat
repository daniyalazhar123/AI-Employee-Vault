@echo off
REM ============================================
REM 🚀 AI EMPLOYEE 24/7 - COMPLETE STARTUP
REM ============================================
REM Bhai! Yeh script complete AI Employee ko
REM 24/7 mode mein start karegi with Qwen CLI!
REM ============================================

echo ============================================
echo 🤖 AI EMPLOYEE 24/7 - STARTING
echo ============================================
echo.
echo Bhai! Complete AI Employee start ho raha hai...
echo.
echo Features:
echo   ✅ Qwen CLI Brain
echo   ✅ 25+ Languages Support
echo   ✅ All Programming Languages
echo   ✅ All AI Frameworks
echo   ✅ Social Media Automation
echo   ✅ Cloud Deployment Ready
echo   ✅ Security Monitoring
echo   ✅ 24/7 Operation
echo.
echo ============================================
echo.

cd /d "C:\Users\CC\Documents\Obsidian Vault"

REM Check if PM2 is installed
where pm2 >nul 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  PM2 not found. Installing...
    npm install -g pm2
)

echo ✅ PM2 is ready!
echo.

REM Install Python dependencies
echo 📦 Installing Python dependencies...
pip install langdetect googletrans==4.0.0-rc1 schedule psutil -q
echo ✅ Python dependencies installed!
echo.

REM Start all processes with PM2
echo 🚀 Starting all AI Employee processes...
echo.

pm2 start ecosystem.config.js

echo.
echo ============================================
echo ✅ AI EMPLOYEE 24/7 STARTED!
echo ============================================
echo.
echo Running Processes:
pm2 list
echo.
echo ============================================
echo.
echo Commands:
echo   pm2 list          - Show all processes
echo   pm2 monit         - Monitor in real-time
echo   pm2 logs          - View logs
echo   pm2 restart all   - Restart all processes
echo   pm2 stop all      - Stop all processes
echo.
echo ============================================
echo.
echo Bhai! AI Employee ab 24/7 chal raha hai!
echo.
echo Testing:
echo   1. python multi_language_agent.py
echo   2. python platinum_demo.py
echo   3. pm2 monit
echo.
echo Khuda Hafiz! AI Employee sambhal lega! 😊
echo.
pause
