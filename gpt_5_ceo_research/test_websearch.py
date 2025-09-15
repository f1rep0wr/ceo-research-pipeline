#!/usr/bin/env python3
"""
Test script for CEO Web Search using OpenAI Responses API
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.ceo_research_gpt5 import research_ceo_with_websearch


async def test_ceo_research():
    """Test the CEO research with web search."""

    test_cases = [
        ("Tim Cook", "Apple"),
        ("Satya Nadella", "Microsoft"),
        ("Jensen Huang", "NVIDIA")
    ]

    for ceo_name, company_name in test_cases:
        print(f"\n{'='*60}")
        print(f"Testing: {ceo_name} at {company_name}")
        print('='*60)

        try:
            profile = await research_ceo_with_websearch(ceo_name, company_name)

            print(f"✓ CEO Name: {profile.ceo_name}")
            print(f"✓ Company: {profile.company_name}")

            if profile.ceo_title:
                print(f"  Title: {profile.ceo_title}")
            if profile.insider_outsider:
                print(f"  Type: {profile.insider_outsider}")
            if profile.appointment_date:
                print(f"  Appointed: {profile.appointment_date}")
            if profile.tenure_years:
                print(f"  Tenure: {profile.tenure_years} years")

            print(f"  Confidence: {profile.confidence_score:.2f}")
            print(f"  Completeness: {profile.data_completeness}")

            # Count non-null fields
            data = profile.model_dump()
            populated = sum(1 for v in data.values() if v is not None)
            print(f"  Fields Populated: {populated}/49")

        except Exception as e:
            print(f"✗ Error: {str(e)}")


if __name__ == "__main__":
    print("CEO Research Test with OpenAI Responses API Web Search")
    print("Note: This requires a valid OpenAI API key with access to GPT-5/GPT-4o")

    asyncio.run(test_ceo_research())