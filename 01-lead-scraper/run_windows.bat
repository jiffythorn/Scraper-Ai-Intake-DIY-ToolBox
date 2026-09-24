@echo off
rem ============================================================
rem  Mr T's DIY Toolbox - Windows launcher
rem  Plain batch file - open it in Notepad to read everything.
rem  Double-click to: create config from example, open it for
rem  editing, then run the scraper.
rem ============================================================
setlocal
cd /d "%~dp0"

if not exist config.yml (
  echo [*] First run: creating config.yml from example...
  copy config.example.yml config.yml >nul
  echo [*] Opening config for editing - set your town + category, save, close.
  notepad config.yml
)

where python >nul 2>nul
if %errorlevel% neq 0 (
  echo [!] Python not found. Install from python.org and tick
  echo     "Add python.exe to PATH" during setup, then run again.
  echo     Opening the download page...
  start https://www.python.org/downloads/
  pause
  exit /b 1
)

python lead_scraper.py
echo.
echo [*] Done. Output: leads.csv  ^(open it in Excel^)
pause
