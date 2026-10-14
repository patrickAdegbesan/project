# Install Sentry as a Scheduled Task on Windows.
# Run in an elevated PowerShell (Run as Administrator):
#   powershell -ExecutionPolicy Bypass -File install.ps1
#
# It registers a task that fires capture.py on:
#   - every logon, and
#   - system resume from sleep (System log, Power-Troubleshooter, Event 1).
#
# The task is listed openly in Task Scheduler under "Sentry Monitor".
# It runs with pythonw.exe so there is no console pop-up (quiet, not hidden).

$ErrorActionPreference = "Stop"

$SentryDir = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$Capture   = Join-Path $SentryDir "capture.py"

# Prefer pythonw.exe (no console window). Fall back to python.exe.
$pyw = (Get-Command pythonw.exe -ErrorAction SilentlyContinue)
if ($pyw) { $PyExe = $pyw.Source } else { $PyExe = (Get-Command python.exe).Source }

Write-Host "Sentry dir : $SentryDir"
Write-Host "Python     : $PyExe"

New-Item -ItemType Directory -Force -Path (Join-Path $SentryDir "evidence") | Out-Null

$Action = New-ScheduledTaskAction -Execute $PyExe `
    -Argument "`"$Capture`" --once" -WorkingDirectory $SentryDir

# Trigger 1: at logon of the current user.
$LogonTrigger = New-ScheduledTaskTrigger -AtLogOn

# Trigger 2: on resume from sleep, via the System event log.
$Class = Get-CimClass MSFT_TaskEventTrigger root/Microsoft/Windows/TaskScheduler
$WakeTrigger = New-CimInstance -CimClass $Class -ClientOnly
$WakeTrigger.Enabled = $true
$WakeTrigger.Subscription = @'
<QueryList><Query Id="0" Path="System"><Select Path="System">
*[System[Provider[@Name='Microsoft-Windows-Power-Troubleshooter']
 and (EventID=1)]]</Select></Query></QueryList>
'@

$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries -StartWhenAvailable

# Run as the logged-on user so it can reach the camera/desktop session.
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" `
    -LogonType Interactive -RunLevel Limited

Register-ScheduledTask -TaskName "Sentry Monitor" `
    -Action $Action -Trigger $LogonTrigger, $WakeTrigger `
    -Settings $Settings -Principal $Principal -Force | Out-Null

Write-Host ""
Write-Host "Installed Scheduled Task 'Sentry Monitor' (visible in Task Scheduler)."
Write-Host "If Microsoft Defender quarantines it, ADD AN EXCLUSION for:"
Write-Host "  $SentryDir"
Write-Host "See docs\antivirus-allow.md - you allow it, you do not hide from it."
