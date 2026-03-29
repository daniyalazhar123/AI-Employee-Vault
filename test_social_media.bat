@echo off
REM ============================================
REM Social Media Manual Testing Script
REM AI Employee Vault - All Platforms
REM ============================================

echo.
echo ============================================================
echo   SOCIAL MEDIA MANUAL TESTING
echo   AI Employee Vault - All Platforms
echo ============================================================
echo.

cd /d "%~dp0"

:MENU
echo.
echo Select Platform to Test:
echo ============================================================
echo   1. LinkedIn
echo   2. Facebook
echo   3. Instagram
echo   4. Twitter (X)
echo   5. WhatsApp
echo   6. Test All Platforms
echo   7. Exit
echo ============================================================
echo.
set /p choice="Enter your choice (1-7): "

if "%choice%"=="1" goto LINKEDIN
if "%choice%"=="2" goto FACEBOOK
if "%choice%"=="3" goto INSTAGRAM
if "%choice%"=="4" goto TWITTER
if "%choice%"=="5" goto WHATSAPP
if "%choice%"=="6" goto ALL
if "%choice%"=="7" goto END
goto MENU

:LINKEDIN
echo.
echo ============================================================
echo   LINKEDIN TESTING
echo ============================================================
echo.
echo [1] Generate Post Draft
echo [2] View Drafts
echo [3] Test Auto-Post (Dry Run)
echo [4] View Posted Logs
echo [5] Back to Menu
echo.
set /p li_choice="Enter choice (1-5): "

if "%li_choice%"=="1" (
    echo.
    echo Generating LinkedIn post...
    python linkedin_post_generator.py "Test Post from AI Employee"
    echo.
    pause
    goto LINKEDIN
)
if "%li_choice%"=="2" (
    echo.
    dir /b Social_Drafts\linkedin_*.md
    set /p draft="Enter draft filename to view: "
    if not "%draft%"=="" type "Social_Drafts\%draft%"
    echo.
    pause
    goto LINKEDIN
)
if "%li_choice%"=="3" (
    echo.
    echo Testing LinkedIn auto-post (DRY RUN)...
    python linkedin_auto_post.py "Test post from AI Employee! #Hackathon2026"
    echo.
    pause
    goto LINKEDIN
)
if "%li_choice%"=="4" (
    echo.
    dir /b Logs\linkedin_post_*.md
    echo.
    pause
    goto LINKEDIN
)
goto LINKEDIN

:FACEBOOK
echo.
echo ============================================================
echo   FACEBOOK TESTING
echo ============================================================
echo.
echo [1] Generate Facebook Post
echo [2] View Facebook Drafts
echo [3] Test MCP Social
echo [4] Back to Menu
echo.
set /p fb_choice="Enter choice (1-4): "

if "%fb_choice%"=="1" (
    echo.
    python facebook_instagram_post.py "Facebook Test Post"
    echo.
    pause
    goto FACEBOOK
)
if "%fb_choice%"=="2" (
    echo.
    dir /b Social_Drafts\facebook_*.md
    set /p draft="Enter draft filename: "
    if not "%draft%"=="" type "Social_Drafts\%draft%"
    echo.
    pause
    goto FACEBOOK
)
if "%fb_choice%"=="3" (
    echo.
    python mcp_social.py --action facebook --content "Test Facebook post"
    echo.
    pause
    goto FACEBOOK
)
goto FACEBOOK

:INSTAGRAM
echo.
echo ============================================================
echo   INSTAGRAM TESTING
echo ============================================================
echo.
echo [1] Generate Instagram Post
echo [2] View Instagram Drafts
echo [3] Test MCP Social
echo [4] Back to Menu
echo.
set /p ig_choice="Enter choice (1-4): "

