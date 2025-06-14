"""
eBay API Setup and Validation Script
Checks dependencies, validates configuration, and guides setup
"""

import os
import sys
import subprocess
import importlib
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    print("Checking Python version...")
    version = sys.version_info
    
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False

def check_required_packages():
    """Check if required packages are installed"""
    print("\nChecking required packages...")
    
    required_packages = {
        'requests': 'HTTP requests library',
        'django': 'Django web framework',
        'decouple': 'Environment variable management'
    }
    
    missing_packages = []
    
    for package, description in required_packages.items():
        try:
            importlib.import_module(package)
            print(f"✅ {package} - {description}")
        except ImportError:
            print(f"❌ {package} - {description} (NOT INSTALLED)")
            missing_packages.append(package)
    
    return missing_packages

def check_django_setup():
    """Check if Django is properly configured"""
    print("\nChecking Django configuration...")
    
    try:
        # Add project root to path
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.append(project_root)
        
        # Try to configure Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parts_interchange.settings')
        import django
        django.setup()
        
        # Try to import models
        from apps.parts.models import Part, Manufacturer, PartCategory
        from apps.vehicles.models import Vehicle
        from apps.fitments.models import Fitment
        
        print("✅ Django configuration - Working")
        print("✅ Django models - Imported successfully")
        return True
        
    except Exception as e:
        print(f"❌ Django configuration - Error: {e}")
        return False

def check_ebay_credentials():
    """Check if eBay API credentials are configured"""
    print("\nChecking eBay API credentials...")
    
    # Check environment variable
    app_id = os.getenv('EBAY_APP_ID')
    if app_id:
        print(f"✅ EBAY_APP_ID environment variable found: {app_id[:10]}...")
        return True
    
    # Check .env file
    env_file = Path('.env')
    if env_file.exists():
        try:
            with open(env_file, 'r') as f:
                content = f.read()
                if 'EBAY_APP_ID=' in content and 'your-ebay-app-id-here' not in content:
                    print("✅ EBAY_APP_ID found in .env file")
                    return True
                else:
                    print("❌ EBAY_APP_ID not properly configured in .env file")
        except Exception as e:
            print(f"❌ Error reading .env file: {e}")
    else:
        print("❌ No .env file found")
    
    print("❌ EBAY_APP_ID not configured")
    return False

def check_file_structure():
    """Check if all required files exist"""
    print("\nChecking file structure...")
    
    required_files = [
        'ebay_parts_extractor.py',
        'test_extractor.py',
        'data_viewer.py',
        'django_importer.py',
        'requirements.txt',
        '.env.example'
    ]
    
    missing_files = []
    
    for filename in required_files:
        if os.path.exists(filename):
            print(f"✅ {filename}")
        else:
            print(f"❌ {filename} (MISSING)")
            missing_files.append(filename)
    
    return missing_files

def install_missing_packages(packages):
    """Install missing packages"""
    if not packages:
        return True
    
    print(f"\nAttempting to install missing packages: {', '.join(packages)}")
    
    try:
        for package in packages:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        
        print("✅ All packages installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False

def create_env_file():
    """Help user create .env file"""
    print("\neBay API Credentials Setup")
    print("=" * 40)
    
    print("To use the eBay API, you need an App ID from eBay Developers.")
    print("\nSteps to get your eBay App ID:")
    print("1. Go to https://developer.ebay.com/")
    print("2. Sign up for a free developer account")
    print("3. Create a new application")
    print("4. Copy your App ID from the 'Application Keys' section")
    
    print(f"\nEnter your eBay App ID (or press Enter to skip):")
    app_id = input("> ").strip()
    
    if app_id and app_id != 'your-ebay-app-id-here':
        try:
            with open('.env', 'w') as f:
                f.write(f"# eBay API Configuration\n")
                f.write(f"EBAY_APP_ID={app_id}\n")
            
            print("✅ .env file created successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error creating .env file: {e}")
            return False
    else:
        print("⚠️  Skipped .env file creation")
        print("You can create it manually later by copying .env.example")
        return False

def run_quick_test():
    """Run a quick test of the extractor"""
    print("\nRunning quick validation test...")
    
    try:
        from ebay_parts_extractor import EbayPartsExtractor
        
        # Test with dummy app ID if no real one available
        app_id = os.getenv('EBAY_APP_ID', 'test-app-id')
        extractor = EbayPartsExtractor(app_id)
        
        # Test pattern extraction
        test_title = "2005-2008 Acura TL AC Compressor - Denso (471-0101) OEM Quality"
        part_name = extractor.extract_part_name(test_title)
        part_number = extractor.extract_part_number(test_title)
        manufacturer = extractor.extract_manufacturer(test_title)
        
        print("✅ Extractor initialization successful")
        print(f"✅ Pattern extraction test: Found '{part_name}', '{part_number}', '{manufacturer}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Extractor test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("eBay Parts Extractor - Setup & Validation")
    print("=" * 50)
    
    # Track setup status
    issues = []
    
    # Check Python version
    if not check_python_version():
        issues.append("Python version")
    
    # Check required packages
    missing_packages = check_required_packages()
    if missing_packages:
        print(f"\n⚠️  Missing packages detected: {', '.join(missing_packages)}")
        install_choice = input("Install missing packages automatically? (y/n): ").lower()
        
        if install_choice in ['y', 'yes']:
            if not install_missing_packages(missing_packages):
                issues.append("Package installation")
        else:
            issues.append("Missing packages")
    
    # Check file structure
    missing_files = check_file_structure()
    if missing_files:
        issues.append("Missing files")
    
    # Check Django setup
    if not check_django_setup():
        issues.append("Django configuration")
    
    # Check eBay credentials
    if not check_ebay_credentials():
        print("\n⚠️  eBay API credentials not configured")
        setup_choice = input("Set up eBay API credentials now? (y/n): ").lower()
        
        if setup_choice in ['y', 'yes']:
            if not create_env_file():
                issues.append("eBay credentials")
        else:
            issues.append("eBay credentials")
    
    # Run quick test if everything looks good
    if not issues:
        run_quick_test()
    
    # Print final status
    print("\n" + "=" * 50)
    print("Setup Status Summary:")
    
    if not issues:
        print("✅ All checks passed! You're ready to use the eBay extractor.")
        print("\nNext steps:")
        print("1. Run: python test_extractor.py")
        print("2. Run: python ebay_parts_extractor.py")
        print("3. Analyze results: python data_viewer.py")
    else:
        print("❌ Issues found that need attention:")
        for issue in issues:
            print(f"  - {issue}")
        
        print("\nPlease resolve these issues before running the extractor.")
        
        if "eBay credentials" in issues:
            print("\nTo set up eBay credentials:")
            print("1. Get App ID from https://developer.ebay.com/")
            print("2. Create .env file with: EBAY_APP_ID=your-app-id-here")
        
        if "Missing packages" in issues:
            print(f"\nTo install missing packages:")
            print(f"pip install {' '.join(missing_packages)}")

if __name__ == "__main__":
    main()
