#!/usr/bin/env bash
# Double-click / run me: opens the n8n Intake Blueprint window.
cd "$(dirname "$0")"
PY=python3; command -v python3 >/dev/null 2>&1 || PY=python
"$PY" intake_gui.py
