"""
Django management command to populate vehicle data from NHTSA API
Usage: python manage.py import_nhtsa_vehicles
"""

import requests
import time
import re
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.vehicles.models import Make, Model, Engine, Trim, Vehicle


class Command(BaseCommand):
    help = 'Import vehicle data from NHTSA API'
    
    def __init__(self):
        super().__init__()
        self.base_url = 'https://vpic.nhtsa.dot.gov/api'
        
        # Filter patterns to reduce noise
        self.noise_patterns = [
            # Chassis codes and internal codes
            r'^[A-Z0-9]{2,4}$',  # Short alphanumeric codes like "A1", "B2X", etc.
            r'CHASSIS',
            r'INCOMPLETE',
            r'CUTAWAY',
            r'STRIPPED',
            
            # Foreign market models (common patterns)
            r'RIGHT HAND DRIVE',
            r'RHD',
            r'EXPORT',
            r'INTL',
            r'INTERNATIONAL',
            
            # Obvious non-consumer models
            r'COMMERCIAL',
            r'FLEET',
            r'TAXI',  
            r'POLICE',
            r'EMERGENCY',
            r'AMBULANCE',
            r'FIRE',
            
            # Prototype/concept cars
            r'CONCEPT',
            r'PROTOTYPE',
            r'EXPERIMENTAL',
            
            # Generic/placeholder entries
            r'^MODEL$',
            r'^UNKNOWN$',
            r'^N/?A$',
            r'^NOT APPLICABLE$',
            r'^TBD$',
            r'^TO BE DETERMINED$',
        ]
        
        # US domestic makes to prioritize
        self.domestic_makes = {
            'CHEVROLET', 'FORD', 'DODGE', 'CHRYSLER', 'PLYMOUTH', 'BUICK', 
            'CADILLAC', 'GMC', 'PONTIAC', 'OLDSMOBILE', 'SATURN', 'LINCOLN',
            'MERCURY', 'JEEP', 'RAM', 'TESLA'
        }
        
        # Common foreign makes that sell in US market
        self.common_foreign_makes = {
            'TOYOTA', 'HONDA', 'NISSAN', 'MAZDA', 'SUBARU', 'MITSUBISHI',
            'HYUNDAI', 'KIA', 'BMW', 'MERCEDES-BENZ', 'AUDI', 'VOLKSWAGEN',
            'PORSCHE', 'VOLVO', 'JAGUAR', 'LAND ROVER', 'LEXUS', 'ACURA',
            'INFINITI', 'FERRARI', 'LAMBORGHINI', 'MASERATI', 'BENTLEY',
            'ROLLS-ROYCE', 'ASTON MARTIN', 'ALFA ROMEO', 'FIAT'
        }
        
    def add_arguments(self, parser):
        parser.add_argument(
            '--years',
            type=str,
            default='2000-2024',
            help='Year range to import (e.g., "2000-2024" or "2020")'
        )
        parser.add_argument(
            '--makes',
            type=str,
            help='Comma-separated list of makes to import (default: all domestic + common foreign)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without making changes'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=50,
            help='Number of records to process in each batch'
        )
        parser.add_argument(
            '--decode-vins',
            action='store_true',
            help='Attempt to decode sample VINs for detailed specs (slower)'
        )
        parser.add_argument(
            '--us-market-only',
            action='store_true',
            default=True,
            help='Filter to US market vehicles only (default: True)'
        )
        
    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        self.batch_size = options['batch_size']
        self.decode_vins = options['decode_vins']
        self.us_market_only = options['us_market_only']
        
        if self.dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No data will be saved'))
        
        # Parse year range
        years = self.parse_years(options['years'])
        makes_filter = options['makes'].split(',') if options['makes'] else None
        
        self.stdout.write(f'Importing vehicles for years: {min(years)}-{max(years)}')
        
        # Step 1: Get and filter makes
        makes_data = self.get_makes()
        
        # Apply make filtering
        if makes_filter:
            makes_data = self.filter_makes_by_list(makes_data, makes_filter)
        elif self.us_market_only:
            makes_data = self.filter_us_market_makes(makes_data)
        
        self.stdout.write(f'Found {len(makes_data)} makes to process')
        
        # Debug: Show filtered makes
        self.stdout.write('Makes to process:')
        for make in makes_data[:20]:  # Show first 20
            self.stdout.write(f'  - {make.get("MakeName")}')
        if len(makes_data) > 20:
            self.stdout.write(f'  ... and {len(makes_data) - 20} more')
        
        for make_data in makes_data:
            self.import_make_data(make_data, years)
            
    def parse_years(self, year_string):
        """Parse year range string into list of years"""
        if '-' in year_string:
            start, end = map(int, year_string.split('-'))
            return list(range(start, end + 1))
        else:
            return [int(year_string)]
    
    def is_noise_model(self, model_name):
        """Check if a model name appears to be noise/unwanted data"""
        if not model_name:
            return True
            
        model_upper = model_name.upper()
        
        # Check against noise patterns
        for pattern in self.noise_patterns:
            if re.search(pattern, model_upper):
                return True
        
        # Check for excessively long model names (likely descriptions)
        if len(model_name) > 50:
            return True
            
        # Check for model names that are mostly numbers
        if len(re.sub(r'[^0-9]', '', model_name)) > len(model_name) * 0.7:
            return True
            
        return False
    
    def filter_us_market_makes(self, makes_data):
        """Filter to US market makes only"""
        allowed_makes = self.domestic_makes.union(self.common_foreign_makes)
        
        filtered = []
        for make in makes_data:
            make_name = make.get('MakeName', '').upper()
            if make_name in allowed_makes:
                filtered.append(make)
        
        return filtered
    
    def filter_makes_by_list(self, makes_data, makes_filter):
        """Filter makes using case-insensitive matching"""
        filtered_makes = []
        makes_filter_upper = [name.upper().strip() for name in makes_filter]
        
        for make in makes_data:
            make_name = make.get('MakeName', '').upper()
            if make_name in makes_filter_upper:
                filtered_makes.append(make)
        
        # If no exact matches, show similar names
        if not filtered_makes:
            self.stdout.write(f'No exact matches found for: {makes_filter}')
            self.stdout.write('Similar makes found:')
            all_makes = self.get_makes()
            for make in all_makes:
                make_name = make.get('MakeName', '')
                if any(filter_name.lower() in make_name.lower() for filter_name in makes_filter):
                    self.stdout.write(f'  - {make_name}')
        
        return filtered_makes
    
    def get_makes(self):
        """Get all vehicle makes from NHTSA"""
        url = f'{self.base_url}/vehicles/GetMakesForVehicleType/car?format=json'
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data['Results']
        except requests.exceptions.RequestException as e:
            self.stdout.write(f'Error fetching makes: {e}')
            return []
    
    def get_models_for_make_year(self, make_name, year):
        """Get models for a specific make and year (more accurate than just make)"""
        url = f'{self.base_url}/vehicles/GetModelsForMakeYear/make/{make_name}/modelyear/{year}?format=json'
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data['Results']
        except requests.exceptions.RequestException as e:
            self.stdout.write(f'Error fetching models for {make_name} {year}: {e}')
            return []
    
    def get_models_for_make(self, make_name):
        """Get all models for a specific make (fallback method)"""
        url = f'{self.base_url}/vehicles/GetModelsForMake/{make_name}?format=json'
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data['Results']
        except requests.exceptions.RequestException as e:
            self.stdout.write(f'Error fetching models for {make_name}: {e}')
            return []
    
    def decode_vin_for_specs(self, vin):
        """Decode a VIN to get detailed specifications"""
        url = f'{self.base_url}/vehicles/DecodeVinValues/{vin}?format=json'
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('Results'):
                return self.parse_vin_decode_results(data['Results'][0])
        except Exception as e:
            self.stdout.write(f'VIN decode error for {vin}: {e}')
        
        return {}
    
    def parse_vin_decode_results(self, vin_data):
        """Parse VIN decode results into structured data"""
        specs = {}
        
        # Map common fields
        field_mappings = {
            'Trim': ['Trim', 'Series'],
            'Engine': ['Engine Model', 'Engine Displacement (L)', 'Engine Displacement (CI)'],
            'EngineDisplacement': ['Displacement (L)', 'Displacement (CC)', 'Displacement (CI)'],
            'EngineCylinders': ['Engine Number of Cylinders'],
            'FuelType': ['Fuel Type - Primary', 'Fuel Type'],
            'Horsepower': ['Engine Power (kW)', 'Engine Brake Horsepower (BHP)', 'Engine HP'],
            'DriveType': ['Drive Type'],
            'TransmissionType': ['Transmission Style', 'Transmission Speeds']
        }
        
        # Extract values
        for key, possible_fields in field_mappings.items():
            for field in possible_fields:
                value = vin_data.get(field)
                if value and value not in ['', 'Not Applicable', 'N/A', None]:
                    specs[key] = value
                    break
        
        return specs
    
    def get_sample_vins_for_make_model_year(self, make_name, model_name, year):
        """Generate sample VINs for a make/model/year combination"""
        # This is a simplified approach - you'd need actual VIN patterns
        # For now, we'll return empty list and rely on other methods
        return []
    
    @transaction.atomic
    def import_make_data(self, make_data, years):
        """Import all data for a specific make"""
        make_name = make_data.get('MakeName')
        make_id = make_data.get('MakeId')
        
        if not make_name:
            return
        
        self.stdout.write(f'Processing make: {make_name}')
        
        # Create or get Make object
        if not self.dry_run:
            make_obj, created = Make.objects.get_or_create(
                name=make_name,
                defaults={'country': 'Unknown'}
            )
            if created:
                self.stdout.write(f'  Created make: {make_name}')
        else:
            make_obj = None
        
        # Process each year for this make
        for year in years:
            try:
                # Get models for make/year combination (more accurate)
                models_data = self.get_models_for_make_year(make_name, year)
                
                if not models_data:
                    # Fallback to general models for make
                    models_data = self.get_models_for_make(make_name)
                
                # Filter out noise models
                clean_models = []
                for model_data in models_data:
                    model_name = model_data.get('Model_Name') or model_data.get('ModelName')
                    if model_name and not self.is_noise_model(model_name):
                        clean_models.append(model_data)
                
                self.stdout.write(f'  {year}: Found {len(clean_models)} clean models (filtered from {len(models_data)})')
                
                for model_data in clean_models:
                    self.import_model_data(make_name, make_obj, model_data, year)
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                self.stdout.write(f'  Error processing {make_name} {year}: {e}')
    
    @transaction.atomic  
    def import_model_data(self, make_name, make_obj, model_data, year):
        """Import model data and create vehicle records"""
        model_name = model_data.get('Model_Name') or model_data.get('ModelName')
        
        if not model_name:
            return
        
        self.stdout.write(f'    Processing model: {model_name}')
        
        # Create Model object
        if not self.dry_run and make_obj:
            model_obj, created = Model.objects.get_or_create(
                make=make_obj,
                name=model_name,
                defaults={'body_style': 'Unknown'}
            )
            if created:
                self.stdout.write(f'      Created model: {make_name} {model_name}')
        else:
            model_obj = None
        
        # Try to get detailed specs if VIN decoding is enabled
        trim_obj = None
        engine_obj = None
        
        if self.decode_vins:
            sample_vins = self.get_sample_vins_for_make_model_year(make_name, model_name, year)
            for vin in sample_vins[:3]:  # Limit to 3 samples to avoid rate limiting
                specs = self.decode_vin_for_specs(vin)
                if specs:
                    # Create Trim if found
                    if specs.get('Trim') and not self.dry_run:
                        trim_obj, _ = Trim.objects.get_or_create(
                            name=specs['Trim'],
                            defaults={'description': f'Trim for {make_name} {model_name}'}
                        )
                    
                    # Create Engine if found
                    if specs.get('Engine') and not self.dry_run:
                        engine_defaults = {
                            'fuel_type': specs.get('FuelType', 'GAS')[:3] if specs.get('FuelType') else 'GAS',
                            'horsepower': self.extract_number(specs.get('Horsepower')),
                            'cylinders': self.extract_number(specs.get('EngineCylinders')),
                            'displacement': self.extract_number(specs.get('EngineDisplacement')),
                        }
                        engine_obj, _ = Engine.objects.get_or_create(
                            name=specs['Engine'],
                            defaults=engine_defaults
                        )
                    break
        
        # Create vehicle record
        try:
            if not self.dry_run and make_obj and model_obj:
                vehicle_data = {
                    'year': year,
                    'make': make_obj,
                    'model': model_obj,
                    'trim': trim_obj,
                    'engine': engine_obj,
                    'is_active': True
                }
                
                vehicle, created = Vehicle.objects.get_or_create(
                    year=year,
                    make=make_obj,
                    model=model_obj,
                    trim=trim_obj,
                    engine=engine_obj,
                    defaults=vehicle_data
                )
                
                if created:
                    self.stdout.write(f'        Created: {year} {make_name} {model_name}')
            else:
                self.stdout.write(f'        Would create: {year} {make_name} {model_name}')
                
        except Exception as e:
            self.stdout.write(f'        Error creating vehicle {year} {make_name} {model_name}: {e}')
    
    def extract_number(self, value):
        """Extract numeric value from string"""
        if not value:
            return None
        
        # Extract first number from string
        match = re.search(r'\d+\.?\d*', str(value))
        if match:
            try:
                return float(match.group())
            except ValueError:
                pass
        return None
    
    def handle_api_error(self, response, context=""):
        """Handle API errors gracefully"""
        if response.status_code == 429:  # Too Many Requests
            self.stdout.write(f'Rate limited, waiting 60 seconds... {context}')
            time.sleep(60)
            return True  # Retry
        elif response.status_code >= 500:
            self.stdout.write(f'Server error ({response.status_code}), skipping... {context}')
            return False  # Skip
        else:
            response.raise_for_status()
            return False
