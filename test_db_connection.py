#!/usr/bin/env python
"""Test database connection independently"""

import os
import sys
from pathlib import Path

# Add the parts_interchange directory to Python path
project_root = Path(__file__).resolve().parent
parts_interchange_dir = project_root / 'parts_interchange'
sys.path.insert(0, str(parts_interchange_dir))

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parts_interchange.settings')

try:
    from decouple import config
    
    # Test 1: Check what DATABASE_URL is being loaded
    print("=== DATABASE CONNECTION TEST ===")
    db_url = config('DATABASE_URL', default='NOT SET')
    print(f"DATABASE_URL from .env: {db_url}")
    
    # Test 2: Parse the URL manually
    if db_url and db_url != 'NOT SET':
        # Parse URL parts
        if '@' in db_url:
            credentials_part, host_db_part = db_url.split('@', 1)
            if '/' in host_db_part:
                host_part, db_name = host_db_part.rsplit('/', 1)
                print(f"Host: {host_part}")
                print(f"Database: {db_name}")
            else:
                print(f"Host+DB: {host_db_part}")
        
        # Test 3: Try direct psycopg connection
        print("\n--- Testing psycopg connection ---")
        try:
            import psycopg
            conn = psycopg.connect(db_url)
            print("✅ psycopg connection successful!")
            conn.close()
        except Exception as e:
            print(f"❌ psycopg connection failed: {e}")
    
    # Test 4: Try Django database connection
    print("\n--- Testing Django database connection ---")
    try:
        import django
        django.setup()
        
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print("✅ Django database connection successful!")
        print(f"Result: {result}")
    except Exception as e:
        print(f"❌ Django database connection failed: {e}")
        
        # Show Django's database configuration
        try:
            from django.conf import settings
            db_config = settings.DATABASES['default']
            print(f"\nDjango database config:")
            for key, value in db_config.items():
                if 'PASSWORD' in key.upper():
                    print(f"  {key}: [HIDDEN]")
                else:
                    print(f"  {key}: {value}")
        except Exception as config_error:
            print(f"Could not get Django config: {config_error}")

except Exception as e:
    print(f"Test script error: {e}")
    import traceback
    traceback.print_exc()
