"""
Configuration constants for thermal control system
"""

# Target temperatures
TARGET_TEMP = 20.0  # Target temperature for DOME sensor (°C)
COOLING_TEMP_MIN = 10.0  # Temperature for 0% fan speed
COOLING_TEMP_MAX = 40.0  # Temperature for 100% fan speed
CPU_FAN_THRESHOLD = 60.0  # CPU temperature to turn on CPU fan (°C)
BODY_FAN_THRESHOLD = 35.0  # BODY temperature to turn on CPU fan (°C)

# I2C Configuration - Sensor locations
# DOME - Camera dome with heater (SHT31)
DOME_BUS = 10
DOME_ADDR = 0x44
DOME_TYPE = 'SHT31'

# BODY - Camera body with fan (BME280)
BODY_BUS = 1
BODY_ADDR = 0x76
BODY_TYPE = 'BME280'

# ENVI - Environment sensor, no actuator (SHT31)
ENVI_BUS = 1
ENVI_ADDR = 0x44
ENVI_TYPE = 'SHT31'

# PWM Configuration
PWM_HEATER = 0  # PWM0 for DOME heating
PWM_FAN = 1     # PWM1 for BODY fan

# PID Parameters
KP = 10.0  # Proportional gain
KI = 0.5   # Integral gain
KD = 2.0   # Derivative gain

# Safety limits
MAX_TEMP = 70.0  # Maximum safe temperature
MIN_TEMP = -20.0  # Minimum valid temperature
MAX_CONSECUTIVE_ERRORS = 5
SENSOR_TIMEOUT = 10  # seconds

# Socket configuration
SOCKET_PATH = "/var/run/thermal-control.sock"
STATUS_PATH = "/var/run/thermal-control-status.json"
