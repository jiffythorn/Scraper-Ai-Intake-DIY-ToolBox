@echo off
rem ============================================================
rem  Build Windows executables for the DIY Toolbox (PyInstaller)
rem  Output goes to dist\ . Run this ON a Windows machine.
rem ============================================================
setlocal
cd /d "%~dp0.."

echo [*] Installing PyInstaller (user install, one time)...
python -m pip install --user --quiet pyinstaller || (
  echo [!] Could not install PyInstaller - check Python ^& internet.
  pause
  exit /b 1
)

echo [*] Building Toolbox GUI...
python -m PyInstaller --onefile --windowed --name Toolbox toolbox.py || goto :err

echo [*] Building lead_scraper...
python -m PyInstaller --onefile --console --name lead_scraper ^
  01-lead-scraper\lead_scraper.py || goto :err

echo [*] Building outreach_runner...
python -m PyInstaller --onefile --console --name outreach_runner ^
  02-ai-outreach-pack\outreach_runner.py || goto :err

echo.
echo [OK] Done. Find your files in dist\
echo      Toolbox.exe, lead_scraper.exe, outreach_runner.exe
echo.
echo NOTE: SmartScreen may warn on first run of unsigned exes -
echo       "More info" ^> "Run anyway". Code-signing removes that.
pause
exit /b 0

:err
echo [!] Build failed - read the error above.
pause
exit /b 1
