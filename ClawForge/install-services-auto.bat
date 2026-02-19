@echo off
REM ====================================================================
REM ClawForge Service Auto-Installer (with Admin Check)
REM ====================================================================

net session >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ===============================================
    echo REQUESTING ADMINISTRATOR PRIVILEGES...
    echo ===============================================
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit
)

REM If we get here, we have admin privileges
cd /d "%~dp0"

echo ===============================================
echo ADMIN PRIVILEGES CONFIRMED
echo ===============================================
echo.

REM Install Backend Service
echo Installing Backend Service...
nssm install ClawForgeBackend "C:\Users\HP\AppData\Local\Programs\Python\Python314\python.exe" >nul 2>&1
nssm set ClawForgeBackend AppParameters "%~dp0backend\api.py --host 0.0.0.0 --port 8888" >nul 2>&1
nssm set ClawForgeBackend AppDirectory "%~dp0backend" >nul 2>&1
nssm set ClawForgeBackend DisplayName "ClawForge AI Backend" >nul 2>&1
nssm set ClawForgeBackend Description "ClawForge AI Assistant Backend with Memory & Web Search" >nul 2>&1
nssm set ClawForgeBackend Start SERVICE_AUTO_START >nul 2>&1
nssm set ClawForgeBackend AppStdout "%~dp0logs\backend.log" >nul 2>&1
nssm set ClawForgeBackend AppStderr "%~dp0logs\backend_error.log" >nul 2>&1
nssm set ClawForgeBackend AppExit Default Restart >nul 2>&1
nssm set ClawForgeBackend AppRestartDelay 5000 >nul 2>&1

if not exist "%~dp0logs" mkdir "%~dp0logs" >nul 2>&1

net start ClawForgeBackend >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [OK] Backend service installed and started
) else (
    echo [ERROR] Backend service failed to start
)

REM Install Frontend Service
echo Installing Frontend Service...
nssm install ClawForgeFrontend "C:\Users\HP\.openclaw\workspace\ClawForge\frontend\node_modules\.bin\vite.cmd" >nul 2>&1
nssm set ClawForgeFrontend AppParameters "--port 4200 --host 0.0.0.0" >nul 2>&1
nssm set ClawForgeFrontend AppDirectory "%~dp0frontend" >nul 2>&1
nssm set ClawForgeFrontend DisplayName "ClawForge AI Frontend" >nul 2>&1
nssm set ClawForgeFrontend Description "ClawForge AI Assistant Frontend Dashboard" >nul 2>&1
nssm set ClawForgeFrontend Start SERVICE_AUTO_START >nul 2>&1
nssm set ClawForgeFrontend AppStdout "%~dp0logs\frontend.log" >nul 2>&1
nssm set ClawForgeFrontend AppStderr "%~dp0logs\frontend_error.log" >nul 2>&1
nssm set ClawForgeFrontend AppExit Default Restart >nul 2>&1
nssm set ClawForgeFrontend AppRestartDelay 5000 >nul 2>&1

net start ClawForgeFrontend >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [OK] Frontend service installed and started
) else (
    echo [ERROR] Frontend service failed to start
)

echo.
echo ===============================================
echo INSTALLATION COMPLETE!
echo ===============================================
echo.
echo Services are now running in the BACKGROUND.
echo They will survive terminal closing and logoff.
echo.
echo URLs:
echo   Frontend: http://localhost:4200
echo   Backend:  http://localhost:8888
echo.
echo To check status:
echo   net start | findstr ClawForge
echo.
echo To stop services:
echo   net stop ClawForgeBackend
echo   net stop ClawForgeFrontend
echo.
pause
