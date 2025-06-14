#!/usr/bin/env python
"""
Simple test to verify environment variable loading
"""

import os
import sys
from pathlib import Path

def test_env_loading():
    print("Testing Environment Variable Loading")
    print("=" * 50)
    
    # Get paths
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent
    env_path = project_root / '.env'
    
    print(f"Current file: {current_file}")
    print(f"Project root: {project_root}")
    print(f"Expected .env path: {env_path}")
    print(f".env file exists: {env_path.exists()}")
    
    if not env_path.exists():
        print(f"❌ .env file not found at {env_path}")
        return False
    
    # Load environment variables
    print(f"\nLoading .env file from {env_path}...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv(env_path)
        print("✅ Loaded using python-dotenv")
        method = "python-dotenv"
    except ImportError:
        print("python-dotenv not available, using manual parsing...")
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        print("✅ Loaded manually")
        method = "manual"
    
    # Test specific environment variables
    print(f"\nTesting environment variables (loaded via {method}):")
    print("-" * 50)
    
    test_vars = ['EBAY_APP_ID', 'EBAY_DEV_ID', 'EBAY_CERT_ID', 'DATABASE_URL', 'DEBUG']
    
    for var in test_vars:
        value = os.getenv(var)
        if value:
            # Show first few characters for security
            display_value = value[:15] + "..." if len(value) > 15 else value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: Not found")
    
    # Specifically test eBay App ID
    ebay_app_id = os.getenv('EBAY_APP_ID')
    if ebay_app_id:
        print(f"\n🎉 Success! EBAY_APP_ID found: {ebay_app_id[:10]}...")
        return True
    else:
        print(f"\n❌ EBAY_APP_ID not found in environment variables")
        return False

if __name__ == "__main__":
    success = test_env_loading()
    print("\n" + "=" * 50)
    if success:
        print("Environment variable loading works! 🎉")
        print("You can now run the eBay extractor.")
    else:
        print("Environment variable loading failed ❌")
