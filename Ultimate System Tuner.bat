@echo off

:: ---------- Script Start ----------
:: Ensure the script is run as Administrator for higher privileges

:: ---------- Kill Browsers ----------
taskkill /F /IM chrome.exe
taskkill /F /IM msedge.exe
taskkill /F /IM brave.exe
taskkill /F /IM firefox.exe

:: ---------- Kill Gaming & Steam ----------
taskkill /F /IM steam.exe
taskkill /F /IM steamwebhelper.exe
taskkill /F /IM steamservice.exe
taskkill /F /IM steam_bootstrapper.exe
taskkill /F /IM steamvr.exe
taskkill /F /IM "Steam Desktop Authenticator.exe"

:: ---------- Kill Xbox & Gaming Services ----------
taskkill /F /IM XboxPcTray.exe
taskkill /F /IM XboxPcAppFT.exe
taskkill /F /IM Xbox.exe
taskkill /F /IM gamingservicesnet.exe
taskkill /F /IM gamingservices.exe

:: ---------- Kill File Sharing & Cloud Services ----------
taskkill /F /IM shareit.exe
taskkill /F /IM shareitservice.exe
taskkill /F /IM googledrivesync.exe
taskkill /F /IM GoogleDriveFS.exe

:: ---------- Kill Communication Tools ----------
taskkill /F /IM discord.exe
taskkill /F /IM WhatsApp.exe

:: ---------- Kill Cloudflare WARP ----------
taskkill /F /IM warp.exe
taskkill /F /IM warp-svc.exe
taskkill /F /IM cloudflare-warp.exe
taskkill /F /IM CloudflareWARP.exe
taskkill /F /IM WARPClient.exe

:: ---------- Kill WeMod ----------
taskkill /F /IM WeMod.exe
taskkill /F /IM WeModHelper.exe
taskkill /F /IM WeModAuxiliaryService.exe

:: ---------- Kill CurseForge ----------
taskkill /F /IM CurseForge.exe
taskkill /F /IM Curse.Agent.Host.exe
taskkill /F /IM Overwolf.exe

:: ---------- Kill TcNo Account Switcher ----------
taskkill /F /IM TcNo-Acc-Switcher-Tray_main.exe
taskkill /F /IM TcNo-Acc-Switcher_main.exe

:: ---------- Kill Spotify ----------
taskkill /F /IM Spotify.exe
taskkill /F /IM SpotifyWebHelper.exe

:: ---------- Kill System Utilities ----------
taskkill /F /IM AvroKeyboard.exe
taskkill /F /IM AvroSetup.exe
taskkill /F /IM Avro.exe
taskkill /F /IM CCleaner64.exe
taskkill /F /IM CCleaner.exe
taskkill /F /IM CCleanerSmartClean.exe
taskkill /F /IM CCXProcess.exe
taskkill /F /IM CCleanerPerformanceOptimizerService.exe
taskkill /F /IM AdobeIPCBroker.exe
taskkill /F /IM crashpad_handler.exe
taskkill /F /IM BraveCrashHandler64.exe
taskkill /F /IM BraveCrashHandler.exe
taskkill /F /IM BraveUpdate.exe
taskkill /F /IM Taskmgr.exe

:: ---------- Kill Torrent & Download Managers ----------
taskkill /F /IM qbittorrent.exe
taskkill /F /IM IDMan.exe

:: ---------- Kill Background Services & Misc ----------
taskkill /F /IM wallpaper32.exe
taskkill /F /IM winrtutil32.exe
taskkill /F /IM wmpnetwk.exe
taskkill /F /IM NewsAndInterests.exe
taskkill /F /IM node.exe
taskkill /F /IM SearchApp.exe

:: ---------- Kill Phone Link ----------
taskkill /F /IM PhoneLink.exe
taskkill /F /IM PhoneExperienceHost.exe
taskkill /F /IM YourPhone.exe
taskkill /F /IM YourPhoneApp.exe

:: ---------- Network Restart ----------
ipconfig /flushdns
for /L %%i in (1,1,20) do ipconfig /flushdns
ipconfig /release
ipconfig /renew

:: ---------- Delete Temporary Files ----------
:checkPrivileges
NET SESSION >NUL 2>&1
IF %ERRORLEVEL% NEQ 0 (
    powershell -Command "Start-Process '%~0' -Verb RunAs"
    EXIT /B
)

:: Delete files in temporary directories
DEL /F /S /Q "C:\Windows\Prefetch\*.*"
DEL /F /S /Q "C:\Windows\Temp\*.*"
DEL /F /S /Q "C:\Users\SHOWRA~1\AppData\Local\Temp\*.*"

:: ---------- PC Repair ----------
sfc /scannow
dism /online /cleanup-image /restorehealth

:: ---------- Final Message ----------
echo All operations have been completed successfully.

:: ---------- Script End ----------
