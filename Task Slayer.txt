@echo off
title Task Slayer
color 0A
echo =============================================================
echo                   "Task Slayer"
echo =============================================================
echo.

:: ==============================================================
::                       Kill Browsers
:: ==============================================================
echo "=========== Killing Browsers ==========="
taskkill /F /IM chrome.exe
taskkill /F /IM msedge.exe
taskkill /F /IM brave.exe
taskkill /F /IM firefox.exe
taskkill /F /IM MicrosoftEdgeUpdate.exe
echo Done!
echo.

:: ==============================================================
::                   Kill Gaming & Steam
:: ==============================================================
echo "=========== Killing Gaming & Steam ==========="
taskkill /F /IM steam.exe
taskkill /F /IM steamwebhelper.exe
taskkill /F /IM steamservice.exe
taskkill /F /IM steam_bootstrapper.exe
taskkill /F /IM steamvr.exe
taskkill /F /IM "Steam Desktop Authenticator.exe"
echo Done!
echo.

:: ==============================================================
::              Kill Xbox & Gaming Services
:: ==============================================================
echo "=========== Killing Xbox & Gaming Services ==========="
taskkill /F /IM XboxPcTray.exe
taskkill /F /IM XboxPcAppFT.exe
taskkill /F /IM Xbox.exe
taskkill /F /IM gamingservicesnet.exe
taskkill /F /IM gamingservices.exe
echo Done!
echo.

:: ==============================================================
::       Kill File Sharing & Cloud Services
:: ==============================================================
echo "=========== Killing File Sharing & Cloud Services ==========="
taskkill /F /IM shareit.exe
taskkill /F /IM shareitservice.exe
taskkill /F /IM googledrivesync.exe
taskkill /F /IM GoogleDriveFS.exe
echo Done!
echo.

:: ==============================================================
::            Kill Communication Tools
:: ==============================================================
echo "=========== Killing Communication Tools ==========="
taskkill /F /IM discord.exe
taskkill /F /IM WhatsApp.exe
echo Done!
echo.

:: ==============================================================
::             Kill Cloudflare WARP
:: ==============================================================
echo "=========== Killing Cloudflare WARP ==========="
taskkill /F /IM warp.exe
taskkill /F /IM warp-svc.exe
taskkill /F /IM cloudflare-warp.exe
taskkill /F /IM CloudflareWARP.exe
taskkill /F /IM WARPClient.exe
echo Done!
echo.

:: ==============================================================
::                 Kill WeMod
:: ==============================================================
echo "=========== Killing WeMod ==========="
taskkill /F /IM WeMod.exe
taskkill /F /IM WeModHelper.exe
taskkill /F /IM WeModAuxiliaryService.exe
echo Done!
echo.

:: ==============================================================
::              Kill CurseForge & Overwolf
:: ==============================================================
echo "=========== Killing CurseForge & Overwolf ==========="
taskkill /F /IM CurseForge.exe
taskkill /F /IM "Curse.Agent.Host.exe"
taskkill /F /IM "Overwolf.exe"
echo Done!
echo.

:: ==============================================================
::         Kill TcNo Account Switcher
:: ==============================================================
echo "=========== Killing TcNo Account Switcher ==========="
taskkill /F /IM "TcNo-Acc-Switcher-Tray_main.exe"
taskkill /F /IM "TcNo-Acc-Switcher_main.exe"
echo Done!
echo.

:: ==============================================================
::                  Kill Spotify
:: ==============================================================
echo "=========== Killing Spotify ==========="
taskkill /F /IM Spotify.exe
taskkill /F /IM SpotifyWebHelper.exe
echo Done!
echo.

:: ==============================================================
::               Kill System Utilities
:: ==============================================================
echo "=========== Killing System Utilities ==========="
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
echo Done!
echo.

:: ==============================================================
::       Kill Torrent & Download Managers
:: ==============================================================
echo "=========== Killing Torrent & Download Managers ==========="
taskkill /F /IM qbittorrent.exe
taskkill /F /IM IDMan.exe
echo Done!
echo.

:: ==============================================================
::   Kill Background Services
:: ==============================================================
echo "=========== Killing Background Services ==========="
taskkill /F /IM wallpaper32.exe
taskkill /F /IM winrtutil32.exe
taskkill /F /IM wmpnetwk.exe
taskkill /F /IM NewsAndInterests.exe
taskkill /F /IM node.exe
taskkill /F /IM SearchApp.exe
echo Done!
echo.

:: ==============================================================
::                Kill Development Tools
:: ==============================================================
echo "=========== Killing Development Tools ==========="
taskkill /F /IM GitHubDesktop.exe
echo Done!
echo.

:: ==============================================================
::                 Kill Network Tools
:: ==============================================================
echo "=========== Killing Network Tools ==========="
taskkill /F /IM DnsJumper.exe
echo Done!
echo.

:: ==============================================================
::                 Kill Phone Link
:: ==============================================================
echo "=========== Killing Phone Link ==========="
taskkill /F /IM PhoneLink.exe
taskkill /F /IM PhoneExperienceHost.exe
taskkill /F /IM YourPhone.exe
taskkill /F /IM YourPhoneApp.exe
echo Done!
echo.

:: ==============================================================
::                    Script Completed
:: =============================================================
echo Task Slayer: All tasks have been terminated!
echo.

pause
exit
