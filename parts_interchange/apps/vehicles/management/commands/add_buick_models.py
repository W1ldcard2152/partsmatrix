from django.core.management.base import BaseCommand
from django.db import transaction
from apps.vehicles.models import Make, Model


class Command(BaseCommand):
    help = 'Add Buick vehicle models from 2000-2025 with generation data including mid-cycle refreshes (facelifts)'

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
            help='Include discontinued models (default: True)'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        include_discontinued = options['include_discontinued']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No data will be saved'))
        
        # Get or verify Buick make exists
        try:
            if not dry_run:
                buick_make = Make.objects.get(name='Buick')
                self.stdout.write(f'✓ Found Buick make: {buick_make}')
            else:
                self.stdout.write('✓ Would use existing Buick make')
        except Make.DoesNotExist:
            self.stdout.write(self.style.ERROR('Buick make not found. Please run: python manage.py add_brands first'))
            return
        
        # Define Buick models with their year ranges and generations
        buick_models = [
            {
                'name': 'LaCrosse',
                'body_style': 'Sedan',
                'years': [
                    {'range': (2005, 2009), 'generation': 'First Gen', 'note': 'First generation'},
                    {'range': (2010, 2016), 'generation': 'Second Gen', 'note': 'Second generation'},
                    {'range': (2017, 2019), 'generation': 'Third Gen', 'note': 'Third generation'}
                ],
                'is_active': False # Discontinued
            },
            {
                'name': 'Regal',
                'body_style': 'Sedan/Sportback/Wagon',
                'years': [
                    {'range': (2011, 2013), 'generation': 'Fourth Gen', 'note': 'Fourth generation (rebadged Opel Insignia) pre-LCI'},
                    {'range': (2014, 2017), 'generation': 'Fourth Gen Facelift', 'note': 'Fourth generation mid-cycle facelift'},
                    {'range': (2018, 2020), 'generation': 'Fifth Gen', 'note': 'Fifth generation (Sportback/TourX)'}
                ],
                'is_active': False # Discontinued
            },
            {
                'name': 'Enclave',
                'body_style': 'SUV',
                'years': [
                    {'range': (2008, 2012), 'generation': 'First Gen', 'note': 'First generation pre-LCI'},
                    {'range': (2013, 2017), 'generation': 'First Gen Facelift', 'note': 'First generation mid-cycle facelift'},
                    {'range': (2018, 2025), 'generation': 'Second Gen', 'note': 'Second generation'}
                ],
                'is_active': True
            },
            {
                'name': 'Encore',
                'body_style': 'Compact SUV',
                'years': [
                    {'range': (2013, 2016), 'generation': 'First Gen', 'note': 'First generation pre-LCI'},
                    {'range': (2017, 2022), 'generation': 'First Gen Facelift', 'note': 'First generation mid-cycle facelift'}
                ],
                'is_active': False # Discontinued
            },
            {
                'name': 'Encore GX',
                'body_style': 'Compact SUV',
                'years': [
                    {'range': (2020, 2023), 'generation': 'First Gen', 'note': 'First generation pre-LCI'},
                    {'range': (2024, 2025), 'generation': 'First Gen Facelift', 'note': 'First generation mid-cycle facelift'}
                ],
                'is_active': True
            },
            {
                'name': 'Envision',
                'body_style': 'Compact SUV',
                'years': [
                    {'range': (2016, 2020), 'generation': 'First Gen', 'note': 'First generation'},
                    {'range': (2021, 2025), 'generation': 'Second Gen', 'note': 'Second generation'}
                ],
                'is_active': True
            },
            {
                'name': 'Cascada',
                'body_style': 'Convertible',
                'years': [
                    {'range': (2016, 2019), 'generation': 'First Gen', 'note': 'First generation'}
                ],
                'is_active': False # Discontinued
            },
            {
                'name': 'Verano',
                'body_style': 'Compact Sedan',
                'years': [
                    {'range': (2012, 2017), 'generation': 'First Gen', 'note': 'First generation'}
                ],
                'is_active': False # Discontinued
            },
            {
                'name': 'Lucerne',
                'body_style': 'Full-size Sedan',
                'years': [
                    {'range': (2006, 2011), 'generation': 'First Gen', 'note': 'First generation'}
                ],
                'is_active': False # Discontinued
            },
            {
                'name': 'Rendezvous',
                'body_style': 'Crossover SUV',
                'years': [
                    {'range': (2002, 2007), 'generation': 'First Gen', 'note': 'First generation'}
                ],
                'is_active': False # Discontinued
            },
            {
                'name': 'Rainier',
                'body_style': 'SUV',
                'years': [
                    {'range': (2004, 2007), 'generation': 'First Gen', 'note': 'First generation'}
                ],
                'is_active': False # Discontinued
            },
            {
                'name': 'Terraza',
                'body_style': 'Minivan',
                'years': [
                    {'range': (2005, 2007), 'generation': 'First Gen', 'note': 'First generation'}
                ],
                'is_active': False # Discontinued
            },
            {
                'name': 'LeSabre',
                'body_style': 'Full-size Sedan',
                'years': [
                    {'range': (2000, 2005), 'generation': 'Eighth Gen', 'note': 'Eighth generation'}
                ],
                'is_active': False # Discontinued
            },
            {
                'name': 'Park Avenue',
                'body_style': 'Full-size Sedan',
                'years': [
                    {'range': (2000, 2005), 'generation': 'Second Gen', 'note': 'Second generation'}
                ],
                'is_active': False # Discontinued
            },
            {
                'name': 'Century',
                'body_style': 'Mid-size Sedan',
                'years': [
                    {'range': (2000, 2005), 'generation': 'Sixth Gen', 'note': 'Sixth generation'}
                ],
                'is_active': False # Discontinued
            }
        ]
        
        # Filter out discontinued models if not requested
        if not include_discontinued:
            buick_models = [model for model in buick_models if model.get('is_active', True)]
            self.stdout.write('Filtering to active models only')
        
        self.stdout.write(f'Processing {len(buick_models)} Buick models...')
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for model_data in buick_models:
            model_name = model_data['name']
            body_style = model_data['body_style']
            is_active = model_data['is_active']
            
            # Create the base model record
            if not dry_run:
                model_obj, created = Model.objects.get_or_create(
                    make=buick_make,
                    name=model_name,
                    defaults={
                        'body_style': body_style,
                        'is_active': is_active
                    }
                )
                
                if created:
                    created_count += 1
                    status = '✓ CREATED'
                elif model_obj.body_style != body_style or model_obj.is_active != is_active:
                    model_obj.body_style = body_style
                    model_obj.is_active = is_active
                    model_obj.save()
                    updated_count += 1
                    status = '↻ UPDATED'
                else:
                    skipped_count += 1
                    status = '- EXISTS'
            else:
                status = '? DRY RUN'
            
            # Display model info with generation breakdown
            self.stdout.write(f'{status} {model_name} ({body_style})')
            
            # Show generation details
            for year_data in model_data['years']:
                start_year, end_year = year_data['range']
                generation = year_data['generation']
                note = year_data['note']
                
                # Filter to our target range (2000-2025)
                display_start = max(start_year, 2000)
                display_end = min(end_year, 2025)
                
                if display_start <= display_end:
                    gen_display = f" {generation}" if generation else ""
                    # Highlight LCI generations
                if 'Facelift' in generation:
                    gen_display = f" {generation} 🔄"
                    self.stdout.write(f'    {display_start}-{display_end}{gen_display}: {note}')
            
            self.stdout.write('')  # Blank line between models
        
        # Summary
        self.stdout.write('=' * 60)
        self.stdout.write('BUICK MODELS SUMMARY (MID-CYCLE REFRESH SUPPORT)')
        self.stdout.write('=' * 60)
        
        if not dry_run:
            self.stdout.write(f'✓ Created: {created_count} models')
            self.stdout.write(f'↻ Updated: {updated_count} models') 
            self.stdout.write(f'- Existed: {skipped_count} models')
            self.stdout.write(f'📊 Total: {created_count + updated_count + skipped_count} models processed')
        else:
            self.stdout.write(f'📊 Would process: {len(buick_models)} models')
        
        # Show generation insights
        self.stdout.write('\n🔍 GENERATION INSIGHTS:')
        self.stdout.write('Buick Platform Evolution with Mid-Cycle Refreshes (Facelifts):')
        self.stdout.write('• Enclave: First Gen→First Gen LCI→Second Gen')
        self.stdout.write('• Regal: Fourth Gen→Fourth Gen LCI→Fifth Gen')
        
        self.stdout.write('\nLCI Refresh Impact:')
        self.stdout.write('• Facelift Models: Significant styling, tech, sometimes powertrain updates')
        self.stdout.write('• Parts Compatibility: Mid-cycle refreshes often require different parts')
        self.stdout.write('• Technology Updates: Infotainment systems, safety features')
        
        self.stdout.write('\n📋 NEXT STEPS:')
        self.stdout.write('1. Add engines: python manage.py add_buick_engines')
        self.stdout.write('2. Add trims: python manage.py add_buick_trims')
        self.stdout.write('3. Create vehicles: python manage.py create_buick_vehicles')
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'\n🎉 Successfully processed {len(buick_models)} Buick models with mid-cycle refresh support!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('\n⚠️  DRY RUN complete - run without --dry-run to save changes')
            )
