@echo off
rem Build all distribution zips (individual + complete) -> dist-packages\
cd /d "%~dp0"
where python >nul 2>nul || (
  echo Python is needed to run the packager. Install from python.org
  echo and tick "Add python.exe to PATH".
  pause
  exit /b 1
)
python make_packages.py %*
pause
