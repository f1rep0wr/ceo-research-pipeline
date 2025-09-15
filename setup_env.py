#!/usr/bin/env python3
"""
Simple script to verify Python 3.11+ and create virtual environment.
Follows KISS principles - straightforward version checking and venv creation.
"""
import sys
import subprocess
import os
from pathlib import Path


def verify_python_version():
    """Verify Python version is 3.11 or higher."""
    required_version = (3, 11)
    current_version = sys.version_info[:2]

    print(f"Current Python version: {sys.version}")
    print(f"Version tuple: {current_version}")

    if current_version < required_version:
        print(f"ERROR: Python {required_version[0]}.{required_version[1]}+ is required.")
        print(f"Current version is {current_version[0]}.{current_version[1]}")
        return False

    print(f"[OK] Python version {current_version[0]}.{current_version[1]} meets requirements (3.11+)")
    return True


def create_virtual_environment():
    """Create virtual environment using built-in venv module."""
    venv_path = Path("venv")

    if venv_path.exists():
        print(f"Virtual environment already exists at: {venv_path.absolute()}")
        return True

    try:
        print(f"Creating virtual environment at: {venv_path.absolute()}")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("[OK] Virtual environment created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to create virtual environment: {e}")
        return False


def get_activation_command():
    """Get the appropriate activation command for the current platform."""
    if sys.platform == "win32":
        return "venv\\Scripts\\activate"
    else:
        return "source venv/bin/activate"


def main():
    """Main function to verify Python and create virtual environment."""
    print("=== Python Environment Setup ===")
    print(f"Working directory: {os.getcwd()}")

    # Step 1: Verify Python version
    if not verify_python_version():
        sys.exit(1)

    # Step 2: Create virtual environment
    if not create_virtual_environment():
        sys.exit(1)

    # Step 3: Display success message and activation instructions
    activation_cmd = get_activation_command()
    print("\n=== Setup Complete ===")
    print("[OK] Python version verified (>=3.11)")
    print("[OK] Virtual environment created")
    print(f"\nTo activate the virtual environment, run:")
    print(f"  {activation_cmd}")


if __name__ == "__main__":
    main()