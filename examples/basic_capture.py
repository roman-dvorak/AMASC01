#!/usr/bin/env python3
"""
Basic capture example for AMASC01 camera.

This example shows how to capture a single image from the camera.
"""

import sys
from pathlib import Path

def main():
    """Main function demonstrating basic capture."""
    print("AMASC01 - Basic Capture Example")
    print("=" * 50)
    print()
    
    # This is a template example
    print("This is a template example for future implementation.")
    print()
    print("When implemented, this script will:")
    print("1. Initialize connection to the camera")
    print("2. Set basic parameters (exposure, gain)")
    print("3. Capture a single image")
    print("4. Save the image to disk")
    print("5. Display basic image information")
    print()
    
    # Example pseudo-code for future implementation:
    print("Example code structure:")
    print("-" * 50)
    print("""
    from amasc01 import Camera
    
    # Initialize camera
    camera = Camera()
    
    # Configure camera
    camera.set_exposure(10.0)  # 10 seconds
    camera.set_gain(50)         # Medium gain
    
    # Capture image
    print("Capturing image...")
    image = camera.capture()
    
    # Save image
    output_path = "captured_image.fits"
    camera.save_image(image, output_path)
    print(f"Image saved to: {output_path}")
    
    # Display info
    print(f"Image shape: {image.shape}")
    print(f"Data type: {image.dtype}")
    print(f"Min value: {image.min()}")
    print(f"Max value: {image.max()}")
    print(f"Mean value: {image.mean()}")
    
    # Close camera
    camera.close()
    """)
    print("-" * 50)
    print()
    print("To implement this functionality:")
    print("1. Install camera driver/SDK")
    print("2. Implement Camera class in amasc01 module")
    print("3. Test with your specific hardware")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {e}")
        sys.exit(1)
