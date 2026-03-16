# Windows Task Scheduler Setup Guide

## AI Employee - Automated Scheduling

This guide helps you setup automated scheduling for your AI Employee watchers using Windows Task Scheduler.

---

## Prerequisites

- Windows 10/11
- Administrator access
- Python 3.13+ installed and in PATH
- AI Employee Vault setup complete

---

## Option 1: Manual Setup (Recommended for Learning)

### Step 1: Open Task Scheduler

1. Press `Win + R`
2. Type: `taskschd.msc`
3. Press Enter

### Step 2: Create Basic Task for Gmail Watcher

1. **Right-click** "Task Scheduler Library" → "Create Basic Task..."
2. **Name:** `AI Employee - Gmail Watcher`
3. **Description:** `Monitor Gmail and create action items`
4. **Trigger:** `When I log on` (or `Daily` at specific time)
5. **Action:** `Start a program`
6. **Program/script:** `python`
7. **Add arguments:** `watchers\gmail_watcher.py`
8. **Start in:** `C:\Users\CC\Documents\Obsidian Vault`
9. **Finish**

### Step 3: Configure Advanced Settings

1. **Right-click** your new task → "Properties"
2. **General tab:**
   - ✅ "Run whether user is logged on or not"
   - ✅ "Run with highest privileges"
3. **Conditions tab:**
   - ❌ Uncheck "Start the task only if computer is on AC power"
   - ✅ "Wake the computer to run this task"
4. **Settings tab:**
   - ✅ "Allow task to be run on demand"
   - ✅ "If task fails, restart every: 1 minute"
   - ✅ "Attempt to restart up to: 3 times"
5. **OK**

---

## Option 2: Automated Setup Script

### Create Scheduled Tasks via PowerShell

Run PowerShell as Administrator and execute:

```powershell
# Navigate to vault directory
$vaultPath = "C:\Users\CC\Documents\Obsidian Vault"
$pythonPath = "python"

# Gmail Watcher Task
$action = New-ScheduledTaskAction -Execute $pythonPath `
  -Argument "watchers\gmail_watcher.py" `
  -WorkingDirectory $vaultPath
  
$trigger = New-ScheduledTaskTrigger -AtLogon
  
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME `
  -LogonType S4U `
  -RunLevel Highest
  
$settings = New-ScheduledTaskSettingsSet `
  -AllowStartIfOnBatteries `
  -DontStopIfGoingOnBatteries `
  -StartWhenAvailable `
  -RestartCount 3 `
  -RestartInterval (New-TimeSpan -Minutes 1)
  
Register-ScheduledTask `
  -TaskName "AI Employee - Gmail Watcher" `
  -Action $action `
  -Trigger $trigger `
  -Principal $principal `
  -Settings $settings `
  -Description "Monitor Gmail and create action items" `
  -Force

Write-Host "✅ Gmail Watcher task created!"

# WhatsApp Watcher Task
$action = New-ScheduledTaskAction -Execute $pythonPath `
  -Argument "watchers\whatsapp_watcher.py" `
  -WorkingDirectory $vaultPath
  
Register-ScheduledTask `
  -TaskName "AI Employee - WhatsApp Watcher" `
  -Action $action `
  -Trigger $trigger `
  -Principal $principal `
  -Settings $settings `
  -Description "Monitor WhatsApp Web for urgent messages" `
  -Force

Write-Host "✅ WhatsApp Watcher task created!"

# Office Watcher Task
$action = New-ScheduledTaskAction -Execute $pythonPath `
  -Argument "watchers\office_watcher.py" `
  -WorkingDirectory $vaultPath
  
Register-ScheduledTask `
  -TaskName "AI Employee - Office Watcher" `
  -Action $action `
  -Trigger $trigger `
  -Principal $principal `
  -Settings $settings `
  -Description "Monitor Office_Files folder for new documents" `
  -Force

Write-Host "✅ Office Watcher task created!"

# Social Watcher Task
$action = New-ScheduledTaskAction -Execute $pythonPath `
  -Argument "watchers\social_watcher.py" `
  -WorkingDirectory $vaultPath
  
Register-ScheduledTask `
  -TaskName "AI Employee - Social Watcher" `
  -Action $action `
  -Trigger $trigger `
  -Principal $principal `
  -Settings $settings `
  -Description "Process social media drafts" `
  -Force

Write-Host "✅ Social Watcher task created!"

# CEO Briefing Task (Every Monday 8 AM)
$action = New-ScheduledTaskAction -Execute $pythonPath `
  -Argument "ceo_briefing.py" `
  -WorkingDirectory $vaultPath
  
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 8am
  
Register-ScheduledTask `
  -TaskName "AI Employee - CEO Briefing" `
  -Action $action `
  -Trigger $trigger `
  -Principal $principal `
  -Settings $settings `
  -Description "Generate weekly CEO briefing every Monday" `
  -Force

Write-Host "✅ CEO Briefing task created!"

Write-Host "`n================================"
Write-Host "All tasks created successfully!"
Write-Host "================================`n"
Write-Host "To view tasks: Open Task Scheduler"
Write-Host "To run manually: Right-click task → Run"
Write-Host "To stop: Right-click task → End"
```

---

## Option 3: Quick Setup Batch File

Save as `setup_tasks.bat` and run as Administrator:

```batch
@echo off
echo ============================================
echo AI Employee - Task Scheduler Setup
echo ============================================
echo.

