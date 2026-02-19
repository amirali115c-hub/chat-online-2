@echo off
REM ====================================================================
REM ClawForge Service Manager
REM ====================================================================

echo ================================================
echo ClawForge Service Manager
echo ================================================
echo.
echo 1. Start all services
echo 2. Stop all services
echo 3. Restart all services
echo 4. Check status
echo 5. View backend logs
echo 6. View frontend logs
echo.
set /p choice="Enter choice (1-6): "

if "%choice%"=="1" (
    echo.
    echo Starting services...
    net start ClawForgeBackend >nul 2>&1 && echo [OK] Backend started || echo [ERROR] Backend failed to start
    net start ClawForgeFrontend >nul 2>&1 && echo [OK] Frontend started || echo [ERROR] Frontend failed to start
) else if "%choice%"=="2" (
    echo.
    echo Stopping services...
    net stop ClawForgeBackend >nul 2>&1 && echo [OK] Backend stopped || echo [ERROR] Backend not running
    net stop ClawForgeFrontend >nul 2>&1 && echo [OK] Frontend stopped || echo [ERROR] Frontend not running
) else if "%choice%"=="3" (
    echo.
    echo Restarting services...
    net stop ClawForgeFrontend >nul 2>&1
    net stop ClawForgeBackend >nul 2>&1
    timeout /t 3 >nul
    net start ClawForgeBackend >nul 2>&1 && echo [OK] Backend started || echo [ERROR] Backend failed
    net start ClawForgeFrontend >nul 2>&1 && echo [OK] Frontend started || echo [ERROR] Frontend failed
) else if "%choice%"=="4" (
    echo.
    echo Service Status:
    echo.
    echo Backend (ClawForgeBackend):
    net start ClawForgeBackend >nul 2>&1 && echo [RUNNING] || echo [STOPPED]
    echo.
    echo Frontend (ClawForgeFrontend):
    net start ClawForgeFrontend >nul 2>&1 && echo [RUNNING] || echo [STOPPED]
    echo.
    echo URLs:
    echo   Frontend: http://localhost:4200
    echo   Backend:  http://localhost:8888
) else if "%choice%"=="5" (
    echo.
    echo Backend Logs:
    echo ================================================
    if exist logs\backend.log (
        type logs\backend.log
    ) else (
        echo Log file not found: logs\backend.log
    )
) else if "%choice%"=="6" (
    echo.
    echo Frontend Logs:
    echo ================================================
    if exist logs\frontend.log (
        type logs\frontend.log
    ) else (
        echo Log file not found: logs\frontend.log
    )
)

echo.
pause
