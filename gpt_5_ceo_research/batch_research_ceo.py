#!/usr/bin/env python3
"""
Batch CEO Research Processor

KISS-compliant batch processor that reads a text file with CEO/Bank pairs
and processes them autonomously with graceful error handling.

Input Format (text file):
    CEO Name 1|Bank Name 1
    CEO Name 2|Bank Name 2
    CEO Name 3|Bank Name 3

Features:
- Graceful error handling (continues to next CEO on errors)
- Progress tracking and reporting
- All existing research functionalities preserved
- Configurable research method and settings
- Comprehensive logging and error reporting
"""

import asyncio
import click
import sys
import time
import os
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Optional
from contextlib import asynccontextmanager

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.ceo_research_progressive import (
    research_ceo_progressive, 
    research_ceo_comprehensive_simple
)
from src.ceo_research_gpt5 import research_ceo_with_websearch  # Legacy
from src.utils.logger import get_logger


@asynccontextmanager
async def _locked_output_file(target: Path, timeout: float = 30.0, poll: float = 0.2):
    """Simple cross-process lock using a temporary .lock file."""
    lock_path = target.with_suffix(target.suffix + '.lock')
    deadline = time.monotonic() + timeout

    while True:
        try:
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            break
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise TimeoutError(f'Timed out waiting for lock on {target}')
            await asyncio.sleep(poll)

    try:
        yield
    finally:
        try:
            os.remove(lock_path)
        except FileNotFoundError:
            pass


@click.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', 
              default=lambda: f'output/batch_ceo_research_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
              help='Output CSV file path (default: timestamped filename)')
@click.option('--method', '-m',
              type=click.Choice(['progressive', 'comprehensive', 'legacy'], case_sensitive=False),
              default='progressive',
              help='Research method to use (default: progressive)')
@click.option('--reasoning-effort', '-r',
              type=click.Choice(['minimal', 'low', 'medium', 'high'], case_sensitive=False),
              default='medium',
              help='GPT-5 reasoning effort level (default: medium)')
@click.option('--max-errors', 
              type=int, 
              default=5,
              help='Maximum consecutive errors before stopping (default: 5)')
@click.option('--delay', 
              type=float, 
              default=2.0,
              help='Delay between requests in seconds (default: 2.0)')
@click.option('--verbose', '-v', is_flag=True,
              help='Show detailed progress for each CEO')
@click.option('--concurrency', '-c',
              type=int,
              default=3,
              help='Number of CEOs to process concurrently (default: 3)')
@click.option('--dry-run', is_flag=True,
              help='Parse input file and show what would be processed without running research')
def batch_research_ceo(input_file: str, output: str, method: str, reasoning_effort: str,
                      max_errors: int, delay: float, verbose: bool, concurrency: int, dry_run: bool):
    """
    Batch process CEO research from a text file.

    INPUT_FILE: Text file with CEO|Bank pairs (one per line)

    Input file format:
        Jamie Dimon|JPMorgan Chase
        Brian Moynihan|Bank of America
        Jane Fraser|Citigroup
        
    Examples:
        # Basic batch processing
        python batch_research_ceo.py ceo_list.txt
        
        # High-quality progressive research with custom output
        python batch_research_ceo.py ceo_list.txt -m progressive -r high -o my_results.csv -v
        
        # Fast comprehensive research with error tolerance
        python batch_research_ceo.py ceo_list.txt -m comprehensive --max-errors 10
        
        # Test what would be processed
        python batch_research_ceo.py ceo_list.txt --dry-run
    """
    
    try:
        asyncio.run(_run_batch_research(
            input_file, output, method, reasoning_effort, max_errors, delay, verbose, concurrency, dry_run
        ))
    except KeyboardInterrupt:
        click.echo("\n[INTERRUPTED] Batch processing interrupted by user.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"[CRITICAL ERROR] Critical error in batch processor: {e}", err=True)
        sys.exit(1)


async def _run_batch_research(
    input_file: str,
    output_path: str, 
    method: str,
    reasoning_effort: str,
    max_errors: int,
    delay: float,
    verbose: bool,
    concurrency: int,
    dry_run: bool
) -> None:
    """Run the batch research process."""
    
    logger = get_logger(__name__)
    start_time = time.time()
    
    # Parse input file
    click.echo("Parsing input file...")
    ceo_bank_pairs = _parse_input_file(input_file)
    
    if not ceo_bank_pairs:
        click.echo("[ERROR] No valid CEO/Bank pairs found in input file.")
        return
    
    click.echo(f"Found {len(ceo_bank_pairs)} CEO/Bank pairs to process")
    
    if dry_run:
        _show_dry_run_preview(ceo_bank_pairs, method, reasoning_effort, output_path, concurrency, delay)
        return
    
    # Initialize tracking
    results = {
        'total': len(ceo_bank_pairs),
        'completed': 0,
        'errors': 0,
        'consecutive_errors': 0,
        'skipped': 0,
        'start_time': start_time
    }
    
    # Create output directory
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    click.echo(f"\nStarting batch research...")
    click.echo(f"   Method: {method}")
    click.echo(f"   Reasoning effort: {reasoning_effort}")
    click.echo(f"   Output: {output_file.absolute()}")
    click.echo(f"   Max consecutive errors: {max_errors}")
    click.echo(f"   Concurrency: {max(1, concurrency)}")
    click.echo(f"   Stagger between starts: {delay}s")
    click.echo()
    
    # Concurrency-lite processing using a semaphore
    sem = asyncio.Semaphore(max(1, concurrency))
    io_lock = asyncio.Lock()  # serialize console output and results updates

    async def worker(index: int, ceo_name: str, bank_name: str):
        async with sem:
            # Progress line
            async with io_lock:
                click.echo(f"[{index}/{results['total']}] Processing: {ceo_name} at {bank_name}")
                if verbose:
                    click.echo(f"   Using {method} method with {reasoning_effort} reasoning...")

            try:
                profile = await _research_single_ceo(
                    ceo_name, bank_name, method, reasoning_effort, verbose
                )

                await _export_to_batch_csv(profile, output_file, verbose)

                async with io_lock:
                    results['completed'] += 1
                    results['consecutive_errors'] = 0
                    if verbose:
                        sources_count = len(profile.to_csv_rows_by_source()) if profile else 0
                        click.echo(f"   [SUCCESS] {sources_count} sources, {profile.confidence_score:.2f} confidence")
                    else:
                        click.echo("   [SUCCESS]")

            except Exception as e:
                error_msg = str(e)
                logger.error(f"Error processing {ceo_name} at {bank_name}: {error_msg}")
                async with io_lock:
                    results['errors'] += 1
                    results['consecutive_errors'] += 1
                    if verbose:
                        click.echo(f"   [ERROR] {error_msg}")
                    else:
                        click.echo(f"   [ERROR] (continuing...)")

            # Periodic progress (non-verbose)
            if not verbose:
                async with io_lock:
                    completed = results['completed']
                    if completed > 0 and completed % 5 == 0:
                        elapsed = time.time() - start_time
                        rate = completed / elapsed * 60 if elapsed > 0 else 0
                        click.echo(f"   Progress: {completed} completed, {results['errors']} errors, {rate:.1f} CEOs/min")

    # Launch tasks with optional stagger between starts
    tasks = []
    for i, (ceo_name, bank_name) in enumerate(ceo_bank_pairs, 1):
        tasks.append(asyncio.create_task(worker(i, ceo_name, bank_name)))
        if delay > 0:
            await asyncio.sleep(delay)

    # Wait for all to finish
    await asyncio.gather(*tasks, return_exceptions=False)

    # Final summary
    _show_batch_summary(results, output_file)


def _parse_input_file(input_file: str) -> List[Tuple[str, str]]:
    """Parse input file and return list of (CEO, Bank) pairs."""
    
    ceo_bank_pairs = []
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse CEO|Bank format
                if '|' not in line:
                    click.echo(f"[WARNING] Line {line_num}: Invalid format (missing |): {line}")
                    continue
                
                parts = line.split('|')
                if len(parts) != 2:
                    click.echo(f"[WARNING] Line {line_num}: Invalid format (expected CEO|Bank): {line}")
                    continue
                
                ceo_name = parts[0].strip()
                bank_name = parts[1].strip()
                
                if not ceo_name or not bank_name:
                    click.echo(f"[WARNING] Line {line_num}: Empty CEO or Bank name: {line}")
                    continue
                
                ceo_bank_pairs.append((ceo_name, bank_name))
    
    except Exception as e:
        click.echo(f"[ERROR] Error reading input file: {e}")
        return []
    
    return ceo_bank_pairs


def _show_dry_run_preview(
    ceo_bank_pairs: List[Tuple[str, str]],
    method: str,
    reasoning_effort: str,
    output_path: str,
    concurrency: int,
    delay: float
):
    """Show what would be processed in dry run mode."""
    
    click.echo("\n" + "="*60)
    click.echo("DRY RUN PREVIEW")
    click.echo("="*60)
    
    click.echo(f"Input file contains: {len(ceo_bank_pairs)} CEO/Bank pairs")
    click.echo(f"Research method: {method}")
    click.echo(f"Reasoning effort: {reasoning_effort}")
    click.echo(f"Output file: {output_path}")
    click.echo(f"Concurrency: {max(1, concurrency)}")
    click.echo(f"Stagger between starts: {delay}s")
    
    click.echo(f"\nCEOs to process:")
    for i, (ceo_name, bank_name) in enumerate(ceo_bank_pairs, 1):
        click.echo(f"  {i:2d}. {ceo_name} at {bank_name}")
    
    click.echo(f"\nEstimated processing time:")
    # Rough estimates based on method
    time_per_ceo = {'progressive': 4, 'comprehensive': 3, 'legacy': 2}[method]
    total_minutes = (len(ceo_bank_pairs) * time_per_ceo) / 60
    
    click.echo(f"  ~{time_per_ceo} minutes per CEO ({method} method)")
    click.echo(f"  ~{total_minutes:.1f} total minutes for {len(ceo_bank_pairs)} CEOs")
    
    click.echo(f"\nRun without --dry-run to start processing")


async def _research_single_ceo(ceo_name: str, bank_name: str, method: str, reasoning_effort: str, verbose: bool):
    """Research a single CEO using the specified method."""
    
    # Use the same research functions as the main CLI
    if method == 'progressive':
        return await research_ceo_progressive(
            ceo_name=ceo_name,
            company_name=bank_name,
            reasoning_effort=reasoning_effort
        )
    elif method == 'comprehensive':
        return await research_ceo_comprehensive_simple(
            ceo_name=ceo_name,
            company_name=bank_name,
            reasoning_effort=reasoning_effort
        )
    elif method == 'legacy':
        return await research_ceo_with_websearch(
            ceo_name=ceo_name,
            company_name=bank_name,
            reasoning_effort=reasoning_effort
        )
    else:
        raise ValueError(f"Unknown method: {method}")


async def _export_to_batch_csv(profile, output_file: Path, verbose: bool):
    """Export profile to CSV in batch mode (append)."""

    # Import here to avoid circular imports
    import csv

    # Get CSV data with separate source columns (one row per CEO)
    csv_row = profile.to_csv_row_with_separate_sources(max_sources=30)

    if verbose:
        total_sources = csv_row.get('total_sources', 0)
        click.echo(f"   Creating single CSV row with {total_sources} sources in separate columns")

    if not csv_row:
        return

    async with _locked_output_file(output_file):
        file_exists = output_file.exists()
        with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_row.keys())

            if not file_exists:
                writer.writeheader()

            writer.writerow(csv_row)


def _show_batch_summary(results: dict, output_file: Path):
    """Show final batch processing summary."""
    
    elapsed_time = time.time() - results['start_time']
    elapsed_minutes = elapsed_time / 60
    
    click.echo("\n" + "="*60)
    click.echo("BATCH PROCESSING COMPLETED")
    click.echo("="*60)
    
    click.echo(f"Results Summary:")
    click.echo(f"   Total CEOs: {results['total']}")
    click.echo(f"   Completed: {results['completed']}")
    click.echo(f"   Errors: {results['errors']}")
    click.echo(f"   Success Rate: {(results['completed'] / results['total']) * 100:.1f}%")
    
    click.echo(f"\nTiming:")
    click.echo(f"   Total Time: {elapsed_minutes:.1f} minutes")
    if results['completed'] > 0:
        avg_time = elapsed_time / results['completed']
        rate = results['completed'] / elapsed_time * 60
        click.echo(f"   Avg per CEO: {avg_time:.1f} seconds")
        click.echo(f"   Processing Rate: {rate:.1f} CEOs/minute")
    
    click.echo(f"\nOutput:")
    click.echo(f"   File: {output_file.absolute()}")
    if output_file.exists():
        file_size = output_file.stat().st_size / 1024  # KB
        click.echo(f"   Size: {file_size:.1f} KB")
        
        # Count rows in output file
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                row_count = sum(1 for line in f) - 1  # Subtract header
            click.echo(f"   Rows: {row_count} CEOs")
        except:
            pass
    
    if results['errors'] > 0:
        click.echo(f"\n[NOTE] {results['errors']} CEOs had errors and were skipped")
        click.echo("   Check logs for detailed error information")
    
    if results['completed'] > 0:
        click.echo(f"\nBatch processing completed successfully!")
        click.echo(f"   Ready for analysis: {output_file.name}")
    else:
        click.echo(f"\n[ERROR] No CEOs were successfully processed")


if __name__ == '__main__':
    batch_research_ceo()
