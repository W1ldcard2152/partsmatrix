"""
Smart Part Parser - Extract part data from raw text dumps
Handles dealer websites, eBay listings, catalog text, etc.
"""

import re
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.parts.models import Part, Manufacturer, PartCategory
from apps.vehicles.models import Vehicle, Make, Model, Engine, Trim
from apps.fitments.models import Fitment


class PartDataExtractor:
    """Extract structured data from unstructured part text"""
    
    def __init__(self):
        # Common part name patterns
        self.part_name_patterns = [
            r'^([^-]+)\s*-\s*(?:Acura|Honda|Toyota|Ford|GM|Chevrolet)',  # "Drive Plate - Acura"
            r'([A-Za-z\s]+?)\s*\([0-9A-Z-]+\)',  # "Drive Plate (26251-P8F-000)"
            r'([A-Za-z\s]+?)\s*-\s*[A-Z]+',      # "Drive Plate - ACURA"
        ]
        
        # Part number patterns (very flexible)
        self.part_number_patterns = [
            r'\(([0-9A-Z-]{8,})\)',              # "(26251-P8F-000)"
            r'Part Number:\s*([0-9A-Z-]+)',      # "Part Number: 26251-P8F-000"
            r'SKU:\s*([0-9A-Z-]+)',              # "SKU: 26251-P8F-000"
            r'([0-9A-Z]{5,}-[0-9A-Z]{3,}-[0-9A-Z]{3,})',  # "26251-P8F-000"
            r'([0-9A-Z]{8,})',                   # Long alphanumeric
        ]
        
        # Vehicle fitment table pattern
        self.fitment_pattern = r'(\d{4})\s+([A-Za-z]+)\s+([A-Za-z0-9\s]+?)\s+([A-Za-z0-9\s,-]+?)\s+([0-9.]+L\s+[A-Za-z0-9\s-]+)'
        
        # Manufacturer mapping
        self.manufacturer_mapping = {
            'acura': 'Acura',
            'honda': 'Honda', 
            'toyota': 'Toyota',
            'lexus': 'Lexus',
            'ford': 'Ford',
            'chevrolet': 'Chevrolet',
            'gm': 'GM',
            'dodge': 'Dodge',
            'chrysler': 'Chrysler',
            'jeep': 'Jeep',
            'ram': 'Ram',
            'bmw': 'BMW',
            'mercedes': 'Mercedes-Benz',
            'audi': 'Audi',
            'volkswagen': 'Volkswagen',
            'vw': 'Volkswagen',
            'nissan': 'Nissan',
            'infiniti': 'Infiniti',
            'mazda': 'Mazda',
            'subaru': 'Subaru',
            'mitsubishi': 'Mitsubishi',
            'hyundai': 'Hyundai',
            'kia': 'Kia',
            'volvo': 'Volvo',
            'porsche': 'Porsche',
        }
        
        # Part category mapping (smart guessing)
        self.category_mapping = {
            'drive plate': 'Transmission & Drivetrain',
            'ac line': 'HVAC & Climate Control',
            'a/c line': 'HVAC & Climate Control', 
            'air conditioning': 'HVAC & Climate Control',
            'brake pad': 'Wheels, Tires & Brakes',
            'brake rotor': 'Wheels, Tires & Brakes',
            'brake disc': 'Wheels, Tires & Brakes',
            'oil filter': 'Filters',
            'air filter': 'Filters',
            'fuel filter': 'Filters',
            'cabin filter': 'Filters',
            'spark plug': 'Engine',
            'ignition coil': 'Engine',
            'alternator': 'Electrical Systems',
            'starter': 'Electrical Systems',
            'battery': 'Electrical Systems',
            'radiator': 'Engine',
            'water pump': 'Engine',
            'thermostat': 'Engine',
            'fuel pump': 'Intake, Exhaust & Fuel',
            'fuel injector': 'Intake, Exhaust & Fuel',
            'muffler': 'Intake, Exhaust & Fuel',
            'catalytic converter': 'Emissions Control',
            'oxygen sensor': 'Emissions Control',
            'strut': 'Steering & Suspension',
            'shock': 'Steering & Suspension',
            'control arm': 'Steering & Suspension',
            'tie rod': 'Steering & Suspension',
            'cv joint': 'Transmission & Drivetrain',
            'cv axle': 'Transmission & Drivetrain',
            'transmission': 'Transmission & Drivetrain',
            'clutch': 'Transmission & Drivetrain',
            'differential': 'Transmission & Drivetrain',
            'driveshaft': 'Transmission & Drivetrain',
            'door handle': 'Door Components & Glass',
            'window regulator': 'Door Components & Glass',
            'door panel': 'Door Components & Glass',
            'headlight': 'Lighting & Visibility',
            'tail light': 'Lighting & Visibility',
            'fog light': 'Lighting & Visibility',
            'turn signal': 'Lighting & Visibility',
            'mirror': 'Body & Exterior',
            'bumper': 'Body & Exterior',
            'fender': 'Body & Exterior',
            'hood': 'Body & Exterior',
            'trunk': 'Body & Exterior',
            'seat': 'Interior',
            'dashboard': 'Interior',
            'steering wheel': 'Interior',
            'gear shift': 'Interior',
            'console': 'Interior',
        }

    def extract_part_name(self, text):
        """Extract part name from text"""
        for pattern in self.part_name_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                name = match.group(1).strip()
                # Clean up the name
                name = re.sub(r'\s+', ' ', name)  # Multiple spaces to single
                name = name.title()  # Title case
                return name
        return None

    def extract_part_number(self, text):
        """Extract part number from text"""
        for pattern in self.part_number_patterns:
            match = re.search(pattern, text)
            if match:
                part_num = match.group(1).strip().upper()
                # Validate part number (basic checks)
                if len(part_num) >= 5 and any(c.isdigit() for c in part_num):
                    return part_num
        return None

    def extract_manufacturer(self, text):
        """Extract manufacturer from text"""
        # Look for explicit manufacturer mentions
        for pattern in [
            r'Manufacturer:\s*([A-Za-z]+)',
            r'([A-Za-z]+)\s+Parts',
            r'-\s*([A-Za-z]+)\s*\(',
            r'Genuine\s+([A-Za-z]+)\s+Parts',
        ]:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                mfg = match.group(1).lower()
                if mfg in self.manufacturer_mapping:
                    return self.manufacturer_mapping[mfg]
        return None

    def guess_category(self, part_name):
        """Guess category from part name"""
        if not part_name:
            return None
            
        name_lower = part_name.lower()
        for keyword, category in self.category_mapping.items():
            if keyword in name_lower:
                return category
        return 'Engine'  # Default fallback

    def extract_fitments(self, text):
        """Extract vehicle fitments from text"""
        fitments = []
        
        # Find the fitment table section
        fitment_section = re.search(
            r'Vehicle Fitment.*?Year\s+Make\s+Model\s+Body.*?Engine.*?\n(.*?)(?:\n\n|\Z)', 
            text, 
            re.DOTALL | re.IGNORECASE
        )
        
        if fitment_section:
            fitment_text = fitment_section.group(1)
            
            # Extract each fitment line
            for match in re.finditer(self.fitment_pattern, fitment_text):
                year = int(match.group(1))
                make = match.group(2).strip()
                model = match.group(3).strip()
                trim = match.group(4).strip()
                engine = match.group(5).strip()
                
                fitments.append({
                    'year': year,
                    'make': make,
                    'model': model,
                    'trim': trim,
                    'engine': engine
                })
        
        return fitments

    def extract_description(self, text):
        """Extract description/notes from text"""
        # Look for description patterns
        desc_patterns = [
            r'Description:\s*([^*\n]+)',
            r'Other Names:\s*([^*\n]+)',
            r'([0-9.]+[tT][lL].*?[lL]\.)',  # "3.2tl. MDX. TL. CL. 3.2l."
        ]
        
        for pattern in desc_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                desc = match.group(1).strip()
                if len(desc) > 5:  # Reasonable description length
                    return desc
        return ''

    def parse_text(self, text):
        """Main parsing function - extract all data"""
        return {
            'part_name': self.extract_part_name(text),
            'part_number': self.extract_part_number(text),
            'manufacturer': self.extract_manufacturer(text),
            'description': self.extract_description(text),
            'fitments': self.extract_fitments(text),
            'category_guess': None  # Will be set after part_name is extracted
        }


