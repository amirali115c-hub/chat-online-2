@echo off
REM ====================================================================
REM Check ClawForge Services Status (Fixed)
REM ====================================================================

set NSSM="C:\Program Files (x86)\nssm-2.24-101-g897c7ad\win64\nssm.exe"

echo ================================================
echo ClawForge Service Status
echo ================================================
echo.

echo Backend Service:
%NSSM% status ClawForgeBackend

echo.
echo Frontend Service:
%NSSM% status ClawForgeFrontend

echo.
echo Windows Services:
net start | findstr /i "ClawForge"

pause
