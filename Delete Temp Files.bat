@echo off
title Delete Temp Files

:: Set larger window size (120 columns x 40 rows)
mode con: cols=120 lines=40

:: Set color (light gray background, green text)
color F0

:: Enable ANSI Escape Codes for Colors (Windows 10+)
echo|set /p=[92m

:: Check for Admin Privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [91m[!] Requesting Administrator Privileges...[0m
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit
)

:: Set color for non-ANSI systems
color 0A

:: Function to display section headers
call :printHeader "Delete Temp Files"
echo.

:: Clear Windows Temp
call :printTask "Cleaning Windows Temp folder..."
del /s /f /q C:\Windows\Temp\*.* 2>nul
for /d %%i in (C:\Windows\Temp\*) do rd /s /q "%%i" 2>nul
call :printSuccess "Windows Temp cleaned!"
timeout /t 1 >nul

:: Clear Windows Prefetch
call :printTask "Cleaning Windows Prefetch folder..."
del /s /f /q C:\Windows\Prefetch\*.* 2>nul
call :printSuccess "Windows Prefetch cleaned!"
timeout /t 1 >nul

:: Clear User Temp Folders
call :printTask "Cleaning User Temp folders..."
for /d %%u in (C:\Users\*) do (
    del /s /f /q "%%u\AppData\Local\Temp\*.*" 2>nul
    for /d %%i in ("%%u\AppData\Local\Temp\*") do rd /s /q "%%i" 2>nul
)
call :printSuccess "User Temp folders cleaned!"
timeout /t 1 >nul

:: Completion Message
call :printHeader "Cleanup Completed Successfully!"
echo.
pause
exit

:: Function to print headers with enhanced formatting
:printHeader
echo [94m==========================================[0m
echo [1;97m        %~1        [0m
echo [94m==========================================[0m
exit /b

:: Function to print tasks with color and better clarity
:printTask
echo [93m[*] %~1...[0m
exit /b

:: Function to print success messages with green highlight
:printSuccess
echo [92m[OK] %~1[0m
exit /b