class Command(BaseCommand):
    help = 'Parse part data from raw text and create database entries'

    def add_arguments(self, parser):
        parser.add_argument(
            'text_file', 
            type=str, 
            help='Path to text file containing raw part data'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without making changes'
        )
        parser.add_argument(
            '--auto-create',
            action='store_true',
            help='Automatically create missing manufacturers/categories'
        )

    def handle(self, *args, **options):
        text_file = options['text_file']
        dry_run = options['dry_run']
        auto_create = options['auto_create']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No data will be saved'))
        
        # Read the text file
        try:
            with open(text_file, 'r', encoding='utf-8') as f:
                raw_text = f.read()
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {text_file}'))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading file: {e}'))
            return

        # Parse the text
        extractor = PartDataExtractor()
        parsed_data = extractor.parse_text(raw_text)
        
        # Set category guess after part name is extracted
        parsed_data['category_guess'] = extractor.guess_category(parsed_data['part_name'])
        
        # Display parsed results
        self.stdout.write('=' * 60)
        self.stdout.write('🧠 SMART PART PARSER RESULTS')
        self.stdout.write('=' * 60)
        
        self.stdout.write(f'📝 Part Name: {parsed_data["part_name"] or "❌ NOT FOUND"}')
        self.stdout.write(f'🔢 Part Number: {parsed_data["part_number"] or "❌ NOT FOUND"}')
        self.stdout.write(f'🏭 Manufacturer: {parsed_data["manufacturer"] or "❌ NOT FOUND"}')
        self.stdout.write(f'📂 Category (Guess): {parsed_data["category_guess"] or "❌ NOT FOUND"}')
        self.stdout.write(f'📄 Description: {parsed_data["description"] or "❌ NOT FOUND"}')
        self.stdout.write(f'🚗 Fitments Found: {len(parsed_data["fitments"])}')
        
        if parsed_data['fitments']:
            self.stdout.write('\n🚗 VEHICLE FITMENTS:')
            for i, fitment in enumerate(parsed_data['fitments'][:5], 1):  # Show first 5
                self.stdout.write(f'  {i}. {fitment["year"]} {fitment["make"]} {fitment["model"]} {fitment["trim"]} {fitment["engine"]}')
            if len(parsed_data['fitments']) > 5:
                self.stdout.write(f'  ... and {len(parsed_data["fitments"]) - 5} more')

        # Validation checks
        self.stdout.write('\n🔍 VALIDATION RESULTS:')
        issues = []
        
        if not parsed_data['part_name']:
            issues.append('❌ Part name not found')
        if not parsed_data['part_number']:
            issues.append('❌ Part number not found')
        if not parsed_data['manufacturer']:
            issues.append('❌ Manufacturer not found')
        if not parsed_data['fitments']:
            issues.append('⚠️  No vehicle fitments found')
        
        if issues:
            for issue in issues:
                self.stdout.write(f'  {issue}')
        else:
            self.stdout.write('  ✅ All required data found!')

        # Try to create the part if we have minimum required data
        if (parsed_data['part_name'] and 
            parsed_data['part_number'] and 
            parsed_data['manufacturer']):
            
            if not dry_run:
                self.create_part_from_data(parsed_data, auto_create)
            else:
                self.stdout.write('\n💾 Would create part with this data (use --dry-run=false to save)')
        else:
            self.stdout.write('\n❌ Insufficient data to create part')
            self.stdout.write('   Need: part_name, part_number, manufacturer')

    def create_part_from_data(self, data, auto_create):
        """Create part and fitments from parsed data"""
        try:
            with transaction.atomic():
                # Get or create manufacturer
                manufacturer = self.get_or_create_manufacturer(
                    data['manufacturer'], auto_create
                )
                if not manufacturer:
                    self.stdout.write(f'❌ Manufacturer "{data["manufacturer"]}" not found')
                    return

                # Get or create category
                category = self.get_or_create_category(
                    data['category_guess'], auto_create
                )
                if not category:
                    self.stdout.write(f'❌ Category "{data["category_guess"]}" not found')
                    return

                # Create the part
                part, created = Part.objects.get_or_create(
                    manufacturer=manufacturer,
                    part_number=data['part_number'],
                    defaults={
                        'name': data['part_name'],
                        'category': category,
                        'description': data['description'],
                        'is_active': True
                    }
                )

                if created:
                    self.stdout.write(f'✅ Created part: {part}')
                else:
                    self.stdout.write(f'ℹ️  Part already exists: {part}')

                # Create fitments
                fitments_created = 0
                for fitment_data in data['fitments']:
                    vehicle = self.get_or_create_vehicle(fitment_data, auto_create)
                    if vehicle:
                        fitment, created = Fitment.objects.get_or_create(
                            part=part,
                            vehicle=vehicle,
                            defaults={'is_verified': False}
                        )
                        if created:
                            fitments_created += 1

                self.stdout.write(f'✅ Created {fitments_created} fitments')
                self.stdout.write('\n🎉 Part creation completed successfully!')

        except Exception as e:
            self.stdout.write(f'❌ Error creating part: {e}')

    def get_or_create_manufacturer(self, name, auto_create):
        """Get or create manufacturer"""
        try:
            return Manufacturer.objects.get(name=name)
        except Manufacturer.DoesNotExist:
            if auto_create:
                # Create basic manufacturer
                mfg = Manufacturer.objects.create(
                    name=name,
                    abbreviation=name.upper()[:10],
                    country='Unknown'
                )
                self.stdout.write(f'✅ Created manufacturer: {mfg}')
                return mfg
            return None

    def get_or_create_category(self, name, auto_create):
        """Get or create category"""
        if not name:
            return None
            
        try:
            return PartCategory.objects.get(name=name)
        except PartCategory.DoesNotExist:
            if auto_create:
                category = PartCategory.objects.create(
                    name=name,
                    description=f'Auto-generated category for {name}'
                )
                self.stdout.write(f'✅ Created category: {category}')
                return category
            return None

    def get_or_create_vehicle(self, fitment_data, auto_create):
        """Get or create vehicle from fitment data"""
        try:
            # Get or create make
            make, _ = Make.objects.get_or_create(
                name=fitment_data['make'],
                defaults={'is_active': True}
            )
            
            # Get or create model  
            model, _ = Model.objects.get_or_create(
                make=make,
                name=fitment_data['model'],
                defaults={'is_active': True}
            )
            
            # Get or create trim
            trim = None
            if fitment_data['trim']:
                trim, _ = Trim.objects.get_or_create(
                    name=fitment_data['trim']
                )
            
            # Get or create engine
            engine = None
            if fitment_data['engine']:
                engine, _ = Engine.objects.get_or_create(
                    name=fitment_data['engine'],
                    defaults={'fuel_type': 'GAS'}
                )
            
            # Get or create vehicle
            vehicle, created = Vehicle.objects.get_or_create(
                year=fitment_data['year'],
                make=make,
                model=model,
                trim=trim,
                engine=engine,
                defaults={'is_active': True}
            )
            
            return vehicle
            
        except Exception as e:
            self.stdout.write(f'⚠️  Could not create vehicle: {e}')
            return None
