#!/usr/bin/env python3
"""
Enhanced CEO Research CLI Tool

KISS-compliant CLI supporting both progressive and comprehensive research approaches.
Choose the method that best fits your needs:

- Progressive (RECOMMENDED): Multiple focused stages for comprehensive, high-quality data
- Comprehensive: Single-pass approach for faster results
- Legacy: Original single prompt (maintained for backward compatibility)

Usage Examples:
    # Progressive research (recommended for best results)
    python research_ceo_enhanced.py "Jamie Dimon" "JPMorgan Chase" --method progressive

    # Comprehensive single-pass (faster)
    python research_ceo_enhanced.py "Brian Moynihan" "Bank of America" --method comprehensive

    # Custom stages only
    python research_ceo_enhanced.py "David Solomon" "Goldman Sachs" --method progressive --stages basic career_details

    # Legacy mode (original behavior)
    python research_ceo_enhanced.py "Jane Fraser" "Citigroup" --method legacy
"""

import asyncio
import click
import csv
import sys
from pathlib import Path
from typing import Optional, List

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.ceo_research_progressive import (
    research_ceo_progressive, 
    research_ceo_comprehensive_simple
)
from src.ceo_research_gpt5 import research_ceo_with_websearch  # Legacy
from src.utils.logger import get_logger


@click.command()
@click.argument('ceo_name')
@click.argument('company_name')
@click.option('--method', '-m', 
              type=click.Choice(['progressive', 'comprehensive', 'legacy'], case_sensitive=False),
              default='progressive',
              help='Research method to use (default: progressive)')
@click.option('--stages', 
              type=str, 
              help='Comma-separated list of stages for progressive method (basic,career_details,succession,post_ceo)')
@click.option('--reasoning-effort', '-r',
              type=click.Choice(['minimal', 'low', 'medium', 'high'], case_sensitive=False),
              default='medium',
              help='GPT-5 reasoning effort level (default: medium)')
@click.option('--output', '-o', 
              default='output/enhanced_ceo_research.csv',
              help='Output CSV file path')
@click.option('--verbose', '-v', is_flag=True,
              help='Show detailed progress and results')
@click.option('--show-methods', is_flag=True,
              help='Show available methods and exit')
def research_ceo_cli(ceo_name: str, company_name: str, method: str, stages: Optional[str],
                     reasoning_effort: str, output: str, verbose: bool, show_methods: bool):
    """
    Enhanced CEO Research CLI with multiple research approaches.

    CEO_NAME: Full name of the CEO to research
    COMPANY_NAME: Name of the company

    Examples:
        # Best quality (recommended)
        python research_ceo_enhanced.py "Tim Cook" "Apple" --method progressive

        # Fast results  
        python research_ceo_enhanced.py "Satya Nadella" "Microsoft" --method comprehensive

        # Custom stages
        python research_ceo_enhanced.py "Andy Jassy" "Amazon" --stages basic,career_details

        # High effort reasoning
        python research_ceo_enhanced.py "Mary Barra" "GM" --reasoning-effort high --verbose
    """
    
    if show_methods:
        _show_available_methods()
        return
        
    try:
        asyncio.run(_run_enhanced_research(
            ceo_name, company_name, method, stages, reasoning_effort, output, verbose
        ))
    except KeyboardInterrupt:
        click.echo("\\nResearch interrupted by user.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


async def _run_enhanced_research(
    ceo_name: str, 
    company_name: str, 
    method: str,
    stages: Optional[str],
    reasoning_effort: str,
    output_path: str,
    verbose: bool
) -> None:
    """Run the enhanced CEO research process."""
    
    logger = get_logger(__name__)
    
    try:
        if verbose:
            click.echo(f"Starting {method} CEO research...")
            click.echo(f"Target: {ceo_name} at {company_name}")
            click.echo(f"Reasoning effort: {reasoning_effort}")
            if stages:
                click.echo(f"Custom stages: {stages}")
            click.echo()
        
        # Parse stages if provided
        stages_list = None
        if stages:
            stages_list = [s.strip() for s in stages.split(',')]
            if verbose:
                click.echo(f"Using stages: {stages_list}")
        
        # Run research based on method
        if method == 'progressive':
            if verbose:
                click.echo("Using progressive research approach (multiple focused stages)...")
            profile = await research_ceo_progressive(
                ceo_name=ceo_name,
                company_name=company_name,
                reasoning_effort=reasoning_effort,
                stages=stages_list
            )
            
        elif method == 'comprehensive':
            if verbose:
                click.echo("Using comprehensive research approach (single enhanced prompt)...")
            profile = await research_ceo_comprehensive_simple(
                ceo_name=ceo_name,
                company_name=company_name,
                reasoning_effort=reasoning_effort
            )
            
        elif method == 'legacy':
            if verbose:
                click.echo("Using legacy research approach (original implementation)...")
            profile = await research_ceo_with_websearch(
                ceo_name=ceo_name,
                company_name=company_name,
                reasoning_effort=reasoning_effort
            )
            
        else:
            raise ValueError(f"Unknown method: {method}")
        
        # Export results
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        await _export_enhanced_csv(profile, output_file, verbose)
        
        # Report results
        if verbose:
            _report_enhanced_verbose_results(profile, output_file, method)
        else:
            _report_enhanced_simple_results(profile, output_file, method)
            
    except Exception as e:
        logger.error(f"Enhanced research failed: {e}")
        raise


async def _export_enhanced_csv(profile, output_file: Path, verbose: bool) -> None:
    """Export CEO profile to CSV with one row per source."""
    
    if verbose:
        click.echo(f"Exporting enhanced results to {output_file}...")
    
    # Check if file exists for headers
    file_exists = output_file.exists()
    
    # Get CSV data with one row per source
    csv_rows = profile.to_csv_rows_by_source()
    
    if verbose:
        click.echo(f"Creating {len(csv_rows)} CSV rows (one per source)...")
    
    # Write to CSV
    if csv_rows:  # Only proceed if we have data
        with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_rows[0].keys())
            
            if not file_exists:
                writer.writeheader()
            
            # Write all rows (one per source)
            for row in csv_rows:
                writer.writerow(row)


