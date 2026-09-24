#!/usr/bin/env bash
# ============================================================
#  Mr T's DIY Toolbox - macOS / Linux launcher
#  Plain shell script - `cat run_mac_linux.sh` to read it all.
#  Creates config from example, runs the scraper.
# ============================================================
set -e
cd "$(dirname "$0")"

if [ ! -f config.yml ]; then
  echo "[*] First run: creating config.yml from example..."
  cp config.example.yml config.yml
  echo "[!] Now edit config.yml (set town + category), save, then re-run."
  ${EDITOR:-nano} config.yml || true
  echo "[*] Re-run me when you've saved your config."
  exit 0
fi

PY=python3
command -v python3 >/dev/null 2>&1 || PY=python

echo "[*] Running scraper with $PY ..."
"$PY" lead_scraper.py

echo
echo "[*] Done. Output: leads.csv"