if "%ig_choice%"=="1" (
    echo.
    python facebook_instagram_post.py "Instagram Test Post"
    echo.
    pause
    goto INSTAGRAM
)
if "%ig_choice%"=="2" (
    echo.
    dir /b Social_Drafts\instagram_*.md
    set /p draft="Enter draft filename: "
    if not "%draft%"=="" type "Social_Drafts\%draft%"
    echo.
    pause
    goto INSTAGRAM
)
if "%ig_choice%"=="3" (
    echo.
    python mcp_social.py --action instagram --content "Test Instagram post #AI"
    echo.
    pause
    goto INSTAGRAM
)
goto INSTAGRAM

:TWITTER
echo.
echo ============================================================
echo   TWITTER (X) TESTING
echo ============================================================
echo.
echo [1] Generate Tweet
echo [2] View Tweet Drafts
echo [3] Test MCP Social
echo [4] Back to Menu
echo.
set /p tw_choice="Enter choice (1-4): "

if "%tw_choice%"=="1" (
    echo.
    python twitter_post.py "Test tweet from AI Employee! #Hackathon2026"
    echo.
    pause
    goto TWITTER
)
if "%tw_choice%"=="2" (
    echo.
    dir /b Social_Drafts\twitter_*.md
    set /p draft="Enter draft filename: "
    if not "%draft%"=="" type "Social_Drafts\%draft%"
    echo.
    pause
    goto TWITTER
)
if "%tw_choice%"=="3" (
    echo.
    python mcp_social.py --action twitter --content "Test tweet!"
    echo.
    pause
    goto TWITTER
)
goto TWITTER

:WHATSAPP
echo.
echo ============================================================
echo   WHATSAPP TESTING
echo ============================================================
echo.
echo [1] Check WhatsApp Watcher
echo [2] Test WhatsApp Watcher
echo [3] Check WhatsApp Session
echo [4] View WhatsApp Messages
echo [5] Open WhatsApp Web
echo [6] Back to Menu
echo.
set /p wa_choice="Enter choice (1-6): "

if "%wa_choice%"=="1" (
    echo.
    python watchers\whatsapp_watcher.py --help
    echo.
    pause
    goto WHATSAPP
)
if "%wa_choice%"=="2" (
    echo.
    cd watchers
    python whatsapp_watcher.py --test
    cd ..
    echo.
    pause
    goto WHATSAPP
)
if "%wa_choice%"=="3" (
    echo.
    dir /b whatsapp_session\
    echo.
    pause
    goto WHATSAPP
)
if "%wa_choice%"=="4" (
    echo.
    dir /b Needs_Action\WHATSAPP_*.md
    set /p msg="Enter message filename: "
    if not "%msg%"=="" type "Needs_Action\%msg%"
    echo.
    pause
    goto WHATSAPP
)
if "%wa_choice%"=="5" (
    echo.
    start https://web.whatsapp.com
    echo WhatsApp Web opened in browser
    echo.
    pause
    goto WHATSAPP
)
goto WHATSAPP

:ALL
echo.
echo ============================================================
echo   TESTING ALL PLATFORMS
echo ============================================================
echo.

echo [1/5] Testing LinkedIn...
python linkedin_post_generator.py "Test Post"
echo.

echo [2/5] Testing Facebook...
python facebook_instagram_post.py "Test Post"
echo.

echo [3/5] Testing Instagram...
echo Instagram draft generated above
echo.

echo [4/5] Testing Twitter...
python twitter_post.py "Test Tweet"
echo.

echo [5/5] Testing WhatsApp...
dir /b Needs_Action\WHATSAPP_*.md
echo.

echo ============================================================
echo   ALL TESTS COMPLETE!
echo ============================================================
echo.
echo View Drafts:
echo   LinkedIn:   dir Social_Drafts\linkedin_*.md
echo   Facebook:   dir Social_Drafts\facebook_*.md
echo   Instagram:  dir Social_Drafts\instagram_*.md
echo   Twitter:    dir Social_Drafts\twitter_*.md
echo.
pause
goto MENU

:END
echo.
echo ============================================================
echo   Testing Session Complete!
echo ============================================================
echo.
exit /b
