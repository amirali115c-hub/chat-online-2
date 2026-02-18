@echo off
echo ====================================
echo    Leo Voice Assistant
echo ====================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.10+ from python.org
    pause
    exit /b 1
)

REM Check Ollama
ollama --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: Ollama not found!
    echo Please install from: https://ollama.com
    echo.
    echo You need Ollama for voice commands to work.
    echo.
    pause
)

echo Starting Leo Voice Assistant...
echo.
python "%~dp0main.py"

if errorlevel 1 (
    echo.
    echo Error occurred! Check the error above.
    pause
)
