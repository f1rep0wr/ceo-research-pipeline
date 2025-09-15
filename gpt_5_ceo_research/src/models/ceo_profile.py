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
    Comprehensive CEO profile data model with 40+ fields.

    Only ceo_name and company_name are required. All other fields are optional
    to avoid forcing completeness when data is incomplete.
    """

    # REQUIRED FIELDS (only these two)
    ceo_name: str = Field(..., description="Full name of the CEO")
    company_name: str = Field(..., description="Name of the company")

    # BASIC INFORMATION
    ceo_title: Optional[str] = Field(None, description="Official title (CEO, President & CEO, etc.)")
    company_ticker: Optional[str] = Field(None, description="Stock ticker symbol")
    company_exchange: Optional[str] = Field(None, description="Stock exchange (NYSE, NASDAQ, etc.)")

    # CLASSIFICATION
    insider_outsider: Optional[str] = Field(None, description="Insider or Outsider classification")
    ceo_type: Optional[str] = Field(None, description="Type of CEO (founder, professional, interim, etc.)")

    # TENURE INFORMATION
    appointment_date: Optional[str] = Field(None, description="Date appointed as CEO (MM/DD/YYYY)")
    start_date: Optional[str] = Field(None, description="Date started as CEO (MM/DD/YYYY)")
    departure_date: Optional[str] = Field(None, description="Date departed as CEO (MM/DD/YYYY or 'incumbent')")
    tenure_years: Optional[float] = Field(None, description="Years as CEO")
    tenure_months: Optional[int] = Field(None, description="Total months as CEO")

    # PERSONAL BACKGROUND
    birth_year: Optional[int] = Field(None, description="Year of birth")
    age: Optional[int] = Field(None, description="Current age or age at departure")
    age_at_appointment: Optional[int] = Field(None, description="Age when appointed CEO")
    nationality: Optional[str] = Field(None, description="Nationality/citizenship")
    gender: Optional[str] = Field(None, description="Gender")
    birthplace: Optional[str] = Field(None, description="Place of birth")

    # EDUCATION
    education_schools: Optional[List[str]] = Field(default_factory=list, description="List of schools attended")
    education_degrees: Optional[List[str]] = Field(default_factory=list, description="List of degrees earned")
    education_majors: Optional[List[str]] = Field(default_factory=list, description="List of academic majors")
    mba_school: Optional[str] = Field(None, description="MBA school if applicable")

    # CAREER HISTORY
    previous_companies: Optional[List[str]] = Field(default_factory=list, description="Previous companies worked at")
    previous_positions: Optional[List[str]] = Field(default_factory=list, description="Previous job titles")
    years_at_company: Optional[int] = Field(None, description="Total years at current company")
    years_before_ceo: Optional[int] = Field(None, description="Years at company before becoming CEO")
    previous_ceo_experience: Optional[bool] = Field(None, description="Whether had CEO experience before")

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

    # COMPANY CONTEXT
    industry: Optional[str] = Field(None, description="Industry/sector")
    company_size: Optional[str] = Field(None, description="Company size category")
    annual_revenue: Optional[float] = Field(None, description="Annual revenue in billions")
    market_cap: Optional[float] = Field(None, description="Market capitalization in billions")
    employee_count: Optional[int] = Field(None, description="Number of employees")
    fortune_ranking: Optional[int] = Field(None, description="Fortune 500/1000 ranking")

    # PERFORMANCE METRICS
    stock_performance: Optional[str] = Field(None, description="Stock performance during tenure")
    revenue_growth: Optional[float] = Field(None, description="Revenue growth percentage during tenure")
    major_achievements: Optional[List[str]] = Field(default_factory=list, description="Major achievements as CEO")

    # DATA QUALITY & SOURCES
    data_completeness: Optional[str] = Field(None, description="Assessment of data completeness")
    primary_sources: Optional[List[str]] = Field(default_factory=list, description="Primary data sources")
    last_updated: Optional[str] = Field(None, description="Last update date")
    confidence_score: Optional[float] = Field(None, description="Confidence in data accuracy (0-1)")
    notes: Optional[str] = Field(None, description="Additional notes or caveats")

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

    class Config:
        """Pydantic configuration for JSON schema generation."""
        json_schema_extra = {
            "example": {
                "ceo_name": "Tim Cook",
                "company_name": "Apple Inc.",
                "ceo_title": "Chief Executive Officer",
                "company_ticker": "AAPL",
                "insider_outsider": "insider",
                "appointment_date": "08/24/2011",
                "departure_date": "incumbent",
                "age": 63,
                "nationality": "American",
                "education_schools": ["Auburn University"],
                "education_degrees": ["Bachelor of Science"],
                "industry": "Technology",
                "primary_sources": ["SEC filings", "Company website"]
            }
        }