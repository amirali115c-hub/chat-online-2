@echo off
echo Starting Brave Browser with debugging enabled...
echo.
echo Once browser opens, go to Upwork and stay on that tab.
echo Then tell Leo you're ready.
echo.
echo If browser doesn't start, check the path below matches your Brave installation.
echo.
pause
"C:\Users\HP\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe" --remote-debugging-port=9222
