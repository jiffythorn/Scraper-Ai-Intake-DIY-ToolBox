#!/usr/bin/env bash
# Build all distribution zips (individual + complete) → dist-packages/
cd "$(dirname "$0")"
PY=python3; command -v python3 >/dev/null 2>&1 || PY=python
"$PY" make_packages.py "$@"
