#!/usr/bin/env bash
# ============================================================
#  Mr T's AI Outreach Pack - macOS / Linux launcher
#  Creates config, drafts for the sample lead, saves it.
# ============================================================
set -e
cd "$(dirname "$0")"

if [ ! -f config.yml ]; then
  echo "[*] First run: creating config.yml from example..."
  cp config.example.yml .yml.tmp 2>/dev/null || true
  cp config.example.yml config.yml
  rm -f .yml.tmp
  echo "[!] Now edit config.yml (set YOUR name/business), save, re-run."
  ${EDITOR:-nano} config.yml || true
  exit 0
fi

PY=python3
command -v python3 >/dev/null 2>&1 || PY=python

echo "[*] Drafting outreach for the sample lead..."
"$PY" outreach_runner.py --lead sample-lead.yml --save

echo
echo "[*] Draft saved under drafts/. Review before ANY sending."
