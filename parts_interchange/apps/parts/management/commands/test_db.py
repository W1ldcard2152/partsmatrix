from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
import sys


class Command(BaseCommand):
    help = 'Test database connection and run basic checks'

    def add_arguments(self, parser):
        parser.add_argument(
            '--migrate',
            action='store_true',
            help='Run migrations after testing connection'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testing database connection...'))
        
        try:
            # Test database connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result:
                    self.stdout.write(self.style.SUCCESS('✅ Database connection successful'))
                
            # Test that we can query basic Django tables
            from django.contrib.auth.models import User
            user_count = User.objects.count()
            self.stdout.write(f'✅ Found {user_count} users in database')
            
            # Test our models
            from apps.parts.models import Manufacturer, Part
            from apps.vehicles.models import Vehicle
            from apps.fitments.models import Fitment
            
            mfg_count = Manufacturer.objects.count()
            part_count = Part.objects.count()
            vehicle_count = Vehicle.objects.count()
            fitment_count = Fitment.objects.count()
            
            self.stdout.write(f'✅ Database contains:')
            self.stdout.write(f'   - {mfg_count} manufacturers')
            self.stdout.write(f'   - {part_count} parts')
            self.stdout.write(f'   - {vehicle_count} vehicles')
            self.stdout.write(f'   - {fitment_count} fitments')
            
            if options['migrate']:
                self.stdout.write(self.style.WARNING('Running migrations...'))
                call_command('migrate', verbosity=1)
                
            self.stdout.write(self.style.SUCCESS('\n🎉 All tests passed! Database is ready.'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Database error: {e}'))
            
            # Provide helpful suggestions
            self.stdout.write('\nTroubleshooting suggestions:')
            self.stdout.write('1. Check your .env file database settings')
            self.stdout.write('2. Verify database server is running')
            self.stdout.write('3. Run: python manage.py migrate')
            self.stdout.write('4. Check network connectivity (if using remote database)')
            
            sys.exit(1)
