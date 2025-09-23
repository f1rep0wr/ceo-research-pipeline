# Per-Source CSV Export Feature

## Overview

The CEO research system now creates **one CSV row per source**, making it much easier to analyze and verify sources. Instead of cramming all sources into semicolon-separated lists, each source gets its own row with complete CEO data.

## How It Works

### Before (Old Method)
- 1 CEO = 1 CSV row
- All sources listed in `source_urls` field as: "url1; url2; url3"
- Hard to analyze individual sources

### After (New Method) [OK]
- 1 CEO = Multiple CSV rows (one per source)
- Each row contains:
  - **All CEO profile data** (name, classification, tenure, etc.)
  - **Individual source information** (URL, type, description)
  - **Source metadata** (source number, total sources)

## New CSV Structure

### Additional Fields Added:
- `source_number`: Sequential number (1, 2, 3, etc.)
- `total_sources`: Total number of sources for this CEO
- `source_url`: Individual source URL 
- `source_type`: "URL" or "Description"
- `source_description`: Classified source type (e.g., "SEC EDGAR Filing")

### Example Output:
```csv
ceo_name,company_name,insider_outsider,source_number,total_sources,source_url,source_type,source_description
Brian Moynihan,Bank of America,insider,1,15,https://www.sec.gov/...,URL,SEC EDGAR Filing
Brian Moynihan,Bank of America,insider,2,15,https://investor.bankofamerica.com/...,URL,Official Company Website
Brian Moynihan,Bank of America,insider,3,15,https://www.cnbc.com/...,URL,Financial News Publication
...and 12 more rows
```

## Source Classification

The system automatically classifies sources into categories:

| Source Type | Examples |
|-------------|----------|
| **SEC EDGAR Filing** | SEC filings from edgar database |
| **Official Company Website** | Bank's investor relations, executive bios |
| **Banking Trade Publication** | American Banker, Bank Director |
| **Financial News Publication** | Reuters, Bloomberg, WSJ, FT |
| **Press Release Distribution** | Business Wire, PR Newswire |
| **LinkedIn Profile/Company Page** | LinkedIn professional profiles |
| **General Business Publication** | Forbes, Fortune, Wikipedia |
| **Other Web Source** | Any other web source |

## Real-World Example

**Brian Moynihan Research Results:**
- [OK] **15 sources found**
- [OK] **15 CSV rows created** (one per source)
- [OK] **Source types identified**: SEC filings, company website, CNBC interview, Reuters article
- [OK] **All CEO data preserved** in each row

## Benefits for Analysis

### 1. **Easy Source Verification**
Each source is on its own row with direct URL - perfect for fact-checking

### 2. **Source Quality Analysis**  
Count sources by type: SEC filings vs news articles vs company websites

### 3. **Pivot Table Ready**
Create pivot tables to analyze:
- Sources per CEO
- Source types by classification (insider vs outsider)
- Data quality by source count

### 4. **Citation Tracking**
Track which specific sources support which data points

### 5. **Research Quality Assessment**
Easily identify CEOs with insufficient sources or low-quality source mix

## Usage

The feature is **automatically enabled**. No changes needed to your commands:

```bash
# Same command as before
python research_ceo_enhanced.py "CEO Name" "Bank Name" --method progressive --verbose

# But now creates multiple rows per CEO (one per source)
```

## CSV Row Count Examples

| Sources Found | CSV Rows Created | Example |
|---------------|------------------|---------|
| 3 sources | 3 rows | Small regional bank CEO |
| 15 sources | 15 rows | Major bank CEO (Brian Moynihan example) |
| 21 sources | 21 rows | Major bank CEO (Jamie Dimon example) |
| 0 sources | 1 row | Row with "No sources available" message |

## Backward Compatibility

- [OK] **All existing fields preserved**
- [OK] **Same command-line interface**
- [OK] **Headers automatically created**
- [OK] **Same file naming and output options**

The only change: **More rows per CEO**, which provides **better source analysis** capabilities.

## Analysis Examples

### Count Sources by CEO:
```excel
=SUMPRODUCT((A:A="CEO Name")*(B:B<>""))  // Count non-empty source rows
```

### Average Sources per Classification:
Create pivot table:
- Rows: `insider_outsider`
- Values: Count of `source_number`

### Source Quality Score:
Weight different source types:
- SEC filings = 5 points
- Company websites = 4 points  
- Trade publications = 3 points
- News articles = 2 points
- Other sources = 1 point

## Summary

The per-source CSV export transforms your CEO research data from hard-to-analyze source lists into a structured, analysis-ready format. Each source gets the attention it deserves with its own row, complete source classification, and direct verification links.

**Perfect for:** Source verification, quality analysis, academic research, and comprehensive CEO database management.