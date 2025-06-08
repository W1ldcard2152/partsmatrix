"""
Quick diagnostic script to identify performance issues
"""
import os
import time
from django.conf import settings
from django.db import connection
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Diagnose database performance issues'

    def handle(self, *args, **options):
        self.stdout.write('=== PERFORMANCE DIAGNOSTIC ===')
        
        # Check database configuration
        db_config = settings.DATABASES['default']
        self.stdout.write(f'Database Engine: {db_config["ENGINE"]}')
        
        if 'postgresql' in db_config['ENGINE']:
            host = db_config.get('HOST', 'Not specified')
            self.stdout.write(f'Database Host: {host}')
            
            if 'render.com' in host or 'amazonaws.com' in host:
                self.stdout.write(self.style.ERROR(
                    '🚨 PERFORMANCE ISSUE FOUND: You are connecting to a REMOTE database!'
                ))
                self.stdout.write(self.style.ERROR(
                    'This causes 200-500ms latency per query!'
                ))
                self.stdout.write(self.style.WARNING(
                    'SOLUTION: Switch to local SQLite for development'
                ))
            else:
                self.stdout.write('✓ Using local database')
        
        # Test query performance
        self.stdout.write('\n=== QUERY PERFORMANCE TEST ===')
        
        start_time = time.time()
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            result = cursor.fetchone()
        query_time = (time.time() - start_time) * 1000
        
        self.stdout.write(f'Simple query time: {query_time:.2f}ms')
        
        if query_time > 100:
            self.stdout.write(self.style.ERROR(
                f'🚨 SLOW QUERY: {query_time:.2f}ms is too slow for development!'
            ))
        elif query_time > 50:
            self.stdout.write(self.style.WARNING(
                f'⚠️  MODERATE DELAY: {query_time:.2f}ms'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'✓ FAST QUERY: {query_time:.2f}ms'
            ))
        
        # Check if debug toolbar is affecting performance
        if 'debug_toolbar' in settings.INSTALLED_APPS:
            self.stdout.write('\n⚠️  Debug toolbar is enabled - this can slow things down')
        
        self.stdout.write('\n=== RECOMMENDATIONS ===')
        if 'render.com' in db_config.get('HOST', ''):
            self.stdout.write('1. Switch to local SQLite for development')
            self.stdout.write('2. Use remote database only for production')
            self.stdout.write('3. Run: export DATABASE_URL="" to force SQLite')
