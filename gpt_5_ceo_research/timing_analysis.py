#!/usr/bin/env python3
"""
CEO Research Timing Analysis Script

This script analyzes where the 10-minute duration for CEO research comes from.
It measures the time taken by each stage of the research process.
"""

import asyncio
import time
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.ceo_research_progressive import ProgressiveCEOResearcher
from src.ceo_research_gpt5 import research_ceo_with_websearch
from src.config.settings import Settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TimingAnalyzer:
    """Analyze timing of CEO research process."""

    def __init__(self):
        self.timings: List[Dict[str, Any]] = []
        self.settings = Settings()
        self.researcher = ProgressiveCEOResearcher(self.settings)

    async def analyze_progressive_research(self, ceo_name: str, company_name: str) -> Dict[str, Any]:
        """Analyze timing for progressive research method."""

        print(f"\n{'='*60}")
        print(f"TIMING ANALYSIS: Progressive Research Method")
        print(f"CEO: {ceo_name}, Company: {company_name}")
        print(f"{'='*60}\n")

        total_start = time.time()
        stage_timings = {}

        try:
            # Stage 1: Basic Information
            print("Stage 1: Basic Information & Classification...")
            stage1_start = time.time()
            basic_info = await self.researcher._run_basic_research(
                ceo_name, company_name, "medium"
            )
            stage1_time = time.time() - stage1_start
            stage_timings['basic_info'] = stage1_time
            print(f"  ✓ Completed in {stage1_time:.2f} seconds")

            # Stage 2: Career Details
            if basic_info:
                print("\nStage 2: Career Details...")
                stage2_start = time.time()
                career_stage = self.researcher.prompts.should_use_insider_or_outsider_career(basic_info)
                career_info = await self.researcher._run_career_research(
                    ceo_name, company_name, basic_info, career_stage, "medium"
                )
                stage2_time = time.time() - stage2_start
                stage_timings['career_details'] = stage2_time
                print(f"  ✓ Completed in {stage2_time:.2f} seconds")

                # Stage 3: Succession Details
                print("\nStage 3: Succession Details...")
                stage3_start = time.time()
                succession_info = await self.researcher._run_succession_research(
                    ceo_name, company_name, basic_info, "medium"
                )
                stage3_time = time.time() - stage3_start
                stage_timings['succession'] = stage3_time
                print(f"  ✓ Completed in {stage3_time:.2f} seconds")

                # Stage 4: Post-CEO Details
                print("\nStage 4: Post-CEO Details...")
                stage4_start = time.time()
                post_ceo_info = await self.researcher._run_post_ceo_research(
                    ceo_name, company_name, basic_info, "medium"
                )
                stage4_time = time.time() - stage4_start
                stage_timings['post_ceo'] = stage4_time
                print(f"  ✓ Completed in {stage4_time:.2f} seconds")

        except Exception as e:
            print(f"\n✗ Error during analysis: {e}")
            stage_timings['error'] = str(e)

        total_time = time.time() - total_start

        # Summary
        print(f"\n{'='*60}")
        print("TIMING SUMMARY")
        print(f"{'='*60}")

        total_stages_time = sum(v for v in stage_timings.values() if isinstance(v, (int, float)))

        for stage, timing in stage_timings.items():
            if isinstance(timing, (int, float)):
                percentage = (timing / total_time) * 100
                print(f"  {stage:20s}: {timing:7.2f}s ({percentage:5.1f}%)")

        print(f"{'  '*10}{'-'*30}")
        print(f"  {'Total API calls':20s}: {total_stages_time:7.2f}s")
        print(f"  {'Total elapsed':20s}: {total_time:7.2f}s")
        print(f"  {'Overhead':20s}: {(total_time - total_stages_time):7.2f}s")

        # Convert to minutes if > 60 seconds
        if total_time > 60:
            print(f"\n  Total time: {total_time/60:.2f} minutes")

        return {
            'method': 'progressive',
            'ceo_name': ceo_name,
            'company_name': company_name,
            'stage_timings': stage_timings,
            'total_time': total_time,
            'total_stages_time': total_stages_time,
            'overhead': total_time - total_stages_time
        }

    async def analyze_comprehensive_research(self, ceo_name: str, company_name: str) -> Dict[str, Any]:
        """Analyze timing for comprehensive research method."""

        print(f"\n{'='*60}")
        print(f"TIMING ANALYSIS: Comprehensive Research Method")
        print(f"CEO: {ceo_name}, Company: {company_name}")
        print(f"{'='*60}\n")

        print("Running single comprehensive query...")
        start_time = time.time()

        try:
            profile = await self.researcher.research_ceo_comprehensive(
                ceo_name, company_name, "medium"
            )
            success = True
            error_msg = None
        except Exception as e:
            success = False
            error_msg = str(e)
            print(f"✗ Error: {e}")

        total_time = time.time() - start_time

        if success:
            print(f"✓ Completed in {total_time:.2f} seconds")

        # Convert to minutes if > 60 seconds
        if total_time > 60:
            print(f"\nTotal time: {total_time/60:.2f} minutes")

        return {
            'method': 'comprehensive',
            'ceo_name': ceo_name,
            'company_name': company_name,
            'total_time': total_time,
            'success': success,
            'error': error_msg
        }

    def print_comparison(self, results: List[Dict[str, Any]]):
        """Print comparison of different methods."""

        print(f"\n{'='*60}")
        print("METHOD COMPARISON")
        print(f"{'='*60}")

        for result in results:
            method = result['method']
            total_time = result['total_time']
            minutes = total_time / 60

            print(f"\n{method.upper()} Method:")
            print(f"  Total time: {total_time:.2f} seconds ({minutes:.2f} minutes)")

            if method == 'progressive' and 'stage_timings' in result:
                print("  Breakdown by stage:")
                for stage, timing in result['stage_timings'].items():
                    if isinstance(timing, (int, float)):
                        print(f"    - {stage}: {timing:.2f}s")

        print(f"\n{'='*60}")
        print("KEY FINDINGS:")
        print(f"{'='*60}")

        # Calculate average times
        prog_times = [r['total_time'] for r in results if r['method'] == 'progressive']
        comp_times = [r['total_time'] for r in results if r['method'] == 'comprehensive']

        if prog_times:
            avg_prog = sum(prog_times) / len(prog_times)
            print(f"  Average progressive time: {avg_prog:.2f}s ({avg_prog/60:.2f} minutes)")

        if comp_times:
            avg_comp = sum(comp_times) / len(comp_times)
            print(f"  Average comprehensive time: {avg_comp:.2f}s ({avg_comp/60:.2f} minutes)")

        # Explain why it might take 10 minutes
        print(f"\n{'='*60}")
        print("WHY DOES IT TAKE ~10 MINUTES?")
        print(f"{'='*60}")
        print("""
The 10-minute duration likely comes from:

1. **GPT-5 Reasoning with Web Search**:
   - Each API call with web search enabled takes significant time
   - GPT-5 performs multiple web searches per stage
   - Web search adds latency for fetching and processing pages

2. **Progressive Method (4 stages)**:
   - Basic Info: ~1-2 minutes (web searches for company, role)
   - Career Details: ~2-3 minutes (extensive career history search)
   - Succession: ~2-3 minutes (predecessor, transition details)
   - Post-CEO: ~2-3 minutes (departure, successor, current role)

3. **Network and Processing Overhead**:
   - API request/response latency
   - JSON parsing and validation
   - Retry logic for failed requests (up to 3 attempts)

4. **High/Medium Reasoning Effort**:
   - Higher reasoning effort = more compute time
   - "medium" effort balances speed vs accuracy
   - "high" effort could push to 15+ minutes

5. **Rate Limiting Considerations**:
   - Batch processing adds 2-second delays between CEOs
   - Prevents API throttling but adds to total time

The ~10 minute estimate appears accurate for thorough research
with multiple web searches and medium reasoning effort.
        """)


async def main():
    """Run timing analysis."""

    analyzer = TimingAnalyzer()
    results = []

    # Test cases
    test_cases = [
        ("Jamie Dimon", "JPMorgan Chase"),
        # Add more if needed for averaging
    ]

    for ceo_name, company_name in test_cases:
        # Test progressive method
        try:
            prog_result = await analyzer.analyze_progressive_research(ceo_name, company_name)
            results.append(prog_result)
        except Exception as e:
            print(f"Failed progressive research: {e}")

        # Test comprehensive method
        try:
            comp_result = await analyzer.analyze_comprehensive_research(ceo_name, company_name)
            results.append(comp_result)
        except Exception as e:
            print(f"Failed comprehensive research: {e}")

    # Print comparison
    if results:
        analyzer.print_comparison(results)


if __name__ == "__main__":
    print("\nStarting CEO Research Timing Analysis...")
    print("This will make real API calls and may take several minutes.\n")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user.")
    except Exception as e:
        print(f"\nAnalysis failed: {e}")