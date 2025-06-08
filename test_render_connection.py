import os
import psycopg
from decouple import config
from django.db import connection
from django.core.exceptions import ImproperlyConfigured

def test_render_connection():
    """Test connection to Render PostgreSQL with external hostname"""
    
    print("=== RENDER DATABASE CONNECTION TEST ===")
    
    # Load from .env
    database_url = config('DATABASE_URL', default=None)
    
    if not database_url:
        print("❌ No DATABASE_URL found in .env file")
        return
    
    # Mask password for display
    display_url = database_url.replace(database_url.split('@')[0].split(':')[-1], '[PASSWORD]')
    print(f"Testing URL: {display_url}")
    
    # Test 1: Direct psycopg connection
    print("\n--- Testing direct psycopg connection ---")
    try:
        conn = psycopg.connect(database_url)
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            version = cur.fetchone()[0]
            print(f"✅ psycopg connection successful!")
            print(f"PostgreSQL version: {version[:50]}...")
        conn.close()
        
    except Exception as e:
        print(f"❌ psycopg connection failed: {e}")
        return
    
    # Test 2: Django connection
    print("\n--- Testing Django database connection ---")
    try:
        # Import Django settings
        import django
        from django.conf import settings
        
        # Configure Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parts_interchange.settings')
        django.setup()
        
        # Test Django connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f"✅ Django connection successful!")
            
        # Check if migrations table exists
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'django_migrations'
                );
            """)
            has_migrations = cursor.fetchone()[0]
            
            if has_migrations:
                cursor.execute("SELECT COUNT(*) FROM django_migrations;")
                migration_count = cursor.fetchone()[0]
                print(f"✅ Database has {migration_count} migrations applied")
            else:
                print("⚠️  Database exists but no migrations found")
                print("   Run: python manage.py migrate")
                
    except Exception as e:
        print(f"❌ Django connection failed: {e}")
        return
    
    print("\n🎉 All tests passed! Your Render database is working correctly.")
    print("\n📋 Next steps:")
    print("1. python manage.py migrate (if needed)")
    print("2. python manage.py runserver")
    print("3. Visit http://localhost:8000/")

if __name__ == "__main__":
    test_render_connection()
