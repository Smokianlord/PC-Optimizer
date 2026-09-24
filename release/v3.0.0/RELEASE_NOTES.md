# PC Optimizer v3.0.0

A new Windows desktop control center for reviewing running apps and performing common maintenance tasks.

## What's new

- Rebuilt interface with Dashboard, App Manager, Maintenance, and an activity log visible on every page.
- Search running desktop apps, select individual processes or use Select all and Deselect all, then confirm before closing them.
- Exclude Windows-hosted and service-managed helpers that immediately restart when their child process is closed.
- Report closed, already stopped, and failed processes separately, and identify selected app names that remain running.
- Refresh DNS and DHCP without a restart. A separate network stack repair resets Winsock and TCP/IP and requires a Windows restart.
- Clean current-user and Windows Temp folders, and run DISM plus System File Checker.
- Include administrator relaunch, command output, and explicit confirmation before maintenance actions.

## Download

Download **PC Optimizer v3.0.0.exe** from this release's assets. It is a standalone Windows x64 executable; Python is not required.

## Important notes

- Save work before closing selected apps. Force-closing can discard unsaved changes.
- The quick network refresh renews DHCP only on adapters that use DHCP. The deeper network stack repair requires a restart to finish applying changes.
- The app does not reset your router or ISP connection.
- The executable is not code signed. Windows may show a SmartScreen prompt.

## Verify the download

The SHA-256 checksum is in **SHA256SUMS.txt**. Compare it with the downloaded EXE before running it.