def _report_enhanced_verbose_results(profile, output_file: Path, method: str) -> None:
    """Report detailed results with enhanced information."""
    
    click.echo("\\n" + "="*70)
    click.echo(f"ENHANCED CEO RESEARCH COMPLETED ({method.upper()} METHOD)")
    click.echo("="*70)
    
    # Core information
    click.echo(f"CEO: {profile.ceo_name}")
    click.echo(f"Company: {profile.company_name}")
    
    if profile.ceo_title:
        click.echo(f"Title: {profile.ceo_title}")
    
    # Classification with confidence
    if profile.insider_outsider:
        confidence_text = ""
        if hasattr(profile, 'insider_outsider_confidence') and profile.insider_outsider_confidence:
            confidence_text = f" (Confidence: {profile.insider_outsider_confidence})"
        click.echo(f"Classification: {profile.insider_outsider.upper()}{confidence_text}")
    
    # Timeline information
    timeline_info = []
    if profile.appointment_date:
        timeline_info.append(f"Appointed: {profile.appointment_date}")
    if profile.start_date and profile.start_date != profile.appointment_date:
        timeline_info.append(f"Started: {profile.start_date}")
    if profile.departure_date:
        timeline_info.append(f"Departed: {profile.departure_date}")
    if profile.tenure_years:
        timeline_info.append(f"Tenure: {profile.tenure_years} years")
    
    if timeline_info:
        click.echo("Timeline: " + " | ".join(timeline_info))
    
    # Career path
    if profile.previous_company:
        click.echo(f"Previous Company: {profile.previous_company}")
    if profile.previous_position:
        click.echo(f"Previous Position: {profile.previous_position}")
    if hasattr(profile, 'initial_join_year') and profile.initial_join_year:
        click.echo(f"First Joined Company: {profile.initial_join_year}")
    
    # Data quality metrics
    click.echo("\\n" + "-"*40)
    click.echo("DATA QUALITY ASSESSMENT")
    click.echo("-"*40)
    
    if profile.data_completeness:
        click.echo(f"Data Completeness: {profile.data_completeness.upper()}")
    if profile.confidence_score:
        click.echo(f"Confidence Score: {profile.confidence_score:.2f}/1.0")
    
    # Source information
    source_count = 0
    if profile.primary_sources:
        source_count += len(profile.primary_sources)
    if hasattr(profile, 'source_urls') and profile.source_urls:
        source_count += len(profile.source_urls)
    
    # Get CSV row count for reporting    
    csv_rows = profile.to_csv_rows_by_source()
    csv_row_count = len(csv_rows)
        
    if source_count > 0:
        click.echo(f"Sources Used: {source_count}")
        click.echo(f"CSV Rows Created: {csv_row_count} (one per source)")
    
    # Enhanced fields summary
    enhanced_fields = 0
    if hasattr(profile, 'was_president') and profile.was_president is not None:
        enhanced_fields += 1
    if hasattr(profile, 'succession_type') and profile.succession_type:
        enhanced_fields += 1
    if hasattr(profile, 'post_ceo_role') and profile.post_ceo_role:
        enhanced_fields += 1
        
    if enhanced_fields > 0:
        click.echo(f"Enhanced Data Fields: {enhanced_fields}")
    
    # Conflicts or issues
    if hasattr(profile, 'conflicting_data_notes') and profile.conflicting_data_notes:
        click.echo(f"[WARNING] Data Conflicts: {profile.conflicting_data_notes}")
    
    if hasattr(profile, 'source_accessibility_issues') and profile.source_accessibility_issues:
        click.echo(f"[WARNING] Source Issues: {profile.source_accessibility_issues}")
    
    # Output location
    click.echo("\\n" + "-"*40)
    click.echo(f"Results saved to: {output_file.absolute()}")
    
    # Notes
    if profile.notes:
        click.echo(f"\\nNotes: {profile.notes}")


