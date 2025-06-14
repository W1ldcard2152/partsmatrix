#!/usr/bin/env python
"""
Comprehensive test for eBay extractor Django setup
Tests both Django imports and eBay API credentials
"""

import os
import sys
import subprocess
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

def check_virtual_environment():
    """Check if we're in the correct virtual environment"""
    print("Checking virtual environment...")
    print("-" * 50)
    
    # Check if we're in a virtual environment
    venv = os.environ.get('VIRTUAL_ENV')
    if venv:
        print(f"✅ Virtual environment active: {venv}")
    else:
        print("⚠️  No virtual environment detected")
        print("You may need to activate the virtual environment:")
        print("   cd 'C:\\Users\\Wildc\\Documents\\Programming\\Parts Matrix'")
        print("   venv\\Scripts\\activate")
    
    # Check Python version
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    return venv is not None

def test_django_setup():
    """Test Django setup and imports"""
    print("\nTesting Django setup...")
    print("-" * 50)
    
    try:
        # Add the Django project to the path
        from pathlib import Path
        
        # Get the project root (Parts Matrix directory)
        project_root = Path(__file__).resolve().parent.parent
        parts_interchange_dir = project_root / 'parts_interchange'
        apps_dir = parts_interchange_dir / 'apps'
        
        print(f"Project root: {project_root}")
        print(f"Parts interchange dir: {parts_interchange_dir}")
        print(f"Apps dir: {apps_dir}")
        print(f"Parts interchange exists: {parts_interchange_dir.exists()}")
        print(f"Apps dir exists: {apps_dir.exists()}")
        
        if not parts_interchange_dir.exists():
            print("❌ Parts interchange directory not found!")
            return False
        
        if not apps_dir.exists():
            print("❌ Apps directory not found!")
            return False
        
        # Add paths in the same order as manage.py
        sys.path.insert(0, str(apps_dir))  # Add apps directory to path
        sys.path.insert(0, str(parts_interchange_dir))  # Add parts_interchange directory to path
        
        # Configure Django settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parts_interchange.settings')
        print(f"Django settings module: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
        
        # Test Django setup
        print("\nTesting Django setup...")
        import django
        django.setup()
        print("✅ Django setup successful!")
        
        # Test model imports
        print("\nTesting Django model imports...")
        from apps.parts.models import Part, Manufacturer, PartCategory
        print("✅ Parts models imported")
        
        from apps.vehicles.models import Vehicle, Make, Model, Engine, Trim
        print("✅ Vehicle models imported")
        
        from apps.fitments.models import Fitment
        print("✅ Fitment models imported")
        
        print("✅ All Django model imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Django setup error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ebay_credentials():
    """Test eBay API credentials"""
    print("\nTesting eBay API credentials...")
    print("-" * 50)
    
    ebay_app_id = os.getenv('EBAY_APP_ID')
    if ebay_app_id:
        print(f"✅ EBAY_APP_ID found: {ebay_app_id[:10]}...")
        return True
    else:
        print("❌ EBAY_APP_ID environment variable not set")
        print("Set it with: set EBAY_APP_ID=your-app-id-here")
        print("Or add it to your .env file")
        return False

def test_ebay_extractor_import():
    """Test importing the eBay extractor itself"""
    print("\nTesting eBay extractor import...")
    print("-" * 50)
    
    try:
        from ebay_parts_extractor import EbayPartsExtractor
        print("✅ EbayPartsExtractor imported successfully!")
        
        # Try to initialize it (this will test if Django setup worked)
        app_id = os.getenv('EBAY_APP_ID', 'test')
        extractor = EbayPartsExtractor(app_id)
        print("✅ EbayPartsExtractor initialized successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ EbayPartsExtractor import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("eBay Extractor - Comprehensive Test Suite")
    print("=" * 60)
    
    all_passed = True
    
    # Test 1: Virtual environment
    venv_ok = check_virtual_environment()
    if not venv_ok:
        print("\n⚠️  Consider activating the virtual environment for best results")
    
    # Test 2: Django setup
    django_ok = test_django_setup()
    if not django_ok:
        all_passed = False
        print("\n❌ Django setup failed - cannot proceed with eBay extractor")
        return
    
    # Test 3: eBay credentials
    creds_ok = test_ebay_credentials()
    if not creds_ok:
        all_passed = False
        print("\n⚠️  eBay credentials not set - API calls will fail")
    
    # Test 4: eBay extractor import
    extractor_ok = test_ebay_extractor_import()
    if not extractor_ok:
        all_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY:")
    print("=" * 60)
    
    if django_ok and extractor_ok:
        print("🎉 eBay Extractor is ready to use!")
        print("\nYou can now run:")
        print("   python test_extractor.py")
        print("   python ebay_parts_extractor.py")
    else:
        print("❌ eBay Extractor is not ready")
        print("\nIssues to fix:")
        if not django_ok:
            print("   - Django setup failed")
        if not extractor_ok:
            print("   - eBay extractor import failed")
        if not creds_ok:
            print("   - eBay API credentials not set")

if __name__ == "__main__":
    main()
