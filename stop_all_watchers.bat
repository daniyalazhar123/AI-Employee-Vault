@echo off
REM ============================================
REM AI Employee - Stop All Watchers
REM ============================================
REM This script stops all watcher processes

echo ============================================
echo AI Employee - Stopping All Watchers
echo ============================================
echo.

REM Stop Gmail Watcher
echo [1/5] Stopping Gmail Watcher...
taskkill /FI "WINDOWTITLE eq Gmail Watcher" /T /F >nul 2>&1
if errorlevel 1 (
    echo Gmail Watcher not running
) else (
    echo Gmail Watcher stopped
)

REM Stop WhatsApp Watcher
echo [2/5] Stopping WhatsApp Watcher...
taskkill /FI "WINDOWTITLE eq WhatsApp Watcher" /T /F >nul 2>&1
if errorlevel 1 (
    echo WhatsApp Watcher not running
) else (
    echo WhatsApp Watcher stopped
)

REM Stop Office Watcher
echo [3/5] Stopping Office Watcher...
taskkill /FI "WINDOWTITLE eq Office Watcher" /T /F >nul 2>&1
if errorlevel 1 (
    echo Office Watcher not running
) else (
    echo Office Watcher stopped
)

REM Stop Social Watcher
echo [4/5] Stopping Social Watcher...
taskkill /FI "WINDOWTITLE eq Social Watcher" /T /F >nul 2>&1
if errorlevel 1 (
    echo Social Watcher not running
) else (
    echo Social Watcher stopped
)

echo.
echo [5/5] Cleanup complete!
echo.
echo ============================================
echo All watchers stopped
echo ============================================
echo.

pause
