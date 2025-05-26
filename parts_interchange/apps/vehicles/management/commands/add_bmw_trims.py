# This goes in: parts_interchange/apps/vehicles/management/commands/add_bmw_trims.py

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.vehicles.models import Trim


class Command(BaseCommand):
    help = 'Add BMW trim levels organized by model and generation'

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
        
        # BMW trim levels organized by model hierarchy and performance tiers
        bmw_trims = [
            # Base Trim Levels (Entry to Mid-Luxury)
            {
                'name': 'Base',
                'description': 'Entry-level BMW with standard luxury features',
                'models': 'All models',
                'price_tier': 'Entry-Luxury'
            },
            {
                'name': 'Premium Package',
                'description': 'Mid-level trim with enhanced comfort and technology',
                'models': '3/4/5/7 Series, X3/X5',
                'price_tier': 'Mid-Luxury'
            },
            {
                'name': 'Luxury Package',
                'description': 'High-end trim with premium materials and features',
                'models': '5/7 Series, X5/X7',
                'price_tier': 'High-Luxury'
            },
            {
                'name': 'Executive Package',
                'description': 'Top-tier luxury with all comfort and tech features',
                'models': '7/8 Series',
                'price_tier': 'Ultra-Luxury'
            },
            
            # 1 Series Designations
            {
                'name': '118i',
                'description': '1.5L turbo 3-cylinder or 2.0L turbo 4-cylinder (FWD/RWD)',
                'models': '1 Series F20, F40, E87',
                'price_tier': 'Entry-Compact'
            },
            {
                'name': '120i',
                'description': '2.0L turbo 4-cylinder (FWD/RWD)',
                'models': '1 Series F20, F40, E87',
                'price_tier': 'Mid-Compact'
            },
            {
                'name': '125i',
                'description': '2.0L turbo 4-cylinder, higher output',
                'models': '1 Series F20, E87',
                'price_tier': 'Performance-Compact'
            },
            {
                'name': '128i',
                'description': '3.0L naturally aspirated I6 (historical)',
                'models': '1 Series E82/E88',
                'price_tier': 'Historical-Compact'
            },
            {
                'name': '135i',
                'description': '3.0L twin-turbo I6 (N54/N55) (historical)',
                'models': '1 Series E82/E88',
                'price_tier': 'Historical-Performance-Compact'
            },
            {
                'name': 'M135i',
                'description': '3.0L turbo 6-cylinder, M Performance tuning',
                'models': '1 Series F20, F40',
                'price_tier': 'M-Performance-Compact'
            },
            {
                'name': 'M140i',
                'description': '3.0L turbo 6-cylinder, M Performance tuning (later F20)',
                'models': '1 Series F20',
                'price_tier': 'M-Performance-Compact'
            },
            {
                'name': '1M Coupe',
                'description': 'Limited production high-performance coupe (historical)',
                'models': '1 Series E82',
                'price_tier': 'M-Division-Special'
            },
            
            # 2 Series Designations
            {
                'name': '218i',
                'description': '1.5L turbo 3-cylinder (FWD/RWD)',
                'models': '2 Series F22, F44, F45, F46',
                'price_tier': 'Entry-Compact'
            },
            {
                'name': '220i',
                'description': '2.0L turbo 4-cylinder',
                'models': '2 Series F22, F44, F45, F46',
                'price_tier': 'Mid-Compact'
            },
            {
                'name': '225i',
                'description': '2.0L turbo 4-cylinder, higher output (FWD)',
                'models': '2 Series F45, F46',
                'price_tier': 'Performance-Compact'
            },
            {
                'name': '225xe',
                'description': '1.5L turbo 3-cylinder plug-in hybrid (FWD)',
                'models': '2 Series F45',
                'price_tier': 'Hybrid-Compact'
            },
            {
                'name': '228i',
                'description': '2.0L turbo 4-cylinder (historical)',
                'models': '2 Series F22/F23',
                'price_tier': 'Historical-Performance-Compact'
            },
            {
                'name': '230i',
                'description': '2.0L turbo 4-cylinder',
                'models': '2 Series F22/F23, G42',
                'price_tier': 'Mid-Performance'
            },
            {
                'name': '235i',
                'description': '3.0L turbo 6-cylinder (historical)',
                'models': '2 Series F22/F23',
                'price_tier': 'Historical-Performance'
            },
            {
                'name': 'M235i',
                'description': '3.0L turbo 6-cylinder, M Performance tuning (historical)',
                'models': '2 Series F22/F23',
                'price_tier': 'M-Performance'
            },
            {
                'name': 'M240i',
                'description': '3.0L turbo 6-cylinder, M Performance tuning',
                'models': '2 Series F22/F23, G42',
                'price_tier': 'M-Performance'
            },
            
            # BMW Model-Specific Numeric Designations
            {
                'name': '320i',
                'description': '2.0L turbo 4-cylinder, rear-wheel drive',
                'models': '3 Series',
                'price_tier': 'Entry-Performance'
            },
            {
                'name': '330i',
                'description': '2.0L turbo 4-cylinder, higher output',
                'models': '3 Series',
                'price_tier': 'Mid-Performance'
            },
            {
                'name': '330e',
                'description': '2.0L turbo 4-cylinder plug-in hybrid',
                'models': '3 Series',
                'price_tier': 'Hybrid-Performance'
            },
            {
                'name': '340i',
                'description': '3.0L turbo 6-cylinder (previous generation)',
                'models': '3 Series F30',
                'price_tier': 'Performance'
            },
            {
                'name': 'M340i',
                'description': '3.0L turbo 6-cylinder, M Performance tuning',
                'models': '3 Series G20',
                'price_tier': 'M-Performance'
            },
            
            # 4 Series Designations
            {
                'name': '430i',
                'description': '2.0L turbo 4-cylinder coupe/convertible',
                'models': '4 Series',
                'price_tier': 'Mid-Performance'
            },
            {
                'name': '440i',
                'description': '3.0L turbo 6-cylinder (previous generation)',
                'models': '4 Series F32',
                'price_tier': 'Performance'
            },
            {
                'name': 'M440i',
                'description': '3.0L turbo 6-cylinder, M Performance tuning',
                'models': '4 Series G22',
                'price_tier': 'M-Performance'
            },
            
            # 5 Series Designations
            {
                'name': '530i',
                'description': '2.0L turbo 4-cylinder luxury sedan',
                'models': '5 Series',
                'price_tier': 'Mid-Luxury'
            },
            {
                'name': '530e',
                'description': '2.0L turbo 4-cylinder plug-in hybrid',
                'models': '5 Series',
                'price_tier': 'Hybrid-Luxury'
            },
            {
                'name': '540i',
                'description': '3.0L turbo 6-cylinder luxury sedan',
                'models': '5 Series',
                'price_tier': 'Performance-Luxury'
            },
            {
                'name': '545e',
                'description': '3.0L turbo 6-cylinder plug-in hybrid',
                'models': '5 Series',
                'price_tier': 'Hybrid-Performance-Luxury'
            },
            {
                'name': '550i',
                'description': '4.4L twin-turbo V8 (previous generation)',
                'models': '5 Series F10',
                'price_tier': 'High-Performance-Luxury'
            },
            
            # 7 Series Designations
            {
                'name': '740i',
                'description': '3.0L turbo 6-cylinder flagship sedan',
                'models': '7 Series',
                'price_tier': 'Luxury-Flagship'
            },
            {
                'name': '745e',
                'description': '3.0L turbo 6-cylinder plug-in hybrid flagship',
                'models': '7 Series',
                'price_tier': 'Hybrid-Flagship'
            },
            {
                'name': '750i',
                'description': '4.4L twin-turbo V8 flagship sedan',
                'models': '7 Series',
                'price_tier': 'Performance-Flagship'
            },
            {
                'name': '760i',
                'description': '6.0L twin-turbo V12 ultimate flagship',
                'models': '7 Series',
                'price_tier': 'Ultimate-Flagship'
            },
            
            # 8 Series Designations
            {
                'name': '840i',
                'description': '3.0L turbo 6-cylinder grand tourer',
                'models': '8 Series',
                'price_tier': 'Grand-Tourer'
            },
            {
                'name': '850i',
                'description': '4.4L twin-turbo V8 grand tourer',
                'models': '8 Series',
                'price_tier': 'Performance-Grand-Tourer'
            },
            
            # X Series SUV Designations
            {
                'name': 'sDrive18i',
                'description': '1.5L turbo 3-cylinder or 2.0L turbo 4-cylinder, RWD',
                'models': 'X1 E84, F48, U11',
                'price_tier': 'Entry-SUV'
            },
            {
                'name': 'sDrive20i',
                'description': '2.0L turbo 4-cylinder, RWD',
                'models': 'X1 E84, F48, U11',
                'price_tier': 'Entry-SUV'
            },
            {
                'name': 'xDrive20i',
                'description': '2.0L turbo 4-cylinder, AWD',
                'models': 'X1 E84, F48, U11',
                'price_tier': 'Mid-SUV'
            },
            {
                'name': 'sDrive28i',
                'description': '2.0L turbo 4-cylinder, rear-wheel drive',
                'models': 'X1 E84, X2 F39',
                'price_tier': 'Entry-SUV'
            },
            {
                'name': 'xDrive28i',
                'description': '2.0L turbo 4-cylinder, all-wheel drive',
                'models': 'X1 E84, F48, X2 F39, X3 E83, F25',
                'price_tier': 'Mid-SUV'
            },
            {
                'name': 'xDrive30i',
                'description': '2.0L turbo 4-cylinder, all-wheel drive',
                'models': 'X3 G01, X4 G02, X5 G05, X6 G06, X7 G07',
                'price_tier': 'Mid-SUV'
            },
            {
                'name': 'xDrive35i',
                'description': '3.0L turbo 6-cylinder (previous generation)',
                'models': 'X3 F25, X5 F15, X6 E71',
                'price_tier': 'Performance-SUV'
            },
            {
                'name': 'M35i',
                'description': '2.0L turbo 4-cylinder, M Performance tuning',
                'models': 'X2 F39, U10',
                'price_tier': 'M-Performance-Compact-SUV'
            },
            {
                'name': 'M40i',
                'description': '3.0L turbo 6-cylinder, M Performance tuning',
                'models': 'X3 G01, X4 G02, X5 F15, X6 F16',
                'price_tier': 'M-Performance-SUV'
            },
            {
                'name': 'xDrive40i',
                'description': '3.0L turbo 6-cylinder, luxury SUV',
                'models': 'X5 G05, X6 G06, X7 G07',
                'price_tier': 'Luxury-SUV'
            },
            {
                'name': 'xDrive50i',
                'description': '4.4L twin-turbo V8, performance SUV',
                'models': 'X5 F15, G05, X6 F16, G06, X7 G07',
                'price_tier': 'Performance-Luxury-SUV'
            },
            {
                'name': 'M50i',
                'description': '4.4L twin-turbo V8, M Performance tuning',
                'models': 'X5 G05, X6 G06, X7 G07',
                'price_tier': 'M-Performance-Luxury-SUV'
            },
            {
                'name': 'M60i',
                'description': '4.4L twin-turbo V8, M Performance tuning (newer)',
                'models': 'X5 G05, X6 G06, X7 G07',
                'price_tier': 'M-Performance-Luxury-SUV'
            },
            {
                'name': 'Alpina XB7',
                'description': 'High-performance variant of X7 by Alpina',
                'models': 'X7 G07',
                'price_tier': 'Ultimate-Luxury-SUV'
            },
            
            # M Division Performance Trims
            {
                'name': 'M Performance',
                'description': 'M Performance tuning package',
                'models': 'Various models with M40i, M50i designations',
                'price_tier': 'M-Performance'
            },
            {
                'name': 'M2',
                'description': 'High-performance compact coupe',
                'models': '2 Series',
                'price_tier': 'M-Division'
            },
            {
                'name': 'M2 Competition',
                'description': 'Track-focused M2 with S55 engine',
                'models': '2 Series F87',
                'price_tier': 'M-Competition'
            },
            {
                'name': 'M3',
                'description': 'High-performance sport sedan',
                'models': '3 Series',
                'price_tier': 'M-Division'
            },
            {
                'name': 'M3 Competition',
                'description': 'Track-focused M3 with enhanced performance',
                'models': '3 Series G80',
                'price_tier': 'M-Competition'
            },
            {
                'name': 'M4',
                'description': 'High-performance sport coupe/convertible',
                'models': '4 Series',
                'price_tier': 'M-Division'
            },
            {
                'name': 'M4 Competition',
                'description': 'Track-focused M4 with enhanced performance',
                'models': '4 Series G82',
                'price_tier': 'M-Competition'
            },
            {
                'name': 'M5',
                'description': 'High-performance luxury sedan',
                'models': '5 Series',
                'price_tier': 'M-Division-Luxury'
            },
            {
                'name': 'M5 Competition',
                'description': 'Ultimate performance luxury sedan',
                'models': '5 Series F90',
                'price_tier': 'M-Ultimate'
            },
            {
                'name': 'M6',
                'description': 'High-performance grand tourer',
                'models': '6 Series',
                'price_tier': 'M-Division-GT'
            },
            {
                'name': 'M8',
                'description': 'High-performance flagship coupe',
                'models': '8 Series',
                'price_tier': 'M-Division-Flagship'
            },
            {
                'name': 'M8 Competition',
                'description': 'Ultimate performance grand tourer',
                'models': '8 Series G14',
                'price_tier': 'M-Ultimate-GT'
            },
            
            # M Division SUV Trims
            {
                'name': 'X3 M',
                'description': 'High-performance compact SUV',
                'models': 'X3',
                'price_tier': 'M-Division-SUV'
            },
            {
                'name': 'X3 M Competition',
                'description': 'Track-focused performance SUV',
                'models': 'X3 F97',
                'price_tier': 'M-Competition-SUV'
            },
            {
                'name': 'X4 M',
                'description': 'High-performance coupe SUV',
                'models': 'X4',
                'price_tier': 'M-Division-Coupe-SUV'
            },
            {
                'name': 'X5 M',
                'description': 'High-performance luxury SUV',
                'models': 'X5',
                'price_tier': 'M-Division-Luxury-SUV'
            },
            {
                'name': 'X5 M Competition',
                'description': 'Ultimate performance luxury SUV',
                'models': 'X5 F95',
                'price_tier': 'M-Ultimate-SUV'
            },
            {
                'name': 'X6 M',
                'description': 'High-performance luxury coupe SUV',
                'models': 'X6',
                'price_tier': 'M-Division-Luxury-Coupe-SUV'
            },
            
            # Special M Editions
            {
                'name': 'M3 CS',
                'description': 'Club Sport - track-focused M3 variant',
                'models': 'M3 E90, F80',
                'price_tier': 'M-Special-Edition'
            },
            {
                'name': 'M4 CS',
                'description': 'Club Sport - track-focused M4 variant',
                'models': 'M4 F82',
                'price_tier': 'M-Special-Edition'
            },
            {
                'name': 'M4 CSL',
                'description': 'Coupe Sport Leichtbau - ultimate M4',
                'models': 'M4 G82',
                'price_tier': 'M-Ultimate-Special'
            },
            {
                'name': 'M5 CS',
                'description': 'Club Sport - most extreme M5',
                'models': 'M5 F90',
                'price_tier': 'M-Ultimate-Special'
            },
            
            # Electric i Series Trims
            {
                'name': 'iX1 xDrive30',
                'description': 'All-electric compact SUV',
                'models': 'iX1 U11',
                'price_tier': 'Electric-SUV'
            },
            {
                'name': 'iX2 xDrive30',
                'description': 'All-electric compact SUV Coupe',
                'models': 'iX2 U10',
                'price_tier': 'Electric-SUV-Coupe'
            },
            {
                'name': 'i4 eDrive35',
                'description': 'Entry-level electric Gran Coupe',
                'models': 'i4 G26',
                'price_tier': 'Electric-Entry'
            },
            {
                'name': 'i4 eDrive40',
                'description': 'Mid-level electric Gran Coupe',
                'models': 'i4 G26',
                'price_tier': 'Electric-Mid'
            },
            {
                'name': 'i4 M50',
                'description': 'M Performance electric Gran Coupe',
                'models': 'i4 G26',
                'price_tier': 'Electric-M-Performance'
            },
            {
                'name': 'i5 eDrive40',
                'description': 'Entry-level electric luxury sedan',
                'models': 'i5 G60',
                'price_tier': 'Electric-Luxury'
            },
            {
                'name': 'i5 M60',
                'description': 'M Performance electric luxury sedan',
                'models': 'i5 G60',
                'price_tier': 'Electric-M-Performance'
            },
            {
                'name': 'i7 eDrive50',
                'description': 'Entry-level electric flagship sedan',
                'models': 'i7 G70',
                'price_tier': 'Electric-Flagship'
            },
            {
                'name': 'i7 xDrive60',
                'description': 'Mid-level electric flagship sedan',
                'models': 'i7 G70',
                'price_tier': 'Electric-Flagship'
            },
            {
                'name': 'i7 M70',
                'description': 'M Performance electric flagship sedan',
                'models': 'i7 G70',
                'price_tier': 'Electric-M-Performance-Flagship'
            },
            {
                'name': 'iX xDrive50',
                'description': 'Electric luxury SUV',
                'models': 'iX G09',
                'price_tier': 'Electric-Luxury-SUV'
            },
            {
                'name': 'iX M60',
                'description': 'M Performance electric luxury SUV',
                'models': 'iX G09',
                'price_tier': 'Electric-M-Performance-SUV'
            },
            
            # Historical/Previous Generation Trims
            {
                'name': '318i',
                'description': '1.8L/2.0L naturally aspirated (historical)',
                'models': '3 Series E46, E90',
                'price_tier': 'Historical-Entry'
            },
            {
                'name': '325i',
                'description': '2.5L naturally aspirated I6 (historical)',
                'models': '3 Series E46, E90',
                'price_tier': 'Historical-Mid'
            },
            {
                'name': '330i NA',
                'description': '3.0L naturally aspirated I6 (historical)',
                'models': '3 Series E46, E90',
                'price_tier': 'Historical-Performance'
            },
            {
                'name': '335i',
                'description': '3.0L twin-turbo I6 (N54/N55)',
                'models': '3 Series E90, F30',
                'price_tier': 'Historical-Turbo'
            },
            {
                'name': '525i',
                'description': '2.5L naturally aspirated I6 (historical)',
                'models': '5 Series E39, E60',
                'price_tier': 'Historical-Luxury'
            },
            {
                'name': '530i NA',
                'description': '3.0L naturally aspirated I6 (historical)',
                'models': '5 Series E39, E60',
                'price_tier': 'Historical-Luxury-Performance'
            },
            {
                'name': '535i',
                'description': '3.0L twin-turbo I6 (N54/N55)',
                'models': '5 Series E60, F10',
                'price_tier': 'Historical-Turbo-Luxury'
            },
            {
                'name': 'M5 V10',
                'description': '5.0L naturally aspirated V10 (S85)',
                'models': 'M5 E60',
                'price_tier': 'Historical-M-V10'
            },
            
            # Body Style Variants
            {
                'name': 'Sedan',
                'description': 'Four-door sedan body style',
                'models': '3/5/7 Series',
                'price_tier': 'Body-Style'
            },
            {
                'name': 'Touring',
                'description': 'Wagon body style (estate)',
                'models': '3/5 Series',
                'price_tier': 'Wagon-Body-Style'
            },
            {
                'name': 'Coupe',
                'description': 'Two-door coupe body style',
                'models': '4/6/8 Series',
                'price_tier': 'Coupe-Body-Style'
            },
            {
                'name': 'Convertible',
                'description': 'Soft-top or hard-top convertible',
                'models': '4/6/8 Series',
                'price_tier': 'Convertible-Body-Style'
            },
            {
                'name': 'Gran Coupe',
                'description': 'Four-door coupe styling',
                'models': '4/6/8 Series',
                'price_tier': 'Gran-Coupe-Body-Style'
            },
            {
                'name': 'Gran Turismo',
                'description': 'Five-door hatchback/GT styling',
                'models': '3/5/6 Series GT',
                'price_tier': 'GT-Body-Style'
            },
            
            # xDrive All-Wheel Drive System
            {
                'name': 'xDrive',
                'description': 'BMW intelligent all-wheel drive system',
                'models': 'Most BMW models (when available)',
                'price_tier': 'AWD-System'
            },
            {
                'name': 'sDrive',
                'description': 'BMW rear-wheel drive system',
                'models': 'X-Series SUVs, Z4',
                'price_tier': 'RWD-System'
            },
            
            # Technology and Option Packages
            {
                'name': 'M Sport Package',
                'description': 'Sport appearance and handling package',
                'models': 'Most BMW models',
                'price_tier': 'Sport-Package'
            },
            {
                'name': 'M Sport Pro Package',
                'description': 'Enhanced M Sport with performance upgrades',
                'models': 'Select models',
                'price_tier': 'Enhanced-Sport-Package'
            },
            {
                'name': 'Comfort Package',
                'description': 'Enhanced comfort and convenience features',
                'models': 'Most BMW models',
                'price_tier': 'Comfort-Package'
            },
            {
                'name': 'Technology Package',
                'description': 'Advanced driver assistance and tech features',
                'models': 'Most BMW models',
                'price_tier': 'Technology-Package'
            },
            {
                'name': 'Driver Assistance Package',
                'description': 'Semi-autonomous driving features',
                'models': 'Current generation models',
                'price_tier': 'Assistance-Package'
            },
            {
                'name': 'Executive Package',
                'description': 'Luxury rear passenger amenities',
                'models': '5/7 Series, X5/X7',
                'price_tier': 'Executive-Package'
            }
        ]
        
        # Filter out discontinued model trims if not requested
        if not include_discontinued:
            discontinued_indicators = ['Historical', 'V10', 'NA ', '318i', '325i', '525i', '535i']
            bmw_trims = [
                trim for trim in bmw_trims 
                if not any(disc_indicator in trim['description'] or disc_indicator in trim['name'] 
                          for disc_indicator in discontinued_indicators)
            ]
            self.stdout.write('Filtering to active model trims only')
        
        self.stdout.write(f'Processing {len(bmw_trims)} BMW trim levels...')
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for trim_data in bmw_trims:
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
        self.stdout.write('BMW TRIMS SUMMARY')
        self.stdout.write('=' * 60)
        
        if not dry_run:
            self.stdout.write(f'✓ Created: {created_count} trim levels')
            self.stdout.write(f'↻ Updated: {updated_count} trim levels')
            self.stdout.write(f'- Existed: {skipped_count} trim levels')
            self.stdout.write(f'📊 Total: {created_count + updated_count + skipped_count} trims processed')
        else:
            self.stdout.write(f'📊 Would process: {len(bmw_trims)} trim levels')
        
        # Trim hierarchy insights
        self.stdout.write('\n🔍 TRIM HIERARCHY INSIGHTS:')
        self.stdout.write('BMW Performance Tiers:')
        self.stdout.write('• Entry: 320i, 330i → M340i (M Performance) → M3 (M Division)')
        self.stdout.write('• Luxury: 530i, 540i → M550i (M Performance) → M5 (M Division)')
        self.stdout.write('• Flagship: 740i, 750i → M760i (M Performance) → No M7')
        self.stdout.write('• SUV: xDrive30i → M40i (M Performance) → X3 M (M Division)')
        
        self.stdout.write('\nKey BMW Trim Patterns:')
        self.stdout.write('• Numeric Codes: Power/engine displacement (320i, 330i, M340i)')
        self.stdout.write('• M Performance: M40i, M50i (enhanced but not full M)')
        self.stdout.write('• M Division: M3, M4, M5 (ultimate performance)')
        self.stdout.write('• xDrive: All-wheel drive available on most models')
        
        # Model-specific notes
        self.stdout.write('\nModel-Specific Trim Notes:')
        self.stdout.write('• 3 Series: 320i → 330i → M340i → M3/M3 Competition')
        self.stdout.write('• 4 Series: 430i → M440i → M4/M4 Competition')
        self.stdout.write('• 5 Series: 530i → 540i → M550i → M5/M5 Competition')
        self.stdout.write('• 7 Series: 740i → 750i → M760i (no M7)')
        self.stdout.write('• X3: sDrive30i → xDrive30i → M40i → X3 M')
        self.stdout.write('• X5: xDrive40i → xDrive50i → M50i → X5 M')
        
        self.stdout.write('\nElectrification:')
        self.stdout.write('• Plug-in Hybrid: 330e, 530e, 545e, 745e')
        self.stdout.write('• Pure Electric: i4 eDrive40/M50, iX eDrive50/M60')
        self.stdout.write('• Future: All models transitioning to electric')
        
        # Special edition notes
        self.stdout.write('\nSpecial Editions:')
        self.stdout.write('• CS (Club Sport): M3 CS, M4 CS, M5 CS - track-focused')
        self.stdout.write('• CSL (Coupe Sport Leichtbau): M4 CSL - ultimate performance')
        self.stdout.write('• Competition: Enhanced performance over base M models')
        
        # Next steps
        self.stdout.write('\n📋 NEXT STEPS:')
        self.stdout.write('1. Create Vehicle records: python manage.py create_bmw_vehicles')
        self.stdout.write('2. Add Part categories: python manage.py add_part_categories')
        self.stdout.write('3. Import NHTSA data: python manage.py import_nhtsa_vehicles --makes BMW')
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'\n🎉 Successfully processed {len(bmw_trims)} BMW trim levels!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('\n⚠️  DRY RUN complete - run without --dry-run to save changes')
            )
