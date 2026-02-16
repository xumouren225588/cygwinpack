@echo off
mkdir "%LOCALAPPDATA%\cygwin-updater"
xcopy * "%LOCALAPPDATA%\cygwin-updater" /E /I /H /Y
cd /d "%LOCALAPPDATA%\cygwin-updater"

.\install.exe
