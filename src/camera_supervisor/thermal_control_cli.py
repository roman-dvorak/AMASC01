#!/usr/bin/env python3
"""
CLI tool for controlling thermal control system via Unix socket
"""

import socket
import json
import sys
import argparse

SOCKET_PATH = "/var/run/thermal-control.sock"
STATUS_PATH = "/var/run/thermal-control-status.json"


def send_command(command):
    """Send command to thermal control daemon"""
    try:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(SOCKET_PATH)
        client.send(json.dumps(command).encode('utf-8'))
        response = client.recv(4096).decode('utf-8')
        client.close()
        return json.loads(response)
    except FileNotFoundError:
        print(f"Error: Socket {SOCKET_PATH} not found. Is the service running?")
        sys.exit(1)
    except Exception as e:
        print(f"Error communicating with daemon: {e}")
        sys.exit(1)


def read_status_file():
    """Read status from JSON file"""
    try:
        with open(STATUS_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Status file {STATUS_PATH} not found. Is the service running?")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading status file: {e}")
        sys.exit(1)


def cmd_status(args):
    """Get system status"""
    if args.from_file:
        status = read_status_file()
    else:
        status = send_command({"command": "status"})

    if "error" in status:
        print(f"Error: {status['error']}")
        return

    def fmt(value):
        """Format numeric values nicely for CLI output."""
        if isinstance(value, (int, float)):
            return f"{value:.2f}"
        if value is None:
            return "N/A"
        return str(value)

    print("=" * 60)
    print("  Thermal Control System Status")
    print("=" * 60)
    
    # DOME Section
    print("\n[DOME - Camera Dome with Heater]")
    print(f"  Temperature:    {fmt(status.get('dome_temp'))}°C")
    print(f"  Humidity:       {fmt(status.get('dome_humidity'))}%")
    print(f"  Dew Point:      {fmt(status.get('dome_dew_point'))}°C")
    print(f"  Heater PWM:     {status.get('heater_pwm', 0):.1f}%", end="")
    if status.get('heater_override') is not None:
        print(f" (MANUAL: {fmt(status['heater_override'])}%)")
    else:
        print(" (AUTO)")
    
    # BODY Section
    print("\n[BODY - Camera Body with Fan]")
    print(f"  Temperature:    {fmt(status.get('body_temp'))}°C")
    print(f"  Humidity:       {fmt(status.get('body_humidity'))}%")
    print(f"  Dew Point:      {fmt(status.get('body_dew_point'))}°C")
    print(f"  Pressure:       {fmt(status.get('body_pressure'))} hPa")
    print(f"  Cooling Fan:    {status.get('fan_pwm', 0):.1f}%", end="")
    if status.get('fan_override') is not None:
        print(f" (MANUAL: {fmt(status['fan_override'])}%)")
    else:
        print(" (AUTO)")
    
    # CPU Section
    print("\n[CPU - Compute Module]")
    print(f"  Temperature:    {fmt(status.get('cpu_temp'))}°C")
    print(f"  CPU Fan:        {'ON' if status.get('cpu_fan_state') else 'OFF'}")
    
    # ENVI Section
    print("\n[ENVI - Environment Sensor]")
    print(f"  Temperature:    {fmt(status.get('envi_temp'))}°C")
    print(f"  Humidity:       {fmt(status.get('envi_humidity'))}%")
    print(f"  Dew Point:      {fmt(status.get('envi_dew_point'))}°C")
    
    # Control Parameters
    print("\n[Control Parameters]")
    print(f"  Target Temp:    {fmt(status.get('target_temp'))}°C (DOME)")
    print(f"  Cooling Range:  {fmt(status.get('cooling_min'))}°C - {fmt(status.get('cooling_max'))}°C (BODY)")
    print(f"  CPU Fan Thresh: {fmt(status.get('cpu_fan_threshold'))}°C")
    print(f"  Body Fan Thresh:{fmt(status.get('body_fan_threshold'))}°C")
    print(f"  Error Count:    {status.get('error_count', 0)}")
    
    print("=" * 60)



def cmd_set_target(args):
    """Set target temperature"""
    response = send_command({"command": "set-target", "temperature": args.temperature})
    if "error" in response:
        print(f"Error: {response['error']}")
    else:
        print(f"Target temperature set to {response['target_temp']}°C")


