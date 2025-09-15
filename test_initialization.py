#!/usr/bin/env python3
"""
Test script to validate complete project initialization and GPT-5 connection.

This script tests:
1. Environment configuration loading
2. Module imports
3. GPT-5 client initialization
4. Actual API connection test (if API key is available)

Following KISS principles - simple validation with clear success/failure reporting.
"""

import os
import sys
from pathlib import Path
import asyncio


def test_environment_setup():
    """Test that environment configuration can be loaded."""
    print("\n=== Testing Environment Setup ===")

    # Check that .env file exists
    env_path = Path.cwd() / ".env"
    if not env_path.exists():
        print(f"[FAILED] .env file not found at: {env_path}")
        return False

    print(f"[OK] .env file found at: {env_path}")

    # Load environment variables from .env
    try:
        from dotenv import load_dotenv
        load_dotenv(env_path)
        print("[OK] .env file loaded successfully")
    except Exception as e:
        print(f"[FAILED] Failed to load .env file: {e}")
        return False

    # Check required environment variables
    required_vars = [
        "OPENAI_API_KEY",
        "GPT5_MODEL",
        "LOG_LEVEL"
    ]

    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
        else:
            # Show first few characters for API key security
            value = os.getenv(var)
            if var == "OPENAI_API_KEY":
                display_value = f"{value[:12]}..." if len(value) > 12 else value
            else:
                display_value = value
            print(f"[OK] {var}: {display_value}")

    if missing_vars:
        print(f"[FAILED] Missing required environment variables: {', '.join(missing_vars)}")
        return False

    return True


def test_module_imports():
    """Test importing all project modules."""
    print("\n=== Testing Module Imports ===")

    # Add project source directory to Python path
    project_src = Path.cwd() / "gpt_5_ceo_research" / "src"
    if not project_src.exists():
        print(f"[FAILED] Project source directory not found: {project_src}")
        return False

    sys.path.insert(0, str(project_src))

    # Test settings import and loading
    try:
        from config.settings import get_settings, Settings
        settings = get_settings()
        print("[OK] config.settings - imported and instantiated")
        print(f"     Model: {settings.gpt5_model}")
        print(f"     Reasoning effort: {settings.default_reasoning_effort}")
        print(f"     Max retries: {settings.max_retries}")
    except Exception as e:
        print(f"[FAILED] config.settings import failed: {e}")
        return False

    # Test constants import
    try:
        from config import constants
        print("[OK] config.constants - imported successfully")
    except Exception as e:
        print(f"[FAILED] config.constants import failed: {e}")
        return False

    # Test logger import
    try:
        from utils.logger import setup_logger, get_logger
        logger = get_logger("test_initialization")
        print("[OK] utils.logger - imported successfully")
        logger.info("Logger test message")
        print("[OK] Logger functionality verified")
    except Exception as e:
        print(f"[FAILED] utils.logger import failed: {e}")
        return False

    # Test GPT5 client import
    try:
        from clients.gpt5_client import GPT5ResponsesClient
        client = GPT5ResponsesClient(settings)
        print("[OK] clients.gpt5_client - imported successfully")
        print(f"[OK] GPT5ResponsesClient instantiated, ready: {client.is_ready}")
        return True, client, settings
    except Exception as e:
        print(f"[FAILED] clients.gpt5_client import failed: {e}")
        return False

    return True


async def test_gpt5_connection(client, settings):
    """Test actual GPT-5 API connection."""
    print("\n=== Testing GPT-5 API Connection ===")

    if not client.is_ready:
        print("[SKIPPED] GPT-5 client not ready (no API key)")
        return False

    try:
        # Test basic connection
        print("Testing API connectivity...")
        success = await client.test_connection()

        if success:
            print("[OK] GPT-5 API connection test successful")

            # Test a simple API call
            print("Testing simple API call...")
            response = await client.create_response(
                prompt="Say 'Hello from GPT-5' to confirm the connection is working.",
                reasoning_effort="minimal"
            )

            if response:
                print("[OK] GPT-5 API call successful")
                print(f"     Response ID: {response.id}")
                print(f"     Model used: {response.model}")
                if hasattr(response, 'output') and hasattr(response.output, 'content'):
                    content = response.output.content[:100] + "..." if len(response.output.content) > 100 else response.output.content
                    print(f"     Response: {content}")
                return True
            else:
                print("[FAILED] GPT-5 API call returned no response")
                return False

        else:
            print("[FAILED] GPT-5 API connection test failed")
            return False

    except Exception as e:
        print(f"[FAILED] GPT-5 API test failed: {e}")
        return False


def test_directory_structure():
    """Verify all required directories and files exist."""
    print("\n=== Testing Directory Structure ===")

    base_path = Path.cwd() / "gpt_5_ceo_research"

    required_structure = {
        "src": True,
        "src/config": True,
        "src/clients": True,
        "src/utils": True,
        "tests": True,
        "scripts": True,
        "docs": True,
        "docker": True,
        "src/__init__.py": False,
        "src/config/__init__.py": False,
        "src/config/settings.py": False,
        "src/config/constants.py": False,
        "src/clients/__init__.py": False,
        "src/clients/gpt5_client.py": False,
        "src/utils/__init__.py": False,
        "src/utils/logger.py": False,
        "tests/__init__.py": False,
        "tests/conftest.py": False,
        "tests/test_initialization.py": False,
    }

    missing_items = []

    for item_path, is_directory in required_structure.items():
        full_path = base_path / item_path

        if is_directory:
            if not full_path.is_dir():
                missing_items.append(f"Directory: {item_path}")
            else:
                print(f"[OK] Directory exists: {item_path}")
        else:
            if not full_path.is_file():
                missing_items.append(f"File: {item_path}")
            else:
                print(f"[OK] File exists: {item_path}")

    if missing_items:
        print(f"[FAILED] Missing items:")
        for item in missing_items:
            print(f"         {item}")
        return False

    print("[OK] All required directories and files exist")
    return True


async def main():
    """Main test orchestration function."""
    print("GPT-5 CEO Research - Complete Setup Validation")
    print("=" * 60)

    # Track test results
    test_results = {}

    # Test 1: Directory Structure
    test_results["directory_structure"] = test_directory_structure()

    # Test 2: Environment Setup
    test_results["environment"] = test_environment_setup()

    # Test 3: Module Imports
    import_result = test_module_imports()
    if isinstance(import_result, tuple):
        test_results["imports"] = import_result[0]
        client = import_result[1]
        settings = import_result[2]
    else:
        test_results["imports"] = import_result
        client = None
        settings = None

    # Test 4: GPT-5 Connection (only if client is available)
    if client and test_results["imports"]:
        test_results["gpt5_connection"] = await test_gpt5_connection(client, settings)
    else:
        test_results["gpt5_connection"] = None
        print("\n[SKIPPED] GPT-5 connection test (client not available)")

    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    passed = 0
    total = 0

    for test_name, result in test_results.items():
        if result is None:
            status = "SKIPPED"
        elif result:
            status = "PASSED"
            passed += 1
            total += 1
        else:
            status = "FAILED"
            total += 1

        print(f"{test_name.replace('_', ' ').title():<25}: {status}")

    print("-" * 60)
    print(f"Overall Status: {passed}/{total} tests passed")

    if passed == total:
        print("\n[SUCCESS] All validation tests passed!")
        print("The GPT-5 CEO Research project is fully initialized and ready to use.")
        return True
    else:
        print(f"\n[PARTIAL] {total - passed} test(s) failed.")
        print("Please check the failed tests above and resolve any issues.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)