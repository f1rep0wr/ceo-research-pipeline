# Bank CEO Project Schema

- Source file: `improvements/bank_ceo_project.csv`
- Row 2 (index 1) contains column labels; trailing empty columns are ignored.
- `schema_map.json` stores canonical snake_case field names derived from the original headers.
- Use `original_to_internal` when parsing CSV rows into models.
- Use `internal_to_original` to export rows back into the project spreadsheet format.
