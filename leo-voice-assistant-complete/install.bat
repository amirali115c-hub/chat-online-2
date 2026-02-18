@echo off
echo ====================================
echo Installing Dependencies
echo ====================================
echo.

echo Installing Python packages...
pip install -r requirements.txt

echo.
echo Installing Playwright browsers...
playwright install chromium

echo.
echo Done!
echo Run main.py or run.bat to start
pause