def cmd_set_cooling(args):
    """Set cooling temperature range"""
    command = {"command": "set-cooling"}
    if args.min is not None:
        command["min"] = args.min
    if args.max is not None:
        command["max"] = args.max

    response = send_command(command)
    if "error" in response:
        print(f"Error: {response['error']}")
    else:
        print(f"Cooling range set to {response['cooling_min']}°C - {response['cooling_max']}°C")


def cmd_heater_override(args):
    """Override heater power"""
    response = send_command({"command": "heater-override", "percent": args.percent})
    if "error" in response:
        print(f"Error: {response['error']}")
    else:
        print(f"Heater manually set to {response['heater_override']}%")


def cmd_heater_auto(args):
    """Return heater to automatic control"""
    response = send_command({"command": "heater-auto"})
    if "error" in response:
        print(f"Error: {response['error']}")
    else:
        print("Heater returned to automatic control")


def cmd_fan_override(args):
    """Override fan speed"""
    response = send_command({"command": "fan-override", "percent": args.percent})
    if "error" in response:
        print(f"Error: {response['error']}")
    else:
        print(f"Fan manually set to {response['fan_override']}%")


def cmd_fan_auto(args):
    """Return fan to automatic control"""
    response = send_command({"command": "fan-auto"})
    if "error" in response:
        print(f"Error: {response['error']}")
    else:
        print("Fan returned to automatic control")


def cmd_set_pid(args):
    """Set PID parameters"""
    command = {"command": "set-pid"}
    if args.kp is not None:
        command["kp"] = args.kp
    if args.ki is not None:
        command["ki"] = args.ki
    if args.kd is not None:
        command["kd"] = args.kd

    response = send_command(command)
    if "error" in response:
        print(f"Error: {response['error']}")
    else:
        print(f"PID parameters: Kp={response['kp']}, Ki={response['ki']}, Kd={response['kd']}")


def main():
    parser = argparse.ArgumentParser(
        description='Thermal Control System CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Status command
    status_parser = subparsers.add_parser('status', help='Get system status')
    status_parser.add_argument('--from-file', action='store_true',
                               help='Read from status file instead of socket')
    status_parser.set_defaults(func=cmd_status)

    # Set target temperature
    target_parser = subparsers.add_parser('set-target', help='Set target temperature')
    target_parser.add_argument('temperature', type=float, help='Target temperature (0-60°C)')
    target_parser.set_defaults(func=cmd_set_target)

    # Set cooling range
    cooling_parser = subparsers.add_parser('set-cooling', help='Set cooling temperature range')
    cooling_parser.add_argument('--min', type=float, help='Minimum temperature for 0% fan')
    cooling_parser.add_argument('--max', type=float, help='Maximum temperature for 100% fan')
    cooling_parser.set_defaults(func=cmd_set_cooling)

    # Heater override
    heater_override_parser = subparsers.add_parser('heater-override', help='Manually set heater power')
    heater_override_parser.add_argument('percent', type=float, help='Heater power percentage (0-100)')
    heater_override_parser.set_defaults(func=cmd_heater_override)

    # Heater auto
    heater_auto_parser = subparsers.add_parser('heater-auto', help='Return heater to automatic control')
    heater_auto_parser.set_defaults(func=cmd_heater_auto)

    # Fan override
    fan_override_parser = subparsers.add_parser('fan-override', help='Manually set fan speed')
    fan_override_parser.add_argument('percent', type=float, help='Fan speed percentage (0-100)')
    fan_override_parser.set_defaults(func=cmd_fan_override)

    # Fan auto
    fan_auto_parser = subparsers.add_parser('fan-auto', help='Return fan to automatic control')
    fan_auto_parser.set_defaults(func=cmd_fan_auto)

    # Set PID
    pid_parser = subparsers.add_parser('set-pid', help='Set PID parameters')
    pid_parser.add_argument('--kp', type=float, help='Proportional gain')
    pid_parser.add_argument('--ki', type=float, help='Integral gain')
    pid_parser.add_argument('--kd', type=float, help='Derivative gain')
    pid_parser.set_defaults(func=cmd_set_pid)

    args = parser.parse_args()

    if not hasattr(args, 'func'):
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == '__main__':
    main()
