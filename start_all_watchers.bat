@echo off
REM ============================================
REM AI Employee - Start All Watchers
REM ============================================
REM This script starts all watcher processes
REM Run as administrator for best results

echo ============================================
echo AI Employee - Starting All Watchers
echo ============================================
echo.

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    echo Please install Python 3.13+ and add to PATH
    pause
    exit /b 1
)

echo Python found!
echo.

REM Create logs directory if not exists
if not exist "Logs" mkdir Logs

REM Start Gmail Watcher
echo [1/5] Starting Gmail Watcher...
start "Gmail Watcher" python watchers\gmail_watcher.py
timeout /t 3 /nobreak >nul

REM Start WhatsApp Watcher
echo [2/5] Starting WhatsApp Watcher...
start "WhatsApp Watcher" python watchers\whatsapp_watcher.py
timeout /t 3 /nobreak >nul

REM Start Office Watcher
echo [3/5] Starting Office Watcher...
start "Office Watcher" python watchers\office_watcher.py
timeout /t 3 /nobreak >nul

REM Start Social Watcher
echo [4/5] Starting Social Watcher...
start "Social Watcher" python watchers\social_watcher.py
timeout /t 3 /nobreak >nul

echo [5/5] All watchers started!
echo.
echo ============================================
echo Status: All watchers are now running
echo ============================================
echo.
echo To stop watchers: Close the terminal windows
echo Or run: stop_all_watchers.bat
echo.
echo Logs are saved in: Logs\ folder
echo ============================================
echo.

REM Keep this window open to see status
echo Monitoring... (Close this window to exit)
pause
