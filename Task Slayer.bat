@echo off
setlocal EnableExtensions
goto :main

:: -------------------------
:: Setup + Helpers (verbose)
:: -------------------------
:InitLog
for /f %%i in ('%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe -NoProfile -Command "(Get-Date).ToString('yyyyMMdd_HHmmss')"') do set "STAMP=%%i"
set "LOG=%~dp0TaskSlayer_%STAMP%.log"
echo ==== Task Slayer run at %DATE% %TIME% ==== > "%LOG%"
exit /b

:EchoAndLog
REM Usage: call :EchoAndLog "text"
echo %~1
>>"%LOG%" echo %~1
exit /b

:KillWithEcho
REM Usage: call :KillWithEcho "process.exe"
taskkill /F /IM "%~1" >nul 2>&1
if %errorlevel%==0 (
  call :EchoAndLog "[KILLED] %~1"
) else (
  call :EchoAndLog "[SKIP]   %~1 (not running or no access)"
)
exit /b

:PSRun
REM Usage: call :PSRun "powershell one-liner"
REM Sends stdout to both console and log; stderr -> log only.
%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe -NoProfile -ExecutionPolicy Bypass -Command %~1 | %SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe -NoProfile -Command "Tee-Object -FilePath '%LOG%' -Append"
REM append errors
if not "%~1"=="" (
  rem errors were already captured by PS; nothing to do
)
exit /b

:StopServiceByDisplay
REM Usage: call :StopServiceByDisplay "Cloudflare WARP"
set "DSP=%~1"
call :PSRun "try{ $d='%DSP%'; $svc=Get-Service -DisplayName $d -ErrorAction Stop; if($svc.Status -ne 'Stopped'){ Stop-Service -InputObject $svc -Force -ErrorAction SilentlyContinue; Start-Sleep -Milliseconds 800 }; Set-Service -InputObject $svc -StartupType Manual -ErrorAction SilentlyContinue; Write-Output ('[SERVICE STOPPED] ' + $svc.Name + ' - ' + $svc.DisplayName) } catch{ Write-Output ('[SERVICE SKIP] %DSP% (not found)') }"
exit /b

:StopServiceByName
REM Usage: call :StopServiceByName "warp-svc"
set "SRV=%~1"
call :PSRun "try{ $n='%SRV%'; $svc=Get-Service -Name $n -ErrorAction Stop; if($svc.Status -ne 'Stopped'){ Stop-Service -InputObject $svc -Force -ErrorAction SilentlyContinue; Start-Sleep -Milliseconds 800 }; Set-Service -InputObject $svc -StartupType Manual -ErrorAction SilentlyContinue; Write-Output ('[SERVICE STOPPED] ' + $svc.Name + ' - ' + $svc.DisplayName) } catch{ Write-Output ('[SERVICE SKIP] %SRV% (not found)') }"
exit /b

:main
title Task Slayer
call :InitLog

:: Require Administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
  call :EchoAndLog "Please run this script as Administrator."
  pause
  exit /b 1
)

:: Fixed window + readable colors
mode con: cols=120 lines=40
color 0A

call :EchoAndLog "============================================================="
call :EchoAndLog "Task Slayer starting..."
call :EchoAndLog "Log: %LOG%"
call :EchoAndLog "============================================================="
echo.

:: ---------- Browsers ----------
call :EchoAndLog "=========== Killing Browsers ==========="
call :KillWithEcho "chrome.exe"
call :KillWithEcho "msedge.exe"
call :KillWithEcho "brave.exe"
call :KillWithEcho "firefox.exe"
call :KillWithEcho "MicrosoftEdgeUpdate.exe"
echo.

:: ---------- Gaming & Steam ----------
call :EchoAndLog "=========== Killing Gaming & Steam ==========="
call :KillWithEcho "steam.exe"
call :KillWithEcho "steamwebhelper.exe"
call :KillWithEcho "steamservice.exe"
call :KillWithEcho "steam_bootstrapper.exe"
call :KillWithEcho "steamvr.exe"
call :KillWithEcho "Steam Desktop Authenticator.exe"
echo.

