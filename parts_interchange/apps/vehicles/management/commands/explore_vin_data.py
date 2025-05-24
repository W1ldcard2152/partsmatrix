"""
Django management command to explore NHTSA VIN decoding capabilities
Usage: python manage.py explore_vin_data --vin <VIN> or --sample-vins
"""

import requests
import json
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Explore NHTSA VIN decoding data to understand available fields'
    
    def __init__(self):
        super().__init__()
        self.base_url = 'https://vpic.nhtsa.dot.gov/api'
        
        # Sample VINs for different vehicle types
        self.sample_vins = {
            'Ford F-150 2021': '1FTMW1T88MFA12345',
            'Honda Civic 2020': '2HGFE2F50LH012345', 
            'Toyota Camry 2019': '4T1B11HK5KU012345',
            'Chevrolet Corvette 2020': '1G1YB2D40L5012345',
            'BMW 3 Series 2021': 'WBA8E9C50M7012345',
            'Tesla Model 3 2021': '5YJ3E1EA4MF012345',
        }

    def add_arguments(self, parser):
        parser.add_argument(
            '--vin',
            type=str,
            help='Specific VIN to decode'
        )
        parser.add_argument(
            '--sample-vins',
            action='store_true',
            help='Decode sample VINs to show available data'
        )
        parser.add_argument(
            '--show-all-fields',
            action='store_true',
            help='Show all available fields, not just vehicle specs'
        )
        parser.add_argument(
            '--get-variables',
            action='store_true',
            help='Get list of all available VIN decode variables'
        )

    def handle(self, *args, **options):
        if options['get_variables']:
            self.get_vin_variables()
        elif options['vin']:
            self.decode_single_vin(options['vin'], options['show_all_fields'])
        elif options['sample_vins']:
            self.decode_sample_vins(options['show_all_fields'])
        else:
            self.stdout.write('Please specify --vin, --sample-vins, or --get-variables')

    def get_vin_variables(self):
        """Get list of all VIN decode variables available from NHTSA"""
        url = f'{self.base_url}/vehicles/GetVehicleVariableList?format=json'
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            self.stdout.write('Available VIN Decode Variables:')
            self.stdout.write('=' * 50)
            
            variables = data.get('Results', [])
            
            # Group by category
            categories = {}
            for var in variables:
                name = var.get('Name', '')
                desc = var.get('Description', '')
                data_type = var.get('DataType', '')
                
                # Simple categorization
                category = 'General'
                if any(word in name.lower() for word in ['engine', 'motor', 'power', 'fuel', 'displacement']):
                    category = 'Engine'
                elif any(word in name.lower() for word in ['transmission', 'drive', 'gear']):
                    category = 'Drivetrain'
                elif any(word in name.lower() for word in ['body', 'door', 'seat', 'cab', 'style']):
                    category = 'Body'
                elif any(word in name.lower() for word in ['safety', 'airbag', 'restraint']):
                    category = 'Safety'
                elif any(word in name.lower() for word in ['trim', 'series', 'level']):
                    category = 'Trim'
                
                if category not in categories:
                    categories[category] = []
                categories[category].append({'name': name, 'desc': desc, 'type': data_type})
            
            for category, vars in categories.items():
                self.stdout.write(f'\n{category}:')
                self.stdout.write('-' * 20)
                for var in sorted(vars, key=lambda x: x['name']):
                    self.stdout.write(f"  {var['name']} ({var['type']})")
                    if var['desc']:
                        self.stdout.write(f"    Description: {var['desc']}")

        except Exception as e:
            self.stdout.write(f'Error getting variables: {e}')

    def decode_single_vin(self, vin, show_all=False):
        """Decode a single VIN and show results"""
        self.stdout.write(f'Decoding VIN: {vin}')
        self.stdout.write('=' * 50)
        
        decoded_data = self.decode_vin(vin)
        if decoded_data:
            self.display_decoded_data(decoded_data, show_all)

    def decode_sample_vins(self, show_all=False):
        """Decode sample VINs to show data variety"""
        for description, vin in self.sample_vins.items():
            self.stdout.write(f'\n{description} - VIN: {vin}')
            self.stdout.write('=' * 60)
            
            decoded_data = self.decode_vin(vin)
            if decoded_data:
                self.display_decoded_data(decoded_data, show_all)
            
            self.stdout.write('\n' + '-' * 60)

    def decode_vin(self, vin):
        """Decode VIN using NHTSA API"""
        url = f'{self.base_url}/vehicles/DecodeVinValues/{vin}?format=json'
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get('Results') and len(data['Results']) > 0:
                return data['Results'][0]
        except Exception as e:
            self.stdout.write(f'Error decoding VIN {vin}: {e}')
        
        return None

    def display_decoded_data(self, data, show_all=False):
        """Display decoded VIN data in organized format"""
        
        # Key fields for vehicle identification
        key_fields = {
            'Make': 'Make',
            'Model': 'Model', 
            'Model Year': 'ModelYear',
            'Trim': 'Trim',
            'Series': 'Series',
            'Body Class': 'BodyClass',
            'Vehicle Type': 'VehicleType',
        }
        
        # Engine specifications
        engine_fields = {
            'Engine Model': 'EngineModel',
            'Engine Displacement (L)': 'DisplacementL',
            'Engine Displacement (CI)': 'DisplacementCI', 
            'Engine Displacement (CC)': 'DisplacementCC',
            'Engine Number of Cylinders': 'EngineCylinders',
            'Engine Configuration': 'EngineConfiguration',
            'Fuel Type - Primary': 'FuelTypePrimary',
            'Engine Power (kW)': 'EnginekW',
            'Engine Brake Horsepower (BHP)': 'EngineBHP',
            'Engine Manufacturer': 'EngineManufacturer',
        }
        
        # Drivetrain specifications
        drivetrain_fields = {
            'Drive Type': 'DriveType',
            'Transmission Style': 'TransmissionStyle',
            'Transmission Speeds': 'TransmissionSpeeds',
        }
        
        # Display sections
        sections = [
            ('Vehicle Information', key_fields),
            ('Engine Specifications', engine_fields),
            ('Drivetrain', drivetrain_fields),
        ]
        
        for section_name, fields in sections:
            self.stdout.write(f'\n{section_name}:')
            found_data = False
            
            for display_name, field_key in fields.items():
                value = data.get(field_key)
                if value and value not in ['', 'Not Applicable', 'N/A', None]:
                    self.stdout.write(f'  {display_name}: {value}')
                    found_data = True
            
            if not found_data:
                self.stdout.write('  No data available')
        
        # Show all fields if requested
        if show_all:
            self.stdout.write('\nAll Available Fields:')
            self.stdout.write('-' * 30)
            
            all_fields = sorted(data.keys())
            for field in all_fields:
                value = data.get(field)
                if value and value not in ['', 'Not Applicable', 'N/A', None]:
                    self.stdout.write(f'  {field}: {value}')

    def extract_key_specs(self, decoded_data):
        """Extract key specifications from decoded data for database storage"""
        specs = {}
        
        # Vehicle basics
        specs['make'] = decoded_data.get('Make', '')
        specs['model'] = decoded_data.get('Model', '')
        specs['year'] = decoded_data.get('ModelYear', '')
        
        # Trim information
        trim_candidates = [
            decoded_data.get('Trim', ''),
            decoded_data.get('Series', ''),
        ]
        specs['trim'] = next((t for t in trim_candidates if t and t not in ['', 'Not Applicable', 'N/A']), '')
        
        # Engine information
        engine_info = {}
        if decoded_data.get('EngineModel'):
            engine_info['name'] = decoded_data['EngineModel']
        
        # Engine displacement
        displacement = (decoded_data.get('DisplacementL') or 
                       decoded_data.get('DisplacementCC') or 
                       decoded_data.get('DisplacementCI'))
        if displacement and displacement != 'Not Applicable':
            engine_info['displacement'] = displacement
        
        # Cylinders
        cylinders = decoded_data.get('EngineCylinders')
        if cylinders and cylinders != 'Not Applicable':
            try:
                engine_info['cylinders'] = int(cylinders)
            except ValueError:
                pass
        
        # Fuel type
        fuel_type = decoded_data.get('FuelTypePrimary', decoded_data.get('FuelType', ''))
        if fuel_type and fuel_type != 'Not Applicable':
            engine_info['fuel_type'] = fuel_type
        
        # Horsepower
        hp = decoded_data.get('EngineBHP') or decoded_data.get('EnginekW')
        if hp and hp != 'Not Applicable':
            engine_info['horsepower'] = hp
        
        specs['engine'] = engine_info if engine_info else None
        
        # Drivetrain
        drivetrain_info = {}
        drive_type = decoded_data.get('DriveType')
        if drive_type and drive_type != 'Not Applicable':
            drivetrain_info['drive_type'] = drive_type
        
        transmission = decoded_data.get('TransmissionStyle')
        if transmission and transmission != 'Not Applicable':
            drivetrain_info['transmission'] = transmission
        
        specs['drivetrain'] = drivetrain_info if drivetrain_info else None
        
        # Body information
        body_info = {}
        body_class = decoded_data.get('BodyClass')
        if body_class and body_class != 'Not Applicable':
            body_info['body_class'] = body_class
        
        vehicle_type = decoded_data.get('VehicleType')
        if vehicle_type and vehicle_type != 'Not Applicable':
            body_info['vehicle_type'] = vehicle_type
        
        specs['body'] = body_info if body_info else None
        
        return specs
