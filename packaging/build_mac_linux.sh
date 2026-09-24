#!/usr/bin/env bash
# ============================================================
#  Build macOS/Linux executables for the DIY Toolbox
#  Output goes to dist/ . Run this ON the target OS.
# ============================================================
set -e
cd "$(dirname "$0")/.."

PY=python3
command -v python3 >/dev/null 2>&1 || PY=python

echo "[*] Installing PyInstaller (user install, one time)..."
"$PY" -m pip install --user --quiet pyinstaller

echo "[*] Building Toolbox GUI..."
"$PY" -m PyInstaller --onefile --windowed --name Toolbox toolbox.py

echo "[*] Building lead_scraper..."
"$PY" -m PyInstaller --onefile --console --name lead_scraper \
  01-lead-scraper/lead_scraper.py

echo "[*] Building outreach_runner..."
"$PY" -m PyInstaller --onefile --console --name outreach_runner \
  02-ai-outreach-pack/outreach_runner.py

echo
echo "[OK] Done. Find your files in dist/:"
ls -lh dist/ | grep -v '^total' || true

if [ "$(uname)" = "Darwin" ]; then
  echo
  echo "macOS note: Gatekeeper may block unsigned binaries."
  echo "  Right-click the app -> Open (once), or codesign + notarize"
  echo "  for a clean first launch."
fi
