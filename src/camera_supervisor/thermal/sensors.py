"""
Temperature and humidity sensor classes
"""
import time
import logging
import math

try:
    import smbus2
except ImportError:
    smbus2 = None

from .config import *

logger = logging.getLogger(__name__)


class SHT31Sensor:
    """SHT31 temperature and humidity sensor"""

    def __init__(self, bus_num, address=0x44):
        self.bus_num = bus_num
        self.address = address
        self.bus = None
        self.last_valid_temp = None
        self.last_read_time = 0
        self.last_valid_humidity = None
        self.last_humidity_time = 0

    def connect(self):
        """Connect to I2C bus"""
        try:
            self.bus = smbus2.SMBus(self.bus_num)
            logger.info(f"Connected to SHT31 on bus {self.bus_num}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to SHT31: {e}")
            return False

    def _read_temperature_and_humidity(self):
        """Perform a single measurement and return (temperature, humidity)."""
        # Send measurement command (high repeatability)
        self.bus.write_i2c_block_data(self.address, 0x2C, [0x06])
        time.sleep(0.02)  # Wait for measurement

        # Read 6 bytes of data
        data = self.bus.read_i2c_block_data(self.address, 0x00, 6)

        # Convert temperature
        temp_raw = (data[0] << 8) | data[1]
        temperature = -45 + (175 * temp_raw / 65535.0)

        # Convert humidity
        hum_raw = (data[3] << 8) | data[4]
        humidity = 100.0 * hum_raw / 65535.0
        # Clamp to [0, 100]
        humidity = max(0.0, min(100.0, humidity))

        return temperature, humidity

    def read_temperature(self):
        """Read temperature from SHT31.

        Also refreshes the stored humidity value from the same measurement.
        """
        try:
            temperature, humidity = self._read_temperature_and_humidity()

            now = time.time()

            # Validate temperature
            if MIN_TEMP <= temperature <= MAX_TEMP:
                self.last_valid_temp = temperature
                self.last_read_time = now
            else:
                logger.warning(f"SHT31 temperature out of range: {temperature}°C")
                temperature = None

            # Always try to update humidity
            if 0.0 <= humidity <= 100.0:
                self.last_valid_humidity = humidity
                self.last_humidity_time = now
            else:
                logger.warning(f"SHT31 humidity out of range: {humidity}%")

            return temperature

        except Exception as e:
            logger.error(f"Failed to read SHT31: {e}")
            return None

    def read_humidity(self):
        """Read relative humidity from SHT31.

        This performs a fresh measurement; the temperature value is also
        updated internally, but only humidity is returned.
        """
        try:
            temperature, humidity = self._read_temperature_and_humidity()
            now = time.time()

            # Update cached values
            if MIN_TEMP <= temperature <= MAX_TEMP:
                self.last_valid_temp = temperature
                self.last_read_time = now

            if 0.0 <= humidity <= 100.0:
                self.last_valid_humidity = humidity
                self.last_humidity_time = now
                return humidity
            else:
                logger.warning(f"SHT31 humidity out of range: {humidity}%")
                return None

        except Exception as e:
            logger.error(f"Failed to read SHT31 humidity: {e}")
            return None

    def is_healthy(self):
        """Check if sensor is providing valid data (temperature based)."""
        if self.last_valid_temp is None:
            return False
        if time.time() - self.last_read_time > SENSOR_TIMEOUT:
            return False
        return True

    def close(self):
        """Close I2C connection"""
        if self.bus:
            self.bus.close()


