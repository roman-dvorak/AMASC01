#!/bin/bash
# Build release tarball of camera_supervisor + systemd units.
#
# Usage: release/build.sh <version> [output_dir]
#   version     e.g. v1.2.0 (git tag)
#   output_dir  default: dist/
#
# Produces:
#   <output_dir>/amasc01-<version>.tar.gz
#   <output_dir>/amasc01-<version>.tar.gz.sha256
#   <output_dir>/install.sh
set -euo pipefail

usage() { sed -n '2,/^set -/s/^# \{0,1\}//p' "$0"; }
case "${1:-}" in
    -h|--help) usage; exit 0 ;;
    "") usage >&2; exit 1 ;;
esac
VERSION="$1"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$(mkdir -p "${2:-$REPO_ROOT/dist}" && cd "${2:-$REPO_ROOT/dist}" && pwd)"

SRC="$REPO_ROOT/src/camera_supervisor"
NAME="amasc01-${VERSION}"
APP_DIR="/opt/amasc01/current"
# Path used in thermal-control.service for git-checkout installs; rewritten for releases
DEV_PATH="/home/astrometers/repos/AMASC01/src/camera_supervisor"

STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
PKG="$STAGE/$NAME"
mkdir -p "$PKG/camera_supervisor" "$PKG/systemd"

#############################################
# Python code
#############################################
cp -r "$SRC/thermal" "$PKG/camera_supervisor/"
cp "$SRC/thermal_control.py" "$SRC/thermal_control_cli.py" "$SRC/README.md" \
   "$SRC/config.txt.fragment" "$SRC/amasc01.env.example" \
   "$PKG/camera_supervisor/"
find "$PKG" -name '__pycache__' -type d -prune -exec rm -rf {} +
chmod -R u=rwX,go=rX "$PKG"
chmod 755 "$PKG/camera_supervisor/thermal_control.py" "$PKG/camera_supervisor/thermal_control_cli.py"

#############################################
# systemd units (point them to /opt/amasc01/current)
#############################################
if ! grep -q "$DEV_PATH" "$SRC/thermal-control.service"; then
    echo "ERROR: $DEV_PATH not found in thermal-control.service" >&2
    exit 1
fi
sed "s|$DEV_PATH|$APP_DIR/camera_supervisor|g" "$SRC/thermal-control.service" \
    > "$PKG/systemd/thermal-control.service"
cp "$SRC/netact-led.service" "$PKG/systemd/"
cp "$REPO_ROOT/systemd/reverse-ssh.service.template" "$PKG/systemd/"

#############################################
# Installer + metadata
#############################################
cp "$REPO_ROOT/release/setup.sh" "$PKG/setup.sh"
chmod 755 "$PKG/setup.sh"
echo "$VERSION" > "$PKG/VERSION"
git -C "$REPO_ROOT" rev-parse HEAD > "$PKG/COMMIT" 2>/dev/null || true

#############################################
# Archive
#############################################
tar -C "$STAGE" --owner=0 --group=0 -czf "$OUT_DIR/$NAME.tar.gz" "$NAME"
(cd "$OUT_DIR" && sha256sum "$NAME.tar.gz" > "$NAME.tar.gz.sha256")
cp "$REPO_ROOT/release/install.sh" "$OUT_DIR/install.sh"

echo "Built:"
echo "  $OUT_DIR/$NAME.tar.gz"
echo "  $OUT_DIR/$NAME.tar.gz.sha256"
echo "  $OUT_DIR/install.sh"
