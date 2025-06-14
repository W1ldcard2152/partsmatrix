#!/usr/bin/env python
"""
Test improved pattern extraction
"""

import os
import sys
from pathlib import Path

# Load environment variables from .env file in project root
project_root = Path(__file__).resolve().parent.parent
env_path = project_root / '.env'

# Load environment variables
try:
    from dotenv import load_dotenv
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    # Fallback: manually parse .env file
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

from ebay_parts_extractor import EbayPartsExtractor

def test_improved_patterns():
    """Test the improved pattern extraction"""
    print("Testing Improved Pattern Extraction")
    print("=" * 50)
    
    app_id = os.getenv('EBAY_APP_ID', 'test')
    extractor = EbayPartsExtractor(app_id)
    
    # Test data with expected results
    test_cases = [
        {
            'title': '2005-2008 Acura TL AC Compressor - Denso (471-0101) OEM Quality',
            'expected_part_name': 'AC Compressor',
            'expected_part_number': '471-0101',
            'expected_manufacturer': 'Denso',
            'expected_fitment_count': 4  # 2005, 2006, 2007, 2008
        },
        {
            'title': 'For 2006 2007 2008 Acura TSX A/C Compressor & Clutch Assembly Sanden',
            'expected_part_name': 'A/C Compressor & Clutch Assembly',
            'expected_part_number': None,
            'expected_manufacturer': 'Sanden',
            'expected_fitment_count': 3  # 2006, 2007, 2008
        },
        {
            'title': 'Acura MDX 2007-2013 Air Conditioning Compressor Part# 38810-RYE-A01',
            'expected_part_name': 'Air Conditioning Compressor',
            'expected_part_number': '38810-RYE-A01',
            'expected_manufacturer': 'Acura',
            'expected_fitment_count': 7  # 2007-2013
        },
        {
            'title': '2010 Honda Civic AC Compressor - Four Seasons 58155',
            'expected_part_name': 'AC Compressor',
            'expected_part_number': '58155',
            'expected_manufacturer': 'Four Seasons',
            'expected_fitment_count': 1  # 2010
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        title = test_case['title']
        print(f"\nTest Case {i}:")
        print(f"Title: {title}")
        print("-" * 40)
        
        # Test part name extraction
        part_name = extractor.extract_part_name(title)
        expected_name = test_case['expected_part_name']
        name_match = part_name == expected_name
        print(f"Part Name: {part_name}")
        print(f"Expected:  {expected_name}")
        print(f"✅ Match" if name_match else f"❌ No match")
        
        # Test part number extraction
        part_number = extractor.extract_part_number(title)
        expected_number = test_case['expected_part_number']
        number_match = part_number == expected_number
        print(f"Part Number: {part_number}")
        print(f"Expected:    {expected_number}")
        print(f"✅ Match" if number_match else f"❌ No match")
        
        # Test manufacturer extraction
        manufacturer = extractor.extract_manufacturer(title)
        expected_mfg = test_case['expected_manufacturer']
        mfg_match = manufacturer == expected_mfg
        print(f"Manufacturer: {manufacturer}")
        print(f"Expected:     {expected_mfg}")
        print(f"✅ Match" if mfg_match else f"❌ No match")
        
        # Test fitment extraction
        fitments = extractor.extract_fitments("", title)
        expected_count = test_case['expected_fitment_count']
        count_match = len(fitments) == expected_count
        print(f"Fitments: {len(fitments)} found (expected: {expected_count})")
        print(f"✅ Match" if count_match else f"❌ No match")
        
        if fitments:
            print("Sample fitments:")
            for fit in fitments[:3]:  # Show first 3
                print(f"  {fit['year']} {fit['make']} {fit['model']}")
            if len(fitments) > 3:
                print(f"  ... and {len(fitments) - 3} more")
        
        # Overall result for this test case
        all_match = name_match and number_match and mfg_match and count_match
        print(f"Overall: {'✅ PASS' if all_match else '❌ FAIL'}")

if __name__ == "__main__":
    test_improved_patterns()
