import os
import psycopg
from pathlib import Path

def test_render_connection_debug():
    """Test connection with detailed debugging"""
    
    print("=== RENDER DATABASE CONNECTION DEBUG TEST ===")
    
    # Check current working directory
    current_dir = os.getcwd()
    print(f"Current directory: {current_dir}")
    
    # Check for .env files
    env_file = Path(".env")
    if env_file.exists():
        print(f"✅ Found .env file at: {env_file.absolute()}")
        
        # Read the actual content
        with open(".env", "r") as f:
            lines = f.readlines()
            
        print("\n📄 .env file contents (DATABASE_URL line only):")
        for i, line in enumerate(lines, 1):
            if line.strip().startswith("DATABASE_URL=") and not line.strip().startswith("#"):
                print(f"Line {i}: {line.strip()}")
                database_url = line.strip().split("=", 1)[1]
                break
        else:
            print("❌ No uncommented DATABASE_URL found in .env")
            return
    else:
        print(f"❌ No .env file found at: {env_file.absolute()}")
        return
    
    # Also try using python-decouple
    try:
        from decouple import config
        decouple_url = config('DATABASE_URL', default='NOT_FOUND')
        print(f"\n🔧 python-decouple reads: {decouple_url.replace('673nkZBU4Kmm1jYqAs7UbpcmzHtPrXAC', '[PASSWORD]') if decouple_url != 'NOT_FOUND' else 'NOT_FOUND'}")
    except ImportError:
        print("\n❌ python-decouple not available")
        decouple_url = None
    
    # Use the URL we found directly from file
    print(f"\n🔍 Testing with URL from file: {database_url.replace('673nkZBU4Kmm1jYqAs7UbpcmzHtPrXAC', '[PASSWORD]')}")
    
    # Extract components for verification
    try:
        # Parse URL components
        if database_url.startswith('postgresql://'):
            url_parts = database_url.replace('postgresql://', '').split('/')
            host_part = url_parts[0].split('@')[1]
            db_name = url_parts[1] if len(url_parts) > 1 else 'NOT_FOUND'
            
            print(f"📊 URL Components:")
            print(f"   Host: {host_part}")
            print(f"   Database: {db_name}")
    except Exception as e:
        print(f"❌ Error parsing URL: {e}")
        return
    
    # Test connection
    print(f"\n--- Testing direct psycopg connection ---")
    try:
        conn = psycopg.connect(database_url)
        with conn.cursor() as cur:
            cur.execute("SELECT current_database(), version();")
            db_name, version = cur.fetchone()
            print(f"✅ Connection successful!")
            print(f"Connected to database: {db_name}")
            print(f"PostgreSQL version: {version[:50]}...")
        conn.close()
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        
        # Additional debugging
        print(f"\n🔍 Debugging info:")
        print(f"   - Check if hostname resolves: ping {host_part}")
        print(f"   - Verify Render database is running in dashboard")
        print(f"   - Confirm external connections are allowed")
        
        return
    
    print(f"\n🎉 Connection test successful!")

if __name__ == "__main__":
    test_render_connection_debug()
