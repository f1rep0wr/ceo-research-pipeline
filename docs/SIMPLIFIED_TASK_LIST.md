# Simplified Development Task List - CEO Research System (KISS Edition)

## Project Overview
**Total Duration**: 1-2 days maximum
**Approach**: Use GPT-5's reasoning for EVERYTHING - no specialized tools
**Key Principle**: Accuracy over completeness - get what's available, don't force metrics

---

## Day 1 Morning: Core Data Model & Research Engine (3-4 hours)

### Task 1: Create Complete CEO Profile Model (45 minutes)
**File**: `gpt_5_ceo_research/src/models/ceo_profile.py`

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

class CEOProfile(BaseModel):
    """All 40+ CEO fields in one clean model"""

    # Basic Information
    ceo_name: str = Field(description="Format: Last, First")
    company_name: str

    # Classification
    insider_outsider: Optional[str] = Field(None, description="insider/outsider/unknown")
    insider_outsider_confidence: Optional[float] = Field(None, min=0, max=1)

    # Tenure Information
    start_date: Optional[str] = Field(None, description="MM/DD/YYYY format")
    start_date_precision: Optional[str] = Field(None, description="exact/month/quarter/year")
    end_date: Optional[str] = Field(None, description="MM/DD/YYYY or 'incumbent'")
    tenure_length_months: Optional[int] = None

    # Background
    birth_year: Optional[int] = None
    age_when_appointed: Optional[int] = None
    nationality: Optional[str] = None
    education_level: Optional[str] = None
    education_schools: Optional[List[str]] = Field(default_factory=list)
    mba: Optional[bool] = None
    stem_degree: Optional[bool] = None

    # Career History
    previous_companies: Optional[List[str]] = Field(default_factory=list)
    years_at_company_before_ceo: Optional[float] = None
    previous_ceo_experience: Optional[bool] = None
    previous_board_member: Optional[bool] = None
    previous_executive_role: Optional[str] = None
    came_from_same_industry: Optional[bool] = None

    # Appointment Context
    predecessor_name: Optional[str] = None
    predecessor_departure_reason: Optional[str] = None
    interim_period: Optional[bool] = None
    planned_succession: Optional[bool] = None
    crisis_appointment: Optional[bool] = None

    # Post-CEO Information
    departure_announced_date: Optional[str] = None
    departure_reason: Optional[str] = Field(None, description="voluntary/forced/retirement/death")
    severance_package: Optional[bool] = None
    stayed_as_chairman: Optional[bool] = None
    stayed_as_board_member: Optional[bool] = None
    next_position: Optional[str] = None

    # Company Context
    company_industry: Optional[str] = None
    company_founded_year: Optional[int] = None
    public_private: Optional[str] = None
    fortune_500_rank: Optional[int] = None

    # Sources & Metadata
    primary_sources: List[str] = Field(default_factory=list, description="URLs of sources")
    data_quality_notes: Optional[str] = None
    last_updated: str = Field(default_factory=lambda: date.today().isoformat())

    def to_csv_row(self) -> dict:
        """Export as CSV-friendly dictionary"""
        return self.model_dump()

    class Config:
        # This schema will be used for GPT-5 structured output
        json_schema_extra = {
            "description": "CEO profile with 40+ data points",
            "examples": [...]
        }
```

**Implementation Notes**:
- Single Pydantic model with ALL fields
- Optional fields (don't force completeness)
- Built-in CSV export
- JSON schema for GPT-5 structured output
- No complex inheritance or abstractions

---

### Task 2: Create Unified CEO Researcher (2-3 hours)
**File**: `gpt_5_ceo_research/src/researcher.py`

```python
from typing import Dict, List, Optional
import asyncio
from src.clients.gpt5_client import GPT5ResponsesClient
from src.models.ceo_profile import CEOProfile
from src.config.settings import Settings

