@echo off
REM ====================================================================
REM ClawForge Service Installation (using your NSSM location)
REM ====================================================================

REM Your NSSM location - with quotes for spaces
set NSSM="C:\Program Files (x86)\nssm-2.24-101-g897c7ad\win64\nssm.exe"

echo ================================================
echo Installing ClawForge Services...
echo ================================================
echo.

REM Stop existing services
echo Stopping existing services...
%NSSM% stop ClawForgeBackend 2>nul
%NSSM% stop ClawForgeFrontend 2>nul
%NSSM% remove ClawForgeBackend 2>nul
%NSSM% remove ClawForgeFrontend 2>nul

REM Install Backend Service
echo Installing Backend Service...
%NSSM% install ClawForgeBackend "C:\Users\HP\AppData\Local\Programs\Python\Python314\python.exe"
%NSSM% set ClawForgeBackend AppParameters "C:\Users\HP\.openclaw\workspace\ClawForge\backend\api.py --host 0.0.0.0 --port 7777"
%NSSM% set ClawForgeBackend AppDirectory "C:\Users\HP\.openclaw\workspace\ClawForge\backend"
%NSSM% set ClawForgeBackend DisplayName "ClawForge AI Backend"
%NSSM% set ClawForgeBackend Description "ClawForge AI Backend with Memory & Web Search"
%NSSM% set ClawForgeBackend Start SERVICE_AUTO_START
%NSSM% set ClawForgeBackend AppExit Default Restart
%NSSM% set ClawForgeBackend AppRestartDelay 5000

REM Install Frontend Service
echo Installing Frontend Service...
%NSSM% install ClawForgeFrontend "C:\Users\HP\.openclaw\workspace\ClawForge\frontend\node_modules\.bin\vite.cmd"
%NSSM% set ClawForgeFrontend AppParameters "--port 4200 --host 0.0.0.0"
%NSSM% set ClawForgeFrontend AppDirectory "C:\Users\HP\.openclaw\workspace\ClawForge\frontend"
%NSSM% set ClawForgeFrontend DisplayName "ClawForge AI Frontend"
%NSSM% set ClawForgeFrontend Description "ClawForge AI Frontend Dashboard"
%NSSM% set ClawForgeFrontend Start SERVICE_AUTO_START
%NSSM% set ClawForgeFrontend AppExit Default Restart
%NSSM% set ClawForgeFrontend AppRestartDelay 5000

REM Start services
echo Starting services...
%NSSM% start ClawForgeBackend
%NSSM% start ClawForgeFrontend

echo.
echo ================================================
echo Installation Complete!
echo ================================================
echo.
echo Services should now be running!
echo.
echo URLs:
echo   http://localhost:4200
echo   http://localhost:7777
echo.
pause
