import re
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db import models

from apps.parts.models import Part, PartCategory, Manufacturer
from apps.vehicles.models import Make, Model, Trim, Engine, Vehicle
from apps.fitments.models import Fitment

class Command(BaseCommand):
    help = 'Import Acura parts data from raw text with improved vehicle matching'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the text file containing raw part data.')
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without making changes'
        )

    def handle(self, *args, **options):
        file_path = options['file_path']
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No data will be saved'))
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_data = f.read()
        except FileNotFoundError:
            raise CommandError(f'File not found at {file_path}')
        except Exception as e:
            raise CommandError(f'Error reading file {file_path}: {e}')
        
        # Define category mapping
        part_category_map = {
            "AC Line": "HVAC & Climate Control",
            "Drive Plate": "Transmission & Drivetrain", 
            # Add more mappings as needed
        }

        try:
            part_name, part_number = self._parse_part_name_and_number(raw_data)
            fitment_data = self._parse_fitment_data(raw_data)

            self.stdout.write(self.style.SUCCESS(f"Parsed Part Name: {part_name}"))
            self.stdout.write(self.style.SUCCESS(f"Parsed Part Number: {part_number}"))
            self.stdout.write(self.style.SUCCESS(f"Raw Fitment Entries: {len(fitment_data)}"))

            # Show what was parsed
            for entry in fitment_data:
                self.stdout.write(f"  {entry['Year']} {entry['Make']} {entry['Model']} | {entry['Body & Trim']} | {entry['Engine & Transmission']}")

            # Dry run - show what vehicles would be matched
            self.stdout.write('\n=== Vehicle Matching Analysis ===')
            for fitment_entry in fitment_data:
                matching_vehicles = self._find_matching_vehicles(fitment_entry)
                if matching_vehicles:
                    self.stdout.write(f"✓ {fitment_entry['Year']} {fitment_entry['Make']} {fitment_entry['Model']} {fitment_entry['Body & Trim']}")
                    for vehicle in matching_vehicles:
                        self.stdout.write(f"    → {vehicle}")
                else:
                    self.stdout.write(f"✗ {fitment_entry['Year']} {fitment_entry['Make']} {fitment_entry['Model']} {fitment_entry['Body & Trim']} (no matches)")

            if not dry_run:
                with transaction.atomic():
                    # Get or create Manufacturer (Acura)
                    manufacturer, _ = Manufacturer.objects.get_or_create(
                        name="Acura",
                        defaults={'abbreviation': 'ACURA', 'country': 'Japan'}
                    )

                    # Get or create PartCategory
                    category_name = part_category_map.get(part_name, "Uncategorized")
                    part_category, _ = PartCategory.objects.get_or_create(
                        name=category_name
                    )

                    # Get or create Part
                    part, created = Part.objects.get_or_create(
                        manufacturer=manufacturer,
                        part_number=part_number,
                        defaults={
                            'name': part_name,
                            'category': part_category,
                        }
                    )
                    
                    if created:
                        self.stdout.write(self.style.SUCCESS(f"Created part: {part}"))
                    else:
                        self.stdout.write(self.style.WARNING(f"Part already exists: {part}"))

                    # Process Fitment Data with proper vehicle matching
                    fitments_created = 0
                    fitments_skipped = 0
                    
                    for fitment_entry in fitment_data:
                        created_count = self._create_fitments_for_entry(
                            part, fitment_entry, dry_run
                        )
                        if created_count > 0:
                            fitments_created += created_count
                            self.stdout.write(f"  ✓ Created {created_count} fitment(s) for {fitment_entry['Year']} {fitment_entry['Make']} {fitment_entry['Model']}")
                        else:
                            fitments_skipped += 1
                            self.stdout.write(f"  ⚠️ No vehicles found for {fitment_entry['Year']} {fitment_entry['Make']} {fitment_entry['Model']} {fitment_entry['Body & Trim']}")

                    self.stdout.write(self.style.SUCCESS(
                        f'\nSUMMARY:\n'
                        f'Part: {part_name} ({part_number})\n'
                        f'Fitments Created: {fitments_created}\n'
                        f'Entries Skipped: {fitments_skipped}\n'
                        f'Total Entries: {len(fitment_data)}'
                    ))

        except Exception as e:
            raise CommandError(f'Error importing parts: {e}')

    def _parse_part_name_and_number(self, raw_data):
        """Parse part name and number from raw data"""
        patterns = [
            r'^(.*?)\s*-\s*Acura\s*\((.*?)\)',
            r'(.*?)\s*-\s*Acura.*?(\d{5}-[A-Z0-9]+-\d{3})',
            r'(.*?)\s*.*?Part Number:\s*([A-Z0-9-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, raw_data, re.MULTILINE)
            if match:
                part_name = match.group(1).strip()
                part_number = match.group(2).strip()
                return part_name, part_number
        
        raise ValueError("Could not parse Part Name and Part Number from raw data.")

    def _parse_fitment_data(self, raw_data):
        """Parse vehicle fitment data with improved extraction"""
        fitment_data = []
        
        # Find the "Vehicle Fitment" section
        fitment_index = raw_data.find('Vehicle Fitment')
        if fitment_index == -1:
            return fitment_data
        
        # Extract everything after "Vehicle Fitment"
        after_fitment = raw_data[fitment_index:]
        
        # Look for the header line
        header_match = re.search(r'Year\s+Make\s+Model\s+Body & Trim\s+Engine & Transmission', after_fitment)
        if not header_match:
            return fitment_data
        
        # Get content after the header
        header_index = after_fitment.find(header_match.group(0))
        after_header = after_fitment[header_index + len(header_match.group(0)):]
        
        # Split into lines and process
        lines = after_header.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this looks like a data row (starts with year)
            if re.match(r'^\d{4}', line):
                # Split by tabs or multiple spaces
                parts = re.split(r'\t+|\s{2,}', line)
                
                if len(parts) >= 5:
                    year = int(parts[0])
                    make = parts[1].strip()
                    model = parts[2].strip()
                    body_trim = parts[3].strip()
                    engine_trans = parts[4].strip()
                    
                    fitment_data.append({
                        'Year': year,
                        'Make': make,
                        'Model': model,
                        'Body & Trim': body_trim,
                        'Engine & Transmission': engine_trans,
                    })
        
        return fitment_data

    def _find_matching_vehicles(self, fitment_entry):
        """Find existing vehicles that match the fitment entry"""
        year = fitment_entry['Year']
        make_name = fitment_entry['Make']
        model_name = fitment_entry['Model']
        body_trim = fitment_entry['Body & Trim']
        engine_trans = fitment_entry['Engine & Transmission']
        
        # Start with year, make, model filter
        vehicles = Vehicle.objects.filter(
            year=year,
            make__name__iexact=make_name,
            model__name__iexact=model_name
        ).select_related('make', 'model', 'trim', 'engine')
        
        # Try to match trim
        if body_trim and body_trim != '-':
            # Split body_trim by comma to handle multiple trims
            trim_parts = [t.strip() for t in body_trim.split(',')]
            trim_filter = models.Q()
            
            for trim_part in trim_parts:
                trim_filter |= models.Q(trim__name__icontains=trim_part)
            
            vehicles_with_trim = vehicles.filter(trim_filter)
            if vehicles_with_trim.exists():
                vehicles = vehicles_with_trim
        
        # Try to match engine
        if engine_trans and engine_trans != '-':
            # Extract displacement from engine string (e.g., "3.2L V6 - Gas")
            engine_displacement_match = re.search(r'(\d+\.\d+)L', engine_trans)
            if engine_displacement_match:
                displacement = float(engine_displacement_match.group(1))
                vehicles_with_engine = vehicles.filter(engine__displacement=displacement)
                if vehicles_with_engine.exists():
                    vehicles = vehicles_with_engine
            else:
                # Try partial name matching
                vehicles_with_engine = vehicles.filter(
                    engine__name__icontains=engine_trans.split('-')[0].strip()
                )
                if vehicles_with_engine.exists():
                    vehicles = vehicles_with_engine
        
        return list(vehicles)

    def _create_fitments_for_entry(self, part, fitment_entry, dry_run=False):
        """Create fitments for a single entry, finding or creating vehicles as needed"""
        if dry_run:
            return 0
        
        # First try to find existing vehicles
        matching_vehicles = self._find_matching_vehicles(fitment_entry)
        
        if matching_vehicles:
            # Use existing vehicles
            created_count = 0
            for vehicle in matching_vehicles:
                fitment, created = Fitment.objects.get_or_create(
                    part=part,
                    vehicle=vehicle
                )
                if created:
                    created_count += 1
            return created_count
        else:
            # Create new vehicle data
            year = fitment_entry['Year']
            make_name = fitment_entry['Make']
            model_name = fitment_entry['Model']
            body_trim = fitment_entry['Body & Trim']
            engine_trans = fitment_entry['Engine & Transmission']
            
            # Get or create make
            make, _ = Make.objects.get_or_create(
                name=make_name,
                defaults={'country': 'Japan' if make_name == 'Acura' else ''}
            )
            
            # Get or create model
            model, _ = Model.objects.get_or_create(
                make=make,
                name=model_name
            )
            
            # Handle trim (parse multiple trims)
            trims_to_create = []
            if body_trim and body_trim != '-':
                trim_parts = [t.strip() for t in body_trim.split(',')]
                for trim_part in trim_parts:
                    if trim_part:
                        trim, _ = Trim.objects.get_or_create(name=trim_part)
                        trims_to_create.append(trim)
            
            # If no specific trims, use None
            if not trims_to_create:
                trims_to_create = [None]
            
            # Handle engine
            engine = None
            if engine_trans and engine_trans != '-':
                # Parse engine details
                engine_name = engine_trans.strip()
                displacement = None
                cylinders = None
                fuel_type = 'GAS'  # Default
                
                # Extract displacement
                displacement_match = re.search(r'(\d+\.\d+)L', engine_trans)
                if displacement_match:
                    displacement = float(displacement_match.group(1))
                
                # Extract cylinder count
                cylinder_match = re.search(r'V(\d+)', engine_trans)
                if cylinder_match:
                    cylinders = int(cylinder_match.group(1))
                
                # Determine fuel type
                if 'Gas' in engine_trans:
                    fuel_type = 'GAS'
                elif 'Diesel' in engine_trans:
                    fuel_type = 'DSL'
                elif 'Hybrid' in engine_trans:
                    fuel_type = 'HYB'
                
                engine, _ = Engine.objects.get_or_create(
                    name=engine_name,
                    defaults={
                        'displacement': displacement,
                        'cylinders': cylinders,
                        'fuel_type': fuel_type
                    }
                )
            
            # Create vehicles for each trim combination
            created_count = 0
            for trim in trims_to_create:
                vehicle, created = Vehicle.objects.get_or_create(
                    year=year,
                    make=make,
                    model=model,
                    trim=trim,
                    engine=engine
                )
                
                # Create fitment
                fitment, fitment_created = Fitment.objects.get_or_create(
                    part=part,
                    vehicle=vehicle
                )
                
                if fitment_created:
                    created_count += 1
            
            return created_count
