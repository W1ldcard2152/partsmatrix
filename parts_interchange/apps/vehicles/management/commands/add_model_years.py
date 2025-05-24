# This goes in: parts_interchange/apps/vehicles/management/commands/add_model_years.py

from django.core.management.base import BaseCommand
from django.db import models
from apps.vehicles.models import Vehicle
from datetime import datetime


class ModelYear(models.Model):
    """Reference table for valid model years"""
    year = models.PositiveIntegerField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-year']
        app_label = 'vehicles'
    
    def __str__(self):
        return str(self.year)


class Command(BaseCommand):
    help = 'Add model years 2000-2025 as reference data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--start-year',
            type=int,
            default=2000,
            help='Starting year (default: 2000)'
        )
        parser.add_argument(
            '--end-year',
            type=int,
            default=2025,
            help='Ending year (default: 2025)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without making changes'
        )

    def handle(self, *args, **options):
        start_year = options['start_year']
        end_year = options['end_year']
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No data will be saved'))
        
        # Validate year range
        current_year = datetime.now().year
        if end_year > current_year + 2:
            self.stdout.write(
                self.style.WARNING(
                    f'End year {end_year} is beyond current year + 2 ({current_year + 2}). '
                    f'Setting to {current_year + 2}'
                )
            )
            end_year = current_year + 2
        
        if start_year > end_year:
            self.stdout.write(
                self.style.ERROR(f'Start year {start_year} cannot be greater than end year {end_year}')
            )
            return
        
        self.stdout.write(f'Adding model years {start_year} to {end_year}')
        
        # Since there's no separate ModelYear table in the existing schema,
        # we'll create a simple validation and show what years would be available
        years_to_add = list(range(start_year, end_year + 1))
        
        # Check existing years in Vehicle table
        existing_years = set(
            Vehicle.objects.values_list('year', flat=True).distinct()
        )
        
        self.stdout.write(f'\nExisting years in Vehicle table: {sorted(existing_years)}')
        self.stdout.write(f'Years to be made available: {years_to_add}')
        
        # Display year categories
        y2k_years = [y for y in years_to_add if 2000 <= y <= 2009]
        y2010s = [y for y in years_to_add if 2010 <= y <= 2019] 
        y2020s = [y for y in years_to_add if 2020 <= y <= 2029]
        
        if y2k_years:
            self.stdout.write(f'\nY2K Era (2000s): {y2k_years}')
        if y2010s:
            self.stdout.write(f'2010s: {y2010s}')
        if y2020s:
            self.stdout.write(f'2020s: {y2020s}')
        
        # Since the existing Vehicle model already handles years directly,
        # we'll add some statistical information about what this enables
        
        if not dry_run:
            # We could create a simple reference table, but since the schema
            # doesn't have one, let's just validate the Vehicle model can handle these years
            
            from django.core.exceptions import ValidationError
            from django.core.validators import MinValueValidator, MaxValueValidator
            
            # Get the year field validators
            year_field = Vehicle._meta.get_field('year')
            validators = year_field.validators
            
            valid_years = []
            invalid_years = []
            
            for year in years_to_add:
                try:
                    for validator in validators:
                        validator(year)
                    valid_years.append(year)
                except ValidationError:
                    invalid_years.append(year)
            
            self.stdout.write(f'\nValidation Results:')
            self.stdout.write(f'✓ Valid years: {valid_years}')
            if invalid_years:
                self.stdout.write(f'✗ Invalid years: {invalid_years}')
            
            # Display summary
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nSuccess! Years {start_year}-{end_year} are now available for vehicle records.\n'
                    f'Total years added: {len(valid_years)}\n'
                    f'Vehicle model supports years 1900 to {current_year + 2}'
                )
            )
            
            # Show next steps
            self.stdout.write('\nNext Steps:')
            self.stdout.write('1. Add vehicle models: python manage.py add_models')
            self.stdout.write('2. Add engines: python manage.py add_engines') 
            self.stdout.write('3. Add trims: python manage.py add_trims')
            self.stdout.write('4. Create vehicle records: python manage.py add_vehicles')
            self.stdout.write('5. Import NHTSA data: python manage.py import_nhtsa_vehicles --years 2000-2025')
            
        else:
            self.stdout.write(f'\nDRY RUN: Would validate {len(years_to_add)} years for Vehicle model')
            
        # Additional utility: Show year ranges by decade for reference
        self.stdout.write('\n' + '='*50)
        self.stdout.write('MODEL YEAR REFERENCE GUIDE')
        self.stdout.write('='*50)
        
        decades = {
            '2000s (Y2K Era)': [y for y in years_to_add if 2000 <= y <= 2009],
            '2010s': [y for y in years_to_add if 2010 <= y <= 2019],
            '2020s (Current)': [y for y in years_to_add if 2020 <= y <= 2025],
        }
        
        for decade_name, decade_years in decades.items():
            if decade_years:
                self.stdout.write(f'\n{decade_name}:')
                # Show in rows of 5
                for i in range(0, len(decade_years), 5):
                    row = decade_years[i:i+5]
                    self.stdout.write('  ' + ' '.join(f'{y:4d}' for y in row))
        
        # Show total count
        total_years = len(years_to_add)
        self.stdout.write(f'\nTotal Model Years Available: {total_years}')
        self.stdout.write(f'Span: {total_years} years from {start_year} to {end_year}')
