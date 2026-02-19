@echo off
REM ====================================================================
REM NSSM Download & Install Script
REM ====================================================================

echo ================================================
echo Downloading NSSM...
echo ================================================

REM Download NSSM
powershell -Command "Invoke-WebRequest -Uri 'https://nssm.cc/release/nssm-2.24.zip' -OutFile 'nssm.zip'"

echo Extracting...
powershell -Command "Expand-Archive -Path 'nssm.zip' -DestinationPath 'C:\nssm' -Force"

echo.
echo ================================================
echo NSSM Installed!
echo ================================================
echo.
echo Location: C:\nssm\release\win64\nssm.exe
echo.
echo Now run this to install ClawForge services:
echo   cd C:\Users\HP\.openclaw\workspace\ClawForge
echo   powershell -ExecutionPolicy Bypass -File install-services.ps1
echo.
pause
