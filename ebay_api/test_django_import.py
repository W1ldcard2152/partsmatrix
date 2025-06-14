#!/usr/bin/env python
"""
Quick test to verify Django imports work correctly
"""

import os
import sys

def test_django_import():
    """Test if Django can be imported with the correct path setup"""
    try:
        print("Testing Django import for eBay extractor...")
        print("-" * 50)
        
        # Add the Django project to the path so we can import Django models
        # Follow the same pattern as manage.py
        from pathlib import Path
        
        # Get the project root (Parts Matrix directory)
        project_root = Path(__file__).resolve().parent.parent
        parts_interchange_dir = project_root / 'parts_interchange'
        apps_dir = parts_interchange_dir / 'apps'
        
        # Add paths in the same order as manage.py
        sys.path.insert(0, str(apps_dir))  # Add apps directory to path
        sys.path.insert(0, str(parts_interchange_dir))  # Add parts_interchange directory to path
        
        print(f"Project root: {project_root}")
        print(f"Parts interchange dir: {parts_interchange_dir}")
        print(f"Apps dir: {apps_dir}")
        print(f"Parts interchange exists: {parts_interchange_dir.exists()}")
        print(f"Apps dir exists: {apps_dir.exists()}")
        
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
        from apps.vehicles.models import Vehicle, Make, Model, Engine, Trim
        from apps.fitments.models import Fitment
        print("✅ All model imports successful!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_django_import()
    print("\n" + "=" * 50)
    if success:
        print("🎉 Django import test PASSED!")
        print("The eBay extractor should now work correctly.")
    else:
        print("❌ Django import test FAILED!")
        print("The eBay extractor needs further debugging.")
