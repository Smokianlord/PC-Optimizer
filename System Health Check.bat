@echo off

DISM /ONLINE /CLEANUP-IMAGE /SCANHEALTH
DISM /ONLINE /CLEANUP-IMAGE /CHECKHEALTH
DISM /ONLINE /CLEANUP-IMAGE /RESTOREHEALTH
Sfc /Scannow