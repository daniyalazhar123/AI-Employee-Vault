@echo off
REM ============================================
REM 💿 PLATINUM TIER - VAULT SYNC (LOCAL)
REM ============================================
REM Run on Local machine every 5 minutes
REM Syncs vault with Cloud VM via Git

cd /d "C:\Users\CC\Documents\Obsidian Vault"

echo ============================================ >> sync.log
echo %date% %time%: Starting Git sync... >> sync.log

REM Git pull - get changes from Cloud
echo %date% %time%: Pulling from remote... >> sync.log
git pull origin main >> sync.log 2>&1
if %errorlevel% neq 0 (
    echo %date% %time%: ERROR - Git pull failed >> sync.log
) else (
    echo %date% %time%: Git pull successful >> sync.log
)

REM Git add - stage local changes
git add .

REM Git status check - any changes to commit?
git diff --cached --quiet
if %errorlevel% equ 0 (
    echo %date% %time%: No changes to commit >> sync.log
) else (
    echo %date% %time%: Committing local changes... >> sync.log
    git commit -m "Local Agent sync %date% %time%" >> sync.log 2>&1
    
    echo %date% %time%: Pushing to remote... >> sync.log
    git push origin main >> sync.log 2>&1
    if %errorlevel% neq 0 (
        echo %date% %time%: ERROR - Git push failed (may need pull first) >> sync.log
    ) else (
        echo %date% %time%: Git push successful >> sync.log
    )
)

echo %date% %time%: Sync complete >> sync.log
echo. >> sync.log
