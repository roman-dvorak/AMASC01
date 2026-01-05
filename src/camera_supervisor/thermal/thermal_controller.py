"""
Main thermal controller class
"""
import time
import logging
import json
import math

from . import config
from .sensors import SHT31Sensor, SHT40Sensor, BME280Sensor, CPUSensor
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

    def __init__(self, cpu_fan_gpio=None, 
                 cpu_fan_threshold=config.CPU_FAN_THRESHOLD,
                 body_fan_threshold=config.BODY_FAN_THRESHOLD):
        self.running = False
        
        # Initialize sensors based on configured types
        if config.DOME_TYPE == 'SHT40':
            self.dome = SHT40Sensor(config.DOME_BUS, config.DOME_ADDR)
        else:
            self.dome = SHT31Sensor(config.DOME_BUS, config.DOME_ADDR)
            
        self.body = BME280Sensor(config.BODY_BUS, config.BODY_ADDR)
        
        if config.ENVI_TYPE == 'SHT40':
            self.envi = SHT40Sensor(config.ENVI_BUS, config.ENVI_ADDR)
        else:
            self.envi = SHT31Sensor(config.ENVI_BUS, config.ENVI_ADDR)
            
        # Initialize actuators with inverted option
        self.heater = PWMController(config.PWM_HEATER, inverted=config.PWM_HEATER_INVERTED)
        self.fan = PWMController(config.PWM_FAN, inverted=config.PWM_FAN_INVERTED)
        self.cpu_fan = GPIOController(cpu_fan_gpio) if cpu_fan_gpio else None
        self.cpu_fan_threshold = cpu_fan_threshold
        self.body_fan_threshold = body_fan_threshold
        
        # CPU fan hysteresis - 10% deadband
        self.cpu_fan_on_threshold = cpu_fan_threshold + (cpu_fan_threshold * 0.1)  # Turn ON at threshold + 10%
        self.cpu_fan_off_threshold = cpu_fan_threshold - (cpu_fan_threshold * 0.1)  # Turn OFF at threshold - 10%
        self.cpu_fan_state = False  # Track fan state for hysteresis
        self.pid = PIDController(config.KP, config.KI, config.KD, config.TARGET_TEMP)
        self.error_count = 0
        self.cpu_sensor = CPUSensor()
        self.fan_override = None  # Manual fan control override
        
        # Failsafe state tracking
        self.failsafe_mode = False
        self.dome_available = False
        self.body_available = False
        self.envi_available = False

    def enter_failsafe_mode(self):
        """Enter failsafe mode - set all outputs to safe values"""
        if not self.failsafe_mode:
            logger.warning("Entering FAILSAFE mode - sensors unavailable")
            self.failsafe_mode = True
        
        # Set outputs to failsafe values
        self.heater.set_duty_cycle(config.FAILSAFE_HEATER_PWM)
        self.fan.set_duty_cycle(config.FAILSAFE_FAN_PWM)
        if self.cpu_fan:
            self.cpu_fan.set_state(config.FAILSAFE_CPU_FAN_STATE)
        
        self.last_heater_pwm = config.FAILSAFE_HEATER_PWM
        self.last_fan_pwm = config.FAILSAFE_FAN_PWM
        self.last_cpu_fan_state = config.FAILSAFE_CPU_FAN_STATE
        
        logger.info(f"Failsafe: Heater={config.FAILSAFE_HEATER_PWM}%, "
                   f"Fan={config.FAILSAFE_FAN_PWM}%, "
                   f"CPU_Fan={'ON' if config.FAILSAFE_CPU_FAN_STATE else 'OFF'}")

    def exit_failsafe_mode(self):
        """Exit failsafe mode - return to normal operation"""
        if self.failsafe_mode:
            logger.info("Exiting FAILSAFE mode - sensors recovered")
            self.failsafe_mode = False
            self.pid.reset()  # Reset PID to avoid integral windup

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
            "cpu_temp": getattr(self, 'last_cpu_temp', None),
            "cpu_fan_threshold": self.cpu_fan_threshold,
            "body_fan_threshold": self.body_fan_threshold,
            "failsafe_mode": self.failsafe_mode,
            "dome_available": self.dome_available,
            "body_available": self.body_available,
            "envi_available": self.envi_available,
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

        # Try to connect to all sensors, but don't fail if some are unavailable
        self.dome_available = self.dome.connect()
        if not self.dome_available:
            logger.warning("DOME sensor not available - will run in failsafe mode")
            
        self.body_available = self.body.connect()
        if not self.body_available:
            logger.warning("BODY sensor not available - will run in failsafe mode")
            
        self.envi_available = self.envi.connect()
        if not self.envi_available:
            logger.warning("ENVI sensor not available - monitoring only")

        # Actuators must work
        heater_ok = self.heater.setup()
        fan_ok = self.fan.setup()
        
        cpu_fan_ok = True
        if self.cpu_fan:
            cpu_fan_ok = self.cpu_fan.setup()

        if not (heater_ok and fan_ok and cpu_fan_ok):
            logger.error("Failed to initialize actuators - cannot continue")
            return False

        # If no sensors available, enter failsafe immediately
        if not (self.dome_available or self.body_available):
            logger.warning("No critical sensors available - starting in failsafe mode")
            self.enter_failsafe_mode()

        logger.info("Initialization complete")
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
                # Read sensors
                dome_temp = None
                body_temp = None
                
                if self.dome_available:
                    dome_temp = self.dome.read_temperature()
                    if dome_temp is None:
                        self.error_count += 1
                        logger.warning(f"DOME read failed (errors: {self.error_count}/{config.MAX_CONSECUTIVE_ERRORS})")
                        if self.error_count >= config.MAX_CONSECUTIVE_ERRORS:
                            logger.error("DOME sensor failed - marking as unavailable")
                            self.dome_available = False
                            self.error_count = 0
                    else:
                        self.error_count = 0

                if self.body_available:
                    body_temp = self.body.read_temperature()
                    if body_temp is None:
                        logger.warning("BODY sensor read failed - marking as unavailable")
                        self.body_available = False

                # Read ENVI sensor (environment monitoring only)
                if self.envi_available:
                    envi_temp = self.envi.read_temperature()
                    if envi_temp is None:
                        logger.warning("ENVI sensor read failed")
                        # Don't mark as unavailable since it's monitoring only

                # Read CPU temperature
                cpu_temp = self.cpu_sensor.read_temperature()
                self.last_cpu_temp = cpu_temp

                # Check if we should be in failsafe mode
                if not self.dome_available and not self.body_available:
                    self.enter_failsafe_mode()
                else:
                    # Try to exit failsafe if sensors recovered
                    if self.failsafe_mode and (self.dome_available or self.body_available):
                        self.exit_failsafe_mode()

                # Control heating based on DOME
                if self.failsafe_mode:
                    # In failsafe, outputs already set
                    pass
                elif dome_temp is not None:
                    heater_pwm = self.pid.update(dome_temp)
                    self.heater.set_duty_cycle(heater_pwm)
                    self.last_heater_pwm = heater_pwm
                    logger.info(f"DOME: {dome_temp:.2f}°C | Heater: {heater_pwm:.1f}%")
                else:
                    # If DOME sensor unavailable, use failsafe heater value
                    self.heater.set_duty_cycle(config.FAILSAFE_HEATER_PWM)
                    self.last_heater_pwm = config.FAILSAFE_HEATER_PWM
                    logger.warning(f"Heater set to failsafe {config.FAILSAFE_HEATER_PWM}% (DOME unavailable)")

                # Control cooling based on BODY
                if self.failsafe_mode:
                    # In failsafe, outputs already set
                    pass
                elif body_temp is not None:
                    if self.fan_override is not None:
                        fan_pwm = self.fan_override
                    else:
                        fan_pwm = self.calculate_fan_speed(body_temp)
                    self.fan.set_duty_cycle(fan_pwm)
                    self.last_fan_pwm = fan_pwm

                    # Control CPU fan with hysteresis (10% deadband) - based on CPU temp only
                    if self.cpu_fan:
                        # Apply hysteresis logic
                        if self.cpu_fan_state:
                            # Fan is ON - turn OFF if CPU temp drops below lower threshold
                            if cpu_temp is None or cpu_temp < self.cpu_fan_off_threshold:
                                self.cpu_fan_state = False
                        else:
                            # Fan is OFF - turn ON if CPU temp exceeds upper threshold
                            if cpu_temp is not None and cpu_temp >= self.cpu_fan_on_threshold:
                                self.cpu_fan_state = True
                        
                        self.cpu_fan.set_state(self.cpu_fan_state)
                        self.last_cpu_fan_state = self.cpu_fan_state
                        
                        # Log with reason why fan is on
                        cpu_temp_str = f"{cpu_temp:.2f}°C" if cpu_temp is not None else "N/A"
                        logger.info(
                            f"BODY: {body_temp:.2f}°C | CPU: {cpu_temp_str} | "
                            f"Fan: {fan_pwm:.1f}% | CPU Fan: {'ON' if self.cpu_fan_state else 'OFF'}"
                        )
                    else:
                        cpu_temp_str = f"{cpu_temp:.2f}°C" if cpu_temp is not None else "N/A"
                        logger.info(f"BODY: {body_temp:.2f}°C | CPU: {cpu_temp_str} | Fan: {fan_pwm:.1f}%")
                else:
                    # If BODY sensor unavailable, use failsafe fan value
                    self.fan.set_duty_cycle(config.FAILSAFE_FAN_PWM)
                    self.last_fan_pwm = config.FAILSAFE_FAN_PWM
                    if self.cpu_fan:
                        self.cpu_fan.set_state(config.FAILSAFE_CPU_FAN_STATE)
                        self.last_cpu_fan_state = config.FAILSAFE_CPU_FAN_STATE
                    logger.warning(f"Fan set to failsafe {config.FAILSAFE_FAN_PWM}% (BODY unavailable)")

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
