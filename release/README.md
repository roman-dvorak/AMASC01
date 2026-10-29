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
   - `get.sh` – download & install bootstrap

   Assets for an existing tag can be rebuilt via *Actions → Release → Run workflow*.

Local build (for testing): `release/build.sh v1.2.0-dev dist`

## Installing on the camera

Latest release:

```bash
curl -fsSL https://github.com/roman-dvorak/AMASC01/releases/latest/download/get.sh | sudo bash
```

Specific version, including the reverse SSH tunnel:

```bash
curl -fsSL https://github.com/roman-dvorak/AMASC01/releases/latest/download/get.sh | sudo bash -s -- --version v1.2.0 --with-reverse-ssh
```

`install.sh` options: `--with-reverse-ssh`, `--no-restart`, `--keep N` (number of kept releases, default 3).

### What the installer does

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
sudo /opt/amasc01/releases/<version>/install.sh
```