class CEOResearcher:
    """Single class that handles all CEO research using GPT-5 reasoning"""

    def __init__(self, settings: Settings):
        self.client = GPT5ResponsesClient(settings)
        self.settings = settings

    async def research_ceo(self, ceo_name: str, company_name: str) -> CEOProfile:
        """
        Complete CEO research in 4 simple steps using GPT-5 reasoning
        NO specialized tools - GPT-5 handles everything
        """

        # Step 1: Generate search queries using GPT-5
        search_queries = await self._generate_search_queries(ceo_name, company_name)

        # Step 2: Execute web searches and collect raw data
        raw_sources = await self._collect_sources(search_queries)

        # Step 3: Extract all CEO data in ONE GPT-5 call with structured output
        ceo_profile = await self._extract_ceo_data(
            ceo_name,
            company_name,
            raw_sources
        )

        # Step 4: Validate and clean the data (optional refinement)
        ceo_profile = await self._validate_and_refine(ceo_profile, raw_sources)

        return ceo_profile

    async def _generate_search_queries(
        self,
        ceo_name: str,
        company_name: str
    ) -> List[str]:
        """Use GPT-5 to generate smart search queries"""

        prompt = f"""Generate 5 specific web search queries to find comprehensive information
        about {ceo_name}, CEO of {company_name}. Include queries for:
        1. Basic appointment/tenure information
        2. Background and career history
        3. Insider/outsider classification
        4. Education and previous positions
        5. Recent news and current status

        Return as JSON array of search query strings."""

        response = await self.client.create_response(
            prompt=prompt,
            reasoning_effort="medium",  # Smart query generation
        )

        # Parse queries from response
        queries = self._parse_json_response(response)
        return queries

    async def _collect_sources(self, queries: List[str]) -> List[Dict]:
        """Execute searches and collect raw source data"""
        sources = []

        for query in queries:
            # Use WebSearch tool or API to get real results
            # CRITICAL: These must be REAL search results, not generated
            search_results = await self._perform_web_search(query)

            for result in search_results[:3]:  # Top 3 per query
                # Fetch actual page content
                content = await self._fetch_page_content(result['url'])
                sources.append({
                    'url': result['url'],
                    'title': result['title'],
                    'content': content[:5000]  # Limit content length
                })

        return sources

    async def _extract_ceo_data(
        self,
        ceo_name: str,
        company_name: str,
        sources: List[Dict]
    ) -> CEOProfile:
        """
        ONE GPT-5 call to extract ALL 40+ fields using structured output
        This replaces ALL the specialized extractors
        """

        # Prepare source text
        source_text = self._format_sources(sources)

        prompt = f"""You are researching {ceo_name}, CEO of {company_name}.

        Based on the following sources, extract all available information to create
        a complete CEO profile. Focus on ACCURACY - only include information that
        is explicitly stated or can be reliably inferred from the sources.

        Sources:
        {source_text}

        Instructions:
        - Extract all 40+ fields if the information is available
        - Use "unknown" or null for information not found in sources
        - For insider/outsider: reason through their career path carefully
        - For dates: convert to MM/DD/YYYY format when possible
        - Include confidence scores where applicable
        - List the source URLs for key facts

        Return as structured JSON matching the CEOProfile schema."""

        response = await self.client.create_response(
            prompt=prompt,
            reasoning_effort="high",  # Maximum reasoning for extraction
            response_format={"type": "json_object"}  # Structured output
        )

        # Parse into CEOProfile model
        profile_data = self._parse_json_response(response)
        profile = CEOProfile(**profile_data)

        return profile

    async def _validate_and_refine(
        self,
        profile: CEOProfile,
        sources: List[Dict]
    ) -> CEOProfile:
        """Optional: Use GPT-5 to validate and resolve any conflicts"""

        prompt = f"""Review this CEO profile for accuracy and consistency:

        {profile.model_dump_json(indent=2)}

        Check for:
        1. Any logical inconsistencies (e.g., age vs birth year)
        2. Conflicting information that needs resolution
        3. Missing information that can be inferred
        4. Obvious errors or unrealistic values

        Return the corrected profile as JSON. Only make changes if you're
        confident they improve accuracy."""

        response = await self.client.create_response(
            prompt=prompt,
            reasoning_effort="medium",
            response_format={"type": "json_object"}
        )

        refined_data = self._parse_json_response(response)
        return CEOProfile(**refined_data)

    async def _perform_web_search(self, query: str) -> List[Dict]:
        """Execute actual web search - MUST return real results"""
        # This will integrate with WebSearch tool or external API
        # NEVER generate fake URLs
        pass

    async def _fetch_page_content(self, url: str) -> str:
        """Fetch actual page content from URL"""
        # This will use WebFetch or similar tool
        # Must fetch REAL content from REAL URLs
        pass

    def _format_sources(self, sources: List[Dict]) -> str:
        """Format sources for GPT-5 prompt"""
        formatted = []
        for i, source in enumerate(sources, 1):
            formatted.append(f"Source {i}: {source['title']}\nURL: {source['url']}\n{source['content']}\n---")
        return "\n".join(formatted)

    def _parse_json_response(self, response) -> dict:
        """Parse JSON from GPT-5 response"""
        import json
        # Extract JSON from response
        return json.loads(response.content)
