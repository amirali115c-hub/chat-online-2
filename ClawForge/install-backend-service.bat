@echo off
REM ====================================================================
REM ClawForge Backend Service Installer (Windows)
REM ====================================================================
REM This script installs ClawForge backend as a Windows Service
REM so it runs permanently in the background
REM ====================================================================

echo ================================================
echo ClawForge Backend Service Installer
echo ================================================

REM Check if NSSM is installed
where nssm >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: NSSM not found!
    echo.
    echo Please install NSSM first:
    echo 1. Download from: https://nssm.cc/download
    echo 2. Extract to: C:\nssm\release\win64
    echo 3. Add to PATH: C:\nssm\release\win64
    echo.
    echo OR run as Administrator:
    echo   choco install nssm
    echo.
    pause
    exit /b 1
)

echo [OK] NSSM found

REM Set variables
set SERVICE_NAME=ClawForgeBackend
set DISPLAY_NAME=ClawForge AI Backend
set DESCRIPTION=ClawForge AI Assistant Backend with Memory & Web Search
set PROGRAM_PATH=%~dp0backend\python.exe
set SCRIPT_PATH=%~dp0backend\api.py
set PORT=8888
set WORKDIR=%~dp0backend

echo.
echo Service Configuration:
echo   Name: %SERVICE_NAME%
echo   Display: %DISPLAY_NAME%
echo   Port: %PORT%
echo   Working Dir: %WORKDIR%
echo.

REM Stop service if already installed
echo Checking for existing service...
net stop %SERVICE_NAME% >nul 2>&1
nssm stop %SERVICE_NAME% >nul 2>&1
nssm remove %SERVICE_NAME% confirm >nul 2>&1

echo Installing service...
nssm install %SERVICE_NAME% "%PROGRAM_PATH%"

REM Configure service
nssm set %SERVICE_NAME% AppParameters "%SCRIPT_PATH% --host 0.0.0.0 --port %PORT%"
nssm set %SERVICE_NAME% AppDirectory "%WORKDIR%"
nssm set %SERVICE_NAME% DisplayName "%DISPLAY_NAME%"
nssm set %SERVICE_NAME% Description "%DESCRIPTION%"
nssm set %SERVICE_NAME% Start SERVICE_AUTO_START
nssm set %SERVICE_NAME% AppStdout "%~dp0logs\backend.log"
nssm set %SERVICE_NAME% AppStderr "%~dp0logs\backend_error.log"
nssm set %SERVICE_NAME% AppStdoutCreationDisposition 4
nssm set %SERVICE_NAME% AppStderrCreationDisposition 4
nssm set %SERVICE_NAME% AppExit Default Restart
nssm set %SERVICE_NAME% AppRestartDelay 5000
nssm set %SERVICE_NAME% IOWindowSizeKiloBytes 8192

REM Create logs directory
if not exist "%~dp0logs" mkdir "%~dp0logs"

echo.
echo Starting service...
net start %SERVICE_NAME% >nul 2>&1
nssm start %SERVICE_NAME%

echo.
echo ================================================
echo Service installed successfully!
echo ================================================
echo.
echo Status:
net start %SERVICE_NAME% 2>&1 | findstr /i "running started"
if %ERRORLEVEL% equ 0 (
    echo [OK] Service is RUNNING
) else (
    echo [WARNING] Service may not have started properly)
echo.
echo To check logs:
echo   type %~dp0logs\backend.log
echo.
echo To manage service:
echo   net start %SERVICE_NAME%  - Start
echo   net stop %SERVICE_NAME%   - Stop
echo   nssm restart %SERVICE_NAME% - Restart
echo   nssm status %SERVICE_NAME%  - Status
echo.
echo Backend URL: http://localhost:%PORT%
echo.
pause
