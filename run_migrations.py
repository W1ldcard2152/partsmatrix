#!/usr/bin/env python
"""
Simple script to run Django migrations and basic setup
"""
import os
import sys
from pathlib import Path

def main():
    print("🔧 Running Django Migrations and Setup")
    print("=" * 40)
    
    # Setup path
    project_root = Path(__file__).resolve().parent
    parts_interchange_dir = project_root / 'parts_interchange'
    sys.path.insert(0, str(parts_interchange_dir))
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parts_interchange.settings')
    
    try:
        import django
        django.setup()
        print("✅ Django setup successful")
        
        from django.core.management import execute_from_command_line
        
        print("\n1. Creating migrations...")
        try:
            execute_from_command_line(['manage.py', 'makemigrations'])
            print("✅ Migrations created successfully")
        except SystemExit as e:
            if e.code == 0:
                print("✅ No new migrations needed")
            else:
                print(f"⚠️  Makemigrations exited with code: {e.code}")
        
        print("\n2. Running migrations...")
        try:
            execute_from_command_line(['manage.py', 'migrate'])
            print("✅ Migrations applied successfully")
        except SystemExit as e:
            if e.code == 0:
                print("✅ Migrations completed")
            else:
                print(f"❌ Migration failed with code: {e.code}")
                return False
        
        print("\n3. Testing database connection...")
        from django.db import connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            print("✅ Database connection successful")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
        
        print("\n4. Running system check...")
        try:
            execute_from_command_line(['manage.py', 'check'])
            print("✅ System check passed")
            return True
        except SystemExit as e:
            if e.code == 0:
                print("✅ System check passed")
                return True
            else:
                print(f"❌ System check failed with code: {e.code}")
                print("Try running: python detailed_diagnostics.py for more info")
                return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    if success:
        print("\n🎉 Setup completed successfully!")
        print("You can now run: python manage.py runserver")
    else:
        print("\n❌ Setup failed. Check errors above.")
        sys.exit(1)
