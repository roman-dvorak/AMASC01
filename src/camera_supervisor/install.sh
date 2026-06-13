#!/bin/bash
set -e

echo "Installing AllSky Camera Thermal Control System..."

# Must be root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo)"
    exit 1
fi

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THERM_SERVICE_FILE="${SCRIPT_DIR}/thermal-control.service"
NET_SERVICE_FILE="${SCRIPT_DIR}/netact-led.service"

CONFIG_FILE="/boot/firmware/config.txt"

#############################################
# Check config.txt path
#############################################
if [ ! -f "$CONFIG_FILE" ]; then
    echo "ERROR: Expected config.txt at /boot/firmware/config.txt"
    echo "File not found: $CONFIG_FILE"
    exit 1
fi

echo "Using config file: $CONFIG_FILE"

#############################################
# Update CAMERA_SUPERVISOR block in config.txt
#############################################

# Pokud blok existuje, smaž ho
if grep -q "# CAMERA_SUPERVISOR START" "$CONFIG_FILE"; then
    echo "Removing existing CAMERA_SUPERVISOR block..."
    sed -i '/# CAMERA_SUPERVISOR START/,/# CAMERA_SUPERVISOR END/d' "$CONFIG_FILE"
else
    echo "No existing CAMERA_SUPERVISOR block found, adding new one..."
fi

# Přidej nový blok na konec
cat >> "$CONFIG_FILE" << 'EOF'

# CAMERA_SUPERVISOR START
dtparam=i2c_arm=on
dtoverlay=i2c-rtc,pcf8563,addr=0x51

dtoverlay=gpio-led,gpio=22,label=sdact,trigger=mmc0,active_low=0
dtoverlay=gpio-led,gpio=27,label=netact,active_low=0
dtoverlay=pwm-2chan,pin=12,func=4,pin2=13,func2=4
# CAMERA_SUPERVISOR END
EOF


#############################################

#############################################
# Create hardware configuration .env file
#############################################
HW_ENV_FILE="/amasc01.env"
if [ ! -f "$HW_ENV_FILE" ]; then
    echo "Creating hardware configuration file: $HW_ENV_FILE"
    cat > "$HW_ENV_FILE" << 'ENVEOF'
# AstroMeters hardware configuration
# Board variant: AMRPI4HAT01A, AMRPI4HAT01B, AMRPI4HAT01C, AMRPI4HAT01D
# AMRPI4HAT01D: PWM channels for heater and fan are swapped
BOARD_VARIANT=AMRPI4HAT01A
ENVEOF
else
    echo "Hardware configuration file already exists: $HW_ENV_FILE"
fi

# Install Python dependencies
#############################################
echo "Installing Python dependencies..."
pip3 install smbus2 --break-system-packages

#############################################
# Create log file
#############################################
mkdir -p /var/log
touch /var/log/thermal_control.log
chmod 644 /var/log/thermal_control.log

#############################################
# Link BOTH systemd services
#############################################
echo "Linking systemd services..."

if [ ! -f "$THERM_SERVICE_FILE" ]; then
    echo "ERROR: thermal-control.service not found at $THERM_SERVICE_FILE"
    exit 1
fi

if [ ! -f "$NET_SERVICE_FILE" ]; then
    echo "ERROR: netact-led.service not found at $NET_SERVICE_FILE"
    exit 1
fi

systemctl link "$THERM_SERVICE_FILE"
systemctl link "$NET_SERVICE_FILE"

systemctl daemon-reload

#############################################
# Enable services
#############################################
echo "Enabling systemd services..."
systemctl enable thermal-control.service
systemctl enable netact-led.service

#############################################
# Final info
#############################################
echo ""
echo "Installation complete!"
echo ""
echo "Services installed:"
echo "  thermal-control.service"
echo "  netact-led.service"
echo ""
echo "To start them now:"
echo "  sudo systemctl start thermal-control"
echo "  sudo systemctl start netact-led"
echo ""
echo "To check status:"
echo "  sudo systemctl status thermal-control"
echo "  sudo systemctl status netact-led"
echo ""
echo "Overlay configuration stored in:"
echo "  $CONFIG_FILE"
echo ""
echo "Between:"
echo "  # CAMERA_SUPERVISOR START"
echo "  # CAMERA_SUPERVISOR END"
echo ""