def _report_enhanced_simple_results(profile, output_file: Path, method: str) -> None:
    """Report simple results with key enhanced metrics."""
    
    click.echo(f"[OK] {method.capitalize()} research completed for {profile.ceo_name} at {profile.company_name}")
    
    # Key metrics
    metrics = []
    if profile.insider_outsider:
        conf_text = ""
        if hasattr(profile, 'insider_outsider_confidence') and profile.insider_outsider_confidence:
            conf_text = f" ({profile.insider_outsider_confidence})"
        metrics.append(f"{profile.insider_outsider.upper()}{conf_text}")
    
    if profile.tenure_years:
        metrics.append(f"Tenure: {profile.tenure_years}y")
    
    if profile.confidence_score:
        metrics.append(f"Quality: {profile.confidence_score:.2f}")
    
    if profile.data_completeness:
        metrics.append(f"Completeness: {profile.data_completeness}")
    
    # Add source count
    csv_rows = profile.to_csv_rows_by_source()
    if len(csv_rows) > 1:
        metrics.append(f"Sources: {len(csv_rows)}")
    
    if metrics:
        click.echo(f"  {' | '.join(metrics)}")
    
    click.echo(f"[OK] Results saved to: {output_file.absolute()} ({len(csv_rows)} rows)")
    
    # Warnings
    if hasattr(profile, 'conflicting_data_notes') and profile.conflicting_data_notes:
        click.echo(f"[WARNING] Data conflicts detected")
    
    if profile.confidence_score and profile.confidence_score < 0.5:
        click.echo(f"[WARNING] Low confidence score ({profile.confidence_score:.2f})")


def _show_available_methods() -> None:
    """Show information about available research methods."""
    
    click.echo("\\n" + "="*60)
    click.echo("AVAILABLE CEO RESEARCH METHODS")
    click.echo("="*60)
    
    click.echo("\\n1. PROGRESSIVE (Recommended)")
    click.echo("   - Multiple focused research stages")
    click.echo("   - Highest data quality and detail")
    click.echo("   - Better handling of complex cases")
    click.echo("   - Stages: basic -> career_details -> succession -> post_ceo")
    click.echo("   - Usage: --method progressive")
    
    click.echo("\\n2. COMPREHENSIVE")
    click.echo("   - Single enhanced prompt")
    click.echo("   - Faster than progressive")
    click.echo("   - Good balance of speed and quality")
    click.echo("   - Usage: --method comprehensive")
    
    click.echo("\\n3. LEGACY")
    click.echo("   - Original implementation")
    click.echo("   - Maintained for compatibility")
    click.echo("   - Basic feature set")
    click.echo("   - Usage: --method legacy")
    
    click.echo("\\nAVAILABLE STAGES (for progressive method):")
    click.echo("   - basic: Core information and insider/outsider classification")
    click.echo("   - career_details: Detailed career progression (insider or outsider specific)")
    click.echo("   - succession: Transition circumstances and board relationships")
    click.echo("   - post_ceo: Post-CEO career and data verification")
    
    click.echo("\\nEXAMPLES:")
    click.echo('   python research_ceo_enhanced.py "CEO Name" "Company" --method progressive')
    click.echo('   python research_ceo_enhanced.py "CEO Name" "Company" --stages basic,career_details')
    click.echo('   python research_ceo_enhanced.py "CEO Name" "Company" --method comprehensive --reasoning-effort high')
    
    click.echo("\\nRECOMMENDATION:")
    click.echo("   Use 'progressive' method for best results, especially for banking/financial CEOs")
    click.echo()


if __name__ == '__main__':
    research_ceo_cli()