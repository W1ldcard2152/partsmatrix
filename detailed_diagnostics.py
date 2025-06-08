#!/usr/bin/env python
"""
Detailed Django diagnostic to identify system check failures
"""
import os
import sys
from pathlib import Path

def main():
    print("🔍 Django System Check Diagnostics")
    print("=" * 50)
    
    # Setup path
    project_root = Path(__file__).resolve().parent
    parts_interchange_dir = project_root / 'parts_interchange'
    sys.path.insert(0, str(parts_interchange_dir))
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parts_interchange.settings')
    
    try:
        import django
        django.setup()
        
        print("1. Running detailed Django system check...")
        from django.core.management import execute_from_command_line
        from django.core.checks import run_checks
        from django.core.checks.registry import registry
        
        # Run system checks with full output
        print("\nRunning system checks with full verbosity...")
        try:
            execute_from_command_line(['manage.py', 'check', '--verbosity=2'])
        except SystemExit as e:
            print(f"System check exited with code: {e.code}")
            
            # Get detailed error information
            print("\n" + "=" * 50)
            print("DETAILED ERROR ANALYSIS")
            print("=" * 50)
            
            # Run checks manually to get detailed output
            all_issues = run_checks()
            
            if all_issues:
                print(f"Found {len(all_issues)} issues:")
                for issue in all_issues:
                    print(f"\n{issue.level_name}: {issue.id}")
                    print(f"  Message: {issue.msg}")
                    if hasattr(issue, 'obj') and issue.obj:
                        print(f"  Object: {issue.obj}")
                    if hasattr(issue, 'hint') and issue.hint:
                        print(f"  Hint: {issue.hint}")
            else:
                print("No specific issues found in manual check.")
            
            # Check specific areas that commonly cause issues
            print("\n" + "-" * 30)
            print("CHECKING SPECIFIC AREAS:")
            print("-" * 30)
            
            # Check models
            print("Checking models...")
            try:
                from django.apps import apps
                for app_config in apps.get_app_configs():
                    try:
                        models = app_config.get_models()
                        print(f"  ✅ {app_config.name}: {len(models)} models")
                    except Exception as e:
                        print(f"  ❌ {app_config.name}: {e}")
            except Exception as e:
                print(f"  ❌ Error checking models: {e}")
            
            # Check URLs
            print("\nChecking URL configuration...")
            try:
                from django.urls import reverse
                from django.conf import settings
                print(f"  ✅ ROOT_URLCONF: {settings.ROOT_URLCONF}")
                
                # Try to import URL patterns
                from django.urls import include
                from parts_interchange.urls import urlpatterns
                print(f"  ✅ Root URL patterns: {len(urlpatterns)} patterns")
                
                # Check each app's URLs
                app_urls = [
                    ('parts', 'apps.parts.urls'),
                    ('api', 'apps.api.urls'),
                ]
                
                for app_name, url_module in app_urls:
                    try:
                        import importlib
                        module = importlib.import_module(url_module)
                        print(f"  ✅ {app_name} URLs: imported successfully")
                    except Exception as e:
                        print(f"  ❌ {app_name} URLs: {e}")
                        
            except Exception as e:
                print(f"  ❌ URL configuration error: {e}")
            
            # Check database
            print("\nChecking database configuration...")
            try:
                from django.conf import settings
                db_config = settings.DATABASES['default']
                print(f"  ✅ Database engine: {db_config['ENGINE']}")
                
                # Test connection
                from django.db import connection
                connection.ensure_connection()
                print("  ✅ Database connection successful")
                
            except Exception as e:
                print(f"  ❌ Database issue: {e}")
            
            # Check installed apps
            print("\nChecking installed apps...")
            try:
                from django.conf import settings
                for app in settings.INSTALLED_APPS:
                    try:
                        import importlib
                        importlib.import_module(app)
                        print(f"  ✅ {app}")
                    except Exception as e:
                        print(f"  ❌ {app}: {e}")
            except Exception as e:
                print(f"  ❌ Error checking apps: {e}")
            
            # Check migrations
            print("\nChecking migrations...")
            try:
                from django.core.management import execute_from_command_line
                import io
                from contextlib import redirect_stdout, redirect_stderr
                
                f = io.StringIO()
                with redirect_stdout(f), redirect_stderr(f):
                    try:
                        execute_from_command_line(['manage.py', 'showmigrations', '--verbosity=0'])
                        print("  ✅ Migration status check completed")
                    except SystemExit:
                        pass  # Expected for management commands
                        
                # Try to identify unapplied migrations
                try:
                    execute_from_command_line(['manage.py', 'showmigrations', '--plan'])
                except SystemExit:
                    pass
                    
            except Exception as e:
                print(f"  ❌ Migration check error: {e}")
            
        print("\n" + "=" * 50)
        print("RECOMMENDED ACTIONS:")
        print("=" * 50)
        print("1. Fix any specific errors shown above")
        print("2. Try running: python manage.py migrate")
        print("3. Check your .env file configuration")
        print("4. Verify all dependencies are installed")
        
    except Exception as e:
        print(f"❌ Setup Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
