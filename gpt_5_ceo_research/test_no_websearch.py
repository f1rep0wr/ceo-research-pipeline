#!/usr/bin/env python3
"""
Test GPT-5 without web search to isolate issues.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.clients.gpt5_client import GPT5ResponsesClient
from src.config.settings import Settings


async def test_gpt5_basic():
    """Test basic GPT-5 functionality without web search."""

    print("Testing basic GPT-5 functionality...")

    # Initialize settings and client
    settings = Settings()
    client = GPT5ResponsesClient(settings)

    if not client.is_ready:
        print("❌ GPT-5 client not ready")
        return False

    try:
        # Simple test without web search
        print("Making simple GPT-5 API call...")
        response = await client.create_response(
            prompt='Return a simple JSON object: {"name": "Tim Cook", "company": "Apple", "title": "CEO"}',
            reasoning_effort="minimal"
        )

        print("✅ API call successful!")
        print(f"Response ID: {response.id}")

        # Extract text using correct structure
        if response.output and len(response.output) >= 2:
            text_content = response.output[1].content[0].text
            print(f"✅ Successfully extracted text: {text_content}")
            return True
        else:
            print("❌ Invalid response structure")
            return False

    except Exception as e:
        print(f"❌ API call failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_gpt5_basic())
    sys.exit(0 if success else 1)