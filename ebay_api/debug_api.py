"""
Debug eBay API Connection
Helps diagnose 500 errors and other API issues
"""

import os
import sys
import requests
import json
from pathlib import Path
from urllib.parse import urlencode

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

def test_ebay_service_status():
    """Check if eBay service is available"""
    print("Testing eBay Service Status...")
    print("-" * 40)
    
    try:
        # Test basic connectivity to eBay
        response = requests.get("https://developer.ebay.com", timeout=10)
        print(f"✅ eBay Developer site accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot reach eBay Developer site: {e}")
        return False
    
    return True

def test_finding_service_minimal():
    """Test minimal eBay Finding Service call"""
    print("\nTesting Minimal eBay Finding Service...")
    print("-" * 40)
    
    app_id = os.getenv('EBAY_APP_ID')
    if not app_id:
        print("❌ EBAY_APP_ID not found")
        return False
    
    # Most minimal possible request
    params = {
        'OPERATION-NAME': 'findItemsByKeywords',
        'SERVICE-VERSION': '1.0.0',
        'SECURITY-APPNAME': app_id,
        'RESPONSE-DATA-FORMAT': 'JSON',
        'keywords': 'compressor',
        'paginationInput.entriesPerPage': '1'
    }
    
    url = "https://svcs.ebay.com/services/search/FindingService/v1"
    
    try:
        print(f"Making request to: {url}")
        print(f"App ID (first 10 chars): {app_id[:10]}...")
        
        response = requests.get(url, params=params, timeout=30)
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ JSON response received")
                
                # Check for API errors
                if 'errorMessage' in data:
                    print("❌ eBay API returned errors:")
                    errors = data['errorMessage']
                    if isinstance(errors, list):
                        for error in errors:
                            if 'error' in error:
                                print(f"   Error: {error['error']}")
                    else:
                        print(f"   Error: {errors}")
                    return False
                
                # Check for successful search result
                search_result = data.get('findItemsByKeywordsResponse', [{}])[0]
                ack = search_result.get('ack', [''])[0]
                print(f"API acknowledgment: {ack}")
                
                if ack == 'Success':
                    print("✅ eBay API call successful!")
                    
                    # Show some basic stats
                    search_results = search_result.get('searchResult', [{}])[0]
                    count = search_results.get('@count', '0')
                    print(f"Items found: {count}")
                    
                    return True
                else:
                    print(f"❌ eBay API call failed with ack: {ack}")
                    return False
                    
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON response: {e}")
                print(f"Response content: {response.text[:500]}...")
                return False
                
        else:
            print(f"❌ HTTP error {response.status_code}")
            print(f"Response content: {response.text[:500]}...")
            return False
            
    except requests.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_advanced_finding_service():
    """Test the more advanced call that was failing"""
    print("\nTesting Advanced eBay Finding Service...")
    print("-" * 40)
    
    app_id = os.getenv('EBAY_APP_ID')
    if not app_id:
        print("❌ EBAY_APP_ID not found")
        return False
    
    # Same parameters that were failing before
    params = {
        'OPERATION-NAME': 'findItemsAdvanced',
        'SERVICE-VERSION': '1.0.0',
        'SECURITY-APPNAME': app_id,
        'RESPONSE-DATA-FORMAT': 'JSON',
        'REST-PAYLOAD': '',
        'keywords': 'Acura AC Compressor',
        'categoryId': '33654',
        'paginationInput.entriesPerPage': '5',
        'itemFilter(0).name': 'MinPrice',
        'itemFilter(0).value': '50.0',
        'itemFilter(1).name': 'Condition',
        'itemFilter(1).value(0)': 'Used',
        'itemFilter(1).value(1)': 'New',
        'itemFilter(2).name': 'ListingType',
        'itemFilter(2).value': 'FixedPrice',
        'sortOrder': 'PricePlusShippingLowest'
    }
    
    url = "https://svcs.ebay.com/services/search/FindingService/v1"
    
    try:
        print(f"Making advanced request to: {url}")
        
        response = requests.get(url, params=params, timeout=30)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ JSON response received")
                
                # Check for API errors
                if 'errorMessage' in data:
                    print("❌ eBay API returned errors:")
                    errors = data['errorMessage']
                    if isinstance(errors, list):
                        for error in errors:
                            if 'error' in error:
                                error_detail = error['error']
                                print(f"   Error ID: {error_detail.get('errorId', 'Unknown')}")
                                print(f"   Domain: {error_detail.get('domain', 'Unknown')}")
                                print(f"   Severity: {error_detail.get('severity', 'Unknown')}")
                                print(f"   Category: {error_detail.get('category', 'Unknown')}")
                                print(f"   Message: {error_detail.get('message', 'Unknown')}")
                    else:
                        print(f"   Error: {errors}")
                    return False
                
                # Check response
                search_result = data.get('findItemsAdvancedResponse', [{}])[0]
                ack = search_result.get('ack', [''])[0]
                print(f"API acknowledgment: {ack}")
                
                if ack == 'Success':
                    print("✅ Advanced eBay API call successful!")
                    
                    search_results = search_result.get('searchResult', [{}])[0]
                    count = search_results.get('@count', '0')
                    print(f"Items found: {count}")
                    
                    return True
                else:
                    print(f"❌ Advanced eBay API call failed with ack: {ack}")
                    return False
                    
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON response: {e}")
                print(f"Response content: {response.text[:500]}...")
                return False
                
        else:
            print(f"❌ HTTP error {response.status_code}")
            print(f"Response content: {response.text[:500]}...")
            return False
            
    except requests.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def check_app_id_validity():
    """Validate the App ID format"""
    print("\nValidating eBay App ID...")
    print("-" * 40)
    
    app_id = os.getenv('EBAY_APP_ID')
    if not app_id:
        print("❌ EBAY_APP_ID not found")
        return False
    
    print(f"App ID: {app_id}")
    print(f"Length: {len(app_id)}")
    
    # eBay App IDs typically follow this pattern: AppName-Environment-PRD/SBX-AppIDHash-KeyHash
    if '-' in app_id:
        parts = app_id.split('-')
        print(f"Parts: {parts}")
        
        if len(parts) >= 4:
            print("✅ App ID format looks correct")
            
            # Check environment
            if 'PRD' in app_id:
                print("✅ Production App ID detected")
            elif 'SBX' in app_id:
                print("ℹ️  Sandbox App ID detected")
            else:
                print("⚠️  Environment unclear from App ID")
                
            return True
        else:
            print("⚠️  App ID format unusual but might be valid")
            return True
    else:
        print("⚠️  App ID format doesn't match typical eBay pattern")
        return True

def main():
    """Run all diagnostic tests"""
    print("eBay API Diagnostic Tool")
    print("=" * 50)
    
    # Test 1: Basic connectivity
    if not test_ebay_service_status():
        print("\n❌ Cannot proceed - basic connectivity failed")
        return
    
    # Test 2: App ID validation
    check_app_id_validity()
    
    # Test 3: Minimal API call
    print("\n" + "=" * 50)
    if test_finding_service_minimal():
        print("\n✅ Basic eBay API works - trying advanced call...")
        
        # Test 4: Advanced API call (the one that was failing)
        test_advanced_finding_service()
    else:
        print("\n❌ Basic eBay API call failed")
        print("\nPossible issues:")
        print("1. Invalid App ID")
        print("2. App ID not activated for production")
        print("3. eBay service temporarily down")
        print("4. Network/firewall issues")
    
    print("\n" + "=" * 50)
    print("Diagnostic complete!")

if __name__ == "__main__":
    main()
