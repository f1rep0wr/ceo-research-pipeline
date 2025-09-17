#!/usr/bin/env python3
"""
Test script to reproduce the validation issue
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.models.ceo_profile import CEOProfile

def test_validation_issue():
    """Test the specific validation issue found in Karen Lynch case"""

    # Simulate the data that caused the validation error
    test_data = {
        "ceo_name": "Karen Lynch",
        "company_name": "CVS Health",
        "years_at_company": 6.4,  # This caused validation error
        "years_before_ceo": 2.2,  # This caused validation error
        "confidence_score": 0.85
    }

    print("Testing data validation with fractional years...")
    print(f"Input data: {test_data}")

    try:
        profile = CEOProfile(**test_data)
        print("SUCCESS: Validation passed")
        print(f"  years_at_company: {profile.years_at_company} (type: {type(profile.years_at_company)})")
        print(f"  years_before_ceo: {profile.years_before_ceo} (type: {type(profile.years_before_ceo)})")
    except Exception as e:
        print("VALIDATION ERROR:")
        print(f"  {e}")
        print("\nThis is the root cause of the issue!")

    # Test with integer values
    print("\n" + "="*50)
    print("Testing with integer values...")
    test_data_int = test_data.copy()
    test_data_int["years_at_company"] = 6
    test_data_int["years_before_ceo"] = 2

    try:
        profile = CEOProfile(**test_data_int)
        print("SUCCESS: Integer validation passed")
        print(f"  years_at_company: {profile.years_at_company} (type: {type(profile.years_at_company)})")
        print(f"  years_before_ceo: {profile.years_before_ceo} (type: {type(profile.years_before_ceo)})")
    except Exception as e:
        print("VALIDATION ERROR:")
        print(f"  {e}")

if __name__ == "__main__":
    test_validation_issue()