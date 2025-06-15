"""
Simple eBay API Test
Uses the most basic eBay Finding API call to test credentials
"""

import os
import requests
import json
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

def test_simple_ebay_call():
    """Test the simplest possible eBay API call"""
    
    app_id = os.getenv('EBAY_APP_ID')
    if not app_id:
        print("❌ EBAY_APP_ID not found")
        return False
    
    print(f"Testing with App ID: {app_id[:15]}...")
    
    # Simplest possible parameters
    params = {
        'OPERATION-NAME': 'findItemsByKeywords',
        'SERVICE-VERSION': '1.0.0',
        'SECURITY-APPNAME': app_id,
        'RESPONSE-DATA-FORMAT': 'JSON',
        'keywords': 'compressor',
        'paginationInput.entriesPerPage': '3'
    }
    
    url = "https://svcs.ebay.com/services/search/FindingService/v1"
    
    try:
        print("Making simple API call...")
        response = requests.get(url, params=params, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check for errors
            if 'errorMessage' in data:
                print("❌ API Error:")
                errors = data['errorMessage']
                if isinstance(errors, list) and len(errors) > 0:
                    error = errors[0].get('error', {})
                    print(f"   Message: {error.get('message', 'Unknown error')}")
                    print(f"   Error ID: {error.get('errorId', 'Unknown')}")
                    return False
            
            # Check response
            response_data = data.get('findItemsByKeywordsResponse', [{}])[0]
            ack = response_data.get('ack', [''])[0]
            
            print(f"API Response: {ack}")
            
            if ack == 'Success':
                search_result = response_data.get('searchResult', [{}])[0]
                count = search_result.get('@count', '0')
                print(f"✅ Success! Found {count} items")
                
                # Show a sample item if available
                items = search_result.get('item', [])
                if items:
                    item = items[0]
                    title = item.get('title', [''])[0]
                    print(f"Sample item: {title[:50]}...")
                
                return True
            else:
                print(f"❌ API call failed: {ack}")
                return False
        
        elif response.status_code == 500:
            print("❌ 500 Server Error - This usually means:")
            print("   1. Invalid App ID or not activated")
            print("   2. App ID is for wrong environment (Sandbox vs Production)")
            print("   3. Missing required parameters")
            print("   4. eBay service temporarily down")
            
            # Try to parse error response
            try:
                error_data = response.json()
                print(f"   Server response: {error_data}")
            except:
                print(f"   Raw response: {response.text[:200]}")
            
            return False
        
        else:
            print(f"❌ HTTP Error {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    print("Simple eBay API Test")
    print("=" * 30)
    test_simple_ebay_call()
