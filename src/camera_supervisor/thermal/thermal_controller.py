"""
Main thermal controller class
"""
import time
import logging
import json
import math

from . import config
from .sensors import SHT31Sensor, BME280Sensor
from .controllers import PWMController, GPIOController, PIDController

logger = logging.getLogger(__name__)


def calculate_dew_point(temperature_c, humidity_percent):
    """Calculate dew point in °C.

    Uses the Magnus formula. Returns None if inputs are missing or invalid.
    """
    if temperature_c is None or humidity_percent is None:
        return None
    if humidity_percent <= 0.0 or humidity_percent > 100.0:
        return None

    a = 17.62
    b = 243.12  # °C
    gamma = (a * temperature_c / (b + temperature_c)) + math.log(humidity_percent / 100.0)
    return (b * gamma) / (a - gamma)


class ThermalController:
    """Main thermal control system"""

    def __init__(self, cpu_fan_gpio=None, cpu_fan_threshold=config.CPU_FAN_THRESHOLD):
        self.running = False
        self.dome = SHT31Sensor(config.DOME_BUS, config.DOME_ADDR)
        self.body = BME280Sensor(config.BODY_BUS, config.BODY_ADDR)
        self.envi = SHT31Sensor(config.ENVI_BUS, config.ENVI_ADDR)
        self.heater = PWMController(config.PWM_HEATER)
        self.fan = PWMController(config.PWM_FAN)
        self.cpu_fan = GPIOController(cpu_fan_gpio) if cpu_fan_gpio else None
        self.cpu_fan_threshold = cpu_fan_threshold
        self.pid = PIDController(config.KP, config.KI, config.KD, config.TARGET_TEMP)
        self.error_count = 0
        self.fan_override = None  # Manual fan control override

    def get_status(self):
        """Get current system status"""
        dome_temp = self.dome.last_valid_temp
        body_temp = self.body.last_valid_temp
        envi_temp = self.envi.last_valid_temp

        dome_humidity = getattr(self.dome, "last_valid_humidity", None)
        body_humidity = getattr(self.body, "last_valid_humidity", None)
        envi_humidity = getattr(self.envi, "last_valid_humidity", None)

        body_pressure = getattr(self.body, "last_valid_pressure", None)

        return {
            "dome_temp": dome_temp,
            "body_temp": body_temp,
            "envi_temp": envi_temp,
            "dome_humidity": dome_humidity,
            "body_humidity": body_humidity,
            "envi_humidity": envi_humidity,
            "body_pressure": body_pressure,
            "dome_dew_point": calculate_dew_point(dome_temp, dome_humidity),
            "body_dew_point": calculate_dew_point(body_temp, body_humidity),
            "envi_dew_point": calculate_dew_point(envi_temp, envi_humidity),
            "heater_pwm": getattr(self, 'last_heater_pwm', 0),
            "fan_pwm": getattr(self, 'last_fan_pwm', 0),
            "cpu_fan_state": getattr(self, 'last_cpu_fan_state', False),
            "target_temp": config.TARGET_TEMP,
            "cooling_min": config.COOLING_TEMP_MIN,
            "cooling_max": config.COOLING_TEMP_MAX,
            "fan_override": self.fan_override,
            "error_count": self.error_count,
        }

    def set_target_temperature(self, temp):
        """Set target temperature"""

        config.TARGET_TEMP = float(temp)
        self.pid.target = config.TARGET_TEMP
        logger.info(f"Target temperature changed to {config.TARGET_TEMP}°C")

    def set_cooling_min(self, temp):
        """Set cooling minimum temperature"""

        config.COOLING_TEMP_MIN = float(temp)
        logger.info(f"Cooling min temperature changed to {config.COOLING_TEMP_MIN}°C")

    def set_cooling_max(self, temp):
        """Set cooling maximum temperature"""

        config.COOLING_TEMP_MAX = float(temp)
        logger.info(f"Cooling max temperature changed to {config.COOLING_TEMP_MAX}°C")

    def setup(self):
        """Initialize all components"""
        logger.info("Initializing thermal control system...")

        success = True
        success &= self.dome.connect()
        success &= self.body.connect()
        success &= self.envi.connect()
        success &= self.heater.setup()
        success &= self.fan.setup()

        if self.cpu_fan:
            success &= self.cpu_fan.setup()

        if not success:
            logger.error("Failed to initialize all components")
            return False

        logger.info("All components initialized successfully")
        return True

    def safe_shutdown(self):
        """Safely shutdown all outputs"""
        logger.info("Performing safe shutdown...")
        self.heater.disable()
        self.fan.disable()
        if self.cpu_fan:
            self.cpu_fan.disable()
        self.dome.close()
        self.body.close()
        self.envi.close()
        logger.info("Safe shutdown complete")

    def calculate_fan_speed(self, temperature):
        """Calculate fan speed based on temperature (linear mapping)"""
        if temperature <= config.COOLING_TEMP_MIN:
            return 0.0
        elif temperature >= config.COOLING_TEMP_MAX:
            return 100.0
        else:
            # Linear interpolation between min and max
            ratio = (temperature - config.COOLING_TEMP_MIN) / (config.COOLING_TEMP_MAX - config.COOLING_TEMP_MIN)
            return ratio * 100.0

    def run(self):
        """Main control loop"""
        self.running = True
        logger.info("Starting thermal control loop...")

        try:
            while self.running:
                # Read DOME sensor (for heating control)
                dome_temp = self.dome.read_temperature()

                # Read BODY sensor (for cooling control)
                body_temp = self.body.read_temperature()

                # Read ENVI sensor (environment monitoring only)
                self.envi.read_temperature()

                # Check sensor health
                if dome_temp is None:
                    self.error_count += 1
                    logger.warning(f"DOME read failed (errors: {self.error_count}/{config.MAX_CONSECUTIVE_ERRORS})")
                else:
                    self.error_count = 0

                # Safety check: shutdown if too many errors
                if self.error_count >= config.MAX_CONSECUTIVE_ERRORS:
                    logger.error("Too many consecutive sensor errors - shutting down for safety")
                    self.safe_shutdown()
                    return False

                # Control heating based on DOME
                if dome_temp is not None:
                    heater_pwm = self.pid.update(dome_temp)
                    self.heater.set_duty_cycle(heater_pwm)
                    self.last_heater_pwm = heater_pwm
                    logger.info(f"DOME: {dome_temp:.2f}°C | Heater: {heater_pwm:.1f}%")
                else:
                    # If sensor fails, turn off heating for safety
                    self.heater.set_duty_cycle(0)
                    logger.warning("Heater disabled due to sensor failure")

                # Control cooling based on BODY
                if body_temp is not None:
                    if self.fan_override is not None:
                        fan_pwm = self.fan_override
                    else:
                        fan_pwm = self.calculate_fan_speed(body_temp)
                    self.fan.set_duty_cycle(fan_pwm)
                    self.last_fan_pwm = fan_pwm

                    # Control CPU fan (on/off based on threshold)
                    if self.cpu_fan:
                        cpu_fan_state = body_temp >= self.cpu_fan_threshold
                        self.cpu_fan.set_state(cpu_fan_state)
                        self.last_cpu_fan_state = cpu_fan_state
                        logger.info(
                            f"BODY: {body_temp:.2f}°C | Fan: {fan_pwm:.1f}% | CPU Fan: {'ON' if cpu_fan_state else 'OFF'}"
                        )
                    else:
                        logger.info(f"BODY: {body_temp:.2f}°C | Fan: {fan_pwm:.1f}%")
                else:
                    # If BODY fails, set fan to 50% and CPU fan ON for safety
                    self.fan.set_duty_cycle(50)
                    if self.cpu_fan:
                        self.cpu_fan.set_state(True)
                    logger.warning("Fan set to 50% and CPU fan ON due to sensor failure")

                # Save status to file
                try:
                    with open(config.STATUS_PATH, "w") as f:
                        json.dump(self.get_status(), f, indent=2)
                except Exception:
                    # Avoid crashing the control loop on status write issues
                    pass

                # Sleep before next iteration
                time.sleep(1.0)

        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
            return True
        except Exception as e:
            logger.error(f"Unexpected error in control loop: {e}")
            return False
        finally:
            self.safe_shutdown()
