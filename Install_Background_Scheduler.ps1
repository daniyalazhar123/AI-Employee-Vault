<#
.SYNOPSIS
    Installs the AI Employee Background Service as a Windows Scheduled Task
    that triggers START_AI_EMPLOYEE_247.bat on system boot (local-first persistence).

.DESCRIPTION
    This script creates a single Windows Scheduled Task that runs the
    AI Employee main orchestrator batch file at system startup with:
      - SYSTEM account (highest privileges)
      - Auto-restart on failure (3 retries, 1-minute interval)
      - Random startup delay (0-2 min) to avoid boot storms
      - Works offline (no cloud dependency)
      - Local-first: runs entirely on the machine

    Unlike install_scheduled_tasks.ps1 (which installs individual Python watchers),
    this script installs the TOP-LEVEL orchestration task that kicks off everything.

.PARAMETER TaskName
    Custom task name (default: AIEmployee-BackgroundService)

.PARAMETER Remove
    Switch to remove the scheduled task instead of installing.

.PARAMETER Status
    Switch to display current task status.

.EXAMPLE
    # Install the background service
    .\Install_Background_Scheduler.ps1

.EXAMPLE
    # Check status
    .\Install_Background_Scheduler.ps1 -Status

.EXAMPLE
    # Remove the scheduled task
    .\Install_Background_Scheduler.ps1 -Remove

.NOTES
    Author: AI Employee Vault
    Requires: Windows 10/11 or Windows Server 2016+
    Run as: Administrator (elevated PowerShell)
#>

param(
    [string]$TaskName = "AIEmployee-BackgroundService",
    [switch]$Remove,
    [switch]$Status
)

$ErrorActionPreference = "Stop"

# Resolve paths dynamically
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BatchFile = Join-Path -Path $ScriptDir -ChildPath "START_AI_EMPLOYEE_247.bat"
$LogDir = Join-Path -Path $ScriptDir -ChildPath "Logs"
$TaskLog = Join-Path -Path $LogDir -ChildPath "BackgroundService.log"

# ---- Helpers ----

function Write-Header {
    param([string]$Text)
    Write-Host "`n============================================" -ForegroundColor Cyan
    Write-Host "  $Text" -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor Cyan
}

function Test-Admin {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function New-LogDirectory {
    if (-not (Test-Path -LiteralPath $LogDir)) {
        New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
        Write-Host "  [*] Created log directory: $LogDir" -ForegroundColor Yellow
    }
}

# ---- Main Logic ----

if ($Status) {
    Write-Header "AI EMPLOYEE BACKGROUND SERVICE STATUS"
    try {
        $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        if ($task) {
            Write-Host "  Task Name   : $($task.TaskName)" -ForegroundColor Green
            Write-Host "  State       : $($task.State)" -ForegroundColor Green
            Write-Host "  Description : $($task.Description)" -ForegroundColor Green
            $actions = $task.Actions
            foreach ($a in $actions) {
                Write-Host "  Action      : $($a.Execute) $($a.Arguments)" -ForegroundColor Gray
            }
            $triggers = $task.Triggers
            foreach ($t in $triggers) {
                Write-Host "  Trigger     : $($t.Enabled -eq 'True' ? 'Enabled' : 'Disabled') - $($t.GetType().Name)" -ForegroundColor Gray
            }
        } else {
            Write-Host "  Task '$TaskName' not found." -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  [x] Failed to query status: $_" -ForegroundColor Red
    }
    exit
}

if ($Remove) {
    Write-Header "REMOVING AI EMPLOYEE BACKGROUND SERVICE"
    try {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue | Out-Null
        Write-Host "  [-] Task '$TaskName' removed successfully." -ForegroundColor Yellow
    } catch {
        Write-Host "  [x] Failed to remove task: $_" -ForegroundColor Red
    }
    exit
}

# ---- Installation ----

Write-Header "INSTALL AI EMPLOYEE BACKGROUND SERVICE"

if (-not (Test-Admin)) {
    Write-Host "  [x] Administrator privileges required." -ForegroundColor Red
    Write-Host "  Please run this script from an elevated PowerShell prompt:" -ForegroundColor Yellow
    Write-Host "    Right-click → 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path -LiteralPath $BatchFile)) {
    Write-Host "  [x] Batch file not found: $BatchFile" -ForegroundColor Red
    Write-Host "  Ensure START_AI_EMPLOYEE_247.bat exists in the vault directory." -ForegroundColor Yellow
    exit 1
}

New-LogDirectory

Write-Host "  [*] Vault Path  : $ScriptDir" -ForegroundColor Gray
Write-Host "  [*] Batch File  : $BatchFile" -ForegroundColor Gray
Write-Host "  [*] Task Name   : $TaskName" -ForegroundColor Gray
Write-Host "  [*] Log File    : $TaskLog" -ForegroundColor Gray
Write-Host ""

# Remove existing task if present (to cleanly reinstall)
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue | Out-Null

# Build task action
$Action = New-ScheduledTaskAction `
    -Execute "cmd.exe" `
    -Argument "/c `"`"$BatchFile`" >> `"$TaskLog`" 2>&1`" `
    -WorkingDirectory $ScriptDir

# Build boot trigger with random delay (0-2 min)
$Trigger = New-ScheduledTaskTrigger -AtStartup -RandomDelay "00:02:00"

# Build settings: auto-restart, battery-tolerant
$Settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -ExecutionTimeLimit (New-TimeSpan -Days 365) `
    -Priority 7

# Build principal: SYSTEM account with highest privileges
$Principal = New-ScheduledTaskPrincipal `
    -UserId "SYSTEM" `
    -LogonType ServiceAccount `
    -RunLevel Highest

# Register the task
try {
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $Action `
        -Trigger $Trigger `
        -Settings $Settings `
        -Principal $Principal `
        -Description "AI Employee 24/7 Background Service — starts the autonomous employee orchestrator at system boot, with auto-restart on failure." `
        -Force | Out-Null

    Write-Host "  [+] Task '$TaskName' installed successfully." -ForegroundColor Green
    Write-Host "  [+] Trigger: At system startup (random delay 0-2 min)" -ForegroundColor Green
    Write-Host "  [+] Principal: SYSTEM (Highest)" -ForegroundColor Green
    Write-Host "  [+] Restart: Up to 3 retries, 1-min interval" -ForegroundColor Green
    Write-Host ""
    Write-Host "  The AI Employee will automatically start on every boot." -ForegroundColor Cyan
    Write-Host "  Logs: $TaskLog" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  To start immediately without rebooting:" -ForegroundColor Yellow
    Write-Host "    Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Yellow
    Write-Host ""

    # Offer to start immediately
    $response = Read-Host "  Start the task now? (Y/N, default: Y)"
    if ($response -eq '' -or $response -eq 'Y' -or $response -eq 'y') {
        Start-ScheduledTask -TaskName $TaskName
        Write-Host "  [+] Task started!" -ForegroundColor Green
    }

} catch {
    Write-Host "  [x] Failed to install task: $_" -ForegroundColor Red
    exit 1
}
