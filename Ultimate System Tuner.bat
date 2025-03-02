@echo off

REM ============================
REM Combined Script
REM ============================

:: This script merges the functionality of all four batch files into one.
:: You can run each script individually by passing an argument, or run them all at once.

if "%~1"=="" (
    echo Usage: %~0 [delete | network | health | task | all]
    echo.
    echo   delete   - Run Delete Temp Files.
    echo   network  - Run Network Reset Utility.
    echo   health   - Run System Health Check.
    echo   task     - Run Task Slayer.
    echo   all      - Run all tasks sequentially.
    exit /b 1
)

if /i "%~1"=="delete"  goto :DeleteTemp
if /i "%~1"=="network" goto :NetworkReset
if /i "%~1"=="health"  goto :SystemHealth
if /i "%~1"=="task"    goto :TaskSlayer
if /i "%~1"=="all"     goto :RunAll

echo Invalid parameter: %~1
exit /b 1


:DeleteTemp
REM ============================
REM (DELETE TEMP FILES CONTENT)
REM Insert the content from "Delete Temp Files.bat" below.
REM ============================

REM Example placeholder:
echo Running Delete Temp Files...
:: Replace this echo block with your actual Delete Temp Files code.

goto :EOF


:NetworkReset
REM ============================
REM (NETWORK RESET UTILITY CONTENT)
REM Insert the content from "Network Reset Utility.bat" below.
REM ============================

echo Running Network Reset Utility...
:: Replace this echo block with your actual Network Reset Utility code.

goto :EOF


:SystemHealth
REM ============================
REM (SYSTEM HEALTH CHECK CONTENT)
REM Insert the content from "System Health Check.bat" below.
REM ============================

echo Running System Health Check...
:: Replace this echo block with your actual System Health Check code.

goto :EOF


:TaskSlayer
REM ============================
REM (TASK SLAYER CONTENT)
REM Insert the content from "Task Slayer.bat" below.
REM ============================

echo Running Task Slayer...
:: Replace this echo block with your actual Task Slayer code.

goto :EOF


:RunAll
call :DeleteTemp
call :NetworkReset
call :SystemHealth
call :TaskSlayer

echo.
echo All tasks have been completed!
pause

goto :EOF
