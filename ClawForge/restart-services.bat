@echo off
REM ====================================================================
REM Restart ClawForge Services with Correct Ports
REM ====================================================================

echo Restarting ClawForge Services...

"C:\Program Files (x86)\nssm-2.24-101-g897c7ad\win64\nssm.exe" restart ClawForgeBackend
"C:\Program Files (x86)\nssm-2.24-101-g897c7ad\win64\nssm.exe" restart ClawForgeFrontend

echo.
echo Services restarted!
echo.
echo Backend:  http://127.0.0.1:7860
echo Frontend: http://127.0.0.1:4200
pause