```

**Implementation Notes**:
- ONE class replaces ALL specialized tools
- 4 simple steps: Generate queries → Search → Extract → Validate
- GPT-5 handles ALL reasoning (no rule-based extractors)
- Real web search integration (no fake URLs)
- Structured output for consistent results
- Focus on accuracy, not arbitrary completeness

---

## Day 1 Afternoon: CLI & Integration (2-3 hours)

### Task 3: Create Simple CLI Interface (1 hour)
**File**: `gpt_5_ceo_research/research_ceo.py`

```python
import asyncio
import click
import csv
from pathlib import Path
from src.researcher import CEOResearcher
from src.config.settings import get_settings

@click.command()
@click.argument('ceo_name')
@click.argument('company_name')
@click.option('--output', '-o', default='output.csv', help='Output CSV file')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
async def research_ceo_cli(ceo_name: str, company_name: str, output: str, verbose: bool):
    """Research a CEO and export data to CSV"""

    settings = get_settings()
    researcher = CEOResearcher(settings)

    if verbose:
        click.echo(f"Researching {ceo_name}, CEO of {company_name}...")

    try:
        # Run the research
        profile = await researcher.research_ceo(ceo_name, company_name)

        # Export to CSV
        output_path = Path(output)
        write_header = not output_path.exists()

        with open(output_path, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=profile.model_fields.keys())
            if write_header:
                writer.writeheader()
            writer.writerow(profile.to_csv_row())

        if verbose:
            click.echo(f"✓ Research complete. Data saved to {output}")
            click.echo(f"  - Classification: {profile.insider_outsider}")
            click.echo(f"  - Tenure Start: {profile.start_date}")
            click.echo(f"  - Sources Used: {len(profile.primary_sources)}")

    except Exception as e:
        click.echo(f"✗ Error: {str(e)}", err=True)
        raise

def main():
    """Entry point for the CLI"""
    asyncio.run(research_ceo_cli())

if __name__ == '__main__':
    main()
```

**Implementation Notes**:
- Simple Click CLI (much simpler than argparse)
- Single CEO lookup (batch can be added later)
- CSV output with append mode
- Verbose mode for debugging
- Clean error handling

---

### Task 4: Web Search Integration (1 hour)
**File**: `gpt_5_ceo_research/src/web_tools.py`

```python
from typing import List, Dict
import aiohttp
from src.config.settings import Settings

class WebTools:
    """Simple web search and fetch utilities"""

    def __init__(self, settings: Settings):
        self.settings = settings

    async def search_web(self, query: str) -> List[Dict]:
        """
        Perform actual web search using available tool
        Returns REAL search results with REAL URLs
        """
        # Option 1: Use the WebSearch tool that's already available
        # Option 2: Integrate with a search API (Serper, SerpAPI, Bing, etc.)

        # This is a placeholder - integrate with actual search tool
        # CRITICAL: Must return real search results, not generated

        results = []
        # ... actual implementation
        return results

    async def fetch_content(self, url: str) -> str:
        """
        Fetch actual content from a URL
        """
        # Option 1: Use WebFetch tool
        # Option 2: Use aiohttp with proper headers

        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    return await response.text()
                return ""
```

**Implementation Notes**:
- Simple wrapper for web operations
- MUST use real search APIs/tools
- NEVER generate fake URLs
- Handle timeouts and errors gracefully

---

### Task 5: Testing with Real CEOs (1 hour)
**File**: `gpt_5_ceo_research/test_real_ceos.py`

```python
import asyncio
from src.researcher import CEOResearcher
from src.config.settings import get_settings

