import re
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.parts.models import Part, PartCategory, Manufacturer
from apps.vehicles.models import Make, Model, Trim, Engine, Vehicle
from apps.fitments.models import Fitment

class Command(BaseCommand):
    help = 'Imports Acura parts data from raw text.'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the text file containing raw part data.')

    def handle(self, *args, **options):
        file_path = options['file_path']
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_data = f.read()
        except FileNotFoundError:
            raise CommandError(f'File not found at {file_path}')
        except Exception as e:
            raise CommandError(f'Error reading file {file_path}: {e}')
        
        # Define a mapping for part names to categories
        part_category_map = {
            "AC Line": "HVAC/Climate Control -> AC Lines & Hoses",
            # Add more mappings as needed
        }

        try:
            part_name, part_number = self._parse_part_name_and_number(raw_data)
            fitment_data = self._parse_fitment_data(raw_data)

            self.stdout.write(self.style.SUCCESS(f"Parsed Part Name: {part_name}"))
            self.stdout.write(self.style.SUCCESS(f"Parsed Part Number: {part_number}"))
            self.stdout.write(self.style.SUCCESS(f"Parsed Fitment Data: {fitment_data}"))

            with transaction.atomic():
                # Get or create Manufacturer (Acura)
                manufacturer, _ = Manufacturer.objects.get_or_create(name="Acura")

                # Get or create PartCategory (handling hierarchical structure)
                category_path_str = part_category_map.get(part_name, "Uncategorized")
                category_names = [name.strip() for name in category_path_str.split('->')]
                
                parent_category = None
                for name in category_names:
                    part_category, _ = PartCategory.objects.get_or_create(
                        name=name,
                        parent_category=parent_category
                    )
                    parent_category = part_category

                # Get or create Part
                part, created = Part.objects.get_or_create(
                    part_number=part_number,
                    defaults={
                        'name': part_name,
                        'manufacturer': manufacturer,
                        'category': part_category,
                    }
                )
                if not created:
                    self.stdout.write(self.style.WARNING(f"Part with number {part_number} already exists. Updating existing part."))
                    part.name = part_name
                    part.manufacturer = manufacturer
                    part.category = part_category
                    part.save()

                # Process Fitment Data
                for fitment_entry in fitment_data:
                    year = fitment_entry['Year']
                    make_name = fitment_entry['Make']
                    model_name = fitment_entry['Model']
                    trim_name = fitment_entry['Body & Trim']
                    engine_name = fitment_entry['Engine & Transmission']

                    make, _ = Make.objects.get_or_create(name=make_name)
                    model, _ = Model.objects.get_or_create(name=model_name, make=make)
                    trim, _ = Trim.objects.get_or_create(name=trim_name) # Trim does not have a 'model' field
                    engine, _ = Engine.objects.get_or_create(name=engine_name)

                    vehicle, _ = Vehicle.objects.get_or_create(
                        year=year,
                        make=make,
                        model=model,
                        trim=trim,
                        engine=engine
                    )

                    Fitment.objects.get_or_create(
                        part=part,
                        vehicle=vehicle
                    )
                    self.stdout.write(self.style.SUCCESS(f"Added fitment for {part_number} to {year} {make_name} {model_name} {trim_name} {engine_name}"))

            self.stdout.write(self.style.SUCCESS(f'Successfully imported part {part_name} ({part_number}) and its fitments.'))

        except Exception as e:
            raise CommandError(f'Error importing parts: {e}')

    def _parse_part_name_and_number(self, raw_data):
        # Regex to find "Part Name - Make (Part Number)"
        match = re.search(r'^(.*?)\s*-\s*Acura\s*\((.*?)\)', raw_data, re.MULTILINE)
        if match:
            part_name = match.group(1).strip()
            part_number = match.group(2).strip()
            return part_name, part_number
        raise ValueError("Could not parse Part Name and Part Number from raw data.")

    def _parse_fitment_data(self, raw_data):
        fitment_data = []
        # Find the "Vehicle Fitment" table
        fitment_table_match = re.search(r'Vehicle Fitment\s*Year\s*Make\s*Model\s*Body & Trim\s*Engine & Transmission\s*(.*?)(?=\n\n|\Z)', raw_data, re.DOTALL)
        
        if fitment_table_match:
            table_content = fitment_table_match.group(1).strip()
            # Split by lines to process each row
            lines = table_content.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Regex to parse each line of the table
                # This regex is more robust for varying whitespace
                row_match = re.match(r'(\d{4})\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*)', line)
                if row_match:
                    fitment_data.append({
                        'Year': int(row_match.group(1).strip()),
                        'Make': row_match.group(2).strip(),
                        'Model': row_match.group(3).strip(),
                        'Body & Trim': row_match.group(4).strip(),
                        'Engine & Transmission': row_match.group(5).strip(),
                    })
        return fitment_data
