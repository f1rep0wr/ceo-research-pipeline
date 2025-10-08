# Bank CEO Project Extensions

This folder contains the new tooling that aligns the GPT-5 research workflow with the ank_ceo_project.csv schema.

## Components

- schema_map.json / README_schema.md ï¿½ canonical column map derived from the project CSV.
- ank_ceo_profile.py ï¿½ unified Pydantic model plus conversion helpers (including confidence warnings).
- project_prompts.py ï¿½ schema-aware prompt wrapper for comprehensive runs.
- data_utils.py ï¿½ CSV load/save helpers that preserve ordering and header metadata.
- ank_ceo_cli.py ï¿½ command-line interface for refreshing selected KEYIDs.
- 
un_demo.py ï¿½ quick sanity check that lists sample KEYIDs.

## Usage

Dry run against two KEYIDs:

`
python -m improvements.bank_ceo_cli --keyid 5015,5016 --dry-run
`

Update a range and write to a new CSV:

`
python -m improvements.bank_ceo_cli --keyid-range 5015-5018 --output improvements/bank_ceo_project_updated.csv
`

The CLI pulls the existing CEO and company names from the dataset, calls the progressive researcher, merges results into the project schema, and injects a notes warning whenever confidence_score < 0.7.

## Verification
Verify existing rows:

```
python -m improvements.verify_cli --input improvements/bank_ceo_project_updated.csv --keyid-range 5015-5020 --responses-fallback --output-report output/verification.md
    
    
    --deep-verify \
    --fields appointment_date,insider \
```

The verifier runs in layers:

1. Quick field sanity checks (required names, insider/outsider flags, dates).
2. Source fetches using the in-house HTTP/Playwright stack, with optional GPT-5 retry for blocked links (`--responses-fallback`).
3. Optional deep verification (`--deep-verify`) that bundles source snippets and asks GPT-5 to confirm the specified fields (`--fields`).

When `--output-report` is provided a Markdown summary is written alongside the console output.
