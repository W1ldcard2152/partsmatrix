#!/usr/bin/env python
"""
Debug the specific fitment parsing issue with Test Case 3
"""

import re

def debug_fitment_parsing():
    """Debug the Acura MDX pattern parsing"""
    print("Debug: Fitment Parsing for 'Acura MDX 2007-2013'")
    print("=" * 60)
    
    title = 'Acura MDX 2007-2013 Air Conditioning Compressor Part# 38810-RYE-A01'
    print(f"Title: {title}")
    print()
    
    # Test each pattern individually
    patterns = [
        (r'(\d{4})-(\d{4})\s+([A-Za-z]+)\s+([A-Za-z0-9]+)(?:\s+[A-Z/]+)?', "year-year make model"),
        (r'(?:For|Fits)\s+(\d{4})\s+(\d{4})\s+(\d{4})\s+([A-Za-z]+)\s+([A-Za-z0-9]+)', "For year year year make model"),
        (r'^([A-Za-z]+)\s+([A-Za-z0-9]+)\s+(\d{4})-(\d{4})\s+', "make model year-year"),
        (r'(?:For|Fits)?\s*(\d{4})\s+([A-Za-z]+)\s+([A-Za-z0-9]+)(?:\s+[A-Z/]+)?', "year make model"),
    ]
    
    for i, (pattern, description) in enumerate(patterns, 1):
        print(f"Pattern {i}: {description}")
        print(f"Regex: {pattern}")
        
        matches = list(re.finditer(pattern, title, re.IGNORECASE))
        if matches:
            for match in matches:
                groups = match.groups()
                print(f"✅ Match found: {groups}")
                print(f"   Full match: '{match.group(0)}'")
                print(f"   Start-End: {match.start()}-{match.end()}")
        else:
            print("❌ No match")
        print()
    
    # Test what's actually happening with current logic
    print("Current Logic Simulation:")
    print("-" * 30)
    
    year_model_patterns = [
        r'(\d{4})-(\d{4})\s+([A-Za-z]+)\s+([A-Za-z0-9]+)(?:\s+[A-Z/]+)?',
        r'(?:For|Fits)\s+(\d{4})\s+(\d{4})\s+(\d{4})\s+([A-Za-z]+)\s+([A-Za-z0-9]+)',
        r'^([A-Za-z]+)\s+([A-Za-z0-9]+)\s+(\d{4})-(\d{4})\s+',
        r'(?:For|Fits)?\s*(\d{4})\s+([A-Za-z]+)\s+([A-Za-z0-9]+)(?:\s+[A-Z/]+)?',
    ]
    
    fitments = []
    for pattern in year_model_patterns:
        matches = re.finditer(pattern, title, re.IGNORECASE)
        for match in matches:
            groups = match.groups()
            print(f"Processing match: {groups}")
            
            if len(groups) == 4 and groups[0].isdigit() and groups[1].isdigit():
                start_year = int(groups[0])
                end_year = int(groups[1])
                make = groups[2].title()
                model = groups[3].upper()
                print(f"  → Parsed as: {start_year}-{end_year} {make} {model}")
            elif len(groups) == 4 and groups[2].isdigit() and groups[3].isdigit():
                make = groups[0].title()
                model = groups[1].upper()
                start_year = int(groups[2])
                end_year = int(groups[3])
                print(f"  → Parsed as: {make} {model} {start_year}-{end_year}")
            else:
                print(f"  → No matching logic for this pattern")
    
    print("\nConclusion:")
    print("The issue is that Pattern 1 is matching first and capturing the wrong groups.")

if __name__ == "__main__":
    debug_fitment_parsing()
