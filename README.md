# Turzx Monitor

Custom Linux setup for a Turzx `USB35INCHIPSV2` 3.5" display, built around `mathoudebine/turing-smart-screen-python` with a temperature-first cyberpunk theme and local overrides for this ArchMerOS machine.

## What This Repo Contains

This repo is the shareable system layer, not a full upstream fork.

It keeps the files that matter for this machine in the project root:

- `theme/MeroCyberTemp/`: the custom theme asset and YAML
- `config.yaml`: the runtime config used by the display app
- `overrides/library/stats.py`: patched upstream renderer with dynamic theme color stops
- `overrides/library/sensors/sensors_custom.py`: custom sensors for NVIDIA or `nouveau` GPU temp/fan/load, network rate, and ping
- `run-monitor.sh`: syncs the root files into the upstream app and launches it
- `sync-project-files.sh`: copies the root theme/config/overrides into the vendored upstream tree
- `setup-vendor.sh`: clones the upstream app and installs its Python environment
- `systemd/turzx-monitor.service`: system service template
- `install-system-service.sh`: installs and enables the service

The upstream runtime bundle lives under `vendor/` at runtime and is ignored by Git.

## Theme

`MeroCyberTemp` is a minimalist portrait dashboard built for this screen and this setup:

- large CPU and GPU temperatures as the primary focus
- cyberpunk palette without turning the whole display into noise
- dynamic temperature coloring:
  - cold = blue
  - around `50C` = green
  - hotter = yellow to orange
  - very hot = red
- memory and disk usage with separate color ramps
- bottom status strip for network throughput and ping
- GPU temperature and load data from NVIDIA via `nvidia-smi`, with fallback to `nouveau` `sensors -j`
- GPU fan readout from `nvidia-settings` RPM when available, otherwise fallback behavior

Theme files:

- [theme/MeroCyberTemp/theme.yaml](/home/zacmero/mero-monitor/theme/MeroCyberTemp/theme.yaml)
- [theme/MeroCyberTemp/background.png](/home/zacmero/mero-monitor/theme/MeroCyberTemp/background.png)

## Project Features Beyond The Theme

- root-first workflow: the custom files in this repo are the source of truth
- safe upstream reuse instead of maintaining a full fork
- systemd boot integration
- custom sensor bridge for Linux NVIDIA and `nouveau` setups where upstream GPU support is limited
- dynamic color-stop support added to upstream text and bar rendering
- manual setup and runtime scripts kept in the repo instead of scattered around the machine

## Runtime Flow

1. `run-monitor.sh` calls `sync-project-files.sh`
2. the root config, theme, and patched files are copied into `vendor/turing-smart-screen-python`
3. the upstream app is launched from its venv
4. systemd uses the same wrapper, so manual runs and service runs stay aligned

## Setup

### 1. Prepare the upstream app

```bash
./setup-vendor.sh
```

This will:

- clone `mathoudebine/turing-smart-screen-python` into `vendor/`
- create `vendor/turing-smart-screen-python/.venv`
- install upstream Python dependencies

### 2. Make sure the screen is accessible

On Arch, the serial device is usually owned by `uucp`.

```bash
sudo usermod -aG uucp "$USER"
```

Then log out and back in, or reboot.

### 3. Run manually

```bash
./run-monitor.sh
```

## Install As A Service

```bash
sudo ./install-system-service.sh
```

That installs [systemd/turzx-monitor.service](/home/zacmero/mero-monitor/systemd/turzx-monitor.service) into `/etc/systemd/system/` and enables it.

Useful commands:

```bash
sudo systemctl restart turzx-monitor.service
sudo systemctl status turzx-monitor.service --no-pager
```

## Main Files

- [config.yaml](/home/zacmero/mero-monitor/config.yaml)
- [run-monitor.sh](/home/zacmero/mero-monitor/run-monitor.sh)
- [sync-project-files.sh](/home/zacmero/mero-monitor/sync-project-files.sh)
- [setup-vendor.sh](/home/zacmero/mero-monitor/setup-vendor.sh)
- [install-system-service.sh](/home/zacmero/mero-monitor/install-system-service.sh)
- [systemd/turzx-monitor.service](/home/zacmero/mero-monitor/systemd/turzx-monitor.service)
- [overrides/library/stats.py](/home/zacmero/mero-monitor/overrides/library/stats.py)
- [overrides/library/sensors/sensors_custom.py](/home/zacmero/mero-monitor/overrides/library/sensors/sensors_custom.py)

## Notes

- `vendor/` is intentionally ignored so the repo stays focused on the custom layer.
- On the current NVIDIA setup, the custom layer reads GPU temperature and utilization through `nvidia-smi` and keeps a small GPU load field under the fan readout.
