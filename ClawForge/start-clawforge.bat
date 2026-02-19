@echo off
echo ============================================
echo    CLAWFORGE - Starting Server
echo ============================================
cd /d "%~dp0backend"
echo Starting backend...
start "ClawForge Backend" cmd /c "python api.py"
echo.
echo Waiting for server to start...
timeout /t 10 /nobreak >nul
echo.
echo ============================================
echo    CLAWFORGE Started!
echo ============================================
echo    Open: http://localhost:7860
echo ============================================
pause
