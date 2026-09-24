@echo off
rem Double-click me: opens the AI Outreach window.
setlocal
cd /d "%~dp0"
where python >nul 2>nul || (
  echo Python is needed once. Opening the download page...
  start https://www.python.org/downloads/
  echo Install it and tick "Add python.exe to PATH", then run me again.
  pause
  exit /b 1
)
python outreach_gui.py
if %errorlevel% neq 0 pause
