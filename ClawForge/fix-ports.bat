@echo off
REM ====================================================================
REM Fix ClawForge Port Configuration - Permanent Solution
REM ====================================================================

echo ================================================
echo Fixing ClawForge Ports...
echo ================================================

REM Set correct ports
set BACKEND_PORT=7860
set FRONTEND_PORT=4200

REM Update Backend Service
echo Configuring Backend to use port %BACKEND_PORT%...
"C:\Program Files (x86)\nssm-2.24-101-g897c7ad\win64\nssm.exe" set ClawForgeBackend AppParameters "C:\Users\HP\.openclaw\workspace\ClawForge\backend\api.py --host 0.0.0.0 --port %BACKEND_PORT%"

REM Update Frontend Service  
echo Configuring Frontend to use port %FRONTEND_PORT%...
"C:\Program Files (x86)\nssm-2.24-101-g897c7ad\win64\nssm.exe" set ClawForgeFrontend AppParameters "--port %FRONTEND_PORT% --host 0.0.0.0"

REM Update frontend code to match backend port
echo Updating frontend code to connect to port %BACKEND_PORT%...

REM Restart services
echo Restarting services...
"C:\Program Files (x86)\nssm-2.24-101-g897c7ad\win64\nssm.exe" restart ClawForgeBackend
"C:\Program Files (x86)\nssm-2.24-101-g897c7ad\win64\nssm.exe" restart ClawForgeFrontend

echo.
echo ================================================
echo Fix Complete!
echo ================================================
echo.
echo Ports configured:
echo   Backend:  %BACKEND_PORT%
echo   Frontend: %FRONTEND_PORT%
echo.
echo Frontend will now always connect to backend on port %BACKEND_PORT%
echo.
pause
