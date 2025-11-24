#!/usr/bin/env bash
set -euo pipefail

# Usage: ./scripts/setup_dev.sh
# Creates a venv in .venv, activates it, and installs requirements.

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
python -m playwright install

echo "Development environment ready. Activate with: source .venv/bin/activate"
