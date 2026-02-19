@echo off
REM ====================================================================
REM Install ClawForge Services
REM ====================================================================

set NSSM="C:\Program Files (x86)\nssm-2.24-101-g897c7ad\win64\nssm.exe"

echo ================================================
echo Installing ClawForge Services...
echo ================================================

REM Stop existing
%NSSM% stop ClawForgeBackend 2>nul
%NSSM% stop ClawForgeFrontend 2>nul
%NSSM% remove ClawForgeBackend 2>nul
%NSSM% remove ClawForgeFrontend 2>nul

REM Install Backend
echo Installing Backend...
%NSSM% install ClawForgeBackend "C:\Users\HP\AppData\Local\Programs\Python\Python314\python.exe"
%NSSM% set ClawForgeBackend AppParameters "C:\Users\HP\.openclaw\workspace\ClawForge\backend\api.py --host 0.0.0.0 --port 7777"
%NSSM% set ClawForgeBackend AppDirectory "C:\Users\HP\.openclaw\workspace\ClawForge\backend"
%NSSM% set ClawForgeBackend DisplayName "ClawForge AI Backend"
%NSSM% set ClawForgeBackend Start SERVICE_AUTO_START
%NSSM% set ClawForgeBackend AppExit Default Restart
%NSSM% set ClawForgeBackend AppRestartDelay 5000

REM Install Frontend
echo Installing Frontend...
%NSSM% install ClawForgeFrontend "C:\Users\HP\.openclaw\workspace\ClawForge\frontend\node_modules\.bin\vite.cmd"
%NSSM% set ClawForgeFrontend AppParameters "--port 4200 --host 0.0.0.0"
%NSSM% set ClawForgeFrontend AppDirectory "C:\Users\HP\.openclaw\workspace\ClawForge\frontend"
%NSSM% set ClawForgeFrontend DisplayName "ClawForge AI Frontend"
%NSSM% set ClawForgeFrontend Start SERVICE_AUTO_START
%NSSM% set ClawForgeFrontend AppExit Default Restart
%NSSM% set ClawForgeFrontend AppRestartDelay 5000

REM Start
%NSSM% start ClawForgeBackend
%NSSM% start ClawForgeFrontend

echo.
echo ================================================
echo Done! Services installed and started!
echo ================================================
echo.
echo URLs:
echo   http://localhost:4200
echo   http://localhost:7777
pause
