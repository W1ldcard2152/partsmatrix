"""
Test script for eBay Parts Extractor
Validates API credentials and basic functionality without making many API calls
"""

import os
import sys

# Load environment variables from .env file in project root
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
env_path = project_root / '.env'

# Load environment variables
try:
    from dotenv import load_dotenv
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Loaded environment variables from {env_path}")
except ImportError:
    # Fallback: manually parse .env file
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        print(f"✅ Manually loaded .env file")
import json
from ebay_parts_extractor import EbayPartsExtractor

def test_api_credentials():
    """Test if eBay API credentials are properly configured"""
    print("Testing eBay API Credentials...")
    print("-" * 40)
    
    # Check for App ID
    app_id = os.getenv('EBAY_APP_ID')
    if not app_id:
        print("❌ EBAY_APP_ID environment variable not set")
        print("Please set your eBay App ID:")
        print("export EBAY_APP_ID='your-app-id-here'")
        return False
    
    print(f"✅ EBAY_APP_ID found: {app_id[:10]}...")
    return True

def test_extractor_initialization():
    """Test if the extractor can be initialized"""
    print("\nTesting Extractor Initialization...")
    print("-" * 40)
    
    try:
        app_id = os.getenv('EBAY_APP_ID')
        extractor = EbayPartsExtractor(app_id)
        print("✅ EbayPartsExtractor initialized successfully")
        return extractor
    except Exception as e:
        print(f"❌ Failed to initialize extractor: {e}")
        return None

def test_pattern_extraction():
    """Test the pattern extraction methods"""
    print("\nTesting Pattern Extraction...")
    print("-" * 40)
    
    app_id = os.getenv('EBAY_APP_ID', 'test')
    extractor = EbayPartsExtractor(app_id)
    
    # Test data similar to eBay listings
    test_cases = [
        {
            'title': '2005-2008 Acura TL AC Compressor - Denso (471-0101) OEM Quality',
            'expected_part_name': 'AC Compressor',
            'expected_part_number': '471-0101',
            'expected_manufacturer': 'Denso'
        },
        {
            'title': 'For 2006 2007 2008 Acura TSX A/C Compressor & Clutch Assembly Sanden',
            'expected_part_name': 'AC Compressor',
            'expected_part_number': None,
            'expected_manufacturer': 'Sanden'
        },
        {
            'title': 'Acura MDX 2007-2013 Air Conditioning Compressor Part# 38810-RYE-A01',
            'expected_part_name': 'Air Conditioning Compressor',
            'expected_part_number': '38810-RYE-A01',
            'expected_manufacturer': 'Acura'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['title'][:50]}...")
        
        # Test part name extraction
        part_name = extractor.extract_part_name(test_case['title'])
        print(f"  Part Name: {part_name} (expected: {test_case['expected_part_name']})")
        
        # Test part number extraction
        part_number = extractor.extract_part_number(test_case['title'])
        print(f"  Part Number: {part_number} (expected: {test_case['expected_part_number']})")
        
        # Test manufacturer extraction
        manufacturer = extractor.extract_manufacturer(test_case['title'])
        print(f"  Manufacturer: {manufacturer} (expected: {test_case['expected_manufacturer']})")
        
        # Test fitment extraction
        fitments = extractor.extract_fitments("", test_case['title'])
        print(f"  Fitments: {len(fitments)} found")
        if fitments:
            print(f"    Example: {fitments[0]}")

def test_single_api_call():
    """Test a single API call to verify connectivity"""
    print("\nTesting Single API Call...")
    print("-" * 40)
    
    app_id = os.getenv('EBAY_APP_ID')
    if not app_id:
        print("❌ Cannot test API call - no App ID")
        return False
    
    extractor = EbayPartsExtractor(app_id)
    
    try:
        # Make a small search to test API connectivity
        items = extractor.search_parts(
            keywords="Acura AC Compressor",
            max_results=5  # Only get 5 items for testing
        )
        
        if items:
            print(f"✅ API call successful - found {len(items)} items")
            
            # Test parsing the first item
            if len(items) > 0:
                ebay_part = extractor.parse_item(items[0])
                if ebay_part:
                    print(f"✅ Successfully parsed item: {ebay_part.title[:50]}...")
                    print(f"   Price: ${ebay_part.price:.2f}")
                    print(f"   Part Name: {ebay_part.part_name or 'Not extracted'}")
                    print(f"   Part Number: {ebay_part.part_number or 'Not extracted'}")
                    print(f"   Manufacturer: {ebay_part.manufacturer or 'Not extracted'}")
                else:
                    print("❌ Failed to parse item")
            return True
        else:
            print("⚠️  API call successful but no items found")
            print("   This could be normal if no matching listings exist")
            return True
            
    except Exception as e:
        print(f"❌ API call failed: {e}")
        return False

def main():
    """Run all tests"""
    print("eBay Parts Extractor - Test Suite")
    print("=" * 50)
    
    # Test 1: Check credentials
    if not test_api_credentials():
        print("\n❌ Cannot proceed without valid eBay App ID")
        return
    
    # Test 2: Initialize extractor
    extractor = test_extractor_initialization()
    if not extractor:
        print("\n❌ Cannot proceed - extractor initialization failed")
        return
    
    # Test 3: Pattern extraction
    test_pattern_extraction()
    
    # Test 4: Single API call
    print("\n" + "=" * 50)
    proceed = input("Run live API test? This will make a real eBay API call (y/n): ").lower()
    if proceed in ['y', 'yes']:
        test_single_api_call()
    else:
        print("Skipped API test")
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    print("✅ = Passed")
    print("❌ = Failed") 
    print("⚠️  = Warning")
    print("\nIf all tests pass, you're ready to run the full extractor!")

if __name__ == "__main__":
    main()
