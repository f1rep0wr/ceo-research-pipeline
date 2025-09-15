#!/usr/bin/env python3
"""
Simple test to verify OpenAI Responses API access
"""

import asyncio
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

async def test_api():
    """Test basic API access."""

    # Load environment
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("[FAIL] No OPENAI_API_KEY found in environment")
        return

    print(f"[OK] API Key found: {api_key[:8]}...")

    # Create client
    client = AsyncOpenAI(api_key=api_key)

    try:
        # Test with simple prompt (no web search)
        print("\n1. Testing basic responses API...")
        response = await client.responses.create(
            model="gpt-4o",  # Use stable model
            input="Say 'API is working'"
        )

        # Extract text
        text = response.output[0].content[0].text
        print(f"[OK] Basic API response: {text}")

        # Test with web search
        print("\n2. Testing with web_search tool...")
        response_web = await client.responses.create(
            model="gpt-4o",
            input="What is the current date?",
            tools=[{"type": "web_search"}]
        )

        text_web = response_web.output[0].content[0].text
        print(f"[OK] Web search response: {text_web[:100]}...")

        print("\n[SUCCESS] API is fully functional!")

    except AttributeError as e:
        print(f"[FAIL] Response structure error: {e}")
        print("   The API might not support responses.create()")

    except Exception as e:
        print(f"[FAIL] API Error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    print("Testing OpenAI Responses API")
    print("="*40)
    asyncio.run(test_api())