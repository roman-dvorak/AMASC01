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
DOME_TYPE = 'SHT40'

# BODY - Camera body with fan (BME280)
BODY_BUS = 1
BODY_ADDR = 0x76
BODY_TYPE = 'BME280'

# ENVI - Environment sensor, no actuator (SHT31)
ENVI_BUS = 1
ENVI_ADDR = 0x44
ENVI_TYPE = 'SHT40'

# PWM Configuration
PWM_HEATER = 0  # PWM0 for DOME heating
PWM_FAN = 1     # PWM1 for BODY fan
PWM_HEATER_INVERTED = False  # If True, 100% = OFF, 0% = ON
PWM_FAN_INVERTED = False     # If True, 100% = OFF, 0% = ON

# PID Parameters
KP = 10.0  # Proportional gain
KI = 0.5   # Integral gain
KD = 2.0   # Derivative gain

# Safety limits
MAX_TEMP = 70.0  # Maximum safe temperature
MIN_TEMP = -20.0  # Minimum valid temperature
MAX_CONSECUTIVE_ERRORS = 5
SENSOR_TIMEOUT = 10  # seconds

# Failsafe mode - values to use when sensors fail
FAILSAFE_HEATER_PWM = 0.0      # Heater OFF for safety
FAILSAFE_FAN_PWM = 100.0       # Fan FULL for cooling
FAILSAFE_CPU_FAN_STATE = True  # CPU fan ON for safety

# Socket configuration
SOCKET_PATH = "/var/run/thermal-control.sock"
STATUS_PATH = "/var/run/thermal-control-status.json"

# Available sensor types:
#   'SHT31'  - SHT31 temperature and humidity sensor
#   'SHT40'  - SHT40 temperature and humidity sensor (improved version)
#   'BME280' - BME280 temperature, humidity, and pressure sensor
#
# To use SHT40 for DOME and/or ENVI sensors, change DOME_TYPE and/or ENVI_TYPE to 'SHT40'
# The controller will automatically instantiate the correct sensor class based on the type.
