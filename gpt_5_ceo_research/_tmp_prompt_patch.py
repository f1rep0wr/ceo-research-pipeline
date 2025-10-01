from pathlib import Path
path = Path('src/prompts/ceo_research_prompts.py')
text = path.read_text()
text = text.replace('- Departure circumstances (if applicable)\n- Reason for leaving (if applicable)\n', '- Departure circumstances (only if a departure has already occurred)\n- Reason for leaving (include only when confirmed)\n')
text = text.replace('    "departure_voluntary": "true/false/null", \n    "was_forced_out": "true/false/null",\n    "retirement_status": "true/false/null",\n', '    "departure_voluntary": "true/false/null",  # set true only if departure already occurred\n    "was_forced_out": "true/false/null",  # mark true only with confirmed involuntary departure\n    "retirement_status": "true/false/null",  # mark true only when retirement is formally announced\n')
text = text.replace('Look for official announcements, board minutes, and press coverage of transitions."""', 'Only populate departure-related fields when you find definitive evidence that the CEO has already left (e.g., regulatory order in effect, resignation filed, successor named).\nLook for official announcements, board minutes, and press coverage of transitions."""')
path.write_text(text)
