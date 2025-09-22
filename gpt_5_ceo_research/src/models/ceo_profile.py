"""
CEO Profile Data Model

This module defines the CEOProfile Pydantic model for structured CEO data.
Follows KISS principles - simple validation, clear structure, minimal complexity.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
import re


class CEOProfile(BaseModel):
    """
    CEO profile data model focused on career and succession information.

    Only ceo_name and company_name are required. All other fields are optional
    to avoid forcing completeness when data is incomplete.
    """

    # REQUIRED FIELDS (only these two)
    ceo_name: str = Field(..., description="Full name of the CEO")
    company_name: str = Field(..., description="Name of the company")

    # BASIC INFORMATION
    ceo_title: Optional[str] = Field(None, description="Official title (CEO, President & CEO, etc.)")

    # CLASSIFICATION
    insider_outsider: Optional[str] = Field(
        None,
        description=(
            "CEO classification based on career path:\n"
            "- 'insider': Promoted from within the company (worked at company before becoming CEO)\n"
            "- 'outsider': Hired from outside the company (first role at company is CEO)\n"
            "- 'unknown': Cannot determine from available information"
        )
    )
    ceo_type: Optional[str] = Field(None, description="Type of CEO (founder, professional, interim, etc.)")

    # TENURE INFORMATION
    appointment_date: Optional[str] = Field(None, description="Date appointed as CEO (MM/DD/YYYY)")
    start_date: Optional[str] = Field(None, description="Date started as CEO (MM/DD/YYYY)")
    departure_date: Optional[str] = Field(None, description="Date departed as CEO (MM/DD/YYYY or 'incumbent')")
    tenure_years: Optional[float] = Field(None, description="Years as CEO")
    tenure_months: Optional[float] = Field(None, description="Total months as CEO")

    # CAREER HISTORY
    previous_company: Optional[str] = Field(None, description="Most recent previous company before current role")
    previous_position: Optional[str] = Field(None, description="Most recent previous position/title before CEO")
    initial_join_year: Optional[int] = Field(None, description="Year first joined the company in ANY role (YYYY)")
    years_at_company: Optional[float] = Field(None, description="Total years at current company")
    years_before_ceo: Optional[float] = Field(None, description="Years at company before becoming CEO")
    previous_ceo_experience: Optional[bool] = Field(None, description="Whether had CEO experience before")

    # ENHANCED INSIDER CAREER PATH FIELDS
    year_insider_joined_firm: Optional[int] = Field(None, description="Year insider first joined firm in executive capacity (for insiders only)")
    last_position_before_ceo: Optional[str] = Field(None, description="Actual job title before becoming CEO (for insiders)")
    was_president: Optional[bool] = Field(None, description="Whether was president before CEO")
    was_board_member: Optional[bool] = Field(None, description="Whether was board member before CEO")
    was_chairman: Optional[bool] = Field(None, description="Whether was chairman before CEO")
    was_ceo_of_subsidiary: Optional[bool] = Field(None, description="Whether was CEO of bank owned by BHC")
    was_other_executive: Optional[bool] = Field(None, description="Whether was other executive before CEO")
    was_board_member_only: Optional[bool] = Field(None, description="Whether was purely board member before CEO")
    was_former_ceo: Optional[bool] = Field(None, description="Whether was former CEO")
    was_former_other_executive: Optional[bool] = Field(None, description="Whether was former non-CEO executive")
    joined_as_executive: Optional[bool] = Field(None, description="Whether joined firm as executive")
    joined_from_early_career: Optional[bool] = Field(None, description="Whether joined from early career/first job")

    # ENHANCED OUTSIDER CAREER PATH FIELDS
    outsider_job_title: Optional[str] = Field(None, description="Actual title before joining (for outsiders only)")
    outsider_firm: Optional[str] = Field(None, description="Actual firm before joining, include city/state if possible")
    was_ceo_of_other_firms: Optional[bool] = Field(None, description="Whether was CEO of other firms before tenure")
    was_other_executive_of_other_firms: Optional[bool] = Field(None, description="Whether was non-CEO executive of other firms")
    was_unattached_to_any: Optional[bool] = Field(None, description="Whether not attached to other firms, own firm, or director roles only")

    # APPOINTMENT CONTEXT
    predecessor_name: Optional[str] = Field(None, description="Name of previous CEO")
    succession_type: Optional[str] = Field(None, description="Type of succession (planned, forced, etc.)")
    interim_period: Optional[bool] = Field(None, description="Whether there was an interim period")
    board_connection: Optional[str] = Field(None, description="Connection to board members")

    # POST-CEO INFORMATION
    departure_reason: Optional[str] = Field(None, description="Reason for departure")
    departure_voluntary: Optional[bool] = Field(None, description="Whether departure was voluntary")
    successor_name: Optional[str] = Field(None, description="Name of successor")
    post_ceo_role: Optional[str] = Field(None, description="Role after CEO (if any)")

    # ENHANCED POST-CEO INFORMATION
    was_forced_out: Optional[bool] = Field(None, description="Whether was forced out, even without explicit statement")
    retirement_status: Optional[bool] = Field(None, description="Whether explicitly stated retirement")
    no_real_job: Optional[bool] = Field(None, description="Whether no job lined up after leaving")
    director_of_some_company: Optional[str] = Field(None, description="Director position and company name")
    age_at_departure: Optional[int] = Field(None, description="Age when retires/leaves, if available")
    next_company: Optional[str] = Field(None, description="Next company if applicable, excluding small personal firms")
    geographic_relocation: Optional[str] = Field(None, description="Whether moved for next role")
    career_advancement_decline: Optional[str] = Field(None, description="Trajectory of next role")
    reason_for_succession: Optional[str] = Field(None, description="Reason for succession if available")
    succession_planned_unplanned: Optional[str] = Field(None, description="Whether succession was planned or unplanned")
    succession_documentation: Optional[bool] = Field(None, description="Whether succession was documented")

    # DATA QUALITY & SOURCES
    data_completeness: Optional[str] = Field(None, description="Assessment of data completeness (high/medium/low)")
    primary_sources: Optional[List[str]] = Field(default_factory=list, description="Primary data sources")
    last_updated: Optional[str] = Field(None, description="Last update date")
    confidence_score: Optional[float] = Field(None, description="Confidence in data accuracy (0-1)")
    notes: Optional[str] = Field(None, description="Additional notes or caveats")

    # ENHANCED SOURCE TRACKING
    source_urls: Optional[List[str]] = Field(default_factory=list, description="Direct URLs to sources accessed")
    conflicting_data_notes: Optional[str] = Field(None, description="Notes on conflicting information found")
    source_accessibility_issues: Optional[str] = Field(None, description="Issues accessing primary sources")
    alternative_verification_paths: Optional[List[str]] = Field(default_factory=list, description="Alternative sources for verification")
    data_precision_level: Optional[str] = Field(None, description="Precision of date information (exact/month-year/year-only)")
    timeline_conflicts: Optional[str] = Field(None, description="Conflicts in timeline information")

    # CLASSIFICATION CONFIDENCE
    insider_outsider_confidence: Optional[str] = Field(None, description="Confidence in insider/outsider classification (HIGH/MEDIUM/LOW/CONFLICTING)")
    career_timeline_verified: Optional[bool] = Field(None, description="Whether career timeline was cross-referenced")

    @field_validator('insider_outsider')
    @classmethod
    def validate_insider_outsider(cls, v: Optional[str]) -> Optional[str]:
        """Validate insider/outsider classification."""
        if v is None:
            return v
        if v.lower() not in ['insider', 'outsider', 'unknown']:
            return 'unknown'  # Don't fail, just set to unknown
        return v.lower()

    @field_validator('appointment_date', 'start_date', 'departure_date')
    @classmethod
    def validate_date_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate date format (MM/DD/YYYY) but allow special values."""
        if v is None:
            return v

        # Allow special values
        if v.lower() in ['incumbent', 'current', 'ongoing', 'unknown', 'n/a']:
            return v

        # Try to validate MM/DD/YYYY format
        date_pattern = r'^\d{1,2}/\d{1,2}/\d{4}$'
        if re.match(date_pattern, v):
            return v

        # Don't fail validation, just return as-is for flexibility
        return v

    def to_csv_row(self) -> Dict[str, Any]:
        """
        Convert the model to a flat dictionary suitable for CSV export.

        Lists are converted to semicolon-separated strings.
        None values are converted to empty strings.
        """
        data = self.model_dump()
        csv_row = {}

        for key, value in data.items():
            if value is None:
                csv_row[key] = ''
            elif isinstance(value, list):
                # Convert lists to semicolon-separated strings
                csv_row[key] = '; '.join(str(item) for item in value)
            else:
                csv_row[key] = value

        return csv_row

    def to_csv_rows_by_source(self) -> List[Dict[str, Any]]:
        """
        Convert the model to multiple CSV rows, one per source.
        
        Each row contains all CEO data plus individual source information.
        This allows for better source analysis and verification.
        
        Returns:
            List[Dict[str, Any]]: List of CSV row dictionaries, one per source
        """
        # Get base CEO data
        base_data = self.model_dump()
        
        # Combine all sources
        all_sources = []
        
        # Add source_urls with type indicator
        if base_data.get('source_urls'):
            for url in base_data['source_urls']:
                if url:  # Skip empty URLs
                    all_sources.append({
                        'source_url': url,
                        'source_type': 'URL',
                        'source_description': self._classify_source_url(url)
                    })
        
        # Add primary_sources with type indicator  
        if base_data.get('primary_sources'):
            for source in base_data['primary_sources']:
                if source:  # Skip empty sources
                    all_sources.append({
                        'source_url': '',  # No URL for primary source descriptions
                        'source_type': 'Description',
                        'source_description': source
                    })
        
        # If no sources, create one row with empty source fields
        if not all_sources:
            all_sources.append({
                'source_url': '',
                'source_type': '',
                'source_description': 'No sources available'
            })
        
        # Create CSV rows
        csv_rows = []
        for i, source in enumerate(all_sources, 1):
            row = {}
            
            # Add all CEO profile fields (excluding list fields that we're expanding)
            for key, value in base_data.items():
                if key in ['source_urls', 'primary_sources', 'alternative_verification_paths']:
                    # Handle list fields differently
                    if isinstance(value, list):
                        row[key] = '; '.join(str(item) for item in value) if value else ''
                    else:
                        row[key] = value if value is not None else ''
                else:
                    # Standard fields
                    if value is None:
                        row[key] = ''
                    elif isinstance(value, list):
                        row[key] = '; '.join(str(item) for item in value)
                    else:
                        row[key] = value
            
            # Add source-specific fields
            row['source_number'] = i
            row['total_sources'] = len(all_sources)
            row['source_url'] = source['source_url']
            row['source_type'] = source['source_type']
            row['source_description'] = source['source_description']
            
            csv_rows.append(row)
        
        return csv_rows

    def to_csv_row_with_separate_sources(self, max_sources: int = 30) -> Dict[str, Any]:
        """
        Convert the model to a single CSV row with each source in a separate column.

        Instead of combining sources in a semicolon-separated list, this method
        creates individual columns for each source (source_1, source_2, etc.)

        Args:
            max_sources: Maximum number of source columns to create (default: 30)

        Returns:
            Dict[str, Any]: Single CSV row with separate source columns
        """
        # Get base data (excluding the list fields we'll expand)
        data = self.model_dump()
        csv_row = {}

        # Process standard fields (excluding source fields we'll handle separately)
        for key, value in data.items():
            if key not in ['source_urls', 'primary_sources', 'alternative_verification_paths']:
                if value is None:
                    csv_row[key] = ''
                elif isinstance(value, list):
                    # Convert other lists to semicolon-separated strings
                    csv_row[key] = '; '.join(str(item) for item in value)
                else:
                    csv_row[key] = value
            elif key == 'alternative_verification_paths':
                # Keep alternative_verification_paths as semicolon-separated
                if value is None:
                    csv_row[key] = ''
                elif isinstance(value, list):
                    csv_row[key] = '; '.join(str(item) for item in value)
                else:
                    csv_row[key] = value

        # Collect all sources (just raw URLs and descriptions)
        all_sources = []

        # Add source_urls first
        if data.get('source_urls'):
            for url in data['source_urls']:
                if url:  # Skip empty URLs
                    all_sources.append(url)

        # Add primary_sources (these are text descriptions)
        if data.get('primary_sources'):
            for source in data['primary_sources']:
                if source:  # Skip empty sources
                    all_sources.append(source)

        # Add individual source columns (just raw sources, no metadata)
        for i in range(1, max_sources + 1):
            if i <= len(all_sources):
                csv_row[f'source_{i}'] = all_sources[i-1]
            else:
                # Empty columns for unused source slots
                csv_row[f'source_{i}'] = ''

        # Add summary field
        csv_row['total_sources'] = len(all_sources)

        return csv_row

    def _classify_source_url(self, url: str) -> str:
        """
        Classify a source URL to provide better source descriptions.
        
        Args:
            url: URL to classify
            
        Returns:
            str: Human-readable description of the source type
        """
        url_lower = url.lower()
        
        if 'sec.gov' in url_lower:
            if 'edgar' in url_lower:
                return 'SEC EDGAR Filing'
            else:
                return 'SEC Website'
        elif any(domain in url_lower for domain in ['jpmorganchase.com', 'bankofamerica.com', 'citigroup.com', 'wellsfargo.com']):
            return 'Official Company Website'
        elif any(domain in url_lower for domain in ['americanbanker.com', 'bankdirector.com']):
            return 'Banking Trade Publication'
        elif any(domain in url_lower for domain in ['reuters.com', 'bloomberg.com', 'wsj.com', 'ft.com']):
            return 'Financial News Publication'
        elif any(domain in url_lower for domain in ['businesswire.com', 'prnewswire.com', 'globenewswire.com']):
            return 'Press Release Distribution'
        elif 'linkedin.com' in url_lower:
            return 'LinkedIn Profile/Company Page'
        elif any(domain in url_lower for domain in ['wikipedia.org', 'forbes.com', 'fortune.com']):
            return 'General Business Publication'
        else:
            return 'Other Web Source'

    class Config:
        """Pydantic configuration for JSON schema generation."""
        json_schema_extra = {
            "example": {
                "ceo_name": "Tim Cook",
                "company_name": "Apple Inc.",
                "ceo_title": "Chief Executive Officer",
                "insider_outsider": "insider",
                "appointment_date": "08/24/2011",
                "departure_date": "incumbent",
                "primary_sources": ["SEC filings", "Company website"]
            }
        }