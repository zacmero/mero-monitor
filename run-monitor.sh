#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UPSTREAM_DIR="$ROOT_DIR/vendor/turing-smart-screen-python"

if [[ ! -x "$UPSTREAM_DIR/.venv/bin/python" ]]; then
  echo "Missing upstream runtime at $UPSTREAM_DIR/.venv/bin/python"
  echo "Run ./setup-vendor.sh first."
  exit 1
fi

"$ROOT_DIR/sync-project-files.sh"

cd "$UPSTREAM_DIR"
exec ./.venv/bin/python ./main.py "$@"
