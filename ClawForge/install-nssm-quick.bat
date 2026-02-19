@echo off
REM ====================================================================
REM Quick NSSM Download & Install
REM ====================================================================

echo ================================================
echo Step 1: Downloading NSSM...
echo ================================================
powershell -Command "Start-BitsTransfer -Source 'https://nssm.cc/release/nssm-2.24.zip' -Destination 'C:\nssm.zip'"

if not exist "C:\nssm.zip" (
    echo Download failed! Trying alternative method...
    powershell -Command "(New-Object System.Net.WebClient).DownloadFile('https://nssm.cc/release/nssm-2.24.zip', 'C:\nssm.zip')"
)

if exist "C:\nssm.zip" (
    echo ================================================
    echo Step 2: Extracting NSSM...
    echo ================================================
    powershell -Command "Expand-Archive -Path 'C:\nssm.zip' -DestinationPath 'C:\nssm' -Force"
    
    if exist "C:\nssm\release\win64\nssm.exe" (
        echo ================================================
        echo NSSM Installed Successfully!
        echo ================================================
        echo.
        echo Now installing ClawForge services...
        echo.
        cd /d C:\Users\HP\.openclaw\workspace\ClawForge
        powershell -ExecutionPolicy Bypass -File install-services.ps1
    ) else (
        echo ERROR: nssm.exe not found after extraction
    )
) else (
    echo ERROR: Download failed!
    echo.
    echo Please download manually:
    echo 1. Go to: https://nssm.cc/release/nssm-2.24.zip
    echo 2. Save to C:\nssm.zip
    echo 3. Right-click C:\nssm.zip ^> Extract All... ^> C:\nssm
)
