param(
    [switch]$Remove,
    [switch]$Status
)

$VaultPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonPath = (Get-Command python).Source
$TaskPrefix = "AIEmployee_"

$tasks = @(
    @{Name="CloudAgent";   Description="Cloud Agent - Draft-Only Mode 24/7";        Script="cloud_agent.py";       Interval=1},
    @{Name="LocalAgent";   Description="Local Agent - Approval & Execute Mode 24/7";  Script="local_agent.py";      Interval=1},
    @{Name="CloudOrch";    Description="Cloud Orchestrator 24/7";                     Script="cloud_orchestrator.py"; Interval=1},
    @{Name="LocalOrch";    Description="Local Orchestrator 24/7";                     Script="local_orchestrator.py"; Interval=1},
    @{Name="VaultSync";    Description="Git vault sync every 5 min";                  Script="vault_sync.py";        Interval=5},
    @{Name="HealthMonitor";Description="Health monitoring every 5 min";               Script="health_monitor.py";    Interval=5},
    @{Name="SecurityGuard";Description="Security checks every 15 min";                Script="security_guard.py";    Interval=15},
    @{Name="GmailWatcher"; Description="Gmail inbox monitoring";                      Script="watchers\gmail_watcher.py";     Interval=1},
    @{Name="WhatsAppWatcher";Description="WhatsApp monitoring";                      Script="watchers\whatsapp_watcher.py";  Interval=1},
    @{Name="OfficeWatcher";Description="Office file monitoring";                     Script="watchers\office_watcher.py";   Interval=1},
    @{Name="SocialWatcher";Description="Social media monitoring";                    Script="watchers\social_watcher.py";   Interval=1},
    @{Name="OdooLeadWatcher";Description="Odoo lead monitoring";                    Script="watchers\odoo_lead_watcher.py"; Interval=1}
)

function Get-TaskName {
    param([string]$Name)
    return "$TaskPrefix$Name"
}

function Install-Task {
    param($task)
    $taskName = Get-TaskName $task.Name
    $scriptPath = Join-Path $VaultPath $task.Script
    $logDir = Join-Path $VaultPath "Logs"
    if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }
    $stdoutLog = Join-Path $logDir "task_$($task.Name)_out.log"
    $stderrLog = Join-Path $logDir "task_$($task.Name)_err.log"

    $action = New-ScheduledTaskAction -Execute $PythonPath -Argument "$scriptPath" -WorkingDirectory $VaultPath
    $trigger = New-ScheduledTaskTrigger -AtStartup -RandomDelay "00:01:00"
    $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)
    $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

    try {
        Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description $task.Description -Force | Out-Null
        Write-Host "  [+] $($task.Name) - $($task.Description)" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "  [x] $($task.Name) - FAILED: $_" -ForegroundColor Red
        return $false
    }
}

function Remove-Task {
    param([string]$Name)
    $taskName = Get-TaskName $Name
    try {
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue | Out-Null
        Write-Host "  [-] $Name removed" -ForegroundColor Yellow
    } catch {}
}

if ($Status) {
    Write-Host "`n=== AI Employee Scheduled Tasks Status ===" -ForegroundColor Cyan
    Get-ScheduledTask -TaskPath "\" | Where-Object { $_.TaskName -like "$TaskPrefix*" } | Format-Table TaskName, State, Description -AutoSize
    exit
}

if ($Remove) {
    Write-Host "`nRemoving AI Employee scheduled tasks..." -ForegroundColor Yellow
    foreach ($task in $tasks) { Remove-Task $task.Name }
    Write-Host "Done." -ForegroundColor Green
    exit
}

Write-Host @"

============================================
  SCHEDULED TASKS - AI EMPLOYEE
  Installer for Windows Task Scheduler
============================================

"@ -ForegroundColor Cyan

$success = 0
$failed = 0
foreach ($task in $tasks) {
    if (Install-Task $task) { $success++ } else { $failed++ }
}

Write-Host @"

Results: $success installed, $failed failed

Managing tasks:
  View status:  PowerShell -File "$($MyInvocation.MyCommand.Path)" -Status
  Remove all:   PowerShell -File "$($MyInvocation.MyCommand.Path)" -Remove

Tasks run as SYSTEM, start at boot, auto-restart on failure.
Logs: $VaultPath\Logs\task_*.log

"@ -ForegroundColor Cyan
