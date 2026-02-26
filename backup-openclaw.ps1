# OpenClaw Backup Script
# Run this to backup all data before reinstalling

$BackupPath = "D:\Openclaw Backup"

# Create backup folder if not exists
if (!(Test-Path $BackupPath)) {
    New-Item -ItemType Directory -Path $BackupPath -Force
    Write-Host "Created: $BackupPath"
}

# Backup workspace
$WorkspaceSrc = "C:\Users\HP\.openclaw\workspace"
$WorkspaceDest = "$BackupPath\workspace"

Write-Host "Backing up workspace..."
Copy-Item -Path $WorkspaceSrc -Destination $WorkspaceDest -Recurse -Force

# Backup OpenClaw config
$OpenClawSrc = "C:\Users\HP\AppData\Roaming\npm\node_modules\openclaw"
$OpenClawDest = "$BackupPath\openclaw-config"

if (Test-Path $OpenClawSrc) {
    Write-Host "Backing up OpenClaw config..."
    Copy-Item -Path $OpenClawSrc -Destination $OpenClawDest -Recurse -Force
}

# Backup Ollama models (optional - they're large)
$OllamaSrc = "$env:USERPROFILE\.ollama"
$OllamaDest = "$BackupPath\ollama-models"

if (Test-Path $OllamaSrc) {
    $choice = Read-Host "Ollama models are large (~GBs). Copy them? (y/n)"
    if ($choice -eq "y") {
        Write-Host "Backing up Ollama models..."
        Copy-Item -Path $OllamaSrc -Destination $OllamaDest -Recurse -Force
    }
}

# Summary
Write-Host ""
Write-Host "========== BACKUP COMPLETE =========="
Write-Host "Location: $BackupPath"
Write-Host ""
Write-Host "Folders backed up:"
Get-ChildItem $BackupPath | ForEach-Object { Write-Host "  - $($_.Name)" }
Write-Host ""
Write-Host "After Linux install:"
Write-Host "1. Copy 'workspace' to your new Linux home folder"
Write-Host "2. Copy 'openclaw-config' to ~/.npm/node_modules/openclaw"
Write-Host "3. Reinstall dependencies (Node.js, Python, Ollama)"
Write-Host "4. Clone your GitHub repos"
