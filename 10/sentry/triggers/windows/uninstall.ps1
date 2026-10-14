# Remove the Sentry Scheduled Task on Windows.
# Run in an elevated PowerShell:
#   powershell -ExecutionPolicy Bypass -File uninstall.ps1
$ErrorActionPreference = "SilentlyContinue"
Unregister-ScheduledTask -TaskName "Sentry Monitor" -Confirm:$false
Write-Host "Removed Scheduled Task 'Sentry Monitor'."
