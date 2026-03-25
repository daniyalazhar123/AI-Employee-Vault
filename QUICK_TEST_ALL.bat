@echo off
REM ============================================
REM AI Employee Vault - Quick Test Script
REM Personal AI Employee Hackathon 0
REM ============================================

echo.
echo ============================================================
echo   AI EMPLOYEE VAULT - QUICK TEST
echo ============================================================
echo.

cd /d "%~dp0"

REM Count Python files
echo [1] Checking Python files...
set /p total_python= <nul
for %%f in (*.py) do set /p total_python= <nul
echo.

REM Test compilation of main files
echo.
echo [2] Testing MCP Servers Compilation...
echo ------------------------------------------------------------
python -m py_compile mcp_email.py && echo   ✅ mcp_email.py
python -m py_compile mcp_browser.py && echo   ✅ mcp_browser.py
python -m py_compile mcp_odoo.py && echo   ✅ mcp_odoo.py
python -m py_compile mcp_social.py && echo   ✅ mcp_social.py

echo.
echo [3] Testing Watchers Compilation...
echo ------------------------------------------------------------
for %%f in (watchers\*.py) do (
    python -m py_compile "%%f" && echo   ✅ %%f
)

echo.
echo [4] Testing Core Systems Compilation...
echo ------------------------------------------------------------
python -m py_compile orchestrator.py && echo   ✅ orchestrator.py
python -m py_compile ralph_loop.py && echo   ✅ ralph_loop.py
python -m py_compile audit_logger.py && echo   ✅ audit_logger.py
python -m py_compile error_recovery.py && echo   ✅ error_recovery.py
python -m py_compile health_monitor.py && echo   ✅ health_monitor.py

echo.
echo [5] Testing Business Logic Compilation...
echo ------------------------------------------------------------
python -m py_compile ceo_briefing_enhanced.py && echo   ✅ ceo_briefing_enhanced.py
python -m py_compile social_summary_generator.py && echo   ✅ social_summary_generator.py
python -m py_compile linkedin_post_generator.py && echo   ✅ linkedin_post_generator.py
python -m py_compile facebook_instagram_post.py && echo   ✅ facebook_instagram_post.py
python -m py_compile twitter_post.py && echo   ✅ twitter_post.py

echo.
echo [6] Testing Platinum Components Compilation...
echo ------------------------------------------------------------
python -m py_compile cloud_orchestrator.py && echo   ✅ cloud_orchestrator.py
python -m py_compile local_orchestrator.py && echo   ✅ local_orchestrator.py
python -m py_compile vault_sync.py && echo   ✅ vault_sync.py
python -m py_compile platinum_demo.py && echo   ✅ platinum_demo.py
python -m py_compile a2a_messenger.py && echo   ✅ a2a_messenger.py

echo.
echo [7] Checking Required Folders...
echo ------------------------------------------------------------
if exist "Needs_Action" (echo   ✅ Needs_Action) else (echo   ❌ Needs_Action)
if exist "Pending_Approval" (echo   ✅ Pending_Approval) else (echo   ❌ Pending_Approval)
if exist "Approved" (echo   ✅ Approved) else (echo   ❌ Approved)
if exist "Done" (echo   ✅ Done) else (echo   ❌ Done)
if exist "Briefings" (echo   ✅ Briefings) else (echo   ❌ Briefings)
if exist "Logs" (echo   ✅ Logs) else (echo   ❌ Logs)
if exist "watchers" (echo   ✅ watchers) else (echo   ❌ watchers)
if exist "cloud" (echo   ✅ cloud) else (echo   ❌ cloud)
if exist "local" (echo   ✅ local) else (echo   ❌ local)

echo.
echo ============================================================
echo   COMPILATION TEST COMPLETE!
echo ============================================================
echo.
echo Next Steps:
echo 1. Review any ❌ failed compilations
echo 2. Fix errors and re-run test
echo 3. For functional testing, see COMPLETE_TESTING_GUIDE.md
echo.
echo Full testing guide: COMPLETE_TESTING_GUIDE.md
echo.
pause
