#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEMPLATE="$SCRIPT_DIR/reverse-ssh.service.template"
SERVICE="$SCRIPT_DIR/reverse-ssh.service"
SERVICE_NAME="reverse-ssh.service"

if [ ! -f "$TEMPLATE" ]; then
    echo "Error: Template $TEMPLATE not found" >&2
    exit 1
fi

# Generate random port in range 10000-65000
PORT=$(shuf -i 10000-65000 -n 1)

# Generate service file from template
sed "s/{{PORT}}/$PORT/g" "$TEMPLATE" > "$SERVICE"

# Install service
sudo cp "$SERVICE" "/etc/systemd/system/$SERVICE_NAME"
sudo systemctl daemon-reload
sudo systemctl enable --now "$SERVICE_NAME"

echo ""
echo "Installed $SERVICE_NAME with port $PORT"
echo ""
echo "# Add this to your ~/.ssh/config:"
echo "Host $(hostname)"
echo "  HostName localhost"
echo "  User astrometers"
echo "  Port $PORT"
echo "  #ProxyJump tunnel.astrometers.eu"
