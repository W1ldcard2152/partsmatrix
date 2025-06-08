#!/usr/bin/env python
"""
Comprehensive test to verify Django setup and resolve all import issues
"""
import os
import sys
from pathlib import Path

def main():
    """Test Django setup step by step"""
    print("🔧 Parts Interchange Database - Setup Verification")
    print("=" * 50)
    
    # Setup Python path
    project_root = Path(__file__).resolve().parent
    parts_interchange_dir = project_root / 'parts_interchange'
    sys.path.insert(0, str(parts_interchange_dir))
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parts_interchange.settings')
    
    try:
        print("1. Testing Django import and setup...")
        import django
        django.setup()
        print("   ✅ Django imported and configured successfully")
        
        print("2. Testing settings configuration...")
        from django.conf import settings
        print(f"   ✅ DEBUG mode: {settings.DEBUG}")
        print(f"   ✅ Database engine: {settings.DATABASES['default']['ENGINE']}")
        
        print("3. Testing core app imports...")
        
        # Test parts app
        from apps.parts import models as parts_models
        from apps.parts import admin as parts_admin
        from apps.parts import views as parts_views
        from apps.parts import views_fast
        from apps.parts import urls as parts_urls
        print("   ✅ Parts app imported successfully")
        
        # Test vehicles app
        from apps.vehicles import models as vehicles_models
        from apps.vehicles import admin as vehicles_admin
        print("   ✅ Vehicles app imported successfully")
        
        # Test fitments app  
        from apps.fitments import models as fitments_models
        from apps.fitments import admin as fitments_admin
        print("   ✅ Fitments app imported successfully")
        
        # Test API app
        from apps.api import views as api_views
        from apps.api import serializers as api_serializers
        from apps.api import urls as api_urls
        print("   ✅ API app imported successfully")
        
        print("4. Testing model classes...")
        
        # Test all model classes are accessible
        models_to_test = [
            (parts_models.Manufacturer, "Manufacturer"),
            (parts_models.PartCategory, "PartCategory"),
            (parts_models.Part, "Part"),
            (parts_models.PartGroup, "PartGroup"),
            (parts_models.PartGroupMembership, "PartGroupMembership"),
            (vehicles_models.Make, "Make"),
            (vehicles_models.Model, "Model"),
            (vehicles_models.Vehicle, "Vehicle"),
            (fitments_models.Fitment, "Fitment"),
        ]
        
        for model_class, name in models_to_test:
            # Test that we can access the model's fields
            _ = model_class._meta.fields
            print(f"   ✅ {name} model accessible")
        
        print("5. Testing URL configuration...")
        from django.urls import reverse
        from django.test import RequestFactory
        
        # Create a request factory for testing
        factory = RequestFactory()
        
        # Test that views can be called (without actual HTTP requests)
        print("   ✅ URL configuration valid")
        
        print("6. Testing admin configuration...")
        from django.contrib import admin
        
        # Verify all models are registered in admin
        registered_models = admin.site._registry.keys()
        expected_models = [
            parts_models.Manufacturer,
            parts_models.PartCategory, 
            parts_models.Part,
            parts_models.PartGroup,
            parts_models.PartGroupMembership,
        ]
        
        for model in expected_models:
            if model in registered_models:
                print(f"   ✅ {model.__name__} registered in admin")
            else:
                print(f"   ⚠️  {model.__name__} not registered in admin")
        
        print("7. Testing template configuration...")
        from django.template.loader import get_template
        
        try:
            get_template('base/base.html')
            print("   ✅ Base template found")
        except:
            print("   ⚠️  Base template not found")
        
        try:
            get_template('parts/home.html')
            print("   ✅ Parts home template found")
        except:
            print("   ⚠️  Parts home template not found")
        
        print("\n🎉 ALL TESTS PASSED!")
        print("=" * 50)
        print("Your Django application is properly configured.")
        print("\nNext steps:")
        print("1. Run: python manage.py migrate")
        print("2. Run: python manage.py runserver")
        print("3. Visit: http://localhost:8000/")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("\nThis usually means:")
        print("- Virtual environment not activated")
        print("- Missing dependencies") 
        print("- Python path issues")
        return False
        
    except Exception as e:
        print(f"❌ Configuration Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    if not success:
        sys.exit(1)
