@echo off
rem ============================================================
rem  Mr T's AI Outreach Pack - Windows launcher
rem  Double-click to: create config, open it for editing, then
rem  draft an email for the sample lead (add real leads later).
rem ============================================================
setlocal
cd /d "%~dp0"

if not exist config.yml (
  echo [*] First run: creating config.yml from example...
  copy config.example.yml config.yml >nul
  echo [*] Opening config for editing - set YOUR name/business, save, close.
  notepad config.yml
)

where python >nul 2>nul
if %errorlevel% neq 0 (
  echo [!] Python not found. Install from python.org and tick
  echo     "Add python.exe to PATH" during setup, then run again.
  start https://www.python.org/downloads/
  pause
  exit /b 1
)

python outreach_runner.py --lead sample-lead.yml --save
echo.
echo [*] Draft saved under drafts\. Review it before ANY sending.
pause
