import json
import re
from pathlib import Path

import pandas as pd

CSV_PATH = Path('improvements/bank_ceo_project.csv')
RAW_DF = pd.read_csv(CSV_PATH, header=None)
HEADER = RAW_DF.iloc[1]

headers = []
for value in HEADER:
    if isinstance(value, float) and pd.isna(value):
        headers.append(None)
    else:
        headers.append(str(value))

def to_snake(name: str) -> str:
    name = name.strip()
    name = name.replace("'", "")
    name = re.sub(r"[\s\-/]+", "_", name)
    name = re.sub(r"[^0-9a-zA-Z_]+", "", name)
    name = re.sub(r"__+", "_", name)
    name = name.strip("_")
    return name.lower() or "field"

mapping = {}
used = set()
for original in headers:
    if not original:
        continue
    base = to_snake(original)
    candidate = base
    suffix = 2
    while candidate in used:
        candidate = f"{base}_{suffix}"
        suffix += 1
    used.add(candidate)
    mapping[original] = candidate

schema = {
    "original_to_internal": mapping,
    "internal_to_original": {v: k for k, v in mapping.items()},
}

schema_path = Path('improvements/schema_map.json')
schema_path.write_text(json.dumps(schema, indent=2))

README_TEXT = """# Bank CEO Project Schema

- Source file: `improvements/bank_ceo_project.csv`
- Row 2 (index 1) contains column labels; trailing empty columns are ignored.
- `schema_map.json` stores canonical snake_case field names derived from the original headers.
- Use `original_to_internal` when parsing CSV rows into models.
- Use `internal_to_original` to export rows back into the project spreadsheet format.
"""

README = Path('improvements/README_schema.md')
README.write_text(README_TEXT)
