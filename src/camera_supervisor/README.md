# Camera Supervisor – AllSky Thermal Control

This component controls the thermal environment of an AllSky camera. It is designed and intended for use with the AstroMeters AMASC01 AllSky Camera (https://astrometers.eu/products/AMASC01/). By maintaining temperature and humidity conditions around the optical dome, it helps prevent fogging and condensation during long-term outdoor operation. It runs as a daemon under `systemd`, reads temperature/humidity/pressure sensors, and drives heater and fan outputs to keep the camera within a safe operating range.

The code is structured as a small Python package (`thermal`) with a simple entrypoint script and a CLI tool for remote control and status.

## Features

- **DOME control (heater + PID)**
  - Maintains the dome temperature close to a configurable target.
  - PID control on the DOME sensor (SHT31).
  - Safety limits enforce a maximum allowed temperature.
- **BODY cooling (fan + CPU fan)**
  - Main fan speed is controlled by BODY temperature (BME280) using a linear mapping between two configurable thresholds.
  - Optional CPU fan controlled via GPIO; turns on when **EITHER** CPU temperature **OR** BODY temperature exceeds their respective thresholds.
- **CPU temperature monitoring**
  - Reads CPU temperature from `/sys/class/thermal/thermal_zone0/temp`.
  - CPU fan controlled independently based on CPU temp threshold.
  - Both CPU and BODY temperature thresholds can be configured separately.
- **Environment monitoring (ENVI)**
  - Additional SHT31 sensor (ENVI) for ambient measurements.
- **Extended telemetry**
  - Temperature and relative humidity from DOME, BODY, and ENVI.
  - CPU temperature.
  - Pressure from the BODY sensor (BME280).
  - Dew point computed for all three sensor locations.
- **Robustness & safety**
  - Sensor values are range-checked; repeated failures trigger a safe shutdown (heater off, fans in safe state).
  - Periodic status snapshot written to a JSON file in `/var/run`.
- **Socket-based control and CLI**
  - Unix domain socket server for remote commands.
  - CLI helper (`thermal_control_cli.py`) to query status and change parameters.

## Repository Layout (camera_supervisor)

- `thermal/`
  - `config.py` – default configuration values (buses, addresses, PID gains, temperature limits, socket paths).
  - `sensors.py` – SHT31, BME280, and CPUSensor drivers (temperature, humidity, pressure).
  - `controllers.py` – PWM, GPIO, and PID controller classes.
  - `thermal_controller.py` – main control loop that ties sensors and actuators together.
  - `socket_server.py` – Unix domain socket server exposing control/status commands.
  - `__init__.py` – package exports.
- `thermal_control.py` – main entrypoint script used by the `systemd` service.
- `thermal_control_cli.py` – CLI client for querying status and adjusting runtime parameters.
- `thermal-control.service` – example `systemd` unit file for the daemon.
- `install.sh` – helper script to install prerequisites and register the service (optional).
- `restart.sh` – convenience script to reload and restart the thermal control service.
- `archive/` – old/legacy versions of the implementation kept for reference; not used by the current system.

All paths below assume this directory is `/home/astrometers/repos/AMASC01/src/camera_supervisor` and that the repository root is `/home/astrometers/repos/AMASC01`.

## Runtime Architecture

### Sensors

The system currently uses four sensors:

- **DOME** – SHT31 on I2C bus `DOME_BUS`, address `DOME_ADDR`.
- **BODY** – BME280 on I2C bus `BODY_BUS`, address `BODY_ADDR`.
- **ENVI** – SHT31 on I2C bus `ENVI_BUS`, address `ENVI_ADDR`.
- **CPU** – System CPU temperature from `/sys/class/thermal/thermal_zone0/temp`.

The exact bus numbers and addresses are defined in `thermal/config.py` and can be overridden by environment variables at startup via `thermal_control.py`.

Each sensor class caches the last valid measurement and exposes health checks via a timeout (`SENSOR_TIMEOUT`).

### Actuators

- **Heater** – PWM output `PWM_HEATER` (PWM channel index) driving the dome heater.
- **Fan** – PWM output `PWM_FAN` driving the main cooling fan.
- **CPU fan (optional)** – GPIO output driving an additional CPU fan.

PWM and GPIO controllers live in `thermal/controllers.py` and are initialized in `ThermalController.setup()`.

### Control Logic

`thermal/thermal_controller.py` implements the main loop:

- Reads sensors every second.
- Uses a PID controller (`PIDController`) on DOME temperature to compute heater PWM.
- Uses a linear mapping from BODY temperature to fan PWM between `COOLING_TEMP_MIN` and `COOLING_TEMP_MAX`.
- Optionally overrides fan speed with a manual value when requested via socket/CLI.
- Controls the CPU fan on/off based on **EITHER**:
  - CPU temperature >= `CPU_FAN_THRESHOLD`, **OR**
  - BODY temperature >= `BODY_FAN_THRESHOLD`
- Writes a status JSON file at `STATUS_PATH` (by default `/var/run/thermal-control-status.json`).

If the DOME sensor fails repeatedly (more than `MAX_CONSECUTIVE_ERRORS` times in a row), the controller performs a **safe shutdown**: heater off, fans set to a safe state, and the loop exits.

### Dew Point

For each sensor location (DOME, BODY, ENVI) the controller:

- Reads temperature and relative humidity.
- Computes the dew point using the Magnus formula.
- Exposes values via `get_status()` and through the CLI.

## Configuration

Configuration defaults live in `thermal/config.py`. At runtime, `thermal_control.py` reads environment variables (set either directly or via the `systemd` unit) and updates the configuration before starting the controller.

Key parameters:

- `TARGET_TEMP` – target DOME temperature (°C) for PID control.
- `COOLING_TEMP_MIN` – BODY temperature (°C) at which fan is 0%.
- `COOLING_TEMP_MAX` – BODY temperature (°C) at which fan is 100%.
- `CPU_FAN_THRESHOLD` – CPU temperature (°C) above which the CPU fan is turned on (default: 60°C).
- `BODY_FAN_THRESHOLD` – BODY temperature (°C) above which the CPU fan is turned on (default: 35°C).
- `MAX_TEMP` / `MIN_TEMP` – valid sensor range and safety limit.
- `MAX_CONSECUTIVE_ERRORS` – number of failed DOME reads before shutdown.
- `SENSOR_TIMEOUT` – maximum age of a sensor reading before it is considered stale.
- `SOCKET_PATH` – Unix socket path (default `/var/run/thermal-control.sock`).
- `STATUS_PATH` – JSON status file path (default `/var/run/thermal-control-status.json`).

In the `thermal-control.service` example, these are set via `Environment=` lines, e.g.:

```ini
Environment="TARGET_TEMP=40"
Environment="COOLING_MIN=30"
Environment="COOLING_MAX=70"
Environment="CPU_FAN_GPIO=518"
Environment="CPU_FAN_THRESHOLD=60"
Environment="BODY_FAN_THRESHOLD=35"
```

## Systemd Service

The recommended way to run the supervisor is as a `systemd` service using `thermal-control.service`:

- **Working directory:** this `camera_supervisor` directory.
- **Runtime directory:** `RuntimeDirectory=thermal-control` (maps to `/var/run/thermal-control/` depending on distro; here it is used for the socket and status file paths).
- **ExecStart:**

```bash
/usr/bin/python3 /home/astrometers/repos/AMASC01/src/camera_supervisor/thermal_control.py
```

To install or update the service manually:

1. Copy or symlink `thermal-control.service` into `/etc/systemd/system/`.
2. Reload systemd units:

   ```bash
   sudo systemctl daemon-reload
   ```

3. Enable and start the service:

   ```bash
   sudo systemctl enable thermal-control.service
   sudo systemctl start thermal-control.service
   ```

4. Check status and logs:

   ```bash
   sudo systemctl status thermal-control.service
   journalctl -u thermal-control.service
   ```

### Quick Restart

Use the provided convenience script to reload and restart the service:

```bash
./restart.sh
```

This script performs:
- `systemctl daemon-reload`
- `systemctl restart thermal-control.service`
- Displays service status and recent logs

## CLI Usage

The CLI tool communicates with the running daemon via the Unix socket at `SOCKET_PATH`.

Basic usage:

```bash
./thermal_control_cli.py status
```

This prints a summary including:

- **DOME section:** Temperature, humidity, dew point, heater PWM.
- **BODY section:** Temperature, humidity, dew point, pressure, cooling fan PWM and mode (AUTO/MANUAL).
- **CPU section:** CPU temperature and CPU fan state (ON/OFF).
- **ENVI section:** Environment temperature, humidity, dew point.
- **Control Parameters:** Target temperature, cooling range, CPU fan threshold, BODY fan threshold, error count.

Other useful commands:

- Set target temperature (0–60 °C):

  ```bash
  ./thermal_control_cli.py set-target 30
  ```

- Set cooling range:

  ```bash
  ./thermal_control_cli.py set-cooling --min 30 --max 60
  ```

- Manually override fan speed (in percent):

  ```bash
  ./thermal_control_cli.py fan-override 50
  ```

- Return fan control to automatic mode:

  ```bash
  ./thermal_control_cli.py fan-auto
  ```

- Adjust PID parameters:

  ```bash
  ./thermal_control_cli.py set-pid --kp 8.0 --ki 0.4 --kd 1.5
  ```

If you add `--from-file` to `status`, the CLI will read the status directly from the JSON file instead of the socket:

```bash
./thermal_control_cli.py status --from-file
```

## Logging

Logging is configured in `thermal_control.py`:

- **Console/journal:** INFO and higher – telemetry suitable for live monitoring (includes CPU temperature in logs).
- **Log file (`/var/log/thermal_control.log`):** WARNING and higher – only start/stop events and errors, to minimize SD card writes.

Make sure the log path is writable by the user running the service (typically `root` under `systemd`).

## Development Notes

- Python 3 is required.
- The code uses `smbus2` for I2C access.
- When modifying the module layout or configuration, keep `thermal_control.py`, `thermal/config.py`, and `thermal-control.service` consistent (paths, environment variables, and import names).
- Old/broken implementations are kept in `archive/` and are not imported anywhere; they can be safely ignored for day-to-day development.
