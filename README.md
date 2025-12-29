# CEO Research Tool

A command-line tool for researching CEO information using GPT-5 with web search capabilities. Designed with KISS principles for simplicity and reliability.

## Features

- Research individual CEOs or process batches
- Comprehensive data collection (29+ fields)
- Tracks when CEOs first joined their companies (initial_join_year)
- Classifies CEOs as insiders vs outsiders
- High-quality data with confidence scores
- Exports results to CSV format

## Requirements

- Python 3.7+
- OpenAI API key with GPT-5 access
- Required packages: see requirements.txt

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set your OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Usage

### Single CEO Research

Research one CEO at a time:

```bash
python research_ceo.py "CEO Name" "Company Name"
```

Examples:
```bash
python research_ceo.py "Tim Cook" "Apple"
python research_ceo.py "Mary Barra" "General Motors"
python research_ceo.py "Satya Nadella" "Microsoft" --verbose
python research_ceo.py "Jamie Dimon" "JPMorgan Chase" --output custom.csv
```

Options:
- `--output` or `-o`: Specify output CSV file (default: output/ceo_research.csv)
- `--verbose` or `-v`: Show detailed progress information

### Batch Processing

Process multiple CEOs from a text file:

```bash
python batch_research.py input_file.txt [output.csv] [delay_seconds]
```

Examples:
```bash
python batch_research.py ceos.txt
python batch_research.py ceos.txt output/results.csv
python batch_research.py ceos.txt output/results.csv 3
```

Arguments:
- `input_file.txt`: Text file with CEO list (required)
- `output.csv`: Output CSV file (optional, default: output/ceo_research.csv)
- `delay_seconds`: Seconds to wait between API calls (optional, default: 2)

### Creating Input Files for Batch Processing

Create a plain text file with one CEO per line, using pipe (|) separator:

**ceos.txt example:**
```
Tim Cook | Apple
Mary Barra | General Motors
Satya Nadella | Microsoft
Jamie Dimon | JPMorgan Chase
Jensen Huang | NVIDIA
```

Features:
- Comments: Lines starting with # are ignored
- Empty lines: Skipped automatically
- Simple format: Just "Name | Company"

**Advanced example with comments:**
```
# Tech CEOs
Tim Cook | Apple
Satya Nadella | Microsoft

# Automotive industry
Mary Barra | General Motors
Jim Farley | Ford

# Financial services
Jamie Dimon | JPMorgan Chase
Brian Moynihan | Bank of America
```

## Output Format

Results are saved to CSV with the following key fields:

- **ceo_name**: Full name of the CEO
- **company_name**: Company name
- **insider_outsider**: Classification (insider/outsider)
- **initial_join_year**: Year first joined company in ANY role
- **appointment_date**: Date became CEO
- **tenure_years**: Years serving as CEO
- **years_before_ceo**: Years at company before becoming CEO
- **confidence_score**: Data quality score (0-1)
- **primary_sources**: Sources used for research
- Plus 20+ additional fields

## Data Quality

Each CEO profile includes:
- **confidence_score**: 0.0 to 1.0 rating of data reliability
- **data_completeness**: high/medium/low assessment
- **primary_sources**: List of sources consulted
- **notes**: Important caveats or context

## Error Handling

- Individual failures don't stop batch processing
- Partial results are saved even if interrupted
- Clear error messages for common issues
- Invalid input lines show warnings but continue

## Tips for Best Results

1. **CEO Names**: Use full formal names (e.g., "Timothy D. Cook" or "Tim Cook")
2. **Company Names**: Use official company names (e.g., "Apple Inc." or "Apple")
3. **Rate Limiting**: Keep default 2-second delay to avoid API throttling
4. **Batch Size**: Process 20-50 CEOs at a time for reliability
5. **Verification**: Check confidence scores to identify low-quality results

## Common Issues

**No results returned:**
- Check your OpenAI API key is set correctly
- Verify you have GPT-5 API access
- Ensure CEO and company names are spelled correctly

**Low confidence scores:**
- May indicate limited public information
- Try using more formal/complete names
- Check if CEO recently appointed (less data available)

**Script errors:**
- Ensure all dependencies are installed
- Check input file format (Name | Company)
- Verify output directory exists and is writable

## Examples of Successful Research

```bash
# Research a single CEO
python research_ceo.py "Mary Barra" "General Motors"
# Output: Correctly identifies her as insider, joined GM in 1980

# Batch process multiple CEOs
python batch_research.py fortune500_ceos.txt output/fortune500_results.csv
# Processes entire list, continues on errors, saves all successful results

# Quick test with verbose output
python research_ceo.py "Jensen Huang" "NVIDIA" --verbose
# Shows detailed progress and data sources
```

## Project Structure

```
gpt_5_ceo_research/
├── research_ceo.py          # Single CEO research CLI
├── batch_research.py         # Batch processing tool
├── src/
│   ├── ceo_research_gpt5.py # Core research logic
│   ├── models/
│   │   └── ceo_profile.py   # CEO data model
│   └── clients/
│       └── gpt5_client.py   # GPT-5 API client
├── output/                   # CSV output directory
└── README.md                 # This file
```

## License

This tool is for research purposes. Ensure compliance with OpenAI's usage policies and respect for data privacy when researching individuals.