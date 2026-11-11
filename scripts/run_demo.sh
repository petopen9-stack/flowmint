#!/usr/bin/env bash
# One-command offline demo for judges
set -euo pipefail
cd "$(dirname "$0")/.."

echo "Installing nearaction (editable)..."
pip install -e . -q

echo ""
echo "Running full offline demo..."
echo ""
nearaction demo
