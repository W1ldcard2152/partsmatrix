# This goes in: parts_interchange/apps/vehicles/management/commands/add_acura_trims.py

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.vehicles.models import Trim


class Command(BaseCommand):
    help = 'Add Acura trim levels organized by model and generation'

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
        
        # Acura trim levels organized by model and generation
        acura_trims = [
            # Universal Trims (used across multiple models)
            {
                'name': 'Base',
                'description': 'Base trim level with standard equipment',
                'models': 'All models',
                'price_tier': 'Entry'
            },
            {
                'name': 'Premium',
                'description': 'Mid-level trim with additional luxury features',
                'models': 'Multiple models',
                'price_tier': 'Mid'
            },
            {
                'name': 'Technology',
                'description': 'Technology-focused trim with advanced features',
                'models': 'Multiple models',
                'price_tier': 'Mid-High'
            },
            {
                'name': 'Advance',
                'description': 'High-end trim with luxury and technology features',
                'models': 'Multiple models',
                'price_tier': 'High'
            },
            
            # Performance Trims
            {
                'name': 'A-Spec',
                'description': 'Sport appearance package with styling enhancements',
                'models': 'TLX, RDX, MDX, ILX',
                'price_tier': 'Mid-High'
            },
            {
                'name': 'Type-S',
                'description': 'High-performance trim with sport-tuned engine and suspension',
                'models': 'TL, CL, RSX, TLX, MDX, Integra',
                'price_tier': 'High-Performance'
            },
            {
                'name': 'Type R',
                'description': 'Track-focused, highest performance trim',
                'models': 'Integra (1997-2001)',
                'price_tier': 'Ultra-Performance'
            },
            
            # TL Specific Trims
            {
                'name': '2.5TL',
                'description': 'TL with 2.5L 5-cylinder engine (Gen 1 only)',
                'models': 'TL Gen 1',
                'price_tier': 'Entry'
            },
            {
                'name': '3.2TL',
                'description': 'TL with 3.2L V6 engine (Gen 1-2)',
                'models': 'TL Gen 1-2',
                'price_tier': 'Mid'
            },
            {
                'name': 'Navigation',
                'description': 'Trim level with factory navigation system',
                'models': 'TL, TSX, MDX, RL',
                'price_tier': 'Mid-High'
            },
            
            # MDX Specific Trims
            {
                'name': 'Touring',
                'description': 'MDX luxury trim with premium amenities',
                'models': 'MDX Gen 1-2',
                'price_tier': 'High'
            },
            {
                'name': 'Elite',
                'description': 'Top-tier MDX trim with all luxury features',
                'models': 'MDX Gen 2-3',
                'price_tier': 'High'
            },
            {
                'name': 'Sport Hybrid',
                'description': 'MDX hybrid powertrain with performance focus',
                'models': 'MDX Gen 3',
                'price_tier': 'High-Tech'
            },
            
            # RDX Specific Trims
            {
                'name': 'Turbo',
                'description': 'RDX with turbocharged engine (Gen 1)',
                'models': 'RDX Gen 1',
                'price_tier': 'Mid'
            },
            {
                'name': 'AWD',
                'description': 'All-wheel drive configuration',
                'models': 'RDX, MDX, TL, TLX',
                'price_tier': 'Mid-High'
            },
            
            # Integra Specific Trims
            {
                'name': 'LS',
                'description': 'Integra Luxury Sport trim',
                'models': 'Integra Gen 3',
                'price_tier': 'Entry'
            },
            {
                'name': 'RS',
                'description': 'Integra Road Sport trim',
                'models': 'Integra Gen 3',
                'price_tier': 'Entry-Mid'
            },
            {
                'name': 'GS',
                'description': 'Integra Grand Sport trim',
                'models': 'Integra Gen 3',
                'price_tier': 'Mid'
            },
            {
                'name': 'GS-R',
                'description': 'Integra Grand Sport Racing trim with VTEC engine',
                'models': 'Integra Gen 3',
                'price_tier': 'High-Performance'
            },
            
            # TSX Specific Trims
            {
                'name': 'Sport Wagon',
                'description': 'TSX wagon body style',
                'models': 'TSX Gen 2',
                'price_tier': 'Mid'
            },
            {
                'name': 'V6',
                'description': 'TSX with 3.5L V6 engine option',
                'models': 'TSX Gen 2',
                'price_tier': 'High'
            },
            
            # ILX Specific Trims
            {
                'name': 'Hybrid',
                'description': 'ILX with hybrid powertrain',
                'models': 'ILX Gen 1',
                'price_tier': 'Mid-Tech'
            },
            {
                'name': 'Dynamic',
                'description': 'ILX with manual transmission and performance focus',
                'models': 'ILX Gen 1',
                'price_tier': 'Mid-Performance'
            },
            
            # RL/RLX Specific Trims
            {
                'name': '3.5RL',
                'description': 'RL with 3.5L V6 engine',
                'models': 'RL',
                'price_tier': 'High'
            },
            {
                'name': 'SH-AWD',
                'description': 'Super Handling All-Wheel Drive system',
                'models': 'RL, RLX, TL, TLX, MDX',
                'price_tier': 'High-Tech'
            },
            {
                'name': 'Sport Hybrid SH-AWD',
                'description': 'RLX hybrid with performance all-wheel drive',
                'models': 'RLX',
                'price_tier': 'Ultra-High'
            },
            
            # NSX Trims
            {
                'name': 'Coupe',
                'description': 'NSX standard coupe configuration',
                'models': 'NSX Gen 1-2',
                'price_tier': 'Supercar'
            },
            {
                'name': 'Targa',
                'description': 'NSX with removable roof panel',
                'models': 'NSX Gen 1',
                'price_tier': 'Supercar'
            },
            
            # ZDX Trims
            {
                'name': 'Technology Package',
                'description': 'ZDX with advanced technology features',
                'models': 'ZDX Gen 1-2',
                'price_tier': 'High-Tech'
            },
            {
                'name': 'Advance Package',
                'description': 'ZDX top-tier trim with all features',
                'models': 'ZDX Gen 1-2',
                'price_tier': 'Ultra-High'
            },
            
            # ADX Trims (2025+)
            {
                'name': 'A-Spec Package',
                'description': 'ADX sport appearance and performance package',
                'models': 'ADX',
                'price_tier': 'Mid-High'
            },
            
            # Package-based Trims
            {
                'name': 'Tech Package',
                'description': 'Technology package add-on',
                'models': 'Multiple models',
                'price_tier': 'Mid-Add-on'
            },
            {
                'name': 'Luxury Package',
                'description': 'Luxury amenities package',
                'models': 'Multiple models',
                'price_tier': 'High-Add-on'
            },
        ]
        
        # Filter out discontinued model trims if not requested
        if not include_discontinued:
            discontinued_models = ['TL', 'TSX', 'RL', 'RLX', 'ILX', 'RSX', 'CL', 'NSX Gen 1', 'ZDX Gen 1']
            acura_trims = [
                trim for trim in acura_trims 
                if not any(disc_model in trim['models'] for disc_model in discontinued_models)
            ]
            self.stdout.write('Filtering to active model trims only')
        
        self.stdout.write(f'Processing {len(acura_trims)} Acura trim levels...')
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for trim_data in acura_trims:
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
        self.stdout.write('ACURA TRIMS SUMMARY')
        self.stdout.write('=' * 60)
        
        if not dry_run:
            self.stdout.write(f'✓ Created: {created_count} trim levels')
            self.stdout.write(f'↻ Updated: {updated_count} trim levels')
            self.stdout.write(f'- Existed: {skipped_count} trim levels')
            self.stdout.write(f'📊 Total: {created_count + updated_count + skipped_count} trims processed')
        else:
            self.stdout.write(f'📊 Would process: {len(acura_trims)} trim levels')
        
        # Trim hierarchy insights
        self.stdout.write('\\n🔍 TRIM HIERARCHY INSIGHTS:')
        self.stdout.write('Entry Level: Base, LS, RS → Premium, GS')
        self.stdout.write('Mid Level: Technology, Navigation → A-Spec, Advance')
        self.stdout.write('High Performance: Type-S → Type R (limited models)')
        self.stdout.write('Luxury Tiers: Touring, Elite → Sport Hybrid SH-AWD')
        
        self.stdout.write('\\nKey Acura Trim Patterns:')
        self.stdout.write('• A-Spec: Sport appearance (current era)')
        self.stdout.write('• Type-S: Performance heritage (1999-present)')
        self.stdout.write('• SH-AWD: Advanced all-wheel drive tech')
        self.stdout.write('• Navigation: Pre-smartphone premium feature')
        
        # Model-specific notes
        self.stdout.write('\\nModel-Specific Trim Notes:')
        self.stdout.write('• TL: 2.5TL/3.2TL (Gen 1-2) → Base/Type-S (Gen 3-4)')
        self.stdout.write('• Integra: LS/RS/GS/GS-R/Type-R → Base/A-Spec/Type-S')
        self.stdout.write('• MDX: Touring/Elite → Technology/Advance/Type-S')
        self.stdout.write('• RDX: Turbo (Gen 1) → Base/A-Spec (current)')
        
        # Next steps
        self.stdout.write('\\n📋 NEXT STEPS:')
        self.stdout.write('1. Create Vehicle records: python manage.py create_acura_vehicles')
        self.stdout.write('2. Start Parts app: python manage.py add_part_categories')
        self.stdout.write('3. Add Parts with Fitments: python manage.py add_parts')
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'\\n🎉 Successfully processed {len(acura_trims)} Acura trim levels!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('\\n⚠️  DRY RUN complete - run without --dry-run to save changes')
            )
