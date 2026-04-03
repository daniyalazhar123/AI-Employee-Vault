@echo off
REM ============================================
REM Start Next.js Dashboard - AI Employee Vault
REM ============================================

echo.
echo ============================================================
echo   STARTING NEXT.JS DASHBOARD
echo   AI Employee Vault
echo ============================================================
echo.

cd /d "%~dp0"

REM Step 1: Check if node_modules exists
if exist "node_modules" (
    echo [1/3] Dependencies already installed
    echo.
) else (
    echo [1/3] Installing dependencies...
    echo This may take 2-3 minutes...
    echo.
    call npm install
    if errorlevel 1 (
        echo.
        echo ERROR: npm install failed!
        echo Please run: npm install
        echo.
        pause
        exit /b 1
    )
)

REM Step 2: Verify Next.js
echo [2/3] Verifying Next.js installation...
npx next --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Next.js not found!
    echo Please run: npm install
    echo.
    pause
    exit /b 1
)
echo   Next.js installed successfully!
echo.

REM Step 3: Start FastAPI backend
echo [3/3] Starting FastAPI backend...
start "FastAPI Backend" python api.py
timeout /t 2 /nobreak >nul
echo   FastAPI started on http://localhost:8000
echo.

REM Step 4: Start Next.js frontend
echo Starting Next.js frontend...
echo Dashboard will open at: http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo.
start http://localhost:3000
timeout /t 2 /nobreak >nul
npm run dev

pause
