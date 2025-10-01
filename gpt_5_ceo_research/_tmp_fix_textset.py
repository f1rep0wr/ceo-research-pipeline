from pathlib import Path
path = Path('improvements/bank_ceo_profile.py')
text = path.read_text()
old = '    "notes_2",\n    "job_title_in_next_company",\n    "next_company",\n    "    }'
new = '    "notes_2",\n    "job_title_in_next_company",\n    "next_company",\n    }'
if old not in text:
    raise SystemExit('pattern not found')
path.write_text(text.replace(old, new, 1))
