#!/usr/bin/env python3
"""Test the fixed extraction function with a mock response."""

import sys
sys.path.insert(0, '.')

from src.ceo_research_gpt5 import _extract_text_from_response

class MockContent:
    def __init__(self, text):
        self.text = text

class MockOutputItem:
    def __init__(self, text):
        self.content = [MockContent(text)]

class MockResponse:
    def __init__(self, text_at_index_1=None, text_at_index_0=None):
        self.output = []
        if text_at_index_0:
            self.output.append(MockOutputItem(text_at_index_0))
        if text_at_index_1:
            # Add dummy item at index 0 if we have text at index 1
            if not text_at_index_0:
                self.output.append(MockOutputItem("dummy"))
            self.output.append(MockOutputItem(text_at_index_1))

def test_extraction():
    print("Testing GPT-5 response extraction fix...")
    print("-" * 50)

    # Test 1: Web search response (text at index 1)
    print("\n1. Testing web search response (text at index 1):")
    response1 = MockResponse(text_at_index_1='{"ceo_name": "Test CEO", "company_name": "Test Corp"}')
    result1 = _extract_text_from_response(response1)
    print(f"   Result: {result1}")
    assert result1 == '{"ceo_name": "Test CEO", "company_name": "Test Corp"}', "Failed to extract from index 1"
    print("   [PASS]")

    # Test 2: Non-web search response (text at index 0)
    print("\n2. Testing non-web search response (text at index 0):")
    response2 = MockResponse(text_at_index_0='{"ceo_name": "Another CEO", "company_name": "Another Corp"}')
    result2 = _extract_text_from_response(response2)
    print(f"   Result: {result2}")
    assert result2 == '{"ceo_name": "Another CEO", "company_name": "Another Corp"}', "Failed to extract from index 0"
    print("   [PASS]")

    # Test 3: Empty response
    print("\n3. Testing empty response:")
    response3 = MockResponse()
    result3 = _extract_text_from_response(response3)
    print(f"   Result: {result3}")
    assert result3 is None, "Should return None for empty response"
    print("   [PASS]")

    # Test 4: Fallback to output_text
    print("\n4. Testing output_text fallback:")
    response4 = MockResponse()
    response4.output_text = '{"ceo_name": "Fallback CEO", "company_name": "Fallback Corp"}'
    result4 = _extract_text_from_response(response4)
    print(f"   Result: {result4}")
    assert result4 == '{"ceo_name": "Fallback CEO", "company_name": "Fallback Corp"}', "Failed to use output_text fallback"
    print("   [PASS]")

    print("\n" + "=" * 50)
    print("All tests passed! The extraction fix is working correctly.")
    print("The function now:")
    print("  1. Checks response.output[1] first (for web search)")
    print("  2. Falls back to response.output[0] (no web search)")
    print("  3. Falls back to response.output_text")
    print("  4. Returns None instead of garbage config strings")

if __name__ == "__main__":
    test_extraction()