@echo off
REM ====================================================================
REM Check ClawForge Service Logs
REM ====================================================================

echo ================================================
echo Backend Service Log
echo ================================================
type C:\Users\HP\.openclaw\workspace\ClawForge\logs\backend.log 2>nul
if errorlevel 1 echo (No log file found)

echo.
echo ================================================
echo Backend Service Error Log
echo ================================================
type C:\Users\HP\.openclaw\workspace\ClawForge\logs\backend_error.log 2>nul
if errorlevel 1 echo (No error log found)

echo.
echo ================================================
echo Frontend Service Log
echo ================================================
type C:\Users\HP\.openclaw\workspace\ClawForge\logs\frontend.log 2>nul
if errorlevel 1 echo (No log file found)

echo.
echo ================================================
echo Frontend Service Error Log
echo ================================================
type C:\Users\HP\.openclaw\workspace\ClawForge\logs\frontend_error.log 2>nul
if errorlevel 1 echo (No error log found)

pause
