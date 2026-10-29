#!/bin/bash
# Install AMASC01 camera_supervisor release on the camera (Raspberry Pi).
# Runs from an extracted release tarball (see release/build.sh, release/get.sh).
#
# Layout:
#   /opt/amasc01/releases/<version>/   installed releases
#   /opt/amasc01/current               -> symlink to the active release
#   /etc/systemd/system/*.service      units pointing to /opt/amasc01/current
#   /amasc01.env                       machine-specific config (never overwritten)
#
# Usage: sudo ./install.sh [options]
#
# Options:
#   -h, --help           show this help
#   --with-reverse-ssh   also install reverse-ssh.service (keeps existing port)
#   --no-restart         do not (re)start services
#   --keep N             number of releases to keep (default 3)
#
# Rollback: sudo /opt/amasc01/releases/<old_version>/install.sh
set -euo pipefail

PREFIX="/opt/amasc01"
CONFIG_FILE="/boot/firmware/config.txt"
HW_ENV_FILE="/amasc01.env"
LOG_FILE="/var/log/thermal_control.log"
CLI_LINK="/usr/local/bin/thermal-control-cli"
UNIT_DIR="/etc/systemd/system"
UNITS=(thermal-control.service netact-led.service)

WITH_REVERSE_SSH=0
RESTART=1
KEEP=3

while [ $# -gt 0 ]; do
    case "$1" in
        --with-reverse-ssh) WITH_REVERSE_SSH=1; shift ;;
        --no-restart) RESTART=0; shift ;;
        --keep) KEEP="${2:?--keep needs a value}"; shift 2 ;;
        -h|--help) sed -n '2,/^set -/s/^# \{0,1\}//p' "$0"; exit 0 ;;
        *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo)" >&2
    exit 1
fi

PKG_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
VERSION="$(cat "$PKG_DIR/VERSION")"
TARGET="$PREFIX/releases/$VERSION"
REBOOT_NEEDED=0

echo "Installing AMASC01 camera supervisor $VERSION..."

#############################################
# Python dependencies
#############################################
if ! python3 -c 'import smbus2' 2>/dev/null; then
    echo "Installing python3-smbus2..."
    if ! { apt-get update -q && apt-get install -y -q python3-smbus2; }; then
        echo "apt failed, falling back to pip..."
        pip3 install smbus2 --break-system-packages
    fi
fi

#############################################
# Copy release into /opt/amasc01/releases/<version>
#############################################
if [ "$PKG_DIR" != "$TARGET" ]; then
    mkdir -p "$PREFIX/releases"
    rm -rf "$TARGET"
    cp -a "$PKG_DIR" "$TARGET"
fi

# Atomic switch of the 'current' symlink
ln -sfn "releases/$VERSION" "$PREFIX/current.new"
mv -T "$PREFIX/current.new" "$PREFIX/current"
echo "Active release: $(readlink "$PREFIX/current")"

#############################################
# CAMERA_SUPERVISOR block in config.txt
#############################################
if [ -f "$CONFIG_FILE" ]; then
    NEW_BLOCK="$(printf '# CAMERA_SUPERVISOR START\n%s\n# CAMERA_SUPERVISOR END' \
        "$(cat "$TARGET/camera_supervisor/config.txt.fragment")")"
    OLD_BLOCK="$(sed -n '/# CAMERA_SUPERVISOR START/,/# CAMERA_SUPERVISOR END/p' "$CONFIG_FILE")"
    if [ "$NEW_BLOCK" != "$OLD_BLOCK" ]; then
        echo "Updating CAMERA_SUPERVISOR block in $CONFIG_FILE..."
        cp "$CONFIG_FILE" "$CONFIG_FILE.amasc01.bak"
        sed -i '/# CAMERA_SUPERVISOR START/,/# CAMERA_SUPERVISOR END/d' "$CONFIG_FILE"
        printf '\n%s\n' "$NEW_BLOCK" >> "$CONFIG_FILE"
        REBOOT_NEEDED=1
    else
        echo "$CONFIG_FILE is up to date"
    fi
else
    echo "WARNING: $CONFIG_FILE not found, skipping device tree overlays"
fi

#############################################
# Machine-specific configuration
#############################################
if [ ! -f "$HW_ENV_FILE" ]; then
    echo "Creating $HW_ENV_FILE (edit BOARD_VARIANT!)"
    cp "$TARGET/camera_supervisor/amasc01.env.example" "$HW_ENV_FILE"
fi

touch "$LOG_FILE"
chmod 644 "$LOG_FILE"

#############################################
# systemd units
#############################################
install_unit() {
    local unit="$1" src="$2"
    # Units installed by 'systemctl link' (old git-checkout install) are symlinks
    # into the repo - remove them so we don't write through into the checkout.
    if [ -L "$UNIT_DIR/$unit" ]; then
        echo "Replacing linked unit $unit"
        systemctl disable "$unit" 2>/dev/null || true
        rm -f "$UNIT_DIR/$unit"
    fi
    install -m 644 "$src" "$UNIT_DIR/$unit"
}

for unit in "${UNITS[@]}"; do
    install_unit "$unit" "$TARGET/systemd/$unit"
done

if [ "$WITH_REVERSE_SSH" -eq 1 ]; then
    # Keep the already assigned port, the tunnel server config depends on it
    PORT="$(grep -oP '127\.0\.0\.1:\K[0-9]+' "$UNIT_DIR/reverse-ssh.service" 2>/dev/null || true)"
    PORT="${PORT:-$(shuf -i 10000-65000 -n 1)}"
    sed "s/{{PORT}}/$PORT/g" "$TARGET/systemd/reverse-ssh.service.template" > "$TARGET/systemd/reverse-ssh.service"
    install_unit reverse-ssh.service "$TARGET/systemd/reverse-ssh.service"
    UNITS+=(reverse-ssh.service)
    if [ ! -f /root/.ssh/tunnel_key ]; then
        echo "WARNING: /root/.ssh/tunnel_key missing, see systemd/README.md"
    fi
fi

systemctl daemon-reload
systemctl enable "${UNITS[@]}"

ln -sfn "$PREFIX/current/camera_supervisor/thermal_control_cli.py" "$CLI_LINK"

if [ "$RESTART" -eq 1 ]; then
    echo "Restarting services..."
    for unit in "${UNITS[@]}"; do
        systemctl restart "$unit" || echo "WARNING: failed to restart $unit"
    done
fi

#############################################
# Remove old releases
#############################################
CURRENT="$(readlink "$PREFIX/current")"
# shellcheck disable=SC2012
ls -1dt "$PREFIX"/releases/*/ 2>/dev/null | tail -n +"$((KEEP + 1))" | while read -r dir; do
    dir="${dir%/}"
    [ "releases/$(basename "$dir")" = "$CURRENT" ] && continue
    echo "Removing old release $(basename "$dir")"
    rm -rf "$dir"
done

#############################################
# Summary
#############################################
echo ""
echo "AMASC01 camera supervisor $VERSION installed."
echo "  Code:     $PREFIX/current/camera_supervisor"
echo "  Config:   $HW_ENV_FILE (overrides Environment= in units)"
echo "  Services: ${UNITS[*]}"
echo "  CLI:      thermal-control-cli status"
if [ "$REBOOT_NEEDED" -eq 1 ]; then
    echo ""
    echo "!!! $CONFIG_FILE changed - reboot required (backup: $CONFIG_FILE.amasc01.bak)"
fi
