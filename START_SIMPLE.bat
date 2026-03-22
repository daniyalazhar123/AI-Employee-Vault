@echo off
REM ============================================
REM 🚀 SIMPLE AI EMPLOYEE STARTER
REM ============================================
REM Bhai! Bas is file pe double click karo!
REM ============================================

echo.
echo ============================================
echo 🤖 AI EMPLOYEE START HO RAHA HAI...
echo ============================================
echo.

cd /d "C:\Users\CC\Documents\Obsidian Vault"

echo Step 1: Checking Python...
python --version
if %errorlevel% neq 0 (
    echo.
    echo ❌ Python install nahi hai!
    echo Please install Python from: https://python.org/
    echo.
    pause
    exit /b 1
)
echo ✅ Python installed!
echo.

echo Step 2: Checking Node.js...
node --version
if %errorlevel% neq 0 (
    echo.
    echo ❌ Node.js install nahi hai!
    echo Please install Node.js from: https://nodejs.org/
    echo.
    pause
    exit /b 1
)
echo ✅ Node.js installed!
echo.

echo Step 3: Installing dependencies...
pip install langdetect googletrans==4.0.0-rc1 schedule psutil -q
echo ✅ Dependencies installed!
echo.

echo Step 4: Testing Multi-Language Agent...
echo.
python multi_language_agent.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ Koi error aaya!
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo ✅ AI EMPLOYEE TEST COMPLETE!
echo ============================================
echo.
pause
