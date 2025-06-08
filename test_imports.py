#!/usr/bin/env python
"""Simple test to check if Django can import properly"""
import os
import sys
from pathlib import Path

# Add the parts_interchange directory to Python path
project_root = Path(__file__).resolve().parent
parts_interchange_dir = project_root / 'parts_interchange'
sys.path.insert(0, str(parts_interchange_dir))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parts_interchange.settings')

try:
    print("Testing Django setup...")
    import django
    django.setup()
    
    print("✓ Django setup successful")
    
    # Test importing the problematic views_fast module
    print("Testing views_fast import...")
    from apps.parts import views_fast
    print("✓ views_fast imported successfully")
    
    # Test URL configuration
    print("Testing URL imports...")
    from apps.parts import urls
    print("✓ URLs imported successfully")
    
    # Test models
    print("Testing models...")
    from apps.parts.models import Part, PartGroup, PartGroupMembership
    print("✓ Models imported successfully")
    
    print("\n🎉 All imports successful! The syntax error is fixed.")
    print("You can now run: python manage.py runserver")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

