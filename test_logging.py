#!/usr/bin/env python3
"""
Test script to verify logging configuration is working properly.
Run this to see what output you get with different LOG_LEVEL settings.
"""

import os
import sys
from pathlib import Path

# Add the parts_interchange directory to Python path
project_root = Path(__file__).resolve().parent
parts_interchange_dir = project_root / 'parts_interchange'
sys.path.insert(0, str(parts_interchange_dir))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parts_interchange.settings')

import django
django.setup()

import logging

# Get loggers
logger = logging.getLogger(__name__)
django_logger = logging.getLogger('django')
db_logger = logging.getLogger('django.db.backends')
apps_logger = logging.getLogger('apps')

def test_logging_levels():
    """Test all logging levels to see what's displayed"""
    print("=== Testing Logging Levels ===")
    print(f"Current LOG_LEVEL from settings: {os.environ.get('LOG_LEVEL', 'Not Set')}")
    
    # Test all levels
    levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    
    for level in levels:
        print(f"\n--- Testing {level} level ---")
        
        # Test main logger
        getattr(logger, level.lower())(f"Main logger {level} message")
        
        # Test Django logger
        getattr(django_logger, level.lower())(f"Django logger {level} message")
        
        # Test apps logger
        getattr(apps_logger, level.lower())(f"Apps logger {level} message")
        
        if level == 'DEBUG':
            # Test database logger
            getattr(db_logger, level.lower())(f"Database logger {level} message")

def show_current_config():
    """Show current logging configuration"""
    from django.conf import settings
    
    print("\n=== Current Logging Configuration ===")
    print(f"LOG_LEVEL: {getattr(settings, 'LOG_LEVEL', 'Not Set')}")
    print(f"DEBUG: {settings.DEBUG}")
    
    # Show effective levels for key loggers
    loggers_to_check = [
        'django',
        'django.db.backends', 
        'django.request',
        'apps',
        __name__
    ]
    
    print("\nEffective Logger Levels:")
    for logger_name in loggers_to_check:
        log = logging.getLogger(logger_name)
        print(f"  {logger_name}: {logging.getLevelName(log.level)}")

if __name__ == '__main__':
    show_current_config()
    test_logging_levels()
    
    print("\n=== Instructions ===")
    print("1. Current LOG_LEVEL is set to WARNING in your .env file")
    print("2. You should only see WARNING, ERROR, and CRITICAL messages above")
    print("3. To see more output, change LOG_LEVEL in .env to INFO or DEBUG")
    print("4. To see less output, change LOG_LEVEL to ERROR or CRITICAL")
    print("\nAvailable LOG_LEVEL values: DEBUG, INFO, WARNING, ERROR, CRITICAL")