class BME280Sensor:
    """BME280 temperature, humidity, and pressure sensor"""

    def __init__(self, bus_num, address=0x76):
        self.bus_num = bus_num
        self.address = address
        self.bus = None
        self.last_valid_temp = None
        self.last_read_time = 0
        self.last_valid_humidity = None
        self.last_humidity_time = 0
        self.last_valid_pressure = None  # hPa
        self.last_pressure_time = 0

        # Calibration parameters (loaded on first use)
        self.dig_T1 = None
        self.dig_T2 = None
        self.dig_T3 = None
        self.dig_P1 = None
        self.dig_P2 = None
        self.dig_P3 = None
        self.dig_P4 = None
        self.dig_P5 = None
        self.dig_P6 = None
        self.dig_P7 = None
        self.dig_P8 = None
        self.dig_P9 = None
        self.dig_H1 = None
        self.dig_H2 = None
        self.dig_H3 = None
        self.dig_H4 = None
        self.dig_H5 = None
        self.dig_H6 = None

        self.t_fine = None

    def connect(self):
        """Connect to I2C bus and initialize BME280"""
        try:
            self.bus = smbus2.SMBus(self.bus_num)
            # Initialize BME280: normal mode, oversampling x1 on all channels
            # ctrl_hum (0xF2): humidity oversampling x1
            self.bus.write_byte_data(self.address, 0xF2, 0x01)
            # ctrl_meas (0xF4): temp and pressure oversampling x1, normal mode
            self.bus.write_byte_data(self.address, 0xF4, 0x27)
            # config (0xF5): standby 0.5ms, filter off
            self.bus.write_byte_data(self.address, 0xF5, 0x00)

            logger.info(f"Connected to BME280 on bus {self.bus_num}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to BME280: {e}")
            return False

    @staticmethod
    def _to_signed(value, bits):
        """Convert unsigned integer to signed with given bit width."""
        if value & (1 << (bits - 1)):
            value -= 1 << bits
        return value

    def _ensure_calibration(self):
        """Load calibration parameters from the sensor if not already loaded."""
        if self.dig_T1 is not None:
            return

        # Temperature and pressure calibration data
        calib = self.bus.read_i2c_block_data(self.address, 0x88, 24)
        self.dig_T1 = calib[1] << 8 | calib[0]
        self.dig_T2 = self._to_signed(calib[3] << 8 | calib[2], 16)
        self.dig_T3 = self._to_signed(calib[5] << 8 | calib[4], 16)

        self.dig_P1 = calib[7] << 8 | calib[6]
        self.dig_P2 = self._to_signed(calib[9] << 8 | calib[8], 16)
        self.dig_P3 = self._to_signed(calib[11] << 8 | calib[10], 16)
        self.dig_P4 = self._to_signed(calib[13] << 8 | calib[12], 16)
        self.dig_P5 = self._to_signed(calib[15] << 8 | calib[14], 16)
        self.dig_P6 = self._to_signed(calib[17] << 8 | calib[16], 16)
        self.dig_P7 = self._to_signed(calib[19] << 8 | calib[18], 16)
        self.dig_P8 = self._to_signed(calib[21] << 8 | calib[20], 16)
        self.dig_P9 = self._to_signed(calib[23] << 8 | calib[22], 16)

        # Humidity calibration data
        self.dig_H1 = self.bus.read_byte_data(self.address, 0xA1)
        calib_h = self.bus.read_i2c_block_data(self.address, 0xE1, 7)
        self.dig_H2 = self._to_signed(calib_h[1] << 8 | calib_h[0], 16)
        self.dig_H3 = calib_h[2]
        e4 = calib_h[3]
        e5 = calib_h[4]
        e6 = calib_h[5]
        self.dig_H4 = self._to_signed((e4 << 4) | (e5 & 0x0F), 12)
        self.dig_H5 = self._to_signed((e6 << 4) | (e5 >> 4), 12)
        self.dig_H6 = self._to_signed(calib_h[6], 8)

    def _read_raw_data(self):
        """Read raw temperature, pressure and humidity from BME280."""
        # Data registers 0xF7..0xFE: pressure(3) + temperature(3) + humidity(2)
        data = self.bus.read_i2c_block_data(self.address, 0xF7, 8)
        adc_p = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        adc_t = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
        adc_h = (data[6] << 8) | data[7]
        return adc_t, adc_p, adc_h

    def _compensate_temperature(self, adc_t):
        """Return temperature in °C and update t_fine."""
        var1 = (adc_t / 16384.0 - self.dig_T1 / 1024.0) * self.dig_T2
        var2 = ((adc_t / 131072.0 - self.dig_T1 / 8192.0) ** 2) * self.dig_T3
        self.t_fine = var1 + var2
        return self.t_fine / 5120.0

    def _compensate_pressure(self, adc_p):
        """Return pressure in hPa using t_fine."""
        if self.t_fine is None:
            return None

        var1 = self.t_fine / 2.0 - 64000.0
        var2 = var1 * var1 * self.dig_P6 / 32768.0
        var2 = var2 + var1 * self.dig_P5 * 2.0
        var2 = var2 / 4.0 + self.dig_P4 * 65536.0
        var1 = (self.dig_P3 * var1 * var1 / 524288.0 + self.dig_P2 * var1) / 524288.0
        var1 = (1.0 + var1 / 32768.0) * self.dig_P1
        if var1 == 0:
            return None

        p = 1048576.0 - adc_p
        p = (p - var2 / 4096.0) * 6250.0 / var1
        var1 = self.dig_P9 * p * p / 2147483648.0
        var2 = p * self.dig_P8 / 32768.0
        p = p + (var1 + var2 + self.dig_P7) / 16.0
        return p / 100.0  # hPa

    def _compensate_humidity(self, adc_h):
        """Return relative humidity in % using t_fine."""
        if self.t_fine is None:
            return None

        h = self.t_fine - 76800.0
        h = (adc_h - (self.dig_H4 * 64.0 + self.dig_H5 / 16384.0 * h)) * (
            self.dig_H2 / 65536.0 * (1.0 + self.dig_H6 / 67108864.0 * h * (
                1.0 + self.dig_H3 / 67108864.0 * h
            ))
        )
        h = h * (1.0 - self.dig_H1 * h / 524288.0)
        if h > 100.0:
            h = 100.0
        elif h < 0.0:
            h = 0.0
        return h

    def read_temperature(self):
        """Read temperature from BME280.

        Also refreshes stored humidity and pressure values.
        """
        try:
            if self.bus is None:
                logger.error("BME280 bus not initialized")
                return None

            self._ensure_calibration()
            adc_t, adc_p, adc_h = self._read_raw_data()

            temperature = self._compensate_temperature(adc_t)
            humidity = self._compensate_humidity(adc_h)
            pressure = self._compensate_pressure(adc_p)

            now = time.time()

            # Validate and store temperature for health checks
            if MIN_TEMP <= temperature <= MAX_TEMP:
                self.last_valid_temp = temperature
                self.last_read_time = now
            else:
                logger.warning(f"BME280 temperature out of range: {temperature}°C")
                temperature = None

            # Store humidity and pressure if valid
            if humidity is not None and 0.0 <= humidity <= 100.0:
                self.last_valid_humidity = humidity
                self.last_humidity_time = now
            elif humidity is not None:
                logger.warning(f"BME280 humidity out of range: {humidity}%")

            if pressure is not None and 300.0 <= pressure <= 1100.0:
                self.last_valid_pressure = pressure
                self.last_pressure_time = now
            elif pressure is not None:
                logger.warning(f"BME280 pressure out of range: {pressure} hPa")

            return temperature

        except Exception as e:
            logger.error(f"Failed to read BME280: {e}")
            return None

    def read_humidity(self):
        """Read relative humidity from BME280.

        This triggers a fresh measurement and returns humidity in %.
        """
        temp = self.read_temperature()
        # We don't care about temp here; just return latest humidity
        return self.last_valid_humidity

    def read_pressure(self):
        """Read pressure from BME280 in hPa.

        This triggers a fresh measurement and returns pressure in hPa.
        """
        temp = self.read_temperature()
        # We don't care about temp here; just return latest pressure
        return self.last_valid_pressure

    def is_healthy(self):
        """Check if sensor is providing valid data (temperature based)."""
        if self.last_valid_temp is None:
            return False
        if time.time() - self.last_read_time > SENSOR_TIMEOUT:
            return False
        return True

    def close(self):
        """Close I2C connection"""
        if self.bus:
            self.bus.close()
