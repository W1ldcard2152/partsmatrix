"""
Debug eBay Browse API Results
Shows what's being filtered out and why
"""

import os
import requests
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

# Load environment variables
project_root = Path(__file__).resolve().parent.parent
env_path = project_root / '.env'

if env_path.exists():
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

class EbayBrowseDebugger:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expires_at = None
        
        self.auth_url = "https://api.ebay.com/identity/v1/oauth2/token"
        self.browse_url = "https://api.ebay.com/buy/browse/v1"

    def get_access_token(self) -> str:
        if (self.access_token and self.token_expires_at and 
            datetime.now() < self.token_expires_at):
            return self.access_token
        
        import base64
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {encoded}'
        }
        
        data = {
            'grant_type': 'client_credentials',
            'scope': 'https://api.ebay.com/oauth/api_scope'
        }
        
        response = requests.post(self.auth_url, headers=headers, data=data, timeout=30)
        response.raise_for_status()
        
        token_data = response.json()
        self.access_token = token_data['access_token']
        expires_in = token_data.get('expires_in', 7200)
        self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)
        
        return self.access_token

    def debug_search_results(self, query: str = "Acura AC Compressor", limit: int = 10):
        """Debug what's actually being returned by the API"""
        
        token = self.get_access_token()
        
        headers = {
            'Authorization': f'Bearer {token}',
            'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US',
            'Content-Type': 'application/json'
        }
        
        params = {
            'q': query,
            'limit': limit,
            'category_ids': "33654",
            'filter': 'buyingOptions:{FIXED_PRICE},price:[50..],conditions:{NEW,USED}'
        }
        
        url = f"{self.browse_url}/item_summary/search"
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        items = data.get('itemSummaries', [])
        
        print(f"\n=== DEBUG: {query} ===")
        print(f"Total items found: {len(items)}")
        print(f"API response total: {data.get('total', 0)}")
        
        for i, item in enumerate(items, 1):
            title = item.get('title', '')
            item_id = item.get('itemId', '')
            price = item.get('price', {}).get('value', 0)
            
            print(f"\n{i}. Item ID: {item_id}")
            print(f"   Title: {title}")
            print(f"   Price: ${price}")
            
            # Test filtering logic
            title_lower = title.lower()
            has_acura = 'acura' in title_lower
            
            # Test manufacturer extraction
            manufacturer = self.extract_manufacturer(title)
            
            print(f"   Has 'acura' in title: {has_acura}")
            print(f"   Extracted manufacturer: {manufacturer}")
            print(f"   Would pass filter: {has_acura or manufacturer == 'Acura'}")
            
            # Show the actual filtering decision
            if has_acura or manufacturer == 'Acura':
                print("   ✅ WOULD BE INCLUDED")
            else:
                print("   ❌ WOULD BE FILTERED OUT")
        
        return items

    def extract_manufacturer(self, text: str) -> str:
        """Same manufacturer extraction logic as main extractor"""
        manufacturer_mapping = {
            'acura': 'Acura', 'honda': 'Honda', 'denso': 'Denso', 'sanden': 'Sanden',
            'delphi': 'Delphi', 'valeo': 'Valeo', 'bosch': 'Bosch', 'four seasons': 'Four Seasons',
        }
        
        text_lower = text.lower()
        
        # Check parts manufacturers first
        parts_manufacturers = ['denso', 'sanden', 'delphi', 'valeo', 'bosch']
        for mfg in parts_manufacturers:
            if mfg in text_lower:
                return manufacturer_mapping[mfg]
        
        # Then vehicle manufacturers
        for key, value in manufacturer_mapping.items():
            if key in text_lower:
                return value
        
        return None

def main():
    client_id = os.getenv('EBAY_APP_ID')
    client_secret = os.getenv('EBAY_CERT_ID')
    
    if not client_id or client_secret:
        print("Missing credentials")
        return
    
    debugger = EbayBrowseDebugger(client_id, client_secret)
    
    print("eBay Browse API Debug - Analyzing Filter Logic")
    print("=" * 60)
    
    # Test each search term
    search_terms = [
        "Acura AC Compressor",
        "Acura A/C Compressor", 
        "Acura Air Conditioning Compressor",
        "Acura Compressor Clutch"
    ]
    
    all_items = []
    
    for term in search_terms:
        items = debugger.debug_search_results(term, limit=5)
        all_items.extend(items)
    
    print(f"\n" + "=" * 60)
    print("SUMMARY:")
    print(f"Total items from all searches: {len(all_items)}")
    
    # Check for duplicates
    unique_ids = set()
    duplicates = 0
    
    for item in all_items:
        item_id = item.get('itemId', '')
        if item_id in unique_ids:
            duplicates += 1
        else:
            unique_ids.add(item_id)
    
    print(f"Unique item IDs: {len(unique_ids)}")
    print(f"Duplicate items: {duplicates}")
    
    # Count how many would pass the filter
    would_pass = 0
    for item in all_items:
        title = item.get('title', '')
        title_lower = title.lower()
        manufacturer = debugger.extract_manufacturer(title)
        
        if 'acura' in title_lower or manufacturer == 'Acura':
            would_pass += 1
    
    print(f"Items that would pass Acura filter: {would_pass}")
    print(f"Items that would be filtered out: {len(all_items) - would_pass}")

if __name__ == "__main__":
    main()
