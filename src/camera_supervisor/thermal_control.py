#!/usr/bin/env python3
"""
AllSky Camera Thermal Control System
Main entry point
"""

import sys
import signal
import logging
import argparse
import os

from thermal import (
    ThermalController, SocketServer,
    TARGET_TEMP, COOLING_TEMP_MIN, COOLING_TEMP_MAX, CPU_FAN_THRESHOLD, BODY_FAN_THRESHOLD
)

# Logging setup
logger = logging.getLogger(__name__)


def signal_handler(signum, frame):
    """Handle termination signals"""
    logger.info(f"Received signal {signum}")
    sys.exit(0)


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='AllSky Camera Thermal Control System',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    def validate_target_temp(value):
        fvalue = float(value)
        if fvalue > 60.0:
            raise argparse.ArgumentTypeError(f"Target temperature {fvalue}°C exceeds maximum allowed (60°C)")
        if fvalue < 0.0:
            raise argparse.ArgumentTypeError(f"Target temperature {fvalue}°C must be positive")
        return fvalue
    
    parser.add_argument(
        '--target-temp',
        type=validate_target_temp,
        default=float(os.getenv('TARGET_TEMP', TARGET_TEMP)),
        metavar='TEMP',
        help=f'Target temperature for DOME sensor (default: {TARGET_TEMP}°C, max: 60°C)'
    )
    
    parser.add_argument(
        '--cooling-min',
        type=float,
        default=float(os.getenv('COOLING_MIN', COOLING_TEMP_MIN)),
        metavar='TEMP',
        help=f'Temperature for 0%% fan speed (default: {COOLING_TEMP_MIN}°C)'
    )
    
    parser.add_argument(
        '--cooling-max',
        type=float,
        default=float(os.getenv('COOLING_MAX', COOLING_TEMP_MAX)),
        metavar='TEMP',
        help=f'Temperature for 100%% fan speed (default: {COOLING_TEMP_MAX}°C)'
    )
    
    parser.add_argument(
        '--cpu-fan-gpio',
        type=int,
        default=int(os.getenv('CPU_FAN_GPIO', '0')) if os.getenv('CPU_FAN_GPIO') else None,
        metavar='PIN',
        help='GPIO pin number for CPU fan control (e.g., 518)'
    )
    
    parser.add_argument(
        '--cpu-fan-threshold',
        type=float,
        default=float(os.getenv('CPU_FAN_THRESHOLD', CPU_FAN_THRESHOLD)),
        metavar='TEMP',
        help=f'Temperature threshold to turn on CPU fan (default: {CPU_FAN_THRESHOLD}°C)'
    )

    parser.add_argument(
        '--body-fan-threshold',
        type=float,
        default=float(os.getenv('BODY_FAN_THRESHOLD', BODY_FAN_THRESHOLD)),
        metavar='TEMP',
        help=f'Body temperature threshold to turn on CPU fan (default: {BODY_FAN_THRESHOLD}°C)'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Set logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--log-file',
        type=str,
        default='/var/log/thermal_control.log',
        metavar='PATH',
        help='Log file path (default: /var/log/thermal_control.log)'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run in test mode (single iteration, then exit)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 2.0.0'
    )
    
    return parser.parse_args()


def setup_logging(level, log_file):
    """Setup logging configuration.

    - Console (stdout/journald): full log level (INFO by default)
    - File (/var/log/thermal_control.log): only WARNINGS and ERRORS
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Root logger
    root = logging.getLogger()
    root.setLevel(numeric_level)

    # Remove any existing handlers (in case of re-init)
    for h in list(root.handlers):
        root.removeHandler(h)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Console / journald handler
    ch = logging.StreamHandler()
    ch.setLevel(numeric_level)
    ch.setFormatter(formatter)
    root.addHandler(ch)

    # File handler: only WARNINGS and ERRORS to spare the SD card
    try:
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.WARNING)
        fh.setFormatter(formatter)
        root.addHandler(fh)
    except Exception as e:
        print(f"Warning: Cannot write to log file {log_file}: {e}")


def main():
    """Main entry point"""
    args = parse_arguments()
    
    # Setup logging
    setup_logging(args.log_level, args.log_file)
    
    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Update global configuration from arguments
    import thermal.config as config
    config.TARGET_TEMP = args.target_temp
    config.COOLING_TEMP_MIN = args.cooling_min
    config.COOLING_TEMP_MAX = args.cooling_max

    # Apply hardware-specific overrides based on board variant
    board_variant = os.getenv("BOARD_VARIANT", "").upper()
    if board_variant:
        logger.info(f"Board variant: {board_variant}")
    if board_variant == "AMRPI4HAT01D":
        config.PWM_HEATER, config.PWM_FAN = config.PWM_FAN, config.PWM_HEATER
        logger.info(f"AMRPI4HAT01D: PWM channels swapped (heater={config.PWM_HEATER}, fan={config.PWM_FAN})")
    
    logger.info("=== AllSky Camera Thermal Control System ===")
    logger.info(f"Target temperature: {config.TARGET_TEMP}°C")
    logger.info(f"Cooling range: {config.COOLING_TEMP_MIN}-{config.COOLING_TEMP_MAX}°C")
    if args.cpu_fan_gpio:
        logger.info(f"CPU fan: GPIO{args.cpu_fan_gpio} (threshold: {args.cpu_fan_threshold}°C)")
    
    logger.warning(f"START: target={config.TARGET_TEMP}°C cooling={config.COOLING_TEMP_MIN}-{config.COOLING_TEMP_MAX}°C cpu_fan_gpio={args.cpu_fan_gpio} cpu_threshold={args.cpu_fan_threshold}°C body_threshold={args.body_fan_threshold}°C")
    
    controller = ThermalController(
        cpu_fan_gpio=args.cpu_fan_gpio,
        cpu_fan_threshold=args.cpu_fan_threshold,
        body_fan_threshold=args.body_fan_threshold
    )
    
    # Update controller's runtime config to match global config
    controller.target_temp = config.TARGET_TEMP
    controller.cooling_min = config.COOLING_TEMP_MIN
    controller.cooling_max = config.COOLING_TEMP_MAX
    
    if not controller.setup():
        logger.error("Failed to setup controller - exiting")
        sys.exit(1)
    
    if args.test:
        logger.info("Running in test mode...")
        dome_temp = controller.dome.read_temperature()
        body_temp = controller.body.read_temperature()
        
        logger.info(f"DOME: {dome_temp}°C" if dome_temp else "DOME: FAILED")
        logger.info(f"BODY: {body_temp}°C" if body_temp else "BODY: FAILED")
        
        controller.safe_shutdown()
        sys.exit(0)
    
    # Start socket server
    socket_server = SocketServer(controller)
    socket_server.start()
    
    try:
        success = controller.run()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        controller.safe_shutdown()
        sys.exit(1)
    finally:
        socket_server.stop()


if __name__ == "__main__":
    main()
