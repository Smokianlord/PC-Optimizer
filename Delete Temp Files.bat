@echo off
:: Request Admin Privileges
:checkPrivileges
NET SESSION >NUL 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO Requesting administrative privileges...
    powershell -Command "Start-Process '%~0' -Verb RunAs"
    EXIT /B
)

:: Delete all files in the specified folders forcefully
echo Deleting files in C:\Windows\Prefetch...
DEL /F /S /Q "C:\Windows\Prefetch\*.*"

echo Deleting files in C:\Windows\Temp...
DEL /F /S /Q "C:\Windows\Temp\*.*"

echo Deleting files in %USERPROFILE%\AppData\Local\Temp...
DEL /F /S /Q "%USERPROFILE%\AppData\Local\Temp\*.*"

:: Optionally, pause to see the results
echo Done!
pause
