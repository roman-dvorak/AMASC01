#!/bin/bash
# Download an AMASC01 release from GitHub and install it.
#
# Latest release:
#   curl -fsSL https://github.com/roman-dvorak/AMASC01/releases/latest/download/get.sh | sudo bash
# Specific version / extra options (passed to install.sh):
#   curl -fsSL https://github.com/roman-dvorak/AMASC01/releases/latest/download/get.sh | sudo bash -s -- --version v1.2.0 --with-reverse-ssh
set -euo pipefail

REPO="${AMASC01_REPO:-roman-dvorak/AMASC01}"
VERSION=""
INSTALL_ARGS=()

usage() {
    cat <<USAGE
Download an AMASC01 release from GitHub ($REPO) and install it.

Usage: get.sh [--version vX.Y.Z] [install options]

Options:
  -h, --help           show this help
  --version TAG        release to install (default: latest)

Install options (passed to install.sh):
  --with-reverse-ssh   also install reverse-ssh.service (keeps existing port)
  --no-restart         do not (re)start services
  --keep N             number of releases to keep (default 3)

Example:
  curl -fsSL https://github.com/$REPO/releases/latest/download/get.sh | sudo bash -s -- --help
USAGE
}

while [ $# -gt 0 ]; do
    case "$1" in
        -h|--help) usage; exit 0 ;;
        --version) VERSION="${2:?--version needs a value}"; shift 2 ;;
        *) INSTALL_ARGS+=("$1"); shift ;;
    esac
done

if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo)" >&2
    exit 1
fi

if [ -z "$VERSION" ]; then
    # /releases/latest redirects to /releases/tag/<version>
    LATEST_URL="$(curl -fsSLI -o /dev/null -w '%{url_effective}' "https://github.com/$REPO/releases/latest")"
    VERSION="${LATEST_URL##*/}"
    if [ -z "$VERSION" ] || [ "$VERSION" = "latest" ]; then
        echo "ERROR: could not determine latest release of $REPO" >&2
        exit 1
    fi
fi

NAME="amasc01-${VERSION}"
BASE_URL="https://github.com/$REPO/releases/download/$VERSION"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "Downloading $NAME from $REPO..."
curl -fSL --retry 3 -o "$TMP/$NAME.tar.gz" "$BASE_URL/$NAME.tar.gz"
curl -fsSL --retry 3 -o "$TMP/$NAME.tar.gz.sha256" "$BASE_URL/$NAME.tar.gz.sha256"

echo "Verifying checksum..."
(cd "$TMP" && sha256sum -c "$NAME.tar.gz.sha256")

tar -C "$TMP" -xzf "$TMP/$NAME.tar.gz"
"$TMP/$NAME/install.sh" "${INSTALL_ARGS[@]}"
