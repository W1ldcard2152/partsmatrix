#!/usr/bin/env python
"""Test the improved Acura parts import"""

import os
import sys
from pathlib import Path

# Setup Django
project_root = Path(__file__).resolve().parent
parts_interchange_dir = project_root / 'parts_interchange'
sys.path.insert(0, str(parts_interchange_dir))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parts_interchange.settings')

import django
django.setup()

# Now run the import command
from django.core.management import call_command

def test_acura_import():
    print("🧪 Testing Acura Parts Import with Dry Run")
    print("=" * 50)
    
    # Test with dry run first
    try:
        call_command(
            'import_acura_parts', 
            'acura_parts_data.txt',
            '--dry-run'
        )
        print("\n✅ Dry run completed successfully!")
        
        # Ask if user wants to run actual import
        response = input("\nRun actual import? (y/n): ")
        if response.lower() == 'y':
            print("\n🚀 Running actual import...")
            call_command(
                'import_acura_parts', 
                'acura_parts_data.txt'
            )
            print("\n🎉 Import completed!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_acura_import()
