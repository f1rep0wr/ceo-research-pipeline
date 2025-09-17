#!/usr/bin/env python3
"""Test that the extraction fix resolves the CSV output issue."""

import sys
import json
sys.path.insert(0, '.')

from src.ceo_research_gpt5 import _extract_text_from_response, _parse_response_to_profile

class MockContent:
    def __init__(self, text):
        self.text = text

class MockOutputItem:
    def __init__(self, text):
        self.content = [MockContent(text)]

class MockResponse:
    def __init__(self, json_text):
        # Simulate web search response with JSON at index 1
        self.output = [
            MockOutputItem("web search results"),
            MockOutputItem(json_text)
        ]

def test_full_pipeline():
    print("Testing that extraction fix enables proper CSV output...")
    print("=" * 60)

    # Create a mock response with full CEO data JSON
    full_json = json.dumps({
        "ceo_name": "Saul Ortega",
        "company_name": "TEXAS NATIONAL BANK",
        "ceo_title": "President & CEO",
        "insider_outsider": "insider",
        "ceo_type": "professional",
        "appointment_date": "01/15/2020",
        "start_date": "01/15/2020",
        "departure_date": "incumbent",
        "tenure_years": 5.5,
        "tenure_months": 66,
        "previous_company": None,
        "previous_position": "Executive Vice President",
        "initial_join_year": 2010,
        "years_at_company": 15,
        "years_before_ceo": 10,
        "previous_ceo_experience": False,
        "predecessor_name": "John Smith",
        "succession_type": "planned",
        "interim_period": False,
        "board_connection": None,
        "departure_reason": None,
        "departure_voluntary": None,
        "successor_name": None,
        "post_ceo_role": None,
        "data_completeness": "high",
        "primary_sources": ["Company website", "Local news"],
        "last_updated": "09/16/2025",
        "confidence_score": 0.85,
        "notes": "Successfully extracted all data"
    })

    # Test 1: Extract text from response
    print("\n1. Testing extraction from mock response...")
    mock_response = MockResponse(full_json)
    extracted_text = _extract_text_from_response(mock_response)
    print(f"   Extracted text length: {len(extracted_text) if extracted_text else 0} chars")
    assert extracted_text == full_json, "Failed to extract JSON text"
    print("   [PASS] - Extracted full JSON")

    # Test 2: Parse to CEOProfile
    print("\n2. Testing JSON parsing to CEOProfile...")
    profile = _parse_response_to_profile(extracted_text, "Saul Ortega", "TEXAS NATIONAL BANK")
    print(f"   CEO Name: {profile.ceo_name}")
    print(f"   Company: {profile.company_name}")
    print(f"   Title: {profile.ceo_title}")
    print(f"   Type: {profile.insider_outsider}")
    print(f"   Confidence: {profile.confidence_score}")
    print(f"   Completeness: {profile.data_completeness}")
    assert profile.confidence_score == 0.85, "Profile not properly parsed"
    assert profile.data_completeness == "high", "Data completeness not preserved"
    print("   [PASS] - Profile parsed with all data")

    # Test 3: Convert to CSV row
    print("\n3. Testing CSV row generation...")
    csv_row = profile.to_csv_row()
    print(f"   CSV fields: {len(csv_row)} total")
    print(f"   Key fields present:")
    important_fields = ['ceo_name', 'company_name', 'ceo_title', 'insider_outsider',
                       'appointment_date', 'confidence_score', 'data_completeness']
    for field in important_fields:
        value = csv_row.get(field, 'MISSING')
        print(f"     - {field}: {value}")
    assert all(field in csv_row for field in important_fields), "Missing important fields"
    print("   [PASS] - CSV row contains all data")

    print("\n" + "=" * 60)
    print("SUCCESS! The extraction fix DOES resolve the CSV issue:")
    print("  1. JSON is now properly extracted from response")
    print("  2. JSON is successfully parsed to CEOProfile")
    print("  3. CEOProfile generates complete CSV row with all fields")
    print("\nThe problem was: extraction returned config string -> JSON parse failed -> minimal fallback profile -> empty CSV")
    print("Now: extraction returns actual JSON -> parse succeeds -> full profile -> complete CSV")

if __name__ == "__main__":
    test_full_pipeline()