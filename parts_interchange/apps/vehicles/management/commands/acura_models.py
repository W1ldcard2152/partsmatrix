# This goes in: parts_interchange/apps/vehicles/management/commands/add_acura_models.py

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.vehicles.models import Make, Model


class Command(BaseCommand):
    help = 'Add Acura vehicle models from 2000-2025 with generation data where applicable'

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
        
        # Get or verify Acura make exists
        try:
            if not dry_run:
                acura_make = Make.objects.get(name='Acura')
                self.stdout.write(f'✓ Found Acura make: {acura_make}')
            else:
                self.stdout.write('✓ Would use existing Acura make')
        except Make.DoesNotExist:
            self.stdout.write(self.style.ERROR('Acura make not found. Please run: python manage.py add_brands first'))
            return
        
        # Define Acura models with their year ranges and generations
        acura_models = [
            # Current Models (as of 2025)
            {
                'name': 'Integra',
                'body_style': 'Sedan/Coupe/Liftback',
                'years': [
                    {'range': (1986, 2001), 'generation': 'Gen 3', 'note': 'Original generation in our timeframe'},
                    {'range': (2023, 2025), 'generation': 'Gen 5', 'note': 'New generation return after 22-year gap'}
                ],
                'is_active': True
            },
            {
                'name': 'TL',
                'body_style': 'Sedan',
                'years': [
                    {'range': (1999, 2003), 'generation': 'Gen 2', 'note': 'Second generation'},
                    {'range': (2004, 2008), 'generation': 'Gen 3', 'note': 'Major redesign'},
                    {'range': (2009, 2014), 'generation': 'Gen 4', 'note': 'Final generation, replaced by TLX'}
                ],
                'is_active': False,
                'discontinued': 2014
            },
            {
                'name': 'TLX',
                'body_style': 'Sedan',
                'years': [
                    {'range': (2015, 2020), 'generation': 'Gen 1', 'note': 'Replaced TL and TSX'},
                    {'range': (2021, 2025), 'generation': 'Gen 2', 'note': 'Major redesign, Type S introduced'}
                ],
                'is_active': True
            },
            {
                'name': 'MDX',
                'body_style': 'SUV',
                'years': [
                    {'range': (2001, 2006), 'generation': 'Gen 1', 'note': 'First luxury SUV with 3rd row'},
                    {'range': (2007, 2013), 'generation': 'Gen 2', 'note': 'Larger, more powerful'},
                    {'range': (2014, 2020), 'generation': 'Gen 3', 'note': 'More refined, hybrid available'},
                    {'range': (2021, 2025), 'generation': 'Gen 4', 'note': 'Current generation, Type S available'}
                ],
                'is_active': True
            },
            {
                'name': 'RDX',
                'body_style': 'SUV',
                'years': [
                    {'range': (2007, 2012), 'generation': 'Gen 1', 'note': 'Turbo 4-cylinder, compact SUV'},
                    {'range': (2013, 2018), 'generation': 'Gen 2', 'note': 'V6 engine, larger size'},
                    {'range': (2019, 2025), 'generation': 'Gen 3', 'note': 'Back to turbo 4, more tech'}
                ],
                'is_active': True
            },
            {
                'name': 'ADX',
                'body_style': 'SUV',
                'years': [
                    {'range': (2025, 2025), 'generation': '', 'note': 'New subcompact SUV, based on HR-V'}
                ],
                'is_active': True
            },
            {
                'name': 'ZDX',
                'body_style': 'SUV',
                'years': [
                    {'range': (2010, 2013), 'generation': 'Gen 1', 'note': 'Fastback SUV, ahead of its time'},
                    {'range': (2024, 2025), 'generation': 'Gen 2', 'note': 'Electric SUV, completely different platform'}
                ],
                'is_active': True
            },
            
            # Discontinued Models (if including discontinued)
            {
                'name': 'CL',
                'body_style': 'Coupe',
                'years': [
                    {'range': (1997, 1999), 'generation': 'Gen 1', 'note': 'First generation'},
                    {'range': (2001, 2003), 'generation': 'Gen 2', 'note': 'Based on TL platform'}
                ],
                'is_active': False,
                'discontinued': 2003
            },
            {
                'name': 'RSX',
                'body_style': 'Coupe',
                'years': [
                    {'range': (2002, 2006), 'generation': '', 'note': 'Replaced Integra coupe, single generation'}
                ],
                'is_active': False,
                'discontinued': 2006
            },
            {
                'name': 'TSX',
                'body_style': 'Sedan',
                'years': [
                    {'range': (2004, 2008), 'generation': 'Gen 1', 'note': 'Based on Euro Accord'},
                    {'range': (2009, 2014), 'generation': 'Gen 2', 'note': 'Larger, wagon available 2011-2014'}
                ],
                'is_active': False,
                'discontinued': 2014
            },
            {
                'name': 'RL',
                'body_style': 'Sedan',
                'years': [
                    {'range': (1996, 2004), 'generation': 'Gen 1', 'note': 'Rebadged Honda Legend'},
                    {'range': (2005, 2012), 'generation': 'Gen 2', 'note': 'SH-AWD available, more tech'}
                ],
                'is_active': False,
                'discontinued': 2012
            },
            {
                'name': 'RLX',
                'body_style': 'Sedan', 
                'years': [
                    {'range': (2014, 2020), 'generation': '', 'note': 'Replaced RL, hybrid available, single generation'}
                ],
                'is_active': False,
                'discontinued': 2020
            },
            {
                'name': 'ILX',
                'body_style': 'Sedan',
                'years': [
                    {'range': (2013, 2015), 'generation': 'Gen 1', 'note': 'Entry level, Civic-based'},
                    {'range': (2016, 2022), 'generation': 'Gen 2', 'note': 'Refreshed design, better engine'}
                ],
                'is_active': False,
                'discontinued': 2022
            },
            {
                'name': 'NSX',
                'body_style': 'Sports Car',
                'years': [
                    {'range': (1991, 2005), 'generation': 'Gen 1', 'note': 'Original supercar, all-aluminum'},
                    {'range': (2016, 2022), 'generation': 'Gen 2', 'note': 'Hybrid supercar, completely new design'}
                ],
                'is_active': False,
                'discontinued': 2022
            }
        ]
        
        # Filter out discontinued models if not requested
        if not include_discontinued:
            acura_models = [model for model in acura_models if model.get('is_active', True)]
            self.stdout.write('Filtering to active models only')
        
        self.stdout.write(f'Processing {len(acura_models)} Acura models...')
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for model_data in acura_models:
            model_name = model_data['name']
            body_style = model_data['body_style']
            is_active = model_data['is_active']
            
            # Create the base model record
            if not dry_run:
                model_obj, created = Model.objects.get_or_create(
                    make=acura_make,
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
                    self.stdout.write(f'    {display_start}-{display_end}{gen_display}: {note}')
            
            # Show discontinuation info
            if 'discontinued' in model_data:
                self.stdout.write(f'    ⚠️  Discontinued: {model_data["discontinued"]}')
            
            self.stdout.write('')  # Blank line between models
        
        # Summary
        self.stdout.write('=' * 60)
        self.stdout.write('ACURA MODELS SUMMARY')
        self.stdout.write('=' * 60)
        
        if not dry_run:
            self.stdout.write(f'✓ Created: {created_count} models')
            self.stdout.write(f'↻ Updated: {updated_count} models') 
            self.stdout.write(f'- Existed: {skipped_count} models')
            self.stdout.write(f'📊 Total: {created_count + updated_count + skipped_count} models processed')
        else:
            self.stdout.write(f'📊 Would process: {len(acura_models)} models')
        
        # Show generation insights
        self.stdout.write('\\n🔍 GENERATION INSIGHTS:')
        self.stdout.write('Models with significant generational changes:')
        self.stdout.write('• TL: 3 generations (Gen 2→3 major change 2004, Gen 3→4 2009)')
        self.stdout.write('• MDX: 4 generations (major updates every 6-7 years)')
        self.stdout.write('• RDX: 3 generations (turbo→V6→turbo engine changes)')
        self.stdout.write('• Integra: Big gap (2001→2023, completely different platforms)')
        self.stdout.write('• NSX: 2 completely different supercars (NA V6 → Hybrid V6)')
        
        # Next steps
        self.stdout.write('\\n📋 NEXT STEPS:')
        self.stdout.write('1. Run migrations: python manage.py makemigrations && python manage.py migrate')
        self.stdout.write('2. Add other brands: python manage.py add_ford_models, etc.')
        self.stdout.write('3. Populate Vehicle records with generations: python manage.py add_vehicles --make Acura')
        self.stdout.write('4. Import NHTSA data: python manage.py import_nhtsa_vehicles --makes Acura')
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'\\n🎉 Successfully processed {len(acura_models)} Acura models!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('\\n⚠️  DRY RUN complete - run without --dry-run to save changes')
            )
