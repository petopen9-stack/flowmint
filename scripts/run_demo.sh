#!/usr/bin/env bash
# One-command offline demo for judges
set -euo pipefail
cd "$(dirname "$0")/.."

echo "Installing flowmint (editable)..."
pip install -e . -q

echo ""
echo "Running full offline demo..."
echo ""
flowmint demo
