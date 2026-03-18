#!/usr/bin/env bash
set -euo pipefail

# Creates a local virtual environment and installs requirements.
# Run from the repo root:
#   ./setup.sh

if [ ! -d .venv ]; then
  python -m venv .venv
fi

# shellcheck source=/dev/null
source .venv/bin/activate
pip install -r requirements.txt

echo "\n✅ Setup complete. Run the generator with: python src/main.py"
