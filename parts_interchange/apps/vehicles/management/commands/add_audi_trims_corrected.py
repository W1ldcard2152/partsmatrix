# This goes in: parts_interchange/apps/vehicles/management/commands/add_audi_trims_corrected.py

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.vehicles.models import Trim


class Command(BaseCommand):
    help = 'Add Audi trim levels - CORRECTED to remove S/RS models since they are now separate models'

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
        
        # CORRECTED Audi trim levels - S/RS models are now separate models, not trims
        # Performance models like S4, S5, RS7, SQ5, etc. are their own models
        audi_trims = [
            # Base Luxury Trim Levels (Used by A, S, and RS models)
            {
                'name': 'Premium',
                'description': 'Base luxury trim with standard Audi features',
                'models': 'A3, A4, A5, A6, A7, A8, Q3, Q5, Q7, Q8, S3, S4, S5, S6, S7, S8, SQ5, SQ7, SQ8',
                'price_tier': 'Entry-Luxury'
            },
            {
                'name': 'Premium Plus',
                'description': 'Mid-level trim with enhanced technology and comfort features',
                'models': 'A3, A4, A5, A6, A7, A8, Q3, Q5, Q7, Q8, S3, S4, S5, S6, S7, S8, SQ5, SQ7, SQ8',
                'price_tier': 'Mid-Luxury'
            },
            {
                'name': 'Prestige',
                'description': 'Top-tier luxury trim with all premium amenities',
                'models': 'A3, A4, A5, A6, A7, A8, Q3, Q5, Q7, Q8, S3, S4, S5, S6, S7, S8, SQ5, SQ7, SQ8',
                'price_tier': 'High-Luxury'
            },
            
            # Engine Power Designations (TFSI System) - Apply to base A models
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
            
            # S-Line Appearance Package (Different from S Models)
            {
                'name': 'S line',
                'description': 'Sport appearance package with aggressive styling (not a performance model)',
                'models': 'A3, A4, A5, A6, A7, Q3, Q5, Q7, Q8',
                'price_tier': 'Sport-Appearance'
            },
            
            # TT Specific Trims (TT is model, these are trims within TT)
            {
                'name': 'Base',
                'description': 'Base trim level for TT sports car',
                'models': 'TT Coupe/Roadster',
                'price_tier': 'Sports-Car-Base'
            },
            {
                'name': 'Sport',
                'description': 'Sport trim for TT with enhanced features',
                'models': 'TT Coupe/Roadster',
                'price_tier': 'Sports-Car-Sport'
            },
            {
                'name': 'Competition',
                'description': 'Competition trim for TT with track-focused features',
                'models': 'TT Coupe/Roadster',
                'price_tier': 'Sports-Car-Competition'
            },
            
            # R8 Specific Trims (R8 is model, these are engine/performance trims)
            {
                'name': 'V8',
                'description': 'R8 with 4.2L V8 engine',
                'models': 'R8 Gen 1',
                'price_tier': 'Supercar-V8'
            },
            {
                'name': 'V10',
                'description': 'R8 with 5.2L V10 engine',
                'models': 'R8 Gen 1/2',
                'price_tier': 'Supercar-V10'
            },
            {
                'name': 'V10 Plus',
                'description': 'High-performance R8 with track-focused setup',
                'models': 'R8 Gen 1/2',
                'price_tier': 'Track-Supercar'
            },
            {
                'name': 'Decennium',
                'description': 'Limited edition R8 celebrating 10 years',
                'models': 'R8 Gen 2',
                'price_tier': 'Limited-Edition'
            },
            {
                'name': 'Performance',
                'description': 'Ultimate R8 trim with maximum power and aero',
                'models': 'R8 Gen 2',
                'price_tier': 'Ultimate-Supercar'
            },
            
            # e-tron Electric Trims (e-tron models get these trim designations)
            {
                'name': '50',
                'description': 'Base electric powertrain with single or dual motor',
                'models': 'e-tron SUV, Q4 e-tron',
                'price_tier': 'Electric-Base'
            },
            {
                'name': '55',
                'description': 'Premium electric powertrain with dual motors',
                'models': 'e-tron SUV',
                'price_tier': 'Electric-Premium'
            },
            {
                'name': 'S',
                'description': 'Performance electric powertrain with triple motors',
                'models': 'e-tron SUV (this is exception - e-tron S is trim, not separate model)',
                'price_tier': 'Electric-Performance'
            },
            
            # Hybrid Trims (TFSI e designation)
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
            
            # Historical/Legacy Trim Designations (Pre-2018)
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
                'name': 'Dynamic',
                'description': 'Dynamic package with sport-tuned features',
                'models': 'S and RS models',
                'price_tier': 'Performance-Package'
            },
            {
                'name': 'Black Edition',
                'description': 'Appearance package with black exterior accents',
                'models': 'Various models',
                'price_tier': 'Appearance-Package'
            },
            {
                'name': 'Carbon Black',
                'description': 'Carbon fiber and black accent package',
                'models': 'S and RS models',
                'price_tier': 'Carbon-Package'
            },
            {
                'name': 'Optic Package',
                'description': 'Styling package with unique design elements',
                'models': 'S and RS models',
                'price_tier': 'Styling-Package'
            },
            
            # Quattro All-Wheel Drive System Designations
            {
                'name': 'quattro',
                'description': 'Audi all-wheel drive system (most common)',
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
            
            # Body Style Designations (When Applicable)
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
            discontinued_indicators = ['Historical', 'TDI', 'R8 V8', 'Clean Diesel']
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
        self.stdout.write('CORRECTED AUDI TRIMS SUMMARY')
        self.stdout.write('=' * 60)
        
        if not dry_run:
            self.stdout.write(f'✓ Created: {created_count} trim levels')
            self.stdout.write(f'↻ Updated: {updated_count} trim levels')
            self.stdout.write(f'- Existed: {skipped_count} trim levels')
            self.stdout.write(f'📊 Total: {created_count + updated_count + skipped_count} trims processed')
        else:
            self.stdout.write(f'📊 Would process: {len(audi_trims)} trim levels')
        
        # Corrected hierarchy insights
        self.stdout.write('\\n🔍 CORRECTED TRIM HIERARCHY:')
        self.stdout.write('🔧 IMPORTANT: S and RS variants are now separate MODELS, not trims!')
        self.stdout.write('')
        self.stdout.write('Model Structure:')
        self.stdout.write('• A4 (model) → Premium/Premium Plus/Prestige (trims)')
        self.stdout.write('• S4 (separate model) → Premium/Premium Plus/Prestige (trims)')  
        self.stdout.write('• RS4 (separate model) → Premium/Premium Plus/Prestige (trims)')
        self.stdout.write('')
        self.stdout.write('Trim Levels Used Across All Models:')
        self.stdout.write('• Premium: Base luxury features')
        self.stdout.write('• Premium Plus: Enhanced technology and comfort')
        self.stdout.write('• Prestige: Top-tier with all amenities')
        self.stdout.write('')
        self.stdout.write('Engine Designations (A models):')
        self.stdout.write('• 30/35/40/45/50/55/60 TFSI: Power level indicators')
        self.stdout.write('')
        self.stdout.write('Special Packages:')
        self.stdout.write('• S line: Appearance package (not performance model)')
        self.stdout.write('• quattro: All-wheel drive system')
        self.stdout.write('• Competition/Dynamic: Performance packages')
        
        # Next steps
        self.stdout.write('\\n📋 NEXT STEPS:')
        self.stdout.write('1. IMPORTANT: Update existing Vehicle records if needed')
        self.stdout.write('2. Use create_audi_vehicles_corrected.py to create proper structure')
        self.stdout.write('3. S4, RS7, SQ5 etc are now separate models with their own trims')
        self.stdout.write('4. Each performance model gets Premium/Premium Plus/Prestige options')
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'\\n🎉 Successfully processed {len(audi_trims)} CORRECTED Audi trim levels!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('\\n⚠️  DRY RUN complete - run without --dry-run to save changes')
            )
