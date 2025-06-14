#!/usr/bin/env python
"""
Quick test for the specific MDX fitment fix
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

def test_mdx_fix():
    """Test if the MDX fitment parsing is now fixed"""
    print("Testing MDX Fitment Fix")
    print("=" * 30)
    
    app_id = os.getenv('EBAY_APP_ID', 'test')
    extractor = EbayPartsExtractor(app_id)
    
    title = 'Acura MDX 2007-2013 Air Conditioning Compressor Part# 38810-RYE-A01'
    print(f"Title: {title}")
    print()
    
    fitments = extractor.extract_fitments("", title)
    
    print(f"Fitments found: {len(fitments)}")
    if fitments:
        first_fitment = fitments[0]
        print(f"First fitment: {first_fitment['year']} {first_fitment['make']} {first_fitment['model']}")
        
        if first_fitment['make'] == 'Acura' and first_fitment['model'] == 'MDX':
            print("✅ SUCCESS! MDX fitment parsing is now correct!")
            print(f"Years covered: {min(f['year'] for f in fitments)} - {max(f['year'] for f in fitments)}")
        else:
            print(f"❌ STILL BROKEN: Got {first_fitment['make']} {first_fitment['model']}")
    else:
        print("❌ No fitments extracted")

if __name__ == "__main__":
    test_mdx_fix()
