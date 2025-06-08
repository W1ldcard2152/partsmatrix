#!/usr/bin/env python
"""Test script to check Django setup and run migrations"""
import os
import sys
from pathlib import Path

def main():
    """Run Django check and migrations"""
    # Add the parts_interchange directory to Python path
    project_root = Path(__file__).resolve().parent
    parts_interchange_dir = project_root / 'parts_interchange'
    sys.path.insert(0, str(parts_interchange_dir))
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parts_interchange.settings')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Run system check
    print("Running Django system check...")
    execute_from_command_line(['manage.py', 'check'])
    
    # Run migrations
    print("Running migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    print("Setup complete! You can now run: python manage.py runserver")

if __name__ == '__main__':
    main()
