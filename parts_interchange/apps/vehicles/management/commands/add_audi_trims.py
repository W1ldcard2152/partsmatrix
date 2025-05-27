# This goes in: parts_interchange/apps/vehicles/management/commands/add_audi_trims.py

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.vehicles.models import Trim


class Command(BaseCommand):
    help = 'Add Audi trim levels organized by model and generation'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without making changes'
        )
        parser.add_argument(
            '--include-discontinued',
            action='store_true',
            default=True,
            help='Include discontinued model trims (default: True)'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        include_discontinued = options['include_discontinued']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No data will be saved'))
        
        # Audi trim levels organized by model hierarchy and performance tiers
        audi_trims = [
            # Base Trim Levels (Entry to Mid-Luxury)
            {
                'name': 'Premium',
                'description': 'Base luxury trim with standard Audi features',
                'models': 'A3, A4, A5, Q3, Q5',
                'price_tier': 'Entry-Luxury'
            },
            {
                'name': 'Premium Plus',
                'description': 'Mid-level trim with enhanced technology and comfort features',
                'models': 'A3, A4, A5, A6, Q3, Q5, Q7',
                'price_tier': 'Mid-Luxury'
            },
            {
                'name': 'Prestige',
                'description': 'Top-tier luxury trim with all premium amenities',
                'models': 'A3, A4, A5, A6, A7, A8, Q3, Q5, Q7, Q8',
                'price_tier': 'High-Luxury'
            },
            
            # Audi Power/Engine Designations (TFSI System)
            {
                'name': '30 TFSI',
                'description': '1.4L turbo engine designation',
                'models': 'A3 (current)',
                'price_tier': 'Base-Engine'
            },
            {
                'name': '35 TFSI',
                'description': '2.0L turbo base engine designation',
                'models': 'A3, A4, A5, Q3, Q5',
                'price_tier': 'Volume-Engine'
            },
            {
                'name': '40 TFSI',
                'description': '2.0L turbo higher output engine designation',
                'models': 'A4, A5, A6, Q5',
                'price_tier': 'Mid-Engine'
            },
            {
                'name': '45 TFSI',
                'description': '2.0L turbo high output or mild hybrid designation',
                'models': 'A4, A5, A6, A7, Q5, Q7, Q8',
                'price_tier': 'Performance-Engine'
            },
            {
                'name': '50 TFSI',
                'description': '3.0L V6 turbo engine designation',
                'models': 'A6, A7, A8, Q7, Q8',
                'price_tier': 'Premium-Engine'
            },
            {
                'name': '55 TFSI',
                'description': '3.0L V6 turbo high output engine designation',
                'models': 'A6, A7, A8, Q7, Q8',
                'price_tier': 'High-Performance-Engine'
            },
            {
                'name': '60 TFSI',
                'description': '4.0L V8 twin-turbo engine designation',
                'models': 'A8, S6, S7, S8',
                'price_tier': 'Ultra-Performance-Engine'
            },
            
            # S-Line Performance Trims
            {
                'name': 'S line',
                'description': 'Sport appearance package with aggressive styling',
                'models': 'A3, A4, A5, A6, A7, Q3, Q5, Q7, Q8',
                'price_tier': 'Sport-Appearance'
            },
            # The following S, RS, TT, R8, and some e-tron models were previously listed as trims but are now models.
            # They have been removed from this file and added to add_audi_models.py and create_audi_vehicles.py.
            
            # Hybrid Trims (TFSI e)
            {
                'name': '50 TFSI e',
                'description': 'Plug-in hybrid with 2.0L turbo + electric motor',
                'models': 'A6, A7, A8, Q5',
                'price_tier': 'Hybrid-Premium'
            },
            {
                'name': '55 TFSI e',
                'description': 'Plug-in hybrid with 3.0L V6 turbo + electric motor',
                'models': 'A8',
                'price_tier': 'Hybrid-Luxury'
            },
            {
                'name': '60 TFSI e',
                'description': 'High-performance plug-in hybrid system',
                'models': 'A8',
                'price_tier': 'Hybrid-Performance'
            },
            
            # Historical/Discontinued Trims
            {
                'name': '1.8T',
                'description': 'Original 1.8L turbo engine designation',
                'models': 'A3 8L, A4 B6, TT 8N (2000-2008)',
                'price_tier': 'Historical-Turbo'
            },
            {
                'name': '1.8T quattro',
                'description': 'Original 1.8L turbo with all-wheel drive',
                'models': 'A3 8L, A4 B6, TT 8N (2000-2008)',
                'price_tier': 'Historical-Turbo-AWD'
            },
            {
                'name': '2.0T',
                'description': '2.0L turbo engine designation (pre-TFSI numbering)',
                'models': 'A3 8P, A4 B7 (2006-2012)',
                'price_tier': 'Historical-Turbo'
            },
            {
                'name': '2.0T quattro',
                'description': '2.0L turbo with all-wheel drive (pre-TFSI numbering)',
                'models': 'A4 B6, B7 (2002-2008)',
                'price_tier': 'Historical-Turbo-AWD'
            },
            {
                'name': '3.2 quattro',
                'description': '3.2L V6 with all-wheel drive',
                'models': 'A3 8P, A4 B7, TT 8J (2006-2012)',
                'price_tier': 'Historical-V6'
            },
            {
                'name': 'FSI',
                'description': 'Direct injection naturally aspirated engines',
                'models': 'Various models (2006-2010)',
                'price_tier': 'Historical-NA'
            },
            {
                'name': 'TDI',
                'description': 'Turbo diesel engine variants',
                'models': 'A3, A4, A6, A8, Q5, Q7 (2009-2015)',
                'price_tier': 'Historical-Diesel'
            },
            {
                'name': 'TDI Clean Diesel',
                'description': 'Advanced diesel with emissions technology',
                'models': 'A3, A6, A7, A8, Q5, Q7 (2014-2015)',
                'price_tier': 'Historical-Clean-Diesel'
            },
            
            # Special Editions and Packages
            {
                'name': 'Competition',
                'description': 'Limited edition with enhanced performance and styling',
                'models': 'RS models',
                'price_tier': 'Special-Edition'
            },
            {
                'name': 'Performance',
                'description': 'Higher output variant of existing performance models',
                'models': 'RS3, RS6, RS7, R8',
                'price_tier': 'Ultimate-Special-Edition'
            },
            {
                'name': 'Black Edition',
                'description': 'Appearance package with black exterior accents',
                'models': 'Various models',
                'price_tier': 'Appearance-Package'
            },
            {
                'name': 'Optic Package',
                'description': 'Styling package with unique design elements',
                'models': 'S and RS models',
                'price_tier': 'Styling-Package'
            },
            
            # Quattro All-Wheel Drive Designations
            {
                'name': 'quattro',
                'description': 'Audi all-wheel drive system',
                'models': 'Most Audi models (when available)',
                'price_tier': 'AWD-System'
            },
            {
                'name': 'ultra quattro',
                'description': 'Efficient on-demand all-wheel drive system',
                'models': 'Select models with fuel efficiency focus',
                'price_tier': 'Efficient-AWD'
            },
            {
                'name': 'sport quattro',
                'description': 'Performance-tuned all-wheel drive system',
                'models': 'S and RS models',
                'price_tier': 'Performance-AWD'
            },
            
            # Body Style Variations
            {
                'name': 'Sedan',
                'description': 'Four-door sedan body style',
                'models': 'A3, A4, A6, A8, S3, S4, S6, S8',
                'price_tier': 'Body-Style'
            },
            {
                'name': 'Avant',
                'description': 'Wagon body style (estate)',
                'models': 'A4, A6, RS4, RS6',
                'price_tier': 'Wagon-Body-Style'
            },
            {
                'name': 'Sportback',
                'description': 'Five-door hatchback/liftback body style',
                'models': 'A5, A7, S5, S7, RS5, RS7',
                'price_tier': 'Sportback-Body-Style'
            },
            {
                'name': 'Coupe',
                'description': 'Two-door coupe body style',
                'models': 'A5, S5, RS5, TT, R8',
                'price_tier': 'Coupe-Body-Style'
            },
            {
                'name': 'Convertible',
                'description': 'Soft-top or hard-top convertible',
                'models': 'A3, A5, S5, RS5, TT, R8',
                'price_tier': 'Convertible-Body-Style'
            },
            {
                'name': 'Cabriolet',
                'description': 'Audi terminology for convertible',
                'models': 'A3, A5, S5, RS5, TT',
                'price_tier': 'Cabriolet-Body-Style'
            },
            {
                'name': 'Roadster',
                'description': 'Two-seat convertible sports car',
                'models': 'TT, R8',
                'price_tier': 'Roadster-Body-Style'
            }
        ]
        
        # Filter out discontinued model trims if not requested
        if not include_discontinued:
            discontinued_indicators = ['Historical', 'TDI', 'R8 V8', 'TT RS', 'Clean Diesel']
            audi_trims = [
                trim for trim in audi_trims 
                if not any(disc_indicator in trim['description'] or disc_indicator in trim['name'] 
                          for disc_indicator in discontinued_indicators)
            ]
            self.stdout.write('Filtering to active model trims only')
        
        self.stdout.write(f'Processing {len(audi_trims)} Audi trim levels...')
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for trim_data in audi_trims:
            trim_name = trim_data['name']
            description = trim_data['description']
            
            if not dry_run:
                # Check if trim already exists
                existing_trims = Trim.objects.filter(name=trim_name)
                
                if existing_trims.exists():
                    # Update description if different
                    trim_obj = existing_trims.first()
                    if trim_obj.description != description:
                        trim_obj.description = description
                        trim_obj.save()
                        updated_count += 1
                        status = '↻ UPDATED'
                    else:
                        skipped_count += 1
                        status = '- EXISTS'
                else:
                    # Create new trim
                    Trim.objects.create(
                        name=trim_name,
                        description=description
                    )
                    created_count += 1
                    status = '✓ CREATED'
            else:
                status = '? DRY RUN'
            
            # Display trim info
            self.stdout.write(f'{status} {trim_name}')
            self.stdout.write(f'    {description}')
            self.stdout.write(f'    Used on: {trim_data["models"]} | Tier: {trim_data["price_tier"]}')
            self.stdout.write('')  # Blank line
        
        # Summary
        self.stdout.write('=' * 60)
        self.stdout.write('AUDI TRIMS SUMMARY')
        self.stdout.write('=' * 60)
        
        if not dry_run:
            self.stdout.write(f'✓ Created: {created_count} trim levels')
            self.stdout.write(f'↻ Updated: {updated_count} trim levels')
            self.stdout.write(f'- Existed: {skipped_count} trim levels')
            self.stdout.write(f'📊 Total: {created_count + updated_count + skipped_count} trims processed')
        else:
            self.stdout.write(f'📊 Would process: {len(audi_trims)} trim levels')
        
        # Trim hierarchy insights
        self.stdout.write('\\n🔍 TRIM HIERARCHY INSIGHTS:')
        self.stdout.write('Audi Luxury Tiers: Premium → Premium Plus → Prestige')
        self.stdout.write('Engine Designations: 30/35/40/45/50/55/60 TFSI (power levels)')
        self.stdout.write('Performance Hierarchy: Base → S line')
        
        self.stdout.write('\\nKey Audi Trim Patterns:')
        self.stdout.write('• TFSI Numbers: Power/engine displacement coding system')
        self.stdout.write('• S Models: Sport performance (now separate models)')
        self.stdout.write('• RS Models: Racing sport, ultimate performance (now separate models)')
        self.stdout.write('• quattro: All-wheel drive technology standard on most')
        
        # Model-specific notes
        self.stdout.write('\\nModel-Specific Trim Notes:')
        self.stdout.write('• A3: Premium/Premium Plus/Prestige')
        self.stdout.write('• A4: Premium/Premium Plus/Prestige')
        self.stdout.write('• A6/A7: Premium Plus/Prestige')
        self.stdout.write('• Q-Series: Premium/Premium Plus/Prestige')
        self.stdout.write('• TT: Premium/Premium Plus/Prestige (now a model)')
        self.stdout.write('• R8: Premium/Premium Plus/Prestige (now a model)')
        
        # Electric transition notes
        self.stdout.write('\\nElectric Transition:')
        self.stdout.write('• Traditional TFSI → TFSI e (plug-in hybrid) → e-tron (full electric)')
        self.stdout.write('• e-tron naming: 50 (base) → 55 (premium)')
        self.stdout.write('• Future: All models transitioning to electric by 2033')
        
        # Next steps
        self.stdout.write('\\n📋 NEXT STEPS:')
        self.stdout.write('1. Create Vehicle records: python manage.py create_audi_vehicles')
        self.stdout.write('2. Add Part categories: python manage.py add_part_categories')
        self.stdout.write('3. Import NHTSA data: python manage.py import_nhtsa_vehicles --makes Audi')
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'\\n🎉 Successfully processed {len(audi_trims)} Audi trim levels!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('\\n⚠️  DRY RUN complete - run without --dry-run to save changes')
            )
