#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../../python"
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
echo "[OK] Python env ready. Activate with: source python/.venv/bin/activate"
