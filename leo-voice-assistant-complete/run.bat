@echo off
echo ====================================
echo    Leo Voice Assistant v5.0
echo    Privacy-Focused PC Control
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

echo Starting Leo Voice Assistant...
echo.

REM Optional: Check Ollama
echo Checking Ollama...
python -c "import requests; r=requests.get('http://localhost:11434/api/tags', timeout=2); print('Ollama: Connected' if r.status_code==200 else 'Ollama: Not running')" 2>nul || echo "Ollama: Not running (will use fallback)"

echo.
echo Starting application...
python "%~dp0main.py"

pause
