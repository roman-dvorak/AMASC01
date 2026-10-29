# Release & installation

Release package contains `camera_supervisor` (thermal control daemon + CLI) and the systemd units
(`thermal-control`, `netact-led`, optionally `reverse-ssh`).

## Creating a release

1. Create a tag and a GitHub release (e.g. `v1.2.0`), via web UI or:

   ```bash
   gh release create v1.2.0 --generate-notes
   ```

2. The [Release workflow](../.github/workflows/release.yml) builds and attaches to the release:
   - `amasc01-v1.2.0.tar.gz` + `.sha256`
   - `install.sh` – downloads the release and runs `setup.sh` from it

   Assets for an existing tag can be rebuilt via *Actions → Release → Run workflow*.

Local build (for testing): `release/build.sh v1.2.0-dev dist`

## Installing on the camera

Latest release:

```bash
curl -fsSL https://github.com/roman-dvorak/AMASC01/releases/latest/download/install.sh | sudo bash
```

Specific version, including the reverse SSH tunnel:

```bash
curl -fsSL https://github.com/roman-dvorak/AMASC01/releases/latest/download/install.sh | sudo bash -s -- --version v1.2.0 --with-reverse-ssh
```

Show help without installing anything:

```bash
curl -fsSL https://github.com/roman-dvorak/AMASC01/releases/latest/download/install.sh | bash -s -- --help
```

### Options

`install.sh` (download bootstrap) accepts `--version` and passes everything else to `setup.sh`:

| Option | Description |
|---|---|
| `--version TAG` | release to install (`install.sh` only, default: latest) |
| `--with-reverse-ssh` | also install `reverse-ssh.service` (keeps already assigned port, see [systemd/README.md](../systemd/README.md)) |
| `--no-restart` | do not (re)start services |
| `--keep N` | number of releases kept in `/opt/amasc01/releases` (default 3) |
| `--report[=FILE]` | print and save installation report (see below) |
| `-h`, `--help` | show help |

### Installation report

`--report` prints a report at the end of the installation and saves it to
`/opt/amasc01/reports/install-<hostname>-<time>.txt` (or to `FILE` with `--report=FILE`):

```
AMASC01 installation report
===========================
Date:          2026-10-29T01:24:18+00:00
Hostname:      amasc01-xyz
Model:         Raspberry Pi 4 Model B Rev 1.5
Serial:        10000000abcdef01
OS:            Debian GNU/Linux 12 (bookworm)
Kernel:        6.6.51+rpt-rpi-v8 (aarch64)
Release:       v1.2.0 (<commit>)
Board variant: AMRPI4HAT01A
Reboot needed: no

Network interfaces:
  INTERFACE    MAC                 STATE    IPv4
  eth0         dc:a6:32:00:00:01   up       192.168.1.20/24
  wlan0        dc:a6:32:00:00:02   down     -

Services:
  thermal-control.service    enabled=enabled   active=active
  netact-led.service         enabled=enabled   active=active
  reverse-ssh.service        enabled=enabled   active=active

Reverse SSH:   port 48685, key ssh-ed25519 AAAA...
```

### What the installer does

Everything is installed system-wide as root, nothing goes into user home directories. Services run as root
(I2C/PWM/GPIO access). The CLI `thermal-control-cli` is usable by any user (the control socket is world-writable).

| Path | Content |
|---|---|
| `/opt/amasc01/releases/<version>/` | installed releases |
| `/opt/amasc01/current` | symlink to the active release |
| `/opt/amasc01/reports/` | installation reports (`--report`) |
| `/etc/systemd/system/*.service` | systemd units (point to `/opt/amasc01/current`) |
| `/amasc01.env` | machine-specific config, never overwritten |
| `/usr/local/bin/thermal-control-cli` | CLI |
| `/var/log/thermal_control.log` | daemon log (warnings and errors) |

Steps:


- installs `python3-smbus2` (apt, pip fallback)
- copies the release to `/opt/amasc01/releases/<version>` and switches `/opt/amasc01/current` to it
- updates the `CAMERA_SUPERVISOR` block in `/boot/firmware/config.txt` (only if changed → prints reboot notice, backup in `config.txt.amasc01.bak`)
- creates `/amasc01.env` if missing – **never overwritten**, put `BOARD_VARIANT` and any overrides
  (`TARGET_TEMP`, `COOLING_MIN`, …) there; values in it override `Environment=` in the unit
- installs units into `/etc/systemd/system` (replaces old units created by `systemctl link` from a git checkout),
  enables and restarts them
- `reverse-ssh`: keeps the already assigned port on upgrade
- links CLI as `thermal-control-cli`

### Rollback

```bash
ls /opt/amasc01/releases
sudo /opt/amasc01/releases/<version>/setup.sh
```
