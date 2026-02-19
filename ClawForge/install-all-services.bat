@echo off
REM ====================================================================
REM ClawForge Complete Service Installation
REM ====================================================================
REM Installs BOTH backend and frontend as Windows Services
REM so they run permanently in the background
REM ====================================================================

echo ================================================
echo ClawForge Service Installation
echo ================================================
echo.
echo This will install both backend and frontend
echo as Windows Services that run permanently.
echo.
echo IMPORTANT: Run this as Administrator!
echo.
pause

echo.
echo ================================================
echo Installing Backend Service...
echo ================================================
call install-backend-service.bat

echo.
echo ================================================
echo Installing Frontend Service...
echo ================================================
call install-frontend-service.bat

echo.
echo ================================================
echo Installation Complete!
echo ================================================
echo.
echo Both services are now running in the background.
echo They will survive:
echo   - Computer restarts (if set to auto-start)
echo   - Terminal/cmd closing
echo   - User logoff
echo.
echo URLs:
echo   Frontend: http://localhost:4200
echo   Backend:  http://localhost:8888
echo.
echo To manage services:
echo   net start/stop ClawForgeBackend
echo   net start/stop ClawForgeFrontend
echo.
pause
