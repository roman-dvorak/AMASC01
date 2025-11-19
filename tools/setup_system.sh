#!/bin/bash
# System setup script for AMASC01 AllSky Camera
# This script installs dependencies and configures the system

set -e

echo "=================================="
echo "AMASC01 System Setup"
echo "=================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

echo "[1/5] Updating package list..."
apt-get update

echo ""
echo "[2/5] Installing system dependencies..."
apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    libusb-1.0-0-dev \
    git \
    curl

echo ""
echo "[3/5] Installing Python packages..."
pip3 install --upgrade pip
pip3 install numpy astropy pyyaml opencv-python

echo ""
echo "[4/5] Creating directory structure..."
mkdir -p /var/amasc01/images
mkdir -p /var/amasc01/calibration
mkdir -p /var/log/amasc01
mkdir -p /etc/amasc01

# Set permissions
chmod 755 /var/amasc01
chmod 755 /var/amasc01/images
chmod 755 /var/amasc01/calibration
chmod 755 /var/log/amasc01

echo ""
echo "[5/5] Setting up udev rules..."
cat > /etc/udev/rules.d/99-amasc01.rules << 'EOF'
# AMASC01 AllSky Camera
# Replace xxxx and yyyy with your camera's vendor and product ID
# Find these values using: lsusb
SUBSYSTEM=="usb", ATTRS{idVendor}=="xxxx", ATTRS{idProduct}=="yyyy", MODE="0666", GROUP="plugdev"
EOF

udevadm control --reload-rules
udevadm trigger

echo ""
echo "=================================="
echo "Setup completed successfully!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Copy config/camera_config.example.yaml to config/camera_config.yaml"
echo "2. Edit the configuration file with your settings"
echo "3. Update udev rules in /etc/udev/rules.d/99-amasc01.rules with your camera IDs"
echo "4. Test camera connection: python3 scripts/test_camera.py"
echo ""
echo "Optional:"
echo "- Install systemd service: cp tools/amasc01.service /etc/systemd/system/"
echo "- Enable service: systemctl enable amasc01"
echo ""
