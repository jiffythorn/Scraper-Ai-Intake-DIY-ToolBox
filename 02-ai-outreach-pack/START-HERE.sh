#!/usr/bin/env bash
# Double-click / run me: opens the AI Outreach window.
cd "$(dirname "$0")"
PY=python3; command -v python3 >/dev/null 2>&1 || PY=python
"$PY" outreach_gui.py
