from django.core.management.base import BaseCommand
from django.db import transaction
from apps.parts.models import PartCategory, PartGroup


class Command(BaseCommand):
    help = 'Create common automotive part groups for junkyard/interchange searches'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without making changes'
        )
        parser.add_argument(
            '--category',
            type=str,
            help='Create part groups for specific category only'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        category_filter = options['category']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No data will be saved'))
        
        # Common automotive part groups for junkyard searches
        part_groups = [
            # Electrical Components
            {
                'name': '12V 100-150A Alternators',
                'description': 'Standard 12V alternators with 100-150 amp output for domestic and import vehicles',
                'category': 'Alternator',
                'voltage': 12.0,
                'amperage': 125.0,  # Average
                'mounting_pattern': 'Standard 3-bolt',
                'connector_type': 'Standard 2-wire + case ground',
                'specifications': {
                    'amp_range': '100-150A',
                    'common_applications': ['Most passenger cars', 'Light trucks'],
                    'typical_years': '1990-2025'
                }
            },
            {
                'name': '12V 150-200A High Output Alternators',
                'description': 'High output 12V alternators for vehicles with high electrical demands',
                'category': 'Alternator',
                'voltage': 12.0,
                'amperage': 175.0,
                'mounting_pattern': 'Heavy duty 3-bolt',
                'connector_type': 'Standard + high amp connection',
                'specifications': {
                    'amp_range': '150-200A+',
                    'common_applications': ['SUVs', 'Trucks', 'Luxury vehicles'],
                    'typical_years': '2000-2025'
                }
            },
            {
                'name': 'Standard 12V Starters - Gear Reduction',
                'description': 'Modern gear reduction starters for most passenger vehicles',
                'category': 'Starter Motor',
                'voltage': 12.0,
                'mounting_pattern': 'Standard 2-bolt',
                'connector_type': 'Solenoid + main power',
                'specifications': {
                    'type': 'Gear Reduction',
                    'common_applications': ['Most modern vehicles'],
                    'typical_years': '1995-2025',
                    'advantages': 'Lighter weight, more torque'
                }
            },
            {
                'name': 'Standard 12V Starters - Direct Drive',
                'description': 'Traditional direct drive starters for older vehicles',
                'category': 'Starter Motor',
                'voltage': 12.0,
                'mounting_pattern': 'Standard 2-bolt',
                'connector_type': 'Solenoid + main power',
                'specifications': {
                    'type': 'Direct Drive',
                    'common_applications': ['Older vehicles', 'Some heavy duty'],
                    'typical_years': '1970-2000',
                    'characteristics': 'Heavier but robust'
                }
            },
            
            # Engine Components
            {
                'name': 'LS Engine Family - Long Blocks',
                'description': 'GM LS series complete engine assemblies (LS1, LS2, LS3, LS6, LSA, etc.)',
                'category': 'Complete Engine Assembly',
                'specifications': {
                    'engine_family': 'GM LS',
                    'displacement_range': '4.8L-7.0L',
                    'configuration': 'V8',
                    'common_models': ['LS1', 'LS2', 'LS3', 'LS6', 'LSA', 'LS9'],
                    'years': '1997-2025',
                    'vehicles': ['Corvette', 'Camaro', 'GTO', 'CTS-V', 'G8']
                },
                'mounting_pattern': 'LS motor mounts',
                'max_length': 29.0,
                'max_width': 26.0,
                'max_height': 28.0
            },
            {
                'name': 'Small Block Chevy (SBC) - Traditional',
                'description': 'Traditional Chevrolet small block engines (283, 305, 307, 327, 350, 400)',
                'category': 'Complete Engine Assembly',
                'specifications': {
                    'engine_family': 'Chevy Small Block',
                    'displacement_range': '283-400 cubic inches',
                    'configuration': 'V8',
                    'common_displacements': ['283', '305', '307', '327', '350', '400'],
                    'years': '1955-2003',
                    'characteristics': 'Traditional pushrod V8'
                },
                'mounting_pattern': 'SBC motor mounts',
                'max_length': 28.0,
                'max_width': 25.0,
                'max_height': 27.0
            },
            {
                'name': 'Ford Modular V8 Engines',
                'description': 'Ford modular V8 family (4.6L, 5.0L, 5.4L, 5.8L)',
                'category': 'Complete Engine Assembly',
                'specifications': {
                    'engine_family': 'Ford Modular',
                    'displacement_range': '4.6L-5.8L',
                    'configuration': 'V8 SOHC/DOHC',
                    'common_displacements': ['4.6L', '5.0L', '5.4L', '5.8L'],
                    'years': '1990-2025',
                    'variants': ['2V', '3V', '4V', 'Coyote']
                },
                'mounting_pattern': 'Modular motor mounts'
            },
            
            # Transmission Components
            {
                'name': '4L60E/4L65E/4L70E Automatic Transmissions',
                'description': 'GM 4L60E family 4-speed automatic transmissions',
                'category': 'Automatic',
                'specifications': {
                    'transmission_family': 'GM 4L60E',
                    'speeds': 4,
                    'type': 'Automatic',
                    'variants': ['4L60E', '4L65E', '4L70E'],
                    'years': '1992-2013',
                    'common_vehicles': ['Camaro', 'Corvette', 'Silverado', 'Tahoe'],
                    'torque_capacity': '300-400 ft-lbs'
                },
                'mounting_pattern': 'GM RWD automatic'
            },
            {
                'name': 'T56/TR6060 Manual Transmissions',
                'description': 'Borg Warner T56 and TR6060 6-speed manual transmissions',
                'category': 'Manual',
                'specifications': {
                    'transmission_family': 'T56/TR6060',
                    'speeds': 6,
                    'type': 'Manual',
                    'variants': ['T56', 'TR6060'],
                    'years': '1992-2025',
                    'common_vehicles': ['Corvette', 'Camaro', 'GTO', 'Challenger', 'Mustang'],
                    'torque_capacity': '450-700+ ft-lbs'
                },
                'mounting_pattern': 'T56 bellhousing pattern'
            },
            
            # Brake Components
            {
                'name': 'Standard Single Piston Brake Calipers',
                'description': 'Single piston floating brake calipers for most passenger vehicles',
                'category': 'Brake Caliper',
                'specifications': {
                    'piston_count': 1,
                    'type': 'Floating',
                    'common_applications': ['Front and rear brakes', 'Most passenger cars'],
                    'years': '1980-2025'
                },
                'mounting_pattern': 'Standard 2-bolt'
            },
            {
                'name': 'Multi-Piston Performance Brake Calipers',
                'description': 'Multi-piston fixed brake calipers for performance applications',
                'category': 'Brake Caliper',
                'specifications': {
                    'piston_count': '2-6',
                    'type': 'Fixed',
                    'common_applications': ['Performance vehicles', 'Sport packages', 'Heavy duty'],
                    'years': '1990-2025'
                },
                'mounting_pattern': 'Performance 2-4 bolt'
            },
            
            # Suspension Components
            {
                'name': 'MacPherson Strut Assemblies - Compact Cars',
                'description': 'Complete MacPherson strut assemblies for compact and mid-size vehicles',
                'category': 'Struts',
                'specifications': {
                    'type': 'MacPherson Strut',
                    'application': 'Front suspension',
                    'common_vehicles': ['Compact cars', 'Mid-size sedans', 'Most FWD vehicles'],
                    'years': '1980-2025'
                },
                'mounting_pattern': '3-bolt top, 2-bolt bottom'
            },
            {
                'name': 'Coil-Over Shock Assemblies - Trucks/SUVs',
                'description': 'Rear coil-over shock assemblies for trucks and SUVs',
                'category': 'Shocks',
                'specifications': {
                    'type': 'Coil-Over Shock',
                    'application': 'Rear suspension',
                    'common_vehicles': ['Pickup trucks', 'SUVs', 'Some RWD cars'],
                    'years': '1990-2025'
                },
                'mounting_pattern': 'Standard shock mounts'
            }
        ]
        
        # Filter by category if specified
        if category_filter:
            part_groups = [pg for pg in part_groups if category_filter.lower() in pg['category'].lower()]
            self.stdout.write(f'Filtering to part groups containing "{category_filter}"')
        
        self.stdout.write(f'Processing {len(part_groups)} part groups...')
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for pg_data in part_groups:
            pg_name = pg_data['name']
            category_name = pg_data['category']
            
            try:
                if not dry_run:
                    # Get or create the category
                    try:
                        category = PartCategory.objects.get(name=category_name)
                    except PartCategory.DoesNotExist:
                        self.stdout.write(f'  Warning: Category "{category_name}" not found, skipping {pg_name}')
                        skipped_count += 1
                        continue
                    
                    # Check if part group already exists
                    existing_pg = PartGroup.objects.filter(name=pg_name).first()
                    
                    if existing_pg:
                        # Update existing part group
                        existing_pg.description = pg_data['description']
                        existing_pg.category = category
                        existing_pg.voltage = pg_data.get('voltage')
                        existing_pg.amperage = pg_data.get('amperage')
                        existing_pg.wattage = pg_data.get('wattage')
                        existing_pg.mounting_pattern = pg_data.get('mounting_pattern', '')
                        existing_pg.connector_type = pg_data.get('connector_type', '')
                        existing_pg.thread_size = pg_data.get('thread_size', '')
                        existing_pg.max_length = pg_data.get('max_length')
                        existing_pg.max_width = pg_data.get('max_width')
                        existing_pg.max_height = pg_data.get('max_height')
                        existing_pg.specifications = pg_data.get('specifications', {})
                        existing_pg.save()
                        updated_count += 1
                        status = '↻ UPDATED'
                    else:
                        # Create new part group
                        PartGroup.objects.create(
                            name=pg_name,
                            description=pg_data['description'],
                            category=category,
                            voltage=pg_data.get('voltage'),
                            amperage=pg_data.get('amperage'),
                            wattage=pg_data.get('wattage'),
                            mounting_pattern=pg_data.get('mounting_pattern', ''),
                            connector_type=pg_data.get('connector_type', ''),
                            thread_size=pg_data.get('thread_size', ''),
                            max_length=pg_data.get('max_length'),
                            max_width=pg_data.get('max_width'),
                            max_height=pg_data.get('max_height'),
                            specifications=pg_data.get('specifications', {}),
                            is_active=True,
                            created_by='system'
                        )
                        created_count += 1
                        status = '✓ CREATED'
                else:
                    status = '? DRY RUN'
                
                # Display part group info
                self.stdout.write(f'{status} {pg_name}')
                self.stdout.write(f'    Category: {category_name}')
                if pg_data.get('voltage'):
                    self.stdout.write(f'    Specs: {pg_data.get("voltage")}V')
                if pg_data.get('amperage'):
                    self.stdout.write(f'           {pg_data.get("amperage")}A')
                if pg_data.get('mounting_pattern'):
                    self.stdout.write(f'    Mount: {pg_data.get("mounting_pattern")}')
                self.stdout.write(f'    Desc: {pg_data["description"][:80]}...')
                self.stdout.write('')  # Blank line
                
            except Exception as e:
                self.stdout.write(f'  Error creating {pg_name}: {e}')
                skipped_count += 1
        
        # Summary
        self.stdout.write('=' * 60)
        self.stdout.write('PART GROUPS SUMMARY')
        self.stdout.write('=' * 60)
        
        if not dry_run:
            self.stdout.write(f'✓ Created: {created_count} part groups')
            self.stdout.write(f'↻ Updated: {updated_count} part groups')
            self.stdout.write(f'- Skipped: {skipped_count} part groups')
            self.stdout.write(f'📊 Total: {created_count + updated_count + skipped_count} processed')
        else:
            self.stdout.write(f'📊 Would process: {len(part_groups)} part groups')
        
        # Next steps
        self.stdout.write('\n📋 NEXT STEPS:')
        self.stdout.write('1. Add parts to groups: python manage.py add_parts_to_groups')
        self.stdout.write('2. Test junkyard search: python manage.py test_junkyard_search')
        self.stdout.write('3. Verify part groups in admin: /admin/parts/partgroup/')
        
        # Usage examples
        self.stdout.write('\n💡 USAGE EXAMPLES:')
        self.stdout.write('Junkyard worker: "I need an alternator for 2010 Chevy 1500"')
        self.stdout.write('→ System finds all 12V 100-150A alternators from ANY vehicle')
        self.stdout.write('→ Shows compatibility: Identical/Compatible/Conditional')
        self.stdout.write('→ Lists installation notes and restrictions')
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'\n🎉 Successfully processed {len(part_groups)} part groups!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('\n⚠️  DRY RUN complete - run without --dry-run to save changes')
            )
