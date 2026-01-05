"""
Hardware controller classes (PWM, GPIO, PID)
"""
import time
import logging
from pathlib import Path

from .config import *

logger = logging.getLogger(__name__)

class GPIOController:
    """Control GPIO output via sysfs"""
    
    def __init__(self, pin):
        self.pin = pin
        self.gpio_path = Path(f"/sys/class/gpio/gpio{pin}")
        self.enabled = False
        
    def get_status(self):
        """Get current system status"""
        return {
            "sht31_temp": self.sht31.last_valid_temp,
            "bme280_temp": self.bme280.last_valid_temp,
            "heater_pwm": getattr(self, 'last_heater_pwm', 0),
            "fan_pwm": getattr(self, 'last_fan_pwm', 0),
            "cpu_fan_state": getattr(self, 'last_cpu_fan_state', False),
            "target_temp": TARGET_TEMP,
            "cooling_min": COOLING_TEMP_MIN,
            "cooling_max": COOLING_TEMP_MAX,
            "fan_override": self.fan_override,
            "error_count": self.error_count
        }
    
    def set_target_temperature(self, temp):
        """Set target temperature"""
        global TARGET_TEMP
        TARGET_TEMP = float(temp)
        self.pid.target = TARGET_TEMP
        logger.info(f"Target temperature changed to {TARGET_TEMP}°C")
    
    def set_cooling_min(self, temp):
        """Set cooling minimum temperature"""
        global COOLING_TEMP_MIN
        COOLING_TEMP_MIN = float(temp)
        logger.info(f"Cooling min temperature changed to {COOLING_TEMP_MIN}°C")
    
    def set_cooling_max(self, temp):
        """Set cooling maximum temperature"""
        global COOLING_TEMP_MAX
        COOLING_TEMP_MAX = float(temp)
        logger.info(f"Cooling max temperature changed to {COOLING_TEMP_MAX}°C")
    
    def save_status(self):
        """Save current status to JSON file"""
        try:
            status = self.get_status()
            with open(STATUS_PATH, 'w') as f:
                json.dump(status, f, indent=2)
        except Exception as e:
            logger.debug(f"Failed to save status: {e}")
    
    
    def setup(self):
        """Initialize GPIO pin"""
        try:
            # Export GPIO if not already exported
            if not self.gpio_path.exists():
                with open("/sys/class/gpio/export", "w") as f:
                    f.write(str(self.pin))
                time.sleep(0.1)
            
            # Set direction to output
            with open(self.gpio_path / "direction", "w") as f:
                f.write("out")
            
            self.enabled = True
            logger.info(f"GPIO{self.pin} initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to setup GPIO{self.pin}: {e}")
            return False
    
    def set_state(self, state):
        """Set GPIO state (True/False or 1/0)"""
        if not self.enabled:
            return False
        
        try:
            value = "1" if state else "0"
            with open(self.gpio_path / "value", "w") as f:
                f.write(value)
            return True
        except Exception as e:
            logger.error(f"Failed to set GPIO{self.pin} state: {e}")
            return False
    
    def disable(self):
        """Disable GPIO output"""
        try:
            if self.gpio_path.exists():
                with open(self.gpio_path / "value", "w") as f:
                    f.write("0")
            self.enabled = False
            logger.info(f"GPIO{self.pin} disabled")
        except Exception as e:
            logger.error(f"Failed to disable GPIO{self.pin}: {e}")


class PWMController:
    """Control PWM outputs via sysfs"""
    
    def __init__(self, channel, inverted=False):
        self.channel = channel
        self.inverted = inverted
        self.base_path = Path(f"/sys/class/pwm/pwmchip0")
        self.pwm_path = self.base_path / f"pwm{channel}"
        self.enabled = False
        
    def setup(self):
        """Initialize PWM channel"""
        try:
            # Export PWM if not already exported
            if not self.pwm_path.exists():
                with open(self.base_path / "export", "w") as f:
                    f.write(str(self.channel))
                time.sleep(0.1)
            
            # Set period (20ms = 50Hz)
            with open(self.pwm_path / "period", "w") as f:
                f.write("20000000")  # 20ms in nanoseconds
            
            self.enabled = True
            inverted_str = " (inverted)" if self.inverted else ""
            logger.info(f"PWM{self.channel} initialized successfully{inverted_str}")
            return True
        except Exception as e:
            logger.error(f"Failed to setup PWM{self.channel}: {e}")
            return False
    
    def set_duty_cycle(self, percent):
        """Set PWM duty cycle (0-100%)"""
        if not self.enabled:
            return False
        
        try:
            percent = max(0.0, min(100.0, percent))
            
            # Apply inversion if configured
            if self.inverted:
                actual_percent = 100.0 - percent
            else:
                actual_percent = percent
                
            duty_ns = int(20000000 * actual_percent / 100.0)
            
            with open(self.pwm_path / "duty_cycle", "w") as f:
                f.write(str(duty_ns))
            
            # Enable PWM if not already enabled
            with open(self.pwm_path / "enable", "r") as f:
                if f.read().strip() != "1":
                    with open(self.pwm_path / "enable", "w") as f:
                        f.write("1")
            
            return True
        except Exception as e:
            logger.error(f"Failed to set PWM{self.channel} duty cycle: {e}")
            return False
    
    def disable(self):
        """Disable PWM output"""
        try:
            if self.pwm_path.exists():
                with open(self.pwm_path / "enable", "w") as f:
                    f.write("0")
                with open(self.pwm_path / "duty_cycle", "w") as f:
                    f.write("0")
            self.enabled = False
            logger.info(f"PWM{self.channel} disabled")
        except Exception as e:
            logger.error(f"Failed to disable PWM{self.channel}: {e}")


class PIDController:
    """PID controller for temperature regulation"""
    
    def __init__(self, kp, ki, kd, target):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.target = target
        self.integral = 0.0
        self.last_error = 0.0
        self.last_time = time.time()
        
    def update(self, current_value):
        """Calculate PID output"""
        current_time = time.time()
        dt = current_time - self.last_time
        
        if dt <= 0:
            dt = 0.01
        
        error = self.target - current_value
        
        # Proportional term
        p_term = self.kp * error
        
        # Integral term with anti-windup
        self.integral += error * dt
        self.integral = max(-100, min(100, self.integral))  # Clamp integral
        i_term = self.ki * self.integral
        
        # Derivative term
        d_term = self.kd * (error - self.last_error) / dt
        
        # Calculate output
        output = p_term + i_term + d_term
        output = max(0, min(100, output))  # Clamp to 0-100%
        
        self.last_error = error
        self.last_time = current_time
        
        return output
    
    def reset(self):
        """Reset PID controller state"""
        self.integral = 0.0
        self.last_error = 0.0
        self.last_time = time.time()

