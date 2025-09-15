#!/usr/bin/env python3
"""
Test GPT-5 with high reasoning effort to see if web search works.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.clients.gpt5_client import GPT5ResponsesClient
from src.config.settings import Settings


async def test_high_reasoning():
    """Test GPT-5 with high reasoning effort and web search."""

    print("Testing GPT-5 with HIGH reasoning effort and web search...")

    settings = Settings()
    client = GPT5ResponsesClient(settings)

    if not client.is_ready:
        print("❌ GPT-5 client not ready")
        return False

    try:
        # Test with HIGH reasoning effort
        print("Making GPT-5 API call with HIGH reasoning effort...")
        response = await client.create_response(
            prompt="Find the current stock price of Apple (AAPL) and return just the price in JSON format like: {'symbol': 'AAPL', 'price': 123.45}",
            reasoning_effort="high",
            tools=[{"type": "web_search"}],
            verbosity="low"
        )

        print("✅ API call with HIGH reasoning successful!")
        print(f"Response ID: {response.id}")

        # Extract text
        if hasattr(response, 'output_text'):
            print(f"✅ Response text: {response.output_text}")
            return True
        else:
            print("❌ Could not extract response text")
            return False

    except Exception as e:
        print(f"❌ API call failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_high_reasoning())
    sys.exit(0 if success else 1)