:: ---------- Xbox / Gaming Services ----------
call :EchoAndLog "=========== Killing Xbox & Gaming Services ==========="
call :KillWithEcho "XboxPcTray.exe"
call :KillWithEcho "XboxPcAppFT.exe"
call :KillWithEcho "Xbox.exe"
call :KillWithEcho "gamingservicesnet.exe"
call :KillWithEcho "gamingservices.exe"
call :StopServiceByName "GamingServices"
call :StopServiceByName "GamingServicesNet"
echo.

:: ---------- File Sharing & Cloud ----------
call :EchoAndLog "=========== Killing File Sharing & Cloud Services ==========="
call :KillWithEcho "shareit.exe"
call :KillWithEcho "shareitservice.exe"
call :KillWithEcho "googledrivesync.exe"
call :KillWithEcho "GoogleDriveFS.exe"
echo.

:: ---------- Comms ----------
call :EchoAndLog "=========== Killing Communication Tools ==========="
call :KillWithEcho "discord.exe"
call :KillWithEcho "WhatsApp.exe"
echo.

:: ---------- Cloudflare WARP ----------
call :EchoAndLog "=========== Killing Cloudflare WARP ==========="
call :KillWithEcho "warp.exe"
call :KillWithEcho "warp-svc.exe"
call :KillWithEcho "cloudflare-warp.exe"
call :KillWithEcho "CloudflareWARP.exe"
call :KillWithEcho "WARPClient.exe"
call :StopServiceByName "warp-svc"
call :StopServiceByDisplay "Cloudflare WARP"
echo.

:: ---------- WeMod ----------
call :EchoAndLog "=========== Killing WeMod ==========="
call :KillWithEcho "WeMod.exe"
call :KillWithEcho "WeModHelper.exe"
call :KillWithEcho "WeModAuxiliaryService.exe"
echo.

:: ---------- CurseForge / Overwolf ----------
call :EchoAndLog "=========== Killing CurseForge & Overwolf ==========="
call :KillWithEcho "CurseForge.exe"
call :KillWithEcho "Curse.Agent.Host.exe"
call :KillWithEcho "Overwolf.exe"
echo.

:: ---------- TcNo ----------
call :EchoAndLog "=========== Killing TcNo Account Switcher ==========="
call :KillWithEcho "TcNo-Acc-Switcher-Tray_main.exe"
call :KillWithEcho "TcNo-Acc-Switcher_main.exe"
echo.

:: ---------- Spotify ----------
call :EchoAndLog "=========== Killing Spotify ==========="
call :KillWithEcho "Spotify.exe"
call :KillWithEcho "SpotifyWebHelper.exe"
echo.

:: ---------- System Utilities (safe) ----------
call :EchoAndLog "=========== Killing System Utilities ==========="
call :KillWithEcho "AvroKeyboard.exe"
call :KillWithEcho "AvroSetup.exe"
call :KillWithEcho "Avro.exe"
call :KillWithEcho "CCleaner64.exe"
call :KillWithEcho "CCleaner.exe"
call :KillWithEcho "CCleanerSmartClean.exe"
call :KillWithEcho "CCXProcess.exe"
call :KillWithEcho "AdobeIPCBroker.exe"
call :KillWithEcho "crashpad_handler.exe"
call :KillWithEcho "BraveCrashHandler64.exe"
call :KillWithEcho "BraveCrashHandler.exe"
call :KillWithEcho "BraveUpdate.exe"
echo.

:: ---------- Torrent / Download ----------
call :EchoAndLog "=========== Killing Torrent & Download Managers ==========="
call :KillWithEcho "qbittorrent.exe"
call :KillWithEcho "IDMan.exe"
echo.

