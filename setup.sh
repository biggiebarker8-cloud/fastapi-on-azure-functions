#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if [[ ! -d ".venv" ]]; then
  python -m venv .venv
fi

source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if command -v func >/dev/null 2>&1; then
  if ! func bundles download; then
    echo "Unable to download extension bundles right now; continue and retry later with: func bundles download"
  fi
else
  echo "Azure Functions Core Tools (func) not found; skipping extension bundle prefetch."
fi

echo "Setup complete."
echo "Activate your environment with: source .venv/bin/activate"
echo "Start locally with: func start"
