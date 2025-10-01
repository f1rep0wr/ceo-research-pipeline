# Bank CEO Project Extensions

This folder contains the new tooling that aligns the GPT-5 research workflow with the ank_ceo_project.csv schema.

## Components

- schema_map.json / README_schema.md — canonical column map derived from the project CSV.
- ank_ceo_profile.py — unified Pydantic model plus conversion helpers (including confidence warnings).
- project_prompts.py — schema-aware prompt wrapper for comprehensive runs.
- data_utils.py — CSV load/save helpers that preserve ordering and header metadata.
- ank_ceo_cli.py — command-line interface for refreshing selected KEYIDs.
- un_demo.py — quick sanity check that lists sample KEYIDs.

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

