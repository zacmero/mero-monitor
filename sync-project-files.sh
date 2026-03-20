#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UPSTREAM_DIR="$ROOT_DIR/vendor/turing-smart-screen-python"
THEME_NAME="MeroCyberTemp"

if [[ ! -d "$UPSTREAM_DIR" ]]; then
  echo "Missing upstream app at $UPSTREAM_DIR"
  echo "Run ./setup-vendor.sh first."
  exit 1
fi

install -Dm644 "$ROOT_DIR/config.yaml" "$UPSTREAM_DIR/config.yaml"
install -Dm644 "$ROOT_DIR/theme/default.yaml" "$UPSTREAM_DIR/res/themes/default.yaml"
install -Dm644 "$ROOT_DIR/overrides/main.py" "$UPSTREAM_DIR/main.py"
install -Dm644 "$ROOT_DIR/overrides/library/stats.py" "$UPSTREAM_DIR/library/stats.py"
install -Dm644 "$ROOT_DIR/overrides/library/sensors/sensors_custom.py" "$UPSTREAM_DIR/library/sensors/sensors_custom.py"
install -Dm644 "$ROOT_DIR/theme/$THEME_NAME/theme.yaml" "$UPSTREAM_DIR/res/themes/$THEME_NAME/theme.yaml"
cp "$ROOT_DIR/theme/$THEME_NAME/background.png" "$UPSTREAM_DIR/res/themes/$THEME_NAME/background.png"
