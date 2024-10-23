@echo off

:: ---------- Task Slayer ----------
:: Run as Administrator for higher privileges

:: Browsers
taskkill /F /IM chrome.exe
taskkill /F /IM msedge.exe
taskkill /F /IM brave.exe
taskkill /F /IM firefox.exe

:: Gaming & Steam
taskkill /F /IM steam.exe
taskkill /F /IM steamwebhelper.exe
taskkill /F /IM steamservice.exe
taskkill /F /IM steam_bootstrapper.exe
taskkill /F /IM steamvr.exe
taskkill /F /IM Steam Desktop Authenticator.exe

:: Xbox & Gaming Services
taskkill /F /IM XboxPcTray.exe
taskkill /F /IM XboxPcAppFT.exe
taskkill /F /IM Xbox.exe
taskkill /F /IM gamingservicesnet.exe
taskkill /F /IM gamingservices.exe

:: File Sharing & Cloud
taskkill /F /IM shareit.exe
taskkill /F /IM shareitservice.exe
taskkill /F /IM googledrivesync.exe
taskkill /F /IM GoogleDriveFS.exe

:: Communication
taskkill /F /IM discord.exe
taskkill /F /IM WhatsApp.exe

:: Cloudflare WARP
taskkill /F /IM warp.exe
taskkill /F /IM warp-svc.exe
taskkill /F /IM cloudflare-warp.exe
taskkill /F /IM CloudflareWARP.exe
taskkill /F /IM WARPClient.exe

:: WeMod
taskkill /F /IM WeMod.exe
taskkill /F /IM WeModHelper.exe
taskkill /F /IM WeModAuxiliaryService.exe

:: CurseForge
taskkill /F /IM CurseForge.exe
taskkill /F /IM Curse.Agent.Host.exe
taskkill /F /IM Overwolf.exe

:: TcNo Account Switcher
taskkill /F /IM TcNo-Acc-Switcher-Tray_main.exe
taskkill /F /IM TcNo-Acc-Switcher_main.exe

:: Spotify
taskkill /F /IM Spotify.exe
taskkill /F /IM SpotifyWebHelper.exe

:: System Utilities
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

:: Torrent & Download Managers
taskkill /F /IM qbittorrent.exe
taskkill /F /IM IDMan.exe

:: Background Services & Misc
taskkill /F /IM wallpaper32.exe
taskkill /F /IM winrtutil32.exe
taskkill /F /IM wmpnetwk.exe
taskkill /F /IM NewsAndInterests.exe
taskkill /F /IM node.exe
taskkill /F /IM SearchApp.exe

:: Phone Link
taskkill /F /IM PhoneLink.exe
taskkill /F /IM PhoneExperienceHost.exe
taskkill /F /IM YourPhone.exe
taskkill /F /IM YourPhoneApp.exe

:: ---------- Network Reset Utility ----------
ipconfig /flushdns
for /L %%i in (1,1,20) do ipconfig /flushdns
ipconfig /release
ipconfig /renew

:: ---------- Delete Temp Files ----------
:: Request Admin Privileges
:checkPrivileges
NET SESSION >NUL 2>&1
IF %ERRORLEVEL% NEQ 0 (
    powershell -Command "Start-Process '%~0' -Verb RunAs"
    EXIT /B
)

:: Delete all files in the specified folders forcefully
DEL /F /S /Q "C:\Windows\Prefetch\*.*"
DEL /F /S /Q "C:\Windows\Temp\*.*"
DEL /F /S /Q "%USERPROFILE%\AppData\Local\Temp\*.*"

:: ---------- System Health Check ----------
sfc /scannow
dism /online /cleanup-image /restorehealth

:: Final Message
echo All operations have been completed successfully.
