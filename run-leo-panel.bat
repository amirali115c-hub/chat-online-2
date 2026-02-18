@echo off
echo ====================================
echo    Leo Control Panel
echo ====================================
echo.
echo Starting...
python "%~dp0leo-control-panel.py"
if errorlevel 1 (
    echo.
    echo Error! Make sure Python is installed.
    pause
)
