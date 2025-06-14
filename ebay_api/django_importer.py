"""
eBay to Django Integration Script
Imports eBay parts data into the Parts Matrix Django database
"""

import os
import sys
import json
import django
from typing import List, Dict, Optional
from datetime import datetime

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parts_interchange.settings')
django.setup()

# Import Django models
from django.db import transaction
from apps.parts.models import Part, Manufacturer, PartCategory
from apps.vehicles.models import Vehicle, Make, Model, Engine, Trim
from apps.fitments.models import Fitment


class EbayDjangoImporter:
    """Import eBay parts data into Django database"""
    
    def __init__(self):
        self.created_parts = 0
        self.updated_parts = 0
        self.created_fitments = 0
        self.skipped_parts = 0
        self.errors = []
        
        # Default category for AC compressors
        self.default_category, _ = PartCategory.objects.get_or_create(
            name='HVAC & Climate Control',
            defaults={'description': 'Heating, Ventilation, and Air Conditioning components'}
        )
    
    def get_or_create_manufacturer(self, manufacturer_name: str) -> Optional[Manufacturer]:
        """Get or create manufacturer object"""
        if not manufacturer_name:
            return None
        
        try:
            manufacturer, created = Manufacturer.objects.get_or_create(
                name=manufacturer_name,
                defaults={
                    'abbreviation': manufacturer_name[:4].upper(),
                    'country': ''
                }
            )
            return manufacturer
        except Exception as e:
            self.errors.append(f"Error creating manufacturer {manufacturer_name}: {e}")
            return None
    
    def find_or_create_vehicle(self, fitment_data: Dict) -> Optional[Vehicle]:
        """Find existing vehicle or create if needed"""
        try:
            year = fitment_data.get('year')
            make_name = fitment_data.get('make')
            model_name = fitment_data.get('model')
            trim_name = fitment_data.get('trim', 'Base')
            engine_name = fitment_data.get('engine', '')
            
            if not all([year, make_name, model_name]):
                return None
            
            # Try to find existing vehicle
            vehicles = Vehicle.objects.filter(
                year=year,
                make__name__iexact=make_name,
                model__name__iexact=model_name,
                trim__name__iexact=trim_name
            )
            
            if vehicles.exists():
                return vehicles.first()
            
            # Vehicle doesn't exist - we won't create new vehicles automatically
            # This is to maintain data integrity with existing vehicle database
            return None
            
        except Exception as e:
            self.errors.append(f"Error finding vehicle {fitment_data}: {e}")
            return None
    
    def import_ebay_part(self, ebay_part_data: Dict) -> bool:
        """Import a single eBay part into the database"""
        try:
            # Extract required fields
            part_name = ebay_part_data.get('part_name')
            part_number = ebay_part_data.get('part_number')
            manufacturer_name = ebay_part_data.get('manufacturer')
            
            # Skip if missing critical data
            if not part_name or not part_number:
                self.skipped_parts += 1
                return False
            
            # Get or create manufacturer
            manufacturer = self.get_or_create_manufacturer(manufacturer_name)
            if not manufacturer:
                # Create a generic "eBay" manufacturer for unknown parts
                manufacturer, _ = Manufacturer.objects.get_or_create(
                    name='Unknown',
                    defaults={'abbreviation': 'UNK', 'country': ''}
                )
            
            # Create part number that includes eBay source
            ebay_part_number = f"EBAY-{ebay_part_data.get('ebay_item_id', '')}-{part_number}"
            
            # Check if part already exists
            existing_part = Part.objects.filter(
                manufacturer=manufacturer,
                part_number=ebay_part_number
            ).first()
            
            if existing_part:
                # Update existing part with eBay data
                existing_part.name = part_name
                existing_part.description = f"eBay Import: {ebay_part_data.get('title', '')[:200]}\n\nOriginal Part Number: {part_number}\nCondition: {ebay_part_data.get('condition', '')}\nPrice: ${ebay_part_data.get('price', 0):.2f}\nSeller: {ebay_part_data.get('seller_username', '')}\neBay URL: {ebay_part_data.get('item_url', '')}"
                existing_part.save()
                self.updated_parts += 1
                part = existing_part
            else:
                # Create new part
                part = Part.objects.create(
                    manufacturer=manufacturer,
                    part_number=ebay_part_number,
                    name=part_name,
                    category=self.default_category,
                    description=f"eBay Import: {ebay_part_data.get('title', '')[:200]}\n\nOriginal Part Number: {part_number}\nCondition: {ebay_part_data.get('condition', '')}\nPrice: ${ebay_part_data.get('price', 0):.2f}\nSeller: {ebay_part_data.get('seller_username', '')}\neBay URL: {ebay_part_data.get('item_url', '')}",
                    is_active=True
                )
                self.created_parts += 1
            
            # Create fitments for vehicles that exist in the database
            fitments_data = ebay_part_data.get('fitments', [])
            for fitment_data in fitments_data:
                vehicle = self.find_or_create_vehicle(fitment_data)
                if vehicle:
                    fitment, created = Fitment.objects.get_or_create(
                        part=part,
                        vehicle=vehicle,
                        defaults={
                            'is_verified': False,
                            'created_by': 'ebay_importer'
                        }
                    )
                    if created:
                        self.created_fitments += 1
            
            return True
            
        except Exception as e:
            self.errors.append(f"Error importing part {ebay_part_data.get('ebay_item_id', 'unknown')}: {e}")
            return False
    
    def import_from_json(self, json_file: str) -> Dict:
        """Import all parts from a JSON file"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                parts_data = json.load(f)
            
            print(f"Starting import of {len(parts_data)} parts from {json_file}")
            print("-" * 60)
            
            with transaction.atomic():
                for i, part_data in enumerate(parts_data, 1):
                    if i % 10 == 0:
                        print(f"Processing part {i}/{len(parts_data)}...")
                    
                    self.import_ebay_part(part_data)
            
            # Return summary
            summary = {
                'total_processed': len(parts_data),
                'created_parts': self.created_parts,
                'updated_parts': self.updated_parts,
                'created_fitments': self.created_fitments,
                'skipped_parts': self.skipped_parts,
                'errors': len(self.errors)
            }
            
            return summary
            
        except Exception as e:
            self.errors.append(f"Error reading file {json_file}: {e}")
            return {'error': str(e)}
    
    def print_summary(self, summary: Dict):
        """Print import summary"""
        print("\nImport Summary:")
        print("=" * 40)
        print(f"Total processed: {summary.get('total_processed', 0)}")
        print(f"Parts created: {summary.get('created_parts', 0)}")
        print(f"Parts updated: {summary.get('updated_parts', 0)}")
        print(f"Fitments created: {summary.get('created_fitments', 0)}")
        print(f"Parts skipped: {summary.get('skipped_parts', 0)}")
        print(f"Errors: {summary.get('errors', 0)}")
        
        if self.errors:
            print("\nError Details:")
            for error in self.errors[:10]:  # Show first 10 errors
                print(f"  - {error}")
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more errors")


def find_ebay_data_files():
    """Find eBay JSON data files in current directory"""
    files = [f for f in os.listdir('.') if f.startswith('ebay_acura_ac_parts_') and f.endswith('.json')]
    return sorted(files)


def main():
    """Main function to run the importer"""
    print("eBay to Django Database Importer")
    print("================================")
    
    # Check if we're in the right directory
    if not os.path.exists('ebay_parts_extractor.py'):
        print("Error: Please run this script from the ebay_api directory")
        return
    
    # Find data files
    data_files = find_ebay_data_files()
    
    if not data_files:
        print("No eBay data files found.")
        print("Please run the eBay extractor first to generate data files.")
        return
    
    print(f"\nFound {len(data_files)} data files:")
    for i, filename in enumerate(data_files, 1):
        file_size = os.path.getsize(filename) / 1024  # KB
        print(f"  {i}. {filename} ({file_size:.1f} KB)")
    
    # Let user choose file
    if len(data_files) == 1:
        selected_file = data_files[0]
        print(f"\nUsing: {selected_file}")
    else:
        print(f"\nSelect file (1-{len(data_files)}) or press Enter for most recent:")
        choice = input("> ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= len(data_files):
            selected_file = data_files[int(choice) - 1]
        else:
            selected_file = data_files[-1]  # Most recent
        
        print(f"Using: {selected_file}")
    
    # Confirm import
    print("\n" + "="*60)
    print("WARNING: This will import eBay data into your Django database.")
    print("Parts will be created with 'EBAY-' prefixed part numbers.")
    print("Only fitments for existing vehicles will be created.")
    print("\nProceed with import? (y/n): ")
    
    confirm = input("> ").lower()
    if confirm not in ['y', 'yes']:
        print("Import cancelled.")
        return
    
    # Run the import
    importer = EbayDjangoImporter()
    summary = importer.import_from_json(selected_file)
    
    # Print results
    if 'error' in summary:
        print(f"\nImport failed: {summary['error']}")
    else:
        importer.print_summary(summary)
    
    print("\nImport complete!")


if __name__ == "__main__":
    main()
