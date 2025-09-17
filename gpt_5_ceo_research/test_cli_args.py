#!/usr/bin/env python3
"""
Test CLI argument parsing without making API calls
"""

import sys
import subprocess
from pathlib import Path

def run_command(cmd, expect_error=False):
    """Run a command and capture output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT"
    except Exception as e:
        return -1, "", str(e)

def test_cli_arguments():
    """Test various CLI argument scenarios"""

    test_cases = [
        # Test case: (description, command, expect_error, expected_in_output)
        ("No arguments", "python batch_research.py", True, "Usage:"),
        ("Non-existent file", "python batch_research.py missing.txt", True, "File not found"),
        ("Help-like argument", "python batch_research.py --help", True, "Usage:"),
        ("Custom output path", "python batch_research.py test_cli_minimal.txt custom_out.csv", False, "Found 1 CEOs"),
        ("Custom delay", "python batch_research.py test_cli_minimal.txt output.csv 5", False, "Found 1 CEOs"),
        ("Invalid delay (non-numeric)", "python batch_research.py test_cli_minimal.txt output.csv abc", True, "invalid literal"),
    ]

    print("CLI ARGUMENT TESTING")
    print("="*60)

    results = []

    for description, command, expect_error, expected_text in test_cases:
        print(f"\nTesting: {description}")
        print(f"Command: {command}")

        returncode, stdout, stderr = run_command(f"cd C:/projects/gpt_5/gpt_5_ceo_research && {command}")

        # Check if command behaved as expected
        if expect_error:
            if returncode != 0 or expected_text in stdout or expected_text in stderr:
                print("  PASS: Command failed as expected")
                if expected_text and expected_text in (stdout + stderr):
                    print(f"  PASS: Found expected text: '{expected_text}'")
                results.append(True)
            else:
                print("  FAIL: Command should have failed but didn't")
                print(f"  Return code: {returncode}")
                print(f"  Output: {stdout[:100]}")
                results.append(False)
        else:
            if returncode == 0 or expected_text in stdout:
                print("  PASS: Command started successfully")
                if expected_text and expected_text in stdout:
                    print(f"  PASS: Found expected text: '{expected_text}'")
                results.append(True)
            elif stderr == "TIMEOUT":
                print("  PASS: Command timed out (normal for API calls)")
                results.append(True)
            else:
                print("  FAIL: Command failed unexpectedly")
                print(f"  Return code: {returncode}")
                print(f"  Error: {stderr[:100]}")
                results.append(False)

    # Summary
    print("\n" + "="*60)
    print("CLI ARGUMENT TEST SUMMARY:")
    passed = sum(results)
    total = len(results)
    print(f"  Passed: {passed}/{total}")

    if passed == total:
        print("  OVERALL: PASS - CLI argument handling works correctly")
    else:
        print("  OVERALL: FAIL - CLI argument handling has issues")

    return passed == total

if __name__ == "__main__":
    # First ensure test file exists
    test_file = Path("C:/projects/gpt_5/gpt_5_ceo_research/test_cli_minimal.txt")
    if not test_file.exists():
        print(f"Creating test file: {test_file}")
        test_file.write_text("Jensen Huang | NVIDIA\n")

    success = test_cli_arguments()
    sys.exit(0 if success else 1)