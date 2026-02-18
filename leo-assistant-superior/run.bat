@echo off
echo ====================================
echo    Leo Voice Assistant
echo ====================================
echo.

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Using standalone mode...
    echo.
    echo Download Python from https://python.org
    pause
    exit /b 1
)

echo Starting Leo Voice Assistant...
python "%~dp0main.py"

pause
