#!/bin/bash
set -e

echo "Installing AllSky Camera Thermal Control System..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Get the absolute path to the service file
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_FILE="${SCRIPT_DIR}/thermal-control.service"

# Install dependencies
echo "Installing Python dependencies..."
pip3 install smbus2 --break-system-packages

# Create log directory
mkdir -p /var/log
touch /var/log/thermal_control.log
chmod 644 /var/log/thermal_control.log

# Link systemd service file
echo "Linking systemd service..."
systemctl link "${SERVICE_FILE}"

# Reload systemd
systemctl daemon-reload

# Enable service
systemctl enable thermal-control.service

echo ""
echo "Installation complete!"
echo ""
echo "Service file linked from: ${SERVICE_FILE}"
echo ""
echo "To start the service:"
echo "  sudo systemctl start thermal-control"
echo ""
echo "To check status:"
echo "  sudo systemctl status thermal-control"
echo ""
echo "To view logs:"
echo "  sudo journalctl -u thermal-control -f"
echo "  or"
echo "  sudo tail -f /var/log/thermal_control.log"
echo ""
echo "Note: Edit ${SERVICE_FILE} to change GPIO pin or other parameters"
