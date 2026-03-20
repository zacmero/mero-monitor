#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UPSTREAM_DIR="$ROOT_DIR/vendor/turing-smart-screen-python"

if [[ ! -d "$UPSTREAM_DIR" ]]; then
  git clone https://github.com/mathoudebine/turing-smart-screen-python.git "$UPSTREAM_DIR"
fi

if [[ ! -f "$UPSTREAM_DIR/main.py" || ! -d "$UPSTREAM_DIR/library" || ! -d "$UPSTREAM_DIR/res" ]]; then
  echo "Vendor app at $UPSTREAM_DIR is incomplete. Remove vendor/ and run this script again."
  exit 1
fi

if [[ ! -x "$UPSTREAM_DIR/.venv/bin/python" ]]; then
  python3 -m venv "$UPSTREAM_DIR/.venv"
fi

"$UPSTREAM_DIR/.venv/bin/pip" install --upgrade pip
"$UPSTREAM_DIR/.venv/bin/pip" install -r "$UPSTREAM_DIR/requirements.txt"

echo "Vendor app prepared at $UPSTREAM_DIR"
