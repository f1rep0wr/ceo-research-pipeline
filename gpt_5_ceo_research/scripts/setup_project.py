#!/usr/bin/env python3
"""
Project structure setup script for gpt_5_ceo_research.
Creates all required directories and __init__.py files according to the design document.
Follows KISS principles - simple directory creation with proper error handling.
"""

from pathlib import Path
import sys


def create_directory_structure():
    """
    Create all directories from the design document with proper __init__.py files.

    Creates the following structure:
    gpt_5_ceo_research/
    +-- src/
    |   +-- __init__.py
    |   +-- config/
    |   |   +-- __init__.py
    |   |   +-- settings.py
    |   |   +-- constants.py
    |   +-- clients/
    |   |   +-- __init__.py
    |   |   +-- gpt5_client.py
    |   +-- utils/
    |       +-- __init__.py
    |       +-- logger.py
    +-- tests/
    |   +-- __init__.py
    |   +-- conftest.py
    |   +-- test_initialization.py
    +-- scripts/
    |   +-- setup_project.py
    +-- docs/
    +-- docker/

    Returns:
        bool: True if all directories were created successfully, False otherwise.
    """
    # Define the base directory structure
    base_path = Path.cwd() / "gpt_5_ceo_research"

    # Define all directories that need to be created
    directories = [
        base_path / "src",
        base_path / "src" / "config",
        base_path / "src" / "clients",
        base_path / "src" / "utils",
        base_path / "tests",
        base_path / "scripts",
        base_path / "docs",
        base_path / "docker"
    ]

    # Define which directories need __init__.py files (Python packages)
    python_packages = [
        base_path / "src",
        base_path / "src" / "config",
        base_path / "src" / "clients",
        base_path / "src" / "utils",
        base_path / "tests"
    ]

    # Define additional files that need to be created
    additional_files = {
        base_path / "src" / "config" / "settings.py": "",
        base_path / "src" / "config" / "constants.py": "",
        base_path / "src" / "clients" / "gpt5_client.py": "",
        base_path / "src" / "utils" / "logger.py": "",
        base_path / "tests" / "conftest.py": "",
        base_path / "tests" / "test_initialization.py": ""
    }

    try:
        print(f"Creating directory structure at: {base_path}")

        # Create all directories
        for directory in directories:
            if directory.exists():
                print(f"Directory already exists: {directory}")
            else:
                directory.mkdir(parents=True, exist_ok=True)
                print(f"Created directory: {directory}")

        # Create __init__.py files for Python packages
        for package_dir in python_packages:
            init_file = package_dir / "__init__.py"
            if init_file.exists():
                print(f"__init__.py already exists: {init_file}")
            else:
                init_file.touch()
                print(f"Created __init__.py: {init_file}")

        # Create additional empty files
        for file_path, content in additional_files.items():
            if file_path.exists():
                print(f"File already exists: {file_path}")
            else:
                file_path.write_text(content)
                print(f"Created file: {file_path}")

        # Copy this setup script to the new scripts directory
        new_setup_script = base_path / "scripts" / "setup_project.py"
        if not new_setup_script.exists():
            new_setup_script.write_text(Path(__file__).read_text())
            print(f"Copied setup script to: {new_setup_script}")

        print("\n=== Directory Structure Creation Complete ===")
        print("[OK] All directories created successfully")
        print("[OK] All __init__.py files created")
        print("[OK] All placeholder files created")

        return True

    except Exception as e:
        print(f"ERROR: Failed to create directory structure: {e}")
        return False


def create_env_example():
    """
    Create .env.example file with all required environment variables.

    Creates a template environment file with all necessary configuration
    variables for the GPT-5 CEO Research application. Uses placeholder
    values and includes helpful comments for each variable.

    Returns:
        bool: True if .env.example was created successfully, False otherwise.
    """
    env_example_content = """# GPT-5 CEO Research Environment Configuration
# Copy this file to .env and update with your actual values

# OpenAI API Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
# Your OpenAI API key - get from https://platform.openai.com/api-keys

# GPT-5 Model Configuration
GPT5_MODEL=gpt-5
# Available options: gpt-5, gpt-5-mini, gpt-5-nano
# gpt-5: Most capable but slowest and most expensive
# gpt-5-mini: Balanced performance and cost
# gpt-5-nano: Fastest and cheapest but less capable

# Default Reasoning Configuration
DEFAULT_REASONING_EFFORT=medium
# Available options: minimal, low, medium, high
# Controls the depth of reasoning the model uses
# Higher values produce better results but take longer

# Output Verbosity
DEFAULT_VERBOSITY=medium
# Available options: low, medium, high
# Controls how detailed the model responses are
# low: concise responses, high: detailed explanations

# API Request Configuration
MAX_RETRIES=3
# Maximum number of retry attempts for failed API requests
# Recommended: 3-5 for production environments

TIMEOUT_SECONDS=120
# Request timeout in seconds
# Adjust based on your typical query complexity

# Logging Configuration
LOG_LEVEL=INFO
# Available options: DEBUG, INFO, WARNING, ERROR
# DEBUG: Detailed debugging information
# INFO: General operational messages
# WARNING: Warning messages only
# ERROR: Error messages only

# Processing Configuration
MAX_ITERATIONS=5
# Maximum number of iterations for iterative processes
# Prevents infinite loops in recursive reasoning

CONFIDENCE_THRESHOLD=0.8
# Confidence threshold for accepting results (0.0-1.0)
# Higher values require more confident results

# Caching Configuration
CACHE_TTL_HOURS=24
# Time-to-live for cached responses in hours
# Set to 0 to disable caching"""

    try:
        env_example_path = Path.cwd() / ".env.example"

        if env_example_path.exists():
            print(f".env.example already exists: {env_example_path}")
            return True

        env_example_path.write_text(env_example_content)
        print(f"Created .env.example: {env_example_path}")

        print("\n=== Environment Configuration Complete ===")
        print("[OK] .env.example created with all required variables")
        print("[OK] All variables documented with helpful comments")
        print("[OK] Placeholder values provided (no actual API keys)")

        return True

    except Exception as e:
        print(f"ERROR: Failed to create .env.example: {e}")
        return False


def main():
    """Main function to create the project directory structure and environment configuration."""
    print("=== Project Setup ===")

    # Create directory structure
    print("Step 1: Creating directory structure...")
    directory_success = create_directory_structure()

    # Create .env.example file
    print("\nStep 2: Creating environment configuration...")
    env_success = create_env_example()

    # Report final results
    if directory_success and env_success:
        print("\n=== Project Setup Complete ===")
        print("[OK] Directory structure created successfully")
        print("[OK] Environment configuration created successfully")
        print("\nNext steps:")
        print("1. Copy .env.example to .env")
        print("2. Update .env with your actual API keys and preferences")
        sys.exit(0)
    else:
        print("\n=== Project Setup Failed ===")
        if not directory_success:
            print("[FAILED] Directory structure creation")
        if not env_success:
            print("[FAILED] Environment configuration creation")
        sys.exit(1)


if __name__ == "__main__":
    main()