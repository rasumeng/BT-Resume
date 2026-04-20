@echo off
REM Resume AI - Application Launcher Batch Wrapper
REM Double-click this to start both backend and frontend

setlocal enabledelayedexpansion

echo.
echo ════════════════════════════════════════════════════════
echo  Resume AI Application Launcher
echo ════════════════════════════════════════════════════════
echo.

REM Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0

REM Run the PowerShell script with proper execution policy
powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%START_APP.ps1"

pause
