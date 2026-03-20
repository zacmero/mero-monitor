#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME=turzx-monitor.service

if [[ ${EUID:-$(id -u)} -ne 0 ]]; then
  echo "Run as root: sudo $ROOT_DIR/install-system-service.sh"
  exit 1
fi

chmod +x   "$ROOT_DIR/setup-vendor.sh"   "$ROOT_DIR/sync-project-files.sh"   "$ROOT_DIR/run-monitor.sh"

install -Dm644   "$ROOT_DIR/systemd/turzx-monitor.service"   "/etc/systemd/system/$SERVICE_NAME"

systemctl daemon-reload
systemctl enable --now "$SERVICE_NAME"

echo "Installed and started $SERVICE_NAME"
