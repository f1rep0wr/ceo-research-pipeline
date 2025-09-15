#!/usr/bin/env python3
"""
Test script to verify the correct OpenAI Responses API format for web search.
Tests both web search and fallback scenarios.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config.settings import get_settings
from openai import AsyncOpenAI, OpenAIError


async def test_api_call_format():
    """Test the basic API call format to ensure it works."""

    try:
        # Get settings
        settings = get_settings()
        client = AsyncOpenAI(api_key=settings.openai_api_key)

        print("=" * 60)
        print("Testing OpenAI Responses API Call Format")
        print("=" * 60)

        # Test 1: Simple API call without web search
        print("\n1. Testing simple API call (no web search)...")
        try:
            response = await client.responses.create(
                model=settings.gpt5_model,
                input="Return exactly: {'test': 'success'}",
                reasoning={"effort": "minimal"},
                text={"verbosity": "low"}
            )

            print(f"[OK] Simple API call successful")
            print(f"  Response type: {type(response)}")
            print(f"  Response attributes: {[attr for attr in dir(response) if not attr.startswith('_')]}")

            # Try different ways to access text
            text_content = None
            access_method = None

            if hasattr(response, 'output_text'):
                text_content = response.output_text
                access_method = "response.output_text"
            elif hasattr(response, 'text'):
                if hasattr(response.text, 'value'):
                    text_content = response.text.value
                    access_method = "response.text.value"
                elif hasattr(response.text, 'text'):
                    text_content = response.text.text
                    access_method = "response.text.text"
                else:
                    text_content = str(response.text)
                    access_method = "str(response.text)"

            if text_content:
                print(f"[OK] Text accessed via: {access_method}")
                print(f"  Content preview: {text_content[:100]}...")
            else:
                print("[FAIL] Could not access text content")

        except Exception as e:
            print(f"[FAIL] Simple API call failed: {e}")
            return False

        # Test 2: API call with web search (expect failure with GPT-5)
        print("\n2. Testing web search API call...")
        try:
            response = await client.responses.create(
                model=settings.gpt5_model,
                input="What is the current weather in New York?",
                tools=[{"type": "web_search_preview"}],
                reasoning={"effort": "minimal"},
                text={"verbosity": "low"}
            )

            print(f"[OK] Web search API call successful (unexpected!)")

            # Try to access text
            if hasattr(response, 'output_text'):
                print(f"  Content preview: {response.output_text[:100]}...")

        except Exception as e:
            print(f"[FAIL] Web search API call failed (expected): {e}")

            # Check if it's the known GPT-5 incompatibility
            if "not supported" in str(e).lower() and "gpt-5" in str(e).lower():
                print("  This is the known GPT-5 web search incompatibility issue")

        # Test 3: Try alternative web search tool name
        print("\n3. Testing alternative web search tool name...")
        try:
            response = await client.responses.create(
                model=settings.gpt5_model,
                input="What is the current weather in New York?",
                tools=[{"type": "web_search"}],  # Without "_preview"
                reasoning={"effort": "minimal"},
                text={"verbosity": "low"}
            )

            print(f"[OK] Alternative web search successful!")

        except Exception as e:
            print(f"[FAIL] Alternative web search failed: {e}")

        print("\n" + "=" * 60)
        print("API Format Test Complete")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"Test setup failed: {e}")
        return False


if __name__ == "__main__":
    print("Testing OpenAI Responses API format for GPT-5")
    success = asyncio.run(test_api_call_format())

    if success:
        print("\n[OK] Basic API connectivity confirmed")
    else:
        print("\n[FAIL] API test failed")