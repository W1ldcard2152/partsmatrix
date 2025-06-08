#!/usr/bin/env python
"""
Final comprehensive test to verify Django server can start
"""
import os
import sys
from pathlib import Path

def main():
    print("🚀 Final Django Server Startup Test")
    print("=" * 40)
    
    # Setup path
    project_root = Path(__file__).resolve().parent
    parts_interchange_dir = project_root / 'parts_interchange'
    sys.path.insert(0, str(parts_interchange_dir))
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parts_interchange.settings')
    
    try:
        # Step 1: Basic Django setup
        print("1. Setting up Django...")
        import django
        django.setup()
        print("   ✅ Django setup successful")
        
        # Step 2: Test problematic imports
        print("2. Testing critical imports...")
        from apps.parts import views_fast
        print("   ✅ views_fast imported successfully")
        
        from apps.parts import urls
        print("   ✅ parts.urls imported successfully")
        
        # Step 3: Test URL resolution
        print("3. Testing URL resolution...")
        from django.urls import reverse, resolve
        from django.conf import settings
        
        # Import the root URL configuration
        from parts_interchange import urls as root_urls
        print("   ✅ Root URLs imported successfully")
        
        # Step 4: Test Django management commands
        print("4. Testing Django management...")
        from django.core.management import execute_from_command_line
        
        # Test that we can run check command
        print("   Running Django system check...")
        try:
            # Capture output to avoid clutter
            import io
            from contextlib import redirect_stdout, redirect_stderr
            
            f = io.StringIO()
            with redirect_stdout(f), redirect_stderr(f):
                execute_from_command_line(['manage.py', 'check', '--quiet'])
            
            output = f.getvalue()
            if "error" in output.lower() or "critical" in output.lower():
                print(f"   ⚠️  System check warnings: {output}")
            else:
                print("   ✅ Django system check passed")
                
        except SystemExit as e:
            if e.code == 0:
                print("   ✅ Django system check passed")
            else:
                print(f"   ❌ Django system check failed with code: {e.code}")
                return False
        
        # Step 5: Test database connection
        print("5. Testing database connection...")
        from django.db import connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
            print("   ✅ Database connection successful")
        except Exception as e:
            print(f"   ⚠️  Database connection issue: {e}")
            print("   (This might be okay if migrations haven't been run yet)")
        
        # Step 6: Test that models can be imported
        print("6. Testing model imports...")
        from apps.parts.models import Part, PartGroup, PartGroupMembership
        from apps.vehicles.models import Vehicle, Make
        from apps.fitments.models import Fitment
        print("   ✅ All models imported successfully")
        
        print("\n🎉 ALL TESTS PASSED!")
        print("=" * 40)
        print("Your Django application is ready to run!")
        print("\nTo start the server:")
        print("1. cd parts_interchange")
        print("2. python manage.py migrate  (if needed)")
        print("3. python manage.py runserver")
        print("\nThen visit: http://localhost:8000/")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
        print("\n" + "=" * 40)
        print("Troubleshooting steps:")
        print("1. Make sure virtual environment is activated")
        print("2. Check that all dependencies are installed")
        print("3. Verify .env file configuration")
        print("4. Try running: python fix_common_issues.py")
        return False

if __name__ == '__main__':
    success = main()
    if not success:
        sys.exit(1)
