"""
Test eBay API with Sandbox Environment
This will help determine if it's a production-specific issue
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

def test_sandbox_vs_production():
    """Test both sandbox and production to isolate the issue"""
    
    try:
        from ebaysdk.finding import Connection as Finding
    except ImportError:
        print("❌ ebaysdk not available")
        return
    
    app_id = os.getenv('EBAY_APP_ID')
    if not app_id:
        print("❌ EBAY_APP_ID not found")
        return
    
    print(f"Testing with App ID: {app_id}")
    print("=" * 50)
    
    # Test 1: Try Sandbox (even with production App ID)
    print("Test 1: Sandbox Environment")
    print("-" * 30)
    
    try:
        # Force sandbox environment
        api_sandbox = Finding(
            appid=app_id, 
            config_file=None,
            domain='svcs.sandbox.ebay.com'  # Sandbox domain
        )
        
        api_sandbox.execute('findItemsByKeywords', {
            'keywords': 'test',
            'paginationInput': {'entriesPerPage': '1'}
        })
        
        response = api_sandbox.response.dict()
        
        if response.get('ack') == 'Success':
            print("✅ Sandbox works! Issue is production-specific")
        else:
            print(f"❌ Sandbox failed: {response}")
            
    except Exception as e:
        print(f"❌ Sandbox error: {e}")
        
        # Check if it's the same rate limit error
        if "exceeded the number of times" in str(e):
            print("   → Same 'rate limit' error in sandbox = configuration issue")
        elif "Authentication" in str(e) or "Invalid" in str(e):
            print("   → Authentication issue - App ID might be production-only")
    
    print("\n" + "-" * 50)
    
    # Test 2: Try Production with minimal call
    print("Test 2: Production Environment (Minimal)")
    print("-" * 30)
    
    try:
        # Production domain (explicit)
        api_prod = Finding(
            appid=app_id,
            config_file=None,
            domain='svcs.ebay.com'  # Production domain
        )
        
        # Most minimal possible call
        api_prod.execute('findItemsByKeywords', {
            'keywords': 'a',  # Single letter
            'paginationInput': {'entriesPerPage': '1'}
        })
        
        response = api_prod.response.dict()
        
        if response.get('ack') == 'Success':
            print("✅ Production works! Previous error was temporary")
        else:
            print(f"❌ Production failed: {response}")
            
    except Exception as e:
        print(f"❌ Production error: {e}")
        
        # Analyze the error
        if "10001" in str(e):
            print("\n🔍 Error 10001 Analysis:")
            print("   This often means:")
            print("   1. App not fully activated for production Finding API")
            print("   2. Missing compliance requirements")
            print("   3. Need to contact eBay Developer Support")
            print("   4. App in restricted/pending state")

def check_app_id_format():
    """Analyze the App ID format for clues"""
    
    app_id = os.getenv('EBAY_APP_ID')
    if not app_id:
        return
    
    print(f"\n🔍 App ID Analysis:")
    print(f"Full App ID: {app_id}")
    
    # Parse the components
    parts = app_id.split('-')
    if len(parts) >= 4:
        app_name = parts[0]
        app_purpose = parts[1] 
        environment = parts[2]
        app_hash = parts[3]
        
        print(f"   App Name: {app_name}")
        print(f"   Purpose: {app_purpose}")
        print(f"   Environment: {environment}")
        print(f"   Hash: {app_hash}...")
        
        if environment == "PRD":
            print("   ✅ Production App ID confirmed")
        elif environment == "SBX":
            print("   ℹ️  Sandbox App ID detected")
        else:
            print(f"   ⚠️  Unknown environment: {environment}")
    
    # Check if this looks like a legitimate production App ID
    if "PRD" in app_id and len(app_id) > 30:
        print("   ✅ App ID format looks correct for production")
    else:
        print("   ⚠️  App ID format might be incomplete")

def main():
    """Run comprehensive sandbox vs production test"""
    print("eBay Environment Diagnostic")
    print("=" * 50)
    
    check_app_id_format()
    
    print("\n" + "=" * 50)
    test_sandbox_vs_production()
    
    print("\n" + "=" * 50)
    print("🎯 Next Steps:")
    print("1. Check eBay Developer Portal for app status")
    print("2. Look for any pending compliance requirements")
    print("3. Verify Finding API is enabled for production")
    print("4. Consider contacting eBay Developer Support if issue persists")

if __name__ == "__main__":
    main()
