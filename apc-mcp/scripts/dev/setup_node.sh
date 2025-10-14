#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../../node"
npm install
echo "[OK] Node deps installed. Run dev with: npm run dev"
