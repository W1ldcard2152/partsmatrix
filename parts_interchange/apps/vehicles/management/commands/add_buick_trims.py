from django.core.management.base import BaseCommand
from django.db import transaction
from apps.vehicles.models import Trim


class Command(BaseCommand):
    help = 'Add Buick trim levels organized by model and generation'

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
        
        # Buick trim levels organized by model hierarchy and performance tiers
        buick_trims = [
            # General Buick Trims
            {
                'name': 'Base',
                'description': 'Standard entry-level trim',
                'models': 'Most Buick models',
                'price_tier': 'Entry'
            },
            {
                'name': 'Preferred',
                'description': 'Mid-level trim with enhanced features',
                'models': 'Most Buick models',
                'price_tier': 'Mid-Range'
            },
            {
                'name': 'Essence',
                'description': 'Higher-end trim with premium features',
                'models': 'Enclave, Envision, LaCrosse',
                'price_tier': 'Premium'
            },
            {
                'name': 'Avenir',
                'description': 'Top-tier luxury sub-brand trim',
                'models': 'Enclave, Envision, LaCrosse',
                'price_tier': 'Luxury'
            },
            {
                'name': 'CX',
                'description': 'Base trim level (historical)',
                'models': 'LaCrosse, Rendezvous, Terraza, Lucerne',
                'price_tier': 'Historical-Entry'
            },
            {
                'name': 'CXL',
                'description': 'Mid-level trim (historical)',
                'models': 'LaCrosse, Rendezvous, Terraza, Lucerne',
                'price_tier': 'Historical-Mid'
            },
            {
                'name': 'CXL Special Edition',
                'description': 'Special edition mid-level trim (historical)',
                'models': 'Lucerne',
                'price_tier': 'Historical-Mid'
            },
            {
                'name': 'CXL Plus',
                'description': 'Enhanced mid-level trim (historical)',
                'models': 'Rainier',
                'price_tier': 'Historical-Mid'
            },
            {
                'name': 'CXS',
                'description': 'Sportier trim (historical)',
                'models': 'LaCrosse',
                'price_tier': 'Historical-Sport'
            },
            {
                'name': 'Super',
                'description': 'Performance-oriented trim (historical)',
                'models': 'Lucerne, LaCrosse',
                'price_tier': 'Historical-Performance'
            },
            {
                'name': 'Limited',
                'description': 'Luxury trim (historical)',
                'models': 'LeSabre, Century',
                'price_tier': 'Historical-Luxury'
            },
            {
                'name': 'Custom',
                'description': 'Base trim (historical)',
                'models': 'LeSabre, Century',
                'price_tier': 'Historical-Entry'
            },
            {
                'name': 'Ultra',
                'description': 'Top luxury trim (historical)',
                'models': 'Park Avenue',
                'price_tier': 'Historical-Luxury'
            },
            
            # Regal Specific Trims
            {
                'name': 'Turbo',
                'description': 'Regal with turbocharged engine',
                'models': 'Regal',
                'price_tier': 'Performance'
            },
            {
                'name': 'GS',
                'description': 'Regal Grand Sport performance trim',
                'models': 'Regal',
                'price_tier': 'High-Performance'
            },
            {
                'name': 'Sportback',
                'description': 'Regal hatchback body style',
                'models': 'Regal',
                'price_tier': 'Body-Style'
            },
            {
                'name': 'TourX',
                'description': 'Regal wagon body style',
                'models': 'Regal',
                'price_tier': 'Body-Style'
            },
            
            # Encore Specific Trims
            {
                'name': 'Sport Touring',
                'description': 'Sport appearance package for Encore',
                'models': 'Encore',
                'price_tier': 'Sport-Package'
            },
            
            # Envision Specific Trims
            {
                'name': 'Premium',
                'description': 'High-end trim for Envision',
                'models': 'Envision',
                'price_tier': 'Premium'
            },
            
            # Verano Specific Trims
            {
                'name': 'Convenience',
                'description': 'Mid-level trim for Verano',
                'models': 'Verano',
                'price_tier': 'Mid-Range'
            },
            {
                'name': 'Leather',
                'description': 'Luxury trim for Verano',
                'models': 'Verano',
                'price_tier': 'Luxury'
            },
            
            # All-Wheel Drive
            {
                'name': 'AWD',
                'description': 'All-wheel drive option',
                'models': 'Most Buick SUVs and some sedans',
                'price_tier': 'Drivetrain'
            },
            {
                'name': 'FWD',
                'description': 'Front-wheel drive option',
                'models': 'Most Buick sedans and some SUVs',
                'price_tier': 'Drivetrain'
            }
        ]
        
        # Filter out discontinued model trims if not requested
        if not include_discontinued:
            discontinued_indicators = ['Historical', 'CX', 'CXL', 'CXL Plus', 'CXS', 'Super', 'Limited', 'Custom', 'Ultra']
            buick_trims = [
                trim for trim in buick_trims 
                if not any(disc_indicator in trim['description'] or disc_indicator in trim['name'] 
                          for disc_indicator in discontinued_indicators)
            ]
            self.stdout.write('Filtering to active model trims only')
        
        self.stdout.write(f'Processing {len(buick_trims)} Buick trim levels...')
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for trim_data in buick_trims:
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
        self.stdout.write('BUICK TRIMS SUMMARY')
        self.stdout.write('=' * 60)
        
        if not dry_run:
            self.stdout.write(f'✓ Created: {created_count} trim levels')
            self.stdout.write(f'↻ Updated: {updated_count} trim levels')
            self.stdout.write(f'- Existed: {skipped_count} trim levels')
            self.stdout.write(f'📊 Total: {created_count + updated_count + skipped_count} trims processed')
        else:
            self.stdout.write(f'📊 Would process: {len(buick_trims)} trim levels')
        
        # Trim hierarchy insights
        self.stdout.write('\n🔍 TRIM HIERARCHY INSIGHTS:')
        self.stdout.write('Buick Trim Progression:')
        self.stdout.write('• Entry: Base, CX, Custom')
        self.stdout.write('• Mid-Range: Preferred, CXL, Convenience')
        self.stdout.write('• Premium/Luxury: Essence, Avenir, Leather, Limited, Ultra, Super')
        self.stdout.write('• Performance: Turbo, GS')
        
        self.stdout.write('\nKey Buick Trim Patterns:')
        self.stdout.write('• Avenir: Introduced as a top-tier luxury sub-brand')
        self.stdout.write('• CX/CXL: Older designations for base and mid-level trims')
        self.stdout.write('• GS: Performance variant for Regal')
        
        # Next steps
        self.stdout.write('\n📋 NEXT STEPS:')
        self.stdout.write('1. Add engines: python manage.py add_buick_engines')
        self.stdout.write('2. Create Vehicle records: python manage.py create_buick_vehicles')
        self.stdout.write('3. Import NHTSA data: python manage.py import_nhtsa_vehicles --makes Buick')
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'\n🎉 Successfully processed {len(buick_trims)} Buick trim levels!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('\n⚠️  DRY RUN complete - run without --dry-run to save changes')
            )
