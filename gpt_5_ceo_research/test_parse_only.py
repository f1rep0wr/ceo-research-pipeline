#!/usr/bin/env python3
"""
Test script to check input parsing without making API calls
"""

def test_input_parsing(input_file: str):
    """Test parsing logic without API calls"""
    ceo_list = []

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                original_line = line
                line = line.strip()

                print(f"Line {line_num:2d}: '{original_line.rstrip()}'")

                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    print(f"         -> SKIPPED (empty or comment)")
                    continue

                # Parse CEO | Company
                if '|' not in line:
                    print(f"         -> WARNING: Invalid format (no pipe): {line}")
                    continue

                parts = line.split('|')
                if len(parts) != 2:
                    print(f"         -> WARNING: Invalid format (multiple pipes): {line}")
                    continue

                ceo_name = parts[0].strip()
                company = parts[1].strip()

                if ceo_name and company:
                    ceo_list.append((ceo_name, company))
                    print(f"         -> VALID: '{ceo_name}' | '{company}'")
                else:
                    print(f"         -> WARNING: Empty name or company: '{ceo_name}' | '{company}'")

    except Exception as e:
        print(f"ERROR: {e}")
        return []

    print(f"\nSUMMARY: Found {len(ceo_list)} valid CEOs")
    for i, (name, company) in enumerate(ceo_list, 1):
        print(f"  {i}. {name} | {company}")

    return ceo_list

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python test_parse_only.py <input_file>")
        sys.exit(1)

    test_input_parsing(sys.argv[1])