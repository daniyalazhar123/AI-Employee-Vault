@echo off
REM AI Employee Dashboard - One-Click Start
REM Personal AI Employee Hackathon 0

echo ╔════════════════════════════════════════════════════════╗
echo ║  🤖 AI Employee Dashboard - Starting...               ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.10+
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python found

REM Install required packages
echo.
echo 📦 Installing required packages...
pip install fastapi uvicorn python-multipart -q

echo ✅ Packages installed

REM Start the dashboard
echo.
echo 🚀 Starting Dashboard API...
echo 📱 Open browser: http://localhost:8000
echo.
echo Press Ctrl+C to stop
echo.

cd /d "%~dp0"
python api.py

pause
