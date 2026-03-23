@echo off
REM AI Employee Dashboard - Next.js 14 Start
REM Pure Python Backend + Next.js 14 Frontend

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

REM Install Python dependencies
echo.
echo 📦 Installing Python dependencies...
pip install fastapi uvicorn python-multipart -q
echo ✅ Python dependencies installed

REM Install Node dependencies
echo.
echo 📦 Installing Next.js dependencies...
call npm install
echo ✅ Next.js dependencies installed

echo.
echo 🚀 Starting Dashboard...
echo 📱 Backend: http://localhost:8000
echo 🖥️  Frontend: http://localhost:3000
echo.
echo Press Ctrl+C to stop
echo.

REM Start backend in background
start "FastAPI Backend" cmd /k "cd .. && python dashboard/api.py"

REM Wait for backend to start
timeout /t 3 /nobreak >nul

REM Start Next.js frontend
cd /d "%~dp0"
npm run dev

pause
