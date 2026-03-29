@echo off
REM ============================================
REM LinkedIn Auto-Posting Setup Script
REM AI Employee Vault
REM ============================================

echo.
echo ============================================================
echo   LINKEDIN AUTO-POSTING SETUP
echo   AI Employee Vault - Personal AI Employee Hackathon 0
echo ============================================================
echo.

cd /d "%~dp0"

REM Step 1: Check Playwright
echo [1/5] Checking Playwright installation...
python -c "from playwright.sync_api import sync_playwright; print('')" 2>nul
if %errorlevel% neq 0 (
    echo    Playwright not found! Installing...
    playwright install chromium
) else (
    echo    Playwright already installed
)
echo.

REM Step 2: Check .env.linkedin file
echo [2/5] Checking LinkedIn configuration...
if exist ".env.linkedin" (
    echo    Configuration file found: .env.linkedin
    echo.
    echo    NEXT STEP: Edit .env.linkedin with your credentials
    echo.
    echo    Open file with: notepad .env.linkedin
    echo.
    echo    Replace these values:
    echo      LINKEDIN_EMAIL=your.email@example.com
    echo      LINKEDIN_PASSWORD=your_password
    echo      DRY_RUN=false  (for actual posting)
) else (
    echo    WARNING: .env.linkedin not found!
    echo    Creating default configuration...
    copy .env.example .env.linkedin >nul
    echo    Created: .env.linkedin
)
echo.

REM Step 3: Test LinkedIn script
echo [3/5] Testing LinkedIn auto-poster script...
if exist "linkedin_auto_post.py" (
    echo    Script found: linkedin_auto_post.py
    python linkedin_auto_post.py --help 2>nul
) else (
    echo    ERROR: linkedin_auto_post.py not found!
)
echo.

REM Step 4: Create test post
echo [4/5] Creating test post draft...
if exist "linkedin_post_generator.py" (
    python linkedin_post_generator.py "AI Employee Hackathon Test" 2>nul
    if exist "Social_Drafts\linkedin_post_*.md" (
        echo    Test draft created successfully
    ) else (
        echo    Draft creation may have failed
    )
) else (
    echo    LinkedIn post generator not found
)
echo.

REM Step 5: Show instructions
echo [5/5] Setup Complete! Next Steps:
echo ============================================================
echo.
echo  STEP 1: Edit .env.linkedin with your credentials
echo  --------------------------------------------------------
echo  1. Run: notepad .env.linkedin
echo  2. Replace:
echo     LINKEDIN_EMAIL=your.email@example.com
echo     LINKEDIN_PASSWORD=your_password
echo     DRY_RUN=false
echo.
echo  STEP 2: Test with dry run (SAFE)
echo  --------------------------------------------------------
echo  python linkedin_auto_post.py "Test post from AI Employee"
echo.
echo  STEP 3: Post to LinkedIn (when ready)
echo  --------------------------------------------------------
echo  python linkedin_auto_post.py "Your actual post content"
echo.
echo  OR post from draft:
echo  python linkedin_auto_post.py --file "Social_Drafts\linkedin_post.md"
echo.
echo ============================================================
echo.
echo  SECURITY REMINDER:
echo  - Never commit .env.linkedin to Git
echo  - Use strong password
echo  - Enable 2FA on LinkedIn
echo  - Start with DRY_RUN=true for testing
echo.
echo ============================================================
echo.
pause
