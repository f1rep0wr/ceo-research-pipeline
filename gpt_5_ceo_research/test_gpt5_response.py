#!/usr/bin/env python
"""
Diagnostic script to understand GPT-5 response structure.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.clients.gpt5_client import GPT5ResponsesClient
from src.config.settings import Settings

async def diagnose_response_structure():
    """Test GPT-5 API and diagnose response structure."""

    # Load environment variables
    load_dotenv()

    # Initialize settings and client
    settings = Settings()
    client = GPT5ResponsesClient(settings)

    print("=" * 60)
    print("GPT-5 Response Structure Diagnostic")
    print("=" * 60)

    try:
        # Make a simple API call
        response = await client.create_response(
            prompt='Return exactly this JSON: ["test1", "test2", "test3"]',
            reasoning_effort='minimal'
        )

        print(f"\n1. Response type: {type(response)}")
        print(f"2. Response attributes: {dir(response)}")

        if hasattr(response, 'text'):
            print(f"\n3. response.text type: {type(response.text)}")
            print(f"4. response.text attributes: {dir(response.text)}")
            print(f"5. response.text as string: {str(response.text)}")

            # Try different ways to access the text
            print("\n" + "=" * 40)
            print("Attempting different access methods:")
            print("=" * 40)

            # Method 1: Direct string conversion
            try:
                text1 = str(response.text)
                print(f"[OK] str(response.text): {text1[:100]}")
            except Exception as e:
                print(f"[FAIL] str(response.text) failed: {e}")

            # Method 2: Check for 'value' attribute
            if hasattr(response.text, 'value'):
                try:
                    text2 = response.text.value
                    print(f"[OK] response.text.value: {text2[:100]}")
                except Exception as e:
                    print(f"[FAIL] response.text.value failed: {e}")
            else:
                print("[FAIL] response.text.value: attribute doesn't exist")

            # Method 3: Check for 'text' attribute
            if hasattr(response.text, 'text'):
                try:
                    text3 = response.text.text
                    print(f"[OK] response.text.text: {text3[:100]}")
                except Exception as e:
                    print(f"[FAIL] response.text.text failed: {e}")
            else:
                print("[FAIL] response.text.text: attribute doesn't exist")

            # Method 4: Check for __str__ method
            if hasattr(response.text, '__str__'):
                try:
                    text4 = response.text.__str__()
                    print(f"[OK] response.text.__str__(): {text4[:100]}")
                except Exception as e:
                    print(f"[FAIL] response.text.__str__() failed: {e}")

            # Method 5: Check if it's callable
            if callable(response.text):
                try:
                    text5 = response.text()
                    print(f"[OK] response.text(): {text5[:100]}")
                except Exception as e:
                    print(f"[FAIL] response.text() failed: {e}")
            else:
                print("[FAIL] response.text(): not callable")

            # Method 6: Try to get the actual object's __dict__
            if hasattr(response.text, '__dict__'):
                print(f"\nresponse.text.__dict__: {response.text.__dict__}")

        # Check for output attribute on response
        print("\n" + "=" * 40)
        print("Checking response.output:")
        print("=" * 40)
        if hasattr(response, 'output'):
            print(f"response.output type: {type(response.output)}")
            print(f"response.output: {response.output}")
            if hasattr(response.output, '__dict__'):
                print(f"response.output.__dict__: {response.output.__dict__}")
        else:
            print("[FAIL] response.output: attribute doesn't exist")

        print("\n" + "=" * 60)
        print("Diagnostic complete!")
        print("=" * 60)

    except Exception as e:
        print(f"\nError during diagnostic: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(diagnose_response_structure())