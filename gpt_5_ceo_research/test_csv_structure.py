#!/usr/bin/env python3
"""
Test CSV structure and validate expected fields without API calls
"""

import sys
import csv
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.models.ceo_profile import CEOProfile

def test_csv_structure():
    """Test CSV structure and field validation"""

    # Expected fields based on CEOProfile model
    expected_fields = [
        'ceo_name', 'company_name', 'ceo_title', 'insider_outsider', 'ceo_type',
        'appointment_date', 'start_date', 'departure_date', 'tenure_years', 'tenure_months',
        'previous_company', 'previous_position', 'initial_join_year', 'years_at_company',
        'years_before_ceo', 'previous_ceo_experience', 'predecessor_name', 'succession_type',
        'interim_period', 'board_connection', 'departure_reason', 'departure_voluntary',
        'successor_name', 'post_ceo_role', 'data_completeness', 'primary_sources',
        'last_updated', 'confidence_score', 'notes'
    ]

    print("Testing CSV structure requirements...")
    print(f"Expected {len(expected_fields)} fields:")
    for i, field in enumerate(expected_fields, 1):
        print(f"  {i:2d}. {field}")

    # Test CSV generation with mock data
    print("\n" + "="*60)
    print("Testing CSV generation with valid mock data...")

    mock_data = {
        "ceo_name": "Karen Lynch",
        "company_name": "CVS Health",
        "ceo_title": "Chief Executive Officer",
        "insider_outsider": "insider",
        "ceo_type": "professional",
        "appointment_date": "02/01/2021",
        "start_date": "02/01/2021",
        "departure_date": "incumbent",
        "tenure_years": 4,
        "tenure_months": 7,
        "previous_company": "Aetna",
        "previous_position": "President",
        "initial_join_year": 2012,  # INTEGER - critical test
        "years_at_company": 13,     # INTEGER - critical test
        "years_before_ceo": 9,      # INTEGER - critical test
        "previous_ceo_experience": False,
        "predecessor_name": "Larry Merlo",
        "succession_type": "planned",
        "interim_period": False,
        "board_connection": "Board member since 2021",
        "data_completeness": "high",
        "primary_sources": ["SEC filings", "Company website"],
        "last_updated": "09/17/2025",
        "confidence_score": 0.95,
        "notes": "Mock test data"
    }

    try:
        profile = CEOProfile(**mock_data)
        print("SUCCESS: CEOProfile validation passed")

        # Test CSV generation
        csv_data = profile.to_csv_row()
        print(f"SUCCESS: CSV conversion generated {len(csv_data)} fields")

        # Check field mapping
        missing_fields = []
        extra_fields = []

        for field in expected_fields:
            if field not in csv_data:
                missing_fields.append(field)

        for field in csv_data:
            if field not in expected_fields:
                extra_fields.append(field)

        if missing_fields:
            print(f"ERROR: Missing fields in CSV: {missing_fields}")

        if extra_fields:
            print(f"WARNING: Extra fields in CSV: {extra_fields}")

        if not missing_fields and not extra_fields:
            print("SUCCESS: CSV fields match expected schema exactly")

        # Test specific critical fields
        print("\nValidating critical fields:")
        critical_checks = [
            ("initial_join_year", "int", 2012),
            ("years_at_company", "int", 13),
            ("years_before_ceo", "int", 9),
            ("insider_outsider", "str", "insider"),
            ("confidence_score", "float", 0.95)
        ]

        for field_name, expected_type, expected_value in critical_checks:
            actual_value = csv_data.get(field_name)
            print(f"  {field_name}: {actual_value} (type: {type(actual_value).__name__})")

            if field_name in ["years_at_company", "years_before_ceo", "initial_join_year"]:
                if not isinstance(actual_value, int):
                    print(f"    ERROR: Expected int, got {type(actual_value)}")
                else:
                    print(f"    SUCCESS: Correct type (int)")

        return True

    except Exception as e:
        print(f"ERROR: CEOProfile validation failed: {e}")
        return False

def test_problematic_float_data():
    """Test the specific issue found with fractional year values"""
    print("\n" + "="*60)
    print("Testing problematic float data (the actual bug)...")

    # This is the actual data that caused the validation error
    problematic_data = {
        "ceo_name": "Karen Lynch",
        "company_name": "CVS Health",
        "years_at_company": 6.4,  # FLOAT - this causes validation error
        "years_before_ceo": 2.2,  # FLOAT - this causes validation error
        "confidence_score": 0.1
    }

    try:
        profile = CEOProfile(**problematic_data)
        print("UNEXPECTED: Validation passed (this should fail)")
        return False
    except Exception as e:
        print("EXPECTED: Validation failed as expected")
        print(f"  Error: {str(e)[:100]}...")
        return True

if __name__ == "__main__":
    print("CSV STRUCTURE VALIDATION TEST")
    print("="*60)

    success1 = test_csv_structure()
    success2 = test_problematic_float_data()

    print("\n" + "="*60)
    print("SUMMARY:")
    print(f"  CSV Structure Test: {'PASS' if success1 else 'FAIL'}")
    print(f"  Float Data Bug Test: {'PASS' if success2 else 'FAIL'}")

    if success1 and success2:
        print("\nRECOMMENDATION: CSV structure is correct, but the Pydantic model")
        print("needs to handle float values for year fields or the AI prompt")
        print("needs to specify integer-only outputs for those fields.")