cd /d "%~dp0"

REM Create tasks using schtasks
schtasks /Create /TN "AI Employee - Gmail Watcher" /TR "python watchers\gmail_watcher.py" /SC ONLOGON /RU SYSTEM /RL HIGHEST /F
schtasks /Create /TN "AI Employee - WhatsApp Watcher" /TR "python watchers\whatsapp_watcher.py" /SC ONLOGON /RU SYSTEM /RL HIGHEST /F
schtasks /Create /TN "AI Employee - Office Watcher" /TR "python watchers\office_watcher.py" /SC ONLOGON /RU SYSTEM /RL HIGHEST /F
schtasks /Create /TN "AI Employee - Social Watcher" /TR "python watchers\social_watcher.py" /SC ONLOGON /RU SYSTEM /RL HIGHEST /F
schtasks /Create /TN "AI Employee - CEO Briefing" /TR "python ceo_briefing.py" /SC WEEKLY /D MON /ST 08:00 /RU SYSTEM /RL HIGHEST /F

echo.
echo ============================================
echo All tasks created successfully!
echo ============================================
echo.
echo Task List:
echo - AI Employee - Gmail Watcher (On logon)
echo - AI Employee - WhatsApp Watcher (On logon)
echo - AI Employee - Office Watcher (On logon)
echo - AI Employee - Social Watcher (On logon)
echo - AI Employee - CEO Briefing (Every Monday 8 AM)
echo.
echo To manage: Open Task Scheduler (taskschd.msc)
echo ============================================
echo.

pause
```

---

## Scheduled Tasks Summary

| Task Name | Trigger | Schedule | Purpose |
|-----------|---------|----------|---------|
| Gmail Watcher | On logon | Continuous | Monitor Gmail |
| WhatsApp Watcher | On logon | Continuous | Monitor WhatsApp |
| Office Watcher | On logon | Continuous | Monitor files |
| Social Watcher | On logon | Continuous | Process drafts |
| CEO Briefing | Weekly | Monday 8 AM | Generate briefing |

---

## Verification

### Check if Tasks are Running

1. Open **Task Scheduler**
2. Navigate to "Task Scheduler Library"
3. Find tasks starting with "AI Employee -"
4. Check "Status" column (should show "Ready" or "Running")

### View Task History

1. **Right-click** task → "Properties"
2. **History** tab
3. **Enable** if not enabled
4. View execution logs

### Test Tasks Manually

1. **Right-click** task → "Run"
2. Check `Logs/` folder for output
3. Verify action files created

---

## Troubleshooting

### Task Won't Run

**Problem:** Task shows "Ready" but doesn't execute

**Solutions:**
1. Check "Run whether user is logged on or not"
2. Enable "Run with highest privileges"
3. Verify Python is in system PATH
4. Test manually: `python watchers\gmail_watcher.py`

### Python Not Found

**Problem:** Error "The system cannot find the file specified"

**Solutions:**
1. Use full Python path: `C:\Python313\python.exe`
2. Add Python to system PATH
3. Verify: `python --version` in cmd

### Permission Denied

**Problem:** Access denied errors

**Solutions:**
1. Run Task Scheduler as Administrator
2. Enable "Run with highest privileges"
3. Check folder permissions

### Watcher Crashes

**Problem:** Watcher stops after some time

**Solutions:**
1. Enable auto-restart in task settings
2. Check `Logs/` folder for errors
3. Increase timeout values
4. Review error handling in scripts

---

## Monitoring

### Daily Checks

- [ ] Check Task Scheduler status
- [ ] Review `Logs/` folder
- [ ] Verify `Needs_Action/` has new files
- [ ] Check `Dashboard.md` updated

### Weekly Checks

- [ ] Review CEO Briefing
- [ ] Clear old processed files
- [ ] Update `Business_Goals.md`
- [ ] Check error rates

### Monthly Checks

- [ ] Audit all tasks
- [ ] Review performance metrics
- [ ] Update schedules if needed
- [ ] Backup task configurations

---

## Export/Backup Tasks

### Export Single Task

```powershell
Export-ScheduledTask -TaskName "AI Employee - Gmail Watcher" | Out-File "gmail_watcher_task.xml"
```

### Export All AI Employee Tasks

```powershell
$tasks = Get-ScheduledTask | Where-Object {$_.TaskName -like "AI Employee*"}
foreach ($task in $tasks) {
    Export-ScheduledTask -TaskName $task.TaskName | Out-File "$($task.TaskName)_backup.xml"
}
```

### Import Task

```powershell
Register-ScheduledTask -Xml (Get-Content "gmail_watcher_task.xml" | Out-String) -TaskName "AI Employee - Gmail Watcher"
```

---

## Best Practices

1. **Run as System:** Use SYSTEM account for reliability
2. **Enable Restart:** Auto-restart on failure (3 attempts)
3. **Log Everything:** Check `Logs/` folder regularly
4. **Test First:** Manually test before scheduling
5. **Monitor:** Setup email alerts for critical failures
6. **Document:** Keep track of all scheduled tasks
7. **Backup:** Export task configurations monthly

---

## Next Steps

After completing this setup:

1. ✅ Verify all tasks created
2. ✅ Test each task manually
3. ✅ Enable task history
4. ✅ Setup monitoring routine
5. ✅ Document in README

---

**Silver Tier Status:** Scheduling ✅ COMPLETE

*Guide created: March 16, 2026*
