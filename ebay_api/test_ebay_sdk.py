"""
eBay SDK Test - Using Official eBay Python SDK
This uses the recommended ebaysdk-python library instead of raw HTTP requests
"""

import os
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

def test_ebaysdk_installation():
    """Test if ebaysdk is installed and working"""
    try:
        from ebaysdk.finding import Connection as Finding
        print("✅ ebaysdk-python is installed")
        return True
    except ImportError:
        print("❌ ebaysdk-python not installed")
        print("Installing it now...")
        
        import subprocess
        import sys
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'ebaysdk'])
            print("✅ ebaysdk-python installed successfully")
            
            # Try importing again
            from ebaysdk.finding import Connection as Finding
            return True
        except Exception as e:
            print(f"❌ Failed to install ebaysdk: {e}")
            return False

def test_ebay_finding_sdk():
    """Test eBay Finding API using the official SDK"""
    
    try:
        from ebaysdk.finding import Connection as Finding
    except ImportError:
        print("❌ Cannot import ebaysdk")
        return False
    
    app_id = os.getenv('EBAY_APP_ID')
    if not app_id:
        print("❌ EBAY_APP_ID not found")
        return False
    
    print(f"Testing with App ID: {app_id[:15]}...")
    
    try:
        # Create connection using the official SDK
        api = Finding(appid=app_id, config_file=None)
        
        # Simple search request
        api.execute('findItemsByKeywords', {
            'keywords': 'compressor',
            'paginationInput': {
                'entriesPerPage': '3'
            }
        })
        
        # Check response
        response = api.response.dict()
        
        # Print some debug info
        print(f"Response keys: {list(response.keys())}")
        
        if 'ack' in response and response['ack'] == 'Success':
            print("✅ eBay SDK call successful!")
            
            search_result = response.get('searchResult', {})
            count = search_result.get('_count', '0')
            print(f"Items found: {count}")
            
            # Show sample item
            items = search_result.get('item', [])
            if items:
                item = items[0] if isinstance(items, list) else items
                title = item.get('title', 'No title')
                print(f"Sample item: {title}")
            
            return True
        
        elif 'errorMessage' in response:
            print("❌ eBay API Error:")
            errors = response['errorMessage']
            if isinstance(errors, dict):
                error = errors.get('error', {})
                print(f"   Message: {error.get('message', 'Unknown')}")
                print(f"   Error ID: {error.get('errorId', 'Unknown')}")
                print(f"   Severity: {error.get('severity', 'Unknown')}")
            
            return False
        
        else:
            print(f"❌ Unexpected response: {response}")
            return False
            
    except Exception as e:
        print(f"❌ SDK call failed: {e}")
        
        # Check if it's a specific eBay error
        if hasattr(e, 'response'):
            try:
                error_response = e.response.dict()
                print(f"Error response: {error_response}")
            except:
                pass
        
        return False

def test_advanced_finding_sdk():
    """Test advanced Finding API call with filters"""
    
    try:
        from ebaysdk.finding import Connection as Finding
    except ImportError:
        print("❌ Cannot import ebaysdk")
        return False
    
    app_id = os.getenv('EBAY_APP_ID')
    if not app_id:
        print("❌ EBAY_APP_ID not found")
        return False
    
    print("Testing advanced Finding API call...")
    
    try:
        api = Finding(appid=app_id, config_file=None)
        
        # Advanced search with filters (similar to your original code)
        api.execute('findItemsAdvanced', {
            'keywords': 'Acura AC Compressor',
            'categoryId': '33654',
            'paginationInput': {
                'entriesPerPage': '5'
            },
            'itemFilter': [
                {
                    'name': 'MinPrice',
                    'value': '50.0'
                },
                {
                    'name': 'Condition',
                    'value': ['Used', 'New']
                },
                {
                    'name': 'ListingType',
                    'value': 'FixedPrice'
                }
            ],
            'sortOrder': 'PricePlusShippingLowest'
        })
        
        response = api.response.dict()
        
        if 'ack' in response and response['ack'] == 'Success':
            print("✅ Advanced eBay SDK call successful!")
            
            search_result = response.get('searchResult', {})
            count = search_result.get('_count', '0')
            print(f"Acura AC Compressors found: {count}")
            
            # Show sample items
            items = search_result.get('item', [])
            if items:
                if isinstance(items, list):
                    for i, item in enumerate(items[:3], 1):
                        title = item.get('title', 'No title')
                        price_info = item.get('sellingStatus', {}).get('currentPrice', {})
                        price = price_info.get('value', 'N/A')
                        print(f"   {i}. {title[:50]}... - ${price}")
                else:
                    # Single item
                    title = items.get('title', 'No title')
                    price_info = items.get('sellingStatus', {}).get('currentPrice', {})
                    price = price_info.get('value', 'N/A')
                    print(f"   1. {title[:50]}... - ${price}")
            
            return True
        
        else:
            print(f"❌ Advanced call failed: {response}")
            return False
            
    except Exception as e:
        print(f"❌ Advanced SDK call failed: {e}")
        return False

def main():
    """Run all SDK tests"""
    print("eBay SDK Test Suite")
    print("=" * 40)
    
    # Test 1: Install/check SDK
    if not test_ebaysdk_installation():
        print("\n❌ Cannot proceed without eBay SDK")
        return
    
    # Test 2: Simple call
    print("\n" + "-" * 40)
    simple_works = test_ebay_finding_sdk()
    
    if simple_works:
        # Test 3: Advanced call
        print("\n" + "-" * 40)
        test_advanced_finding_sdk()
    
    print("\n" + "=" * 40)
    print("SDK Test Complete!")
    
    if simple_works:
        print("✅ Your eBay credentials work with the official SDK!")
        print("Consider updating your extractor to use ebaysdk-python")
    else:
        print("❌ eBay API access issue - check your App ID and permissions")

if __name__ == "__main__":
    main()