:: ---------- Background services ----------
call :EchoAndLog "=========== Killing Background Services ==========="
call :KillWithEcho "wallpaper32.exe"
call :KillWithEcho "winrtutil32.exe"
call :KillWithEcho "wmpnetwk.exe"
call :KillWithEcho "NewsAndInterests.exe"
call :KillWithEcho "node.exe"
call :KillWithEcho "SearchApp.exe"
echo.

:: ---------- Development ----------
call :EchoAndLog "=========== Killing Development Tools ==========="
call :KillWithEcho "GitHubDesktop.exe"
call :KillWithEcho "figma_agent.exe"
echo.

:: ---------- Network tools ----------
call :EchoAndLog "=========== Killing Network Tools ==========="
call :KillWithEcho "DnsJumper.exe"
echo.

:: ---------- Phone Link ----------
call :EchoAndLog "=========== Killing Phone Link ==========="
call :KillWithEcho "PhoneLink.exe"
call :KillWithEcho "PhoneExperienceHost.exe"
call :KillWithEcho "YourPhone.exe"
call :KillWithEcho "YourPhoneApp.exe"
echo.

:: ---------- Adobe ----------
call :EchoAndLog "=========== Killing Adobe and Related Services ==========="
call :KillWithEcho "AdobeCollabSync.exe"
call :KillWithEcho "acrotray.exe"
call :KillWithEcho "armsvc.exe"
call :KillWithEcho "AGMService.exe"
echo.

:: ---------- Canva ----------
call :EchoAndLog "=========== Killing Canva ==========="
call :KillWithEcho "Canva.exe"
echo.

:: ---------- NordVPN & NordSec updater ----------
call :EchoAndLog "=========== Killing NordVPN ==========="
call :KillWithEcho "NordVPN.exe"
call :KillWithEcho "nordvpn-service.exe"
call :KillWithEcho "NordSecUpdateService.exe"
call :StopServiceByName "nordvpn-service"
call :StopServiceByName "NordSecUpdateService"
call :StopServiceByDisplay "NordSec Update Service"
echo.

:: ---------- Windows Search Indexer (optional) ----------
call :EchoAndLog "=========== Killing Windows Search Indexer ==========="
call :KillWithEcho "SearchIndexer.exe"
call :KillWithEcho "SearchProtocolHost.exe"
call :KillWithEcho "SearchFilterHost.exe"
echo.

:: ---------- NVIDIA helper/telemetry ----------
call :EchoAndLog "=========== Killing NVIDIA helpers ==========="
call :KillWithEcho "NVDisplay.Container.exe"
call :KillWithEcho "nvcontainer.exe"
call :KillWithEcho "NVIDIA Share.exe"
call :KillWithEcho "NVIDIA ShadowPlay Helper.exe"
call :KillWithEcho "NVIDIA Web Helper.exe"
call :KillWithEcho "NVIDIA Web Helper Service.exe"
call :KillWithEcho "PresentMon.exe"
call :KillWithEcho "NVRLA.exe"
call :StopServiceByName "NVDisplay.ContainerLocalSystem"
call :StopServiceByDisplay "NVIDIA Display Container LS"
call :StopServiceByName "NvContainerLocalSystem"
call :StopServiceByDisplay "NVIDIA LocalSystem Container"
call :StopServiceByName "NvFvSvc"
call :StopServiceByDisplay "NVIDIA FrameView SDK service"
echo.

:: ---------- Nahimic ----------
call :EchoAndLog "=========== Killing Nahimic (audio enhancer) ==========="
call :KillWithEcho "NahimicService.exe"
call :StopServiceByName "NahimicService"
call :StopServiceByDisplay "NahimicService"
echo.

call :EchoAndLog "Task Slayer complete."
call :EchoAndLog "(Kept Avast, DisplayFusion, Logitech G HUB, and TrafficMonitor.exe running.)"
echo.
echo View log for any red errors:
echo   "%LOG%"
echo.
pause
exit /b
