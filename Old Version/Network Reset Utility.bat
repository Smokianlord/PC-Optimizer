@echo off
title Network Reset Utility

:: Set fixed window size (120 columns x 40 rows)
mode con: cols=120 lines=40

:: Enable ANSI Escape Codes for Colors (Windows 10+)
echo|set /p=[96m

:: Check for Admin Privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [91m[!] Requesting Administrator Privileges...[0m
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit
)

:: Set color for non-ANSI systems (Green text and black background)
color 0A

:: Display Header
call :printHeader "Network Reset Utility"
echo.

:: Flushing DNS cache multiple times
call :printTask "Flushing DNS Cache"
for /L %%i in (1,1,20) do (
    ipconfig /flushdns >nul
)
call :printSuccess "DNS Cache Flushed!"

:: Releasing and renewing IP
call :printTask "Releasing IP Address"
ipconfig /release >nul
call :printSuccess "IP Address Released!"

call :printTask "Renewing IP Address"
ipconfig /renew >nul
call :printSuccess "IP Address Renewed!"

:: Resetting Winsock
call :printTask "Resetting Winsock"
netsh winsock reset >nul
call :printSuccess "Winsock Reset Successfully!"

:: Resetting TCP/IP stack
call :printTask "Resetting TCP/IP Stack"
netsh int ip reset >nul
call :printSuccess "TCP/IP Stack Reset Successfully!"

:: Restarting Network Adapter
call :printTask "Restarting Network Adapter"
for /f "tokens=1 delims=: " %%A in ('wmic nic where "NetEnabled=True" get NetConnectionID ^| findstr /v "NetConnectionID"') do (
    netsh interface set interface "%%A" admin=disable >nul
    timeout /t 3 /nobreak >nul
    netsh interface set interface "%%A" admin=enable >nul
)
call :printSuccess "Network Adapter Restarted!"

:: Display new network configuration
call :printTask "Fetching New Network Configuration"
ipconfig /all
echo.

:: Completion Message
call :printHeader "Network Reset Completed Successfully!"
echo.
pause
exit

:: Function to print headers with enhanced formatting
:printHeader
echo [94m==========================================
echo [1;97m        %~1        [0m
echo [94m==========================================[0m
exit /b

:: Function to print tasks with color and better clarity
:printTask
echo [96m[*] %~1...[0m
exit /b

:: Function to print success messages with green highlight
:printSuccess
echo [92m[OK] %~1[0m
exit /b