async def test_known_ceos():
    """Test with well-known CEOs to verify accuracy"""

    test_cases = [
        ("Cook, Tim", "Apple"),
        ("Nadella, Satya", "Microsoft"),
        ("Pichai, Sundar", "Google"),
        ("Musk, Elon", "Tesla"),
        ("Barra, Mary", "General Motors")
    ]

    settings = get_settings()
    researcher = CEOResearcher(settings)

    results = []
    for ceo_name, company in test_cases:
        print(f"\nTesting: {ceo_name} ({company})")
        try:
            profile = await researcher.research_ceo(ceo_name, company)

            # Check key fields
            accuracy_check = {
                'name': profile.ceo_name,
                'company': profile.company_name,
                'classification': profile.insider_outsider,
                'has_start_date': bool(profile.start_date),
                'has_education': bool(profile.education_schools),
                'sources_count': len(profile.primary_sources)
            }

            results.append(accuracy_check)
            print(f"  ✓ Classification: {profile.insider_outsider}")
            print(f"  ✓ Start Date: {profile.start_date}")
            print(f"  ✓ Sources: {len(profile.primary_sources)}")

        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            results.append({'error': str(e)})

    # Summary
    print("\n" + "="*50)
    print("RESULTS SUMMARY")
    successful = len([r for r in results if 'error' not in r])
    print(f"Success Rate: {successful}/{len(test_cases)}")

if __name__ == "__main__":
    asyncio.run(test_known_ceos())
```

**Implementation Notes**:
- Test with real, well-known CEOs
- Verify accuracy of key fields
- No arbitrary "completeness" scores
- Focus on accuracy of what IS found

---

## Day 2 (Optional): Enhancements

### Task 6: Batch Processing (2 hours)
**Only if single CEO lookup works perfectly**

```python
@click.option('--batch', '-b', type=click.Path(exists=True), help='CSV file with CEOs to research')
async def research_batch(batch_file: str):
    """Process multiple CEOs from CSV"""
    # Simple loop through CSV
    # No complex orchestration needed
```

### Task 7: Caching Layer (1 hour)
**Only if API costs become an issue**

```python
class SimpleCache:
    """Basic file-based cache for search results"""
    # Cache search results to avoid duplicate API calls
    # Simple JSON files, no Redis needed
```

---

## Success Metrics (Simplified)

### What Success Looks Like:
1. **Accuracy**: Information extracted matches reality
2. **No Hallucination**: All sources are real, all URLs work
3. **Best Effort Completeness**: Get what's available, don't force it
4. **Clean Output**: Valid CSV with all fields

### What We're NOT Measuring:
- ❌ Arbitrary "80% completeness" - if data doesn't exist, that's fine
- ❌ Processing speed metrics - accuracy first
- ❌ Complex confidence scores - GPT-5 handles this

---

## Testing Strategy (Simplified)

### Essential Tests Only:
1. **Model Tests**: CEOProfile validates data correctly
2. **Integration Test**: Can research one real CEO end-to-end
3. **Output Test**: CSV export works correctly

### Skip These Over-Engineered Tests:
- ❌ Testing each "tool" separately (we only have one researcher)
- ❌ Mock GPT-5 responses (test with real API)
- ❌ Complex retry logic tests (already built into client)

---

## File Structure (Final)

```
gpt_5_ceo_research/
├── src/
│   ├── models/
│   │   └── ceo_profile.py        # The ONE data model
│   ├── researcher.py              # The ONE research class
│   └── web_tools.py              # Simple web utilities
├── research_ceo.py               # CLI interface
├── test_real_ceos.py             # Real-world testing
└── output/                       # CSV outputs
```

That's it! No 10+ specialized tools, no complex orchestration, no phase management.

---

## Implementation Order (Do This Today)

1. **Hour 1**: Create CEOProfile model with all 40+ fields
2. **Hour 2-3**: Build CEOResearcher with 4-step process
3. **Hour 4**: Add web search integration (real searches only)
4. **Hour 5**: Create CLI and test with 5 real CEOs
5. **Hour 6**: Debug and refine based on real results

**By end of day**: Working CEO research system with all 40+ fields!

---

## Key Principles Throughout

1. **GPT-5 Does the Thinking**: No rule-based extractors or classifiers
2. **Real Data Only**: No generated URLs or fake sources
3. **Accuracy Over Completeness**: Better to have missing fields than wrong data
4. **KISS Architecture**: One model, one researcher, one CLI
5. **Structured but Simple**: Clean code, not a hacky script, but not over-engineered

This is the entire project. No weeks of development. No specialized tools. Just GPT-5's reasoning power properly directed.