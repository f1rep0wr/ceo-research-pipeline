#!/usr/bin/env python3
"""
CEO Research CLI Tool

Simple command-line interface for researching CEOs and exporting to CSV.
Follows KISS principles - straightforward CLI, clear output, no complex features.
"""

import asyncio
import click
import csv
import sys
from pathlib import Path
from typing import Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.ceo_research_gpt5 import research_ceo_with_websearch
from src.utils.logger import get_logger


@click.command()
@click.argument('ceo_name')
@click.argument('company_name')
@click.option('--output', '-o', default='output/ceo_research.csv',
              help='Output CSV file path')
@click.option('--verbose', '-v', is_flag=True,
              help='Show verbose output during research')
def research_ceo_cli(ceo_name: str, company_name: str, output: str,
                     verbose: bool):
    """
    Research a CEO and export results to CSV.

    CEO_NAME: Full name of the CEO to research
    COMPANY_NAME: Name of the company

    Examples:
        python research_ceo.py "Tim Cook" "Apple"
        python research_ceo.py "Satya Nadella" "Microsoft" --verbose
        python research_ceo.py "Mary Barra" "General Motors" -o custom_output.csv
    """
    try:
        asyncio.run(_run_research(ceo_name, company_name, output, verbose))
    except KeyboardInterrupt:
        click.echo("\nResearch interrupted by user.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


async def _run_research(ceo_name: str, company_name: str, output_path: str,
                       verbose: bool) -> None:
    """
    Run the CEO research process asynchronously.

    Args:
        ceo_name: Name of the CEO to research
        company_name: Name of the company
        output_path: Path to output CSV file
        verbose: Whether to show verbose output
    """
    logger = get_logger(__name__)

    try:
        # Run research using simple websearch
        if verbose:
            click.echo("Starting CEO research with websearch...")
            click.echo(f"Researching {ceo_name} at {company_name}...")

        profile = await research_ceo_with_websearch(
            ceo_name=ceo_name,
            company_name=company_name
        )

        # Create output directory if needed
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Export to CSV
        await _export_to_csv(profile, output_file, verbose)

        # Report results
        if verbose:
            _report_verbose_results(profile, output_file)
        else:
            _report_simple_results(profile, output_file)

    except Exception as e:
        logger.error(f"Research failed: {e}")
        raise


async def _export_to_csv(profile, output_file: Path, verbose: bool) -> None:
    """
    Export CEO profile to CSV file with proper Unicode handling.

    Args:
        profile: CEOProfile object to export
        output_file: Path to output CSV file
        verbose: Whether to show verbose output
    """
    if verbose:
        click.echo(f"Exporting results to {output_file}...")

    # Check if file exists to determine if we need to write headers
    file_exists = output_file.exists()

    # Get CSV data
    csv_data = profile.to_csv_row()

    # Write to CSV with proper Unicode encoding
    with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_data.keys())

        # Write header if file is new
        if not file_exists:
            writer.writeheader()

        # Write data row
        writer.writerow(csv_data)


def _report_verbose_results(profile, output_file: Path) -> None:
    """Report detailed results in verbose mode."""
    click.echo("\n" + "="*60)
    click.echo("RESEARCH COMPLETED")
    click.echo("="*60)
    click.echo(f"CEO: {profile.ceo_name}")
    click.echo(f"Company: {profile.company_name}")

    if profile.ceo_title:
        click.echo(f"Title: {profile.ceo_title}")

    if profile.insider_outsider:
        click.echo(f"Type: {profile.insider_outsider}")

    if profile.appointment_date:
        click.echo(f"Appointed: {profile.appointment_date}")

    if profile.tenure_years:
        click.echo(f"Tenure: {profile.tenure_years} years")

    if profile.data_completeness:
        click.echo(f"Data Completeness: {profile.data_completeness}")

    if profile.confidence_score:
        click.echo(f"Confidence Score: {profile.confidence_score:.2f}")

    click.echo(f"\nResults exported to: {output_file.absolute()}")

    if profile.primary_sources:
        click.echo(f"Sources used: {len(profile.primary_sources)}")


def _report_simple_results(profile, output_file: Path) -> None:
    """Report simple results in normal mode."""
    click.echo(f"[OK] Research completed for {profile.ceo_name} at {profile.company_name}")
    click.echo(f"[OK] Results exported to: {output_file.absolute()}")

    # Show key metrics if available
    metrics = []
    if profile.tenure_years:
        metrics.append(f"Tenure: {profile.tenure_years} years")
    if profile.insider_outsider:
        metrics.append(f"Type: {profile.insider_outsider}")
    if profile.confidence_score:
        metrics.append(f"Confidence: {profile.confidence_score:.2f}")

    if metrics:
        click.echo(f"  {' | '.join(metrics)}")


if __name__ == '__main__':
    research_ceo_cli()