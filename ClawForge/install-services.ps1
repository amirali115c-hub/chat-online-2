# ClawForge Service Installer (PowerShell)
# Run as Administrator

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "ClawForge Service Installation" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check for admin privileges
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "[!] Requesting Administrator privileges..." -ForegroundColor Yellow
    $arguments = "-ExecutionPolicy Bypass -File `"$PSCommandPath`""
    Start-Process -FilePath "powershell.exe" -Verb RunAs -ArgumentList $arguments
    exit
}

# Paths
$backendPython = "C:\Users\HP\AppData\Local\Programs\Python\Python314\python.exe"
$backendScript = "$PSScriptRoot\backend\api.py"
$frontendNode = "$PSScriptRoot\frontend\node_modules\.bin\vite.cmd"
$logsDir = "$PSScriptRoot\logs"

# Create logs directory
if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
}

Write-Host "[1/4] Installing Backend Service..." -ForegroundColor Green

# Install Backend Service
& nssm install ClawForgeBackend $backendPython *>$null
& nssm set ClawForgeBackend AppParameters "`"$backendScript`" --host 0.0.0.0 --port 8888" *>$null
& nssm set ClawForgeBackend AppDirectory "$PSScriptRoot\backend" *>$null
& nssm set ClawForgeBackend DisplayName "ClawForge AI Backend" *>$null
& nssm set ClawForgeBackend Description "ClawForge AI Assistant Backend with Memory & Web Search" *>$null
& nssm set ClawForgeBackend Start SERVICE_AUTO_START *>$null
& nssm set ClawForgeBackend AppStdout "$logsDir\backend.log" *>$null
& nssm set ClawForgeBackend AppStderr "$logsDir\backend_error.log" *>$null
& nssm set ClawForgeBackend AppExit Default Restart *>$null
& nssm set ClawForgeBackend AppRestartDelay 5000 *>$null

& net start ClawForgeBackend *>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "    [OK] Backend service installed and started" -ForegroundColor Green
} else {
    Write-Host "    [ERROR] Backend service failed to start" -ForegroundColor Red
}

Write-Host "[2/4] Installing Frontend Service..." -ForegroundColor Green

# Install Frontend Service
& nssm install ClawForgeFrontend $frontendNode *>$null
& nssm set ClawForgeFrontend AppParameters "--port 4200 --host 0.0.0.0" *>$null
& nssm set ClawForgeFrontend AppDirectory "$PSScriptRoot\frontend" *>$null
& nssm set ClawForgeFrontend DisplayName "ClawForge AI Frontend" *>$null
& nssm set ClawForgeFrontend Description "ClawForge AI Assistant Frontend Dashboard" *>$null
& nssm set ClawForgeFrontend Start SERVICE_AUTO_START *>$null
& nssm set ClawForgeFrontend AppStdout "$logsDir\frontend.log" *>$null
& nssm set ClawForgeFrontend AppStderr "$logsDir\frontend_error.log" *>$null
& nssm set ClawForgeFrontend AppExit Default Restart *>$null
& nssm set ClawForgeFrontend AppRestartDelay 5000 *>$null

& net start ClawForgeFrontend *>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "    [OK] Frontend service installed and started" -ForegroundColor Green
} else {
    Write-Host "    [ERROR] Frontend service failed to start" -ForegroundColor Red
}

Write-Host "[3/4] Verifying services..." -ForegroundColor Green

# Check services
$backendStatus = & net start ClawForgeBackend *>$null ? "RUNNING" : "STOPPED"
$frontendStatus = & net start ClawForgeFrontend *>$null ? "RUNNING" : "STOPPED"

Write-Host "    Backend:  $backendStatus" -ForegroundColor $(if ($backendStatus -eq "RUNNING") { "Green" } else { "Red" })
Write-Host "    Frontend: $frontendStatus" -ForegroundColor $(if ($frontendStatus -eq "RUNNING") { "Green" } else { "Red" })

Write-Host "[4/4] Complete!" -ForegroundColor Green

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "INSTALLATION COMPLETE!" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services are now running in the BACKGROUND." -ForegroundColor White
Write-Host "They will survive terminal closing and logoff." -ForegroundColor White
Write-Host ""
Write-Host "URLs:" -ForegroundColor Yellow
Write-Host "  Frontend: http://localhost:4200" -ForegroundColor Cyan
Write-Host "  Backend:  http://localhost:8888" -ForegroundColor Cyan
Write-Host ""
Write-Host "To manage services:" -ForegroundColor Yellow
Write-Host "  net start ClawForgeBackend   - Start" -ForegroundColor White
Write-Host "  net stop ClawForgeBackend    - Stop" -ForegroundColor White
Write-Host "  net start ClawForgeFrontend  - Start" -ForegroundColor White
Write-Host "  net stop ClawForgeFrontend   - Stop" -ForegroundColor White
Write-Host ""
