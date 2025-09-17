#!/usr/bin/env python3
"""
Batch CEO Research Tool - KISS Implementation

Reads a plain text file with CEOs and processes them sequentially.
Continues on errors. Simple and reliable.

Usage:
    python batch_research.py ceos.txt
    python batch_research.py ceos.txt --output custom.csv
    python batch_research.py ceos.txt --delay 3

Input file format:
    Tim Cook | Apple
    Mary Barra | General Motors
    # Comments are supported
    Satya Nadella | Microsoft
"""

import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.ceo_research_gpt5 import research_ceo_with_websearch
from src.models.ceo_profile import CEOProfile
from src.utils.logger import get_logger
import csv


async def batch_research(input_file: str, output_file: str = None, delay: int = 2):
    """
    Process multiple CEOs from a text file.

    Args:
        input_file: Path to text file with CEO list
        output_file: Output CSV path (default: output/ceo_research.csv)
        delay: Seconds to wait between requests
    """
    logger = get_logger(__name__)

    # Default output
    if output_file is None:
        output_file = "output/ceo_research.csv"

    # Read input file
    ceo_list = []
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue

                # Parse CEO | Company
                if '|' not in line:
                    print(f"[WARNING] Line {line_num} invalid format (need 'Name | Company'): {line}")
                    continue

                parts = line.split('|')
                if len(parts) != 2:
                    print(f"[WARNING] Line {line_num} invalid format: {line}")
                    continue

                ceo_name = parts[0].strip()
                company = parts[1].strip()

                if ceo_name and company:
                    ceo_list.append((ceo_name, company))

    except FileNotFoundError:
        print(f"[ERROR] File not found: {input_file}")
        return
    except Exception as e:
        print(f"[ERROR] Error reading file: {e}")
        return

    if not ceo_list:
        print("[ERROR] No valid CEOs found in input file")
        return

    print(f"[INFO] Found {len(ceo_list)} CEOs to research")
    print(f"[INFO] Output will be saved to: {output_file}\n")

    # Ensure output directory exists
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    # Process each CEO
    successful = 0
    failed = []

    for i, (ceo_name, company) in enumerate(ceo_list, 1):
        print(f"[{i}/{len(ceo_list)}] Researching {ceo_name} at {company}...", end="", flush=True)

        try:
            # Research CEO
            profile = await research_ceo_with_websearch(ceo_name, company)

            # Save to CSV
            await _save_to_csv(profile, output_file)

            successful += 1
            print(f" [OK] (confidence: {profile.confidence_score:.2f})")

        except Exception as e:
            failed.append((ceo_name, company))
            logger.error(f"Failed: {ceo_name} at {company} - {e}")
            print(f" [FAILED] (error: {str(e)[:50]})")

        # Delay between requests (except last)
        if i < len(ceo_list) and delay > 0:
            time.sleep(delay)

    # Summary
    print("\n" + "="*50)
    print(f"[COMPLETE] Successfully researched: {successful}/{len(ceo_list)}")

    if failed:
        print(f"[FAILED] Failed to research: {len(failed)}")
        for ceo, company in failed[:5]:  # Show first 5 failures
            print(f"   - {ceo} ({company})")
        if len(failed) > 5:
            print(f"   ... and {len(failed)-5} more")

    print(f"\n[OUTPUT] Results saved to: {Path(output_file).absolute()}")


async def _save_to_csv(profile: CEOProfile, output_file: str):
    """Append profile to CSV file."""
    file_exists = Path(output_file).exists()

    # Get CSV row
    csv_data = profile.to_csv_row()

    # Write to CSV
    with open(output_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=csv_data.keys())

        # Write header if new file
        if not file_exists:
            writer.writeheader()

        writer.writerow(csv_data)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python batch_research.py <input_file.txt> [output.csv] [delay_seconds]")
        print("\nExample input file:")
        print("  Tim Cook | Apple")
        print("  Mary Barra | General Motors")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    delay = int(sys.argv[3]) if len(sys.argv) > 3 else 2

    # Run async
    asyncio.run(batch_research(input_file, output_file, delay))


if __name__ == "__main__":
    main()