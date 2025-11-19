#!/usr/bin/env python3
"""
Capture images from AMASC01 camera.

This script captures images from the AllSky camera based on configuration.
"""

import argparse
import sys
import time
from pathlib import Path

def load_config(config_path):
    """Load configuration from YAML file."""
    try:
        import yaml
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except ImportError:
        print("Error: PyYAML not installed. Install with: pip install pyyaml")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: Configuration file not found: {config_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)

def capture_image(config, output_path=None):
    """
    Capture a single image from the camera.
    
    Args:
        config: Configuration dictionary
        output_path: Optional output path override
    """
    print("Capturing image...")
    print(f"Exposure: {config['camera']['exposure']}s")
    print(f"Gain: {config['camera']['gain']}")
    
    # Placeholder for actual camera capture
    print("⚠ Camera capture not implemented yet")
    print("  This is a template script for future implementation")
    
    if output_path:
        print(f"Would save to: {output_path}")
    else:
        output_dir = config['storage']['output_path']
        print(f"Would save to: {output_dir}")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Capture images from AMASC01 AllSky camera'
    )
    parser.add_argument(
        '-c', '--config',
        default='config/camera_config.yaml',
        help='Path to configuration file'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file path (overrides config)'
    )
    parser.add_argument(
        '-e', '--exposure',
        type=float,
        help='Exposure time in seconds (overrides config)'
    )
    parser.add_argument(
        '-g', '--gain',
        type=int,
        help='Gain value 0-100 (overrides config)'
    )
    parser.add_argument(
        '--continuous',
        action='store_true',
        help='Continuous capture mode'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Interval between captures in continuous mode (seconds)'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Override with command line arguments
    if args.exposure:
        config['camera']['exposure'] = args.exposure
    if args.gain:
        config['camera']['gain'] = args.gain
    
    # Capture mode
    if args.continuous:
        print(f"Starting continuous capture (interval: {args.interval}s)")
        print("Press Ctrl+C to stop")
        try:
            while True:
                capture_image(config, args.output)
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\nStopping continuous capture")
    else:
        capture_image(config, args.output)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {e}")
        sys.exit(1)
