# AMASC01 – AstroMeters AllSky Camera

This is the main source repository for the [AstroMeters AMASC01 AllSky Camera](https://astrometers.eu/products/AMASC01/).
It contains open-source components used to monitor and control the hardware, and is primarily intended for
firmware/software development and customization of the camera.

## Repository layout

- `src/camera_supervisor/`  
  Python-based thermal control daemon and CLI for the AMASC01. It manages heating and ventilation around the
  optical dome (DOME/BODY/ENVI sensors) to maintain safe operating temperatures and helps prevent fogging and
  condensation during long-term outdoor operation.

Additional firmware and support tools may be added under `src/` in the future as the platform evolves.

## Camera supervisor

The `camera_supervisor` component is designed to run on the AMASC01 control electronics. It:

- Reads temperature, humidity and pressure from internal sensors.
- Controls the heater and fans (including an optional CPU fan) using PID and linear fan control.
- Computes dew point for multiple sensor locations to better protect the optical dome from fogging.
- Exposes a Unix domain socket API and a small CLI (`thermal_control_cli.py`) for status and runtime configuration.

For detailed documentation, installation and `systemd` integration, see:

- `src/camera_supervisor/README.md`

## Development

- The code is written in Python 3.
- Hardware access relies on I2C (via `smbus2`), PWM and GPIO interfaces provided by the AMASC01 platform.
- Contributions and local customizations should follow the existing layout under `src/` and keep
  `camera_supervisor` self-contained.

