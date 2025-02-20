@echo off
title System Health Check
:: Check for Admin Privileges
NET SESSION >NUL 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Requesting Administrative Privileges...
    PowerShell -Command "Start-Process '%0' -Verb RunAs"
    exit /b
)

:: Set readable color scheme (Light Yellow Text on Black Background)
color 0E

:: Display Header
echo ==================================================
echo       SYSTEM HEALTH CHECK
echo ==================================================

:: Function to show progress bar
echo.
echo [1/5] Scanning system health (This may take a while)...
echo --------------------------------------------------
DISM /ONLINE /CLEANUP-IMAGE /SCANHEALTH
echo Done!
timeout /t 2 >nul

echo.
echo [2/5] Checking system health...
echo --------------------------------------------------
DISM /ONLINE /CLEANUP-IMAGE /CHECKHEALTH
echo Done!
timeout /t 2 >nul

echo.
echo [3/5] Restoring system health (This may take a while)...
echo --------------------------------------------------
DISM /ONLINE /CLEANUP-IMAGE /RESTOREHEALTH
echo Done!
timeout /t 2 >nul

echo.
echo [4/5] Running System File Checker (This may take a while)...
echo --------------------------------------------------
SFC /SCANNOW
echo Done!
timeout /t 2 >nul

echo.
echo [5/5] Running disk check (Requires restart if needed)...
echo --------------------------------------------------
chkdsk C: /F /R
echo Done!
timeout /t 2 >nul

:: Final message
echo.
echo ==================================================
echo        All tasks completed successfully!
echo ==================================================

:: Pause before exit
pause
