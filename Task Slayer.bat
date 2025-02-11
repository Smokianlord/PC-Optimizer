@echo off

:: Browsers
taskkill /F /IM chrome.exe
taskkill /F /IM msedge.exe
taskkill /F /IM brave.exe
taskkill /F /IM firefox.exe
taskkill /F /IM opera.exe
taskkill /F /IM safari.exe

:: Gaming & Steam
taskkill /F /IM steam.exe
taskkill /F /IM steamwebhelper.exe
taskkill /F /IM steamservice.exe
taskkill /F /IM steam_bootstrapper.exe
taskkill /F /IM steamvr.exe
taskkill /F /IM epicgameslauncher.exe
taskkill /F /IM origin.exe
taskkill /F /IM GOGGalaxy.exe
taskkill /F /IM battle.net.exe

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
taskkill /F /IM Dropbox.exe
taskkill /F /IM OneDrive.exe
taskkill /F /IM Box.exe
taskkill /F /IM pCloud.exe
taskkill /F /IM Sync.exe

:: Communication
taskkill /F /IM discord.exe
taskkill /F /IM WhatsApp.exe
taskkill /F /IM Slack.exe
taskkill /F /IM Skype.exe
taskkill /F /IM Telegram.exe
taskkill /F /IM TeamViewer.exe
taskkill /F /IM Zoom.exe
taskkill /F /IM MicrosoftTeams.exe

:: Cloudflare WARP
taskkill /F /IM warp.exe
taskkill /F /IM warp-svc.exe
taskkill /F /IM cloudflare-warp.exe
taskkill /F /IM CloudflareWARP.exe
taskkill /F /IM WARPClient.exe

:: System Utilities
taskkill /F /IM AvroKeyboard.exe
taskkill /F /IM AvroSetup.exe
taskkill /F /IM Avro.exe
taskkill /F /IM CCleaner64.exe
taskkill /F /IM CCleaner.exe
taskkill /F /IM CCleanerSmartClean.exe
taskkill /F /IM CCXProcess.exe
taskkill /F /IM AdobeIPCBroker.exe
taskkill /F /IM crashpad_handler.exe
taskkill /F /IM BraveCrashHandler64.exe
taskkill /F /IM BraveCrashHandler.exe
taskkill /F /IM Taskmgr.exe
taskkill /F /IM Notepad++.exe
taskkill /F /IM VisualStudio.exe
taskkill /F /IM WinRAR.exe
taskkill /F /IM 7zFM.exe

:: Torrent & Download Managers
taskkill /F /IM qbittorrent.exe
taskkill /F /IM IDMan.exe
taskkill /F /IM uTorrent.exe
taskkill /F /IM FreeDownloadManager.exe
taskkill /F /IM JDownloader.exe

:: Media Players
taskkill /F /IM vlc.exe
taskkill /F /IM iTunes.exe
taskkill /F /IM WindowsMediaPlayer.exe
taskkill /F /IM MediaMonkey.exe
taskkill /F /IM Spotify.exe
taskkill /F /IM AIMP.exe
taskkill /F /IM PotPlayer.exe

:: Virtual Machines
taskkill /F /IM VirtualBox.exe
taskkill /F /IM VMware.exe
taskkill /F /IM Hyper-V.exe

:: Background Services & Misc
taskkill /F /IM wallpaper32.exe
taskkill /F /IM winrtutil32.exe
taskkill /F /IM wmpnetwk.exe
taskkill /F /IM NewsAndInterests.exe
taskkill /F /IM node.exe
taskkill /F /IM SearchApp.exe
taskkill /F /IM FortniteLauncher.exe
taskkill /F /IM blizzard.exe
taskkill /F /IM MinecraftLauncher.exe
taskkill /F /IM EpicGamesLauncher.exe

:: Phone Link
taskkill /F /IM PhoneLink.exe
taskkill /F /IM PhoneExperienceHost.exe
taskkill /F /IM YourPhone.exe
taskkill /F /IM YourPhoneApp.exe

echo All specified processes have been closed.
pause
