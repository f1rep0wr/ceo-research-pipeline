#!/usr/bin/env python3
"""
Quick test to verify the GPT-5 CEO research pipeline is working.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.ceo_research_gpt5 import research_ceo_with_websearch


async def quick_test():
    """Quick test with minimal reasoning."""

    print("Testing GPT-5 CEO research pipeline...")
    print("This should verify:")
    print("- GPT5ResponsesClient is working")
    print("- Web search tools are enabled")
    print("- Response parsing is correct")
    print("-" * 50)

    try:
        # Test with medium reasoning effort
        profile = await research_ceo_with_websearch(
            "Tim Cook",
            "Apple",
            reasoning_effort="medium"
        )

        print("✅ SUCCESS: Pipeline completed!")
        print(f"CEO: {profile.ceo_name}")
        print(f"Company: {profile.company_name}")
        print(f"Title: {profile.ceo_title}")
        print(f"Industry: {profile.industry}")
        print(f"Confidence: {profile.confidence_score}")
        print(f"Data completeness: {profile.data_completeness}")
        print(f"Sources count: {len(profile.primary_sources) if profile.primary_sources else 0}")

        if profile.primary_sources:
            print("Sources used:")
            for source in profile.primary_sources[:3]:  # Show first 3 sources
                print(f"  - {source}")

        return True

    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(quick_test())
    sys.exit(0 if success else 1)