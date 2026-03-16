@echo off
REM ============================================
REM AI Employee - Task Scheduler Setup
REM ============================================
REM This script creates scheduled tasks for all watchers
REM Run as Administrator!

echo ============================================
echo AI Employee - Task Scheduler Setup
echo ============================================
echo.

cd /d "%~dp0"

REM Check if running as admin
net session >nul 2>&1
if errorlevel 1 (
    echo ERROR: This script must be run as Administrator!
    echo Right-click and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo Running as Administrator...
echo.

REM Get full Python path
where python >%temp%\python_path.txt 2>nul
set /p PYTHON_PATH=<%temp%\python_path.txt
del %temp%\python_path.txt

if "%PYTHON_PATH%"=="" (
    echo ERROR: Python not found in PATH!
    echo Please install Python 3.13+ and add to PATH
    echo.
    pause
    exit /b 1
)

echo Python found: %PYTHON_PATH%
echo.

REM Create tasks using schtasks
echo [1/5] Creating Gmail Watcher task...
schtasks /Create /TN "AI Employee - Gmail Watcher" /TR "\"%PYTHON_PATH%\" watchers\gmail_watcher.py" /SC ONLOGON /RU SYSTEM /RL HIGHEST /F >nul 2>&1
if errorlevel 1 (
    echo Failed to create Gmail Watcher task
) else (
    echo Gmail Watcher task created!
)

echo [2/5] Creating WhatsApp Watcher task...
schtasks /Create /TN "AI Employee - WhatsApp Watcher" /TR "\"%PYTHON_PATH%\" watchers\whatsapp_watcher.py" /SC ONLOGON /RU SYSTEM /RL HIGHEST /F >nul 2>&1
if errorlevel 1 (
    echo Failed to create WhatsApp Watcher task
) else (
    echo WhatsApp Watcher task created!
)

echo [3/5] Creating Office Watcher task...
schtasks /Create /TN "AI Employee - Office Watcher" /TR "\"%PYTHON_PATH%\" watchers\office_watcher.py" /SC ONLOGON /RU SYSTEM /RL HIGHEST /F >nul 2>&1
if errorlevel 1 (
    echo Failed to create Office Watcher task
) else (
    echo Office Watcher task created!
)

echo [4/5] Creating Social Watcher task...
schtasks /Create /TN "AI Employee - Social Watcher" /TR "\"%PYTHON_PATH%\" watchers\social_watcher.py" /SC ONLOGON /RU SYSTEM /RL HIGHEST /F >nul 2>&1
if errorlevel 1 (
    echo Failed to create Social Watcher task
) else (
    echo Social Watcher task created!
)

echo [5/5] Creating CEO Briefing task...
schtasks /Create /TN "AI Employee - CEO Briefing" /TR "\"%PYTHON_PATH%\" ceo_briefing.py" /SC WEEKLY /D MON /ST 08:00 /RU SYSTEM /RL HIGHEST /F >nul 2>&1
if errorlevel 1 (
    echo Failed to create CEO Briefing task
) else (
    echo CEO Briefing task created!
)

echo.
echo ============================================
echo Task Scheduler Setup Complete!
echo ============================================
echo.
echo Tasks Created:
echo - AI Employee - Gmail Watcher (On logon)
echo - AI Employee - WhatsApp Watcher (On logon)
echo - AI Employee - Office Watcher (On logon)
echo - AI Employee - Social Watcher (On logon)
echo - AI Employee - CEO Briefing (Every Monday 8 AM)
echo.
echo To manage tasks:
echo 1. Open Task Scheduler (taskschd.msc)
echo 2. Find tasks starting with "AI Employee -"
echo 3. Right-click to Run/Disable/Properties
echo.
echo To verify:
echo - Open Task Scheduler
echo - Check task status shows "Ready"
echo - Right-click task and select "Run" to test
echo.
echo ============================================
echo.

pause
