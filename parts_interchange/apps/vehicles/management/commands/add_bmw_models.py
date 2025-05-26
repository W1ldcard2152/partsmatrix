# This goes in: parts_interchange/apps/vehicles/management/commands/add_bmw_models.py

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.vehicles.models import Make, Model


class Command(BaseCommand):
    help = 'Add BMW vehicle models from 2000-2025 with generation data including LCI mid-cycle refreshes'

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
        
        # Get or verify BMW make exists
        try:
            if not dry_run:
                bmw_make = Make.objects.get(name='BMW')
                self.stdout.write(f'✓ Found BMW make: {bmw_make}')
            else:
                self.stdout.write('✓ Would use existing BMW make')
        except Make.DoesNotExist:
            self.stdout.write(self.style.ERROR('BMW make not found. Please run: python manage.py add_brands first'))
            return
        
        # Define BMW models with their year ranges and generations INCLUDING LCI refreshes
        bmw_models = [
            # 1 Series (E8x, F2x, F40)
            {
                'name': '1 Series',
                'body_style': 'Hatchback/Coupe/Convertible',
                'years': [
                    {'range': (2004, 2007), 'generation': 'E87', 'note': 'First generation hatchback (Europe only)'},
                    {'range': (2008, 2013), 'generation': 'E82/E88', 'note': 'First generation coupe/convertible (global)'},
                    {'range': (2012, 2014), 'generation': 'F20', 'note': 'Second generation hatchback pre-LCI (Europe only)'},
                    {'range': (2015, 2019), 'generation': 'F20 LCI', 'note': 'F20 LCI facelift (Europe only)'},
                    {'range': (2019, 2025), 'generation': 'F40', 'note': 'Third generation hatchback (FWD, Europe only)'}
                ],
                'is_active': True
            },
            # 2 Series (F22/F23, F45/F46, G42)
            {
                'name': '2 Series',
                'body_style': 'Coupe/Convertible/Active Tourer/Gran Tourer',
                'years': [
                    {'range': (2014, 2017), 'generation': 'F22/F23', 'note': 'First generation coupe/convertible pre-LCI'},
                    {'range': (2018, 2021), 'generation': 'F22/F23 LCI', 'note': 'F22/F23 LCI facelift'},
                    {'range': (2014, 2017), 'generation': 'F45/F46', 'note': 'Active Tourer/Gran Tourer (FWD, Europe only)'},
                    {'range': (2018, 2021), 'generation': 'F45/F46 LCI', 'note': 'F45/F46 LCI facelift (Europe only)'},
                    {'range': (2020, 2025), 'generation': 'F44 Gran Coupe', 'note': 'First generation Gran Coupe (FWD)'},
                    {'range': (2022, 2025), 'generation': 'G42', 'note': 'Second generation coupe'}
                ],
                'is_active': True
            },
            # 3 Series (E46, E90/E91/E92/E93, F30/F31/F34, G20/G21)
            {
                'name': '3 Series',
                'body_style': 'Sedan/Wagon/Coupe/Convertible',
                'years': [
                    {'range': (1999, 2006), 'generation': 'E46', 'note': 'Fourth generation, last naturally aspirated era'},
                    {'range': (2006, 2008), 'generation': 'E90', 'note': 'Fifth generation pre-LCI, N52 naturally aspirated'},
                    {'range': (2009, 2011), 'generation': 'E90 LCI', 'note': 'E90 LCI facelift, updated styling and iDrive'},
                    {'range': (2012, 2015), 'generation': 'F30', 'note': 'Sixth generation pre-LCI, turbo era begins'},
                    {'range': (2016, 2018), 'generation': 'F30 LCI', 'note': 'F30 LCI facelift, LED headlights standard'},
                    {'range': (2019, 2022), 'generation': 'G20', 'note': 'Seventh generation pre-LCI, new platform'},
                    {'range': (2023, 2025), 'generation': 'G20 LCI', 'note': 'G20 LCI facelift, updated technology and styling'}
                ],
                'is_active': True
            },
            {
                'name': '4 Series',
                'body_style': 'Coupe/Convertible/Gran Coupe',
                'years': [
                    {'range': (2014, 2016), 'generation': 'F32', 'note': 'First 4 Series, split from 3 Series coupe'},
                    {'range': (2017, 2020), 'generation': 'F32 LCI', 'note': 'F32 LCI facelift, updated styling'},
                    {'range': (2021, 2025), 'generation': 'G22', 'note': 'Second generation, controversial large grille'}
                ],
                'is_active': True
            },
            {
                'name': '5 Series',
                'body_style': 'Sedan/Wagon',
                'years': [
                    {'range': (1997, 2003), 'generation': 'E39', 'note': 'Fourth generation, classic BMW design'},
                    {'range': (2004, 2007), 'generation': 'E60', 'note': 'Fifth generation pre-LCI, Chris Bangle design'},
                    {'range': (2008, 2010), 'generation': 'E60 LCI', 'note': 'E60 LCI facelift, updated styling and tech'},
                    {'range': (2011, 2013), 'generation': 'F10', 'note': 'Sixth generation pre-LCI, return to classic proportions'},
                    {'range': (2014, 2016), 'generation': 'F10 LCI', 'note': 'F10 LCI facelift, LED headlights standard'},
                    {'range': (2017, 2020), 'generation': 'G30', 'note': 'Seventh generation pre-LCI, CLAR platform'},
                    {'range': (2021, 2025), 'generation': 'G30 LCI', 'note': 'G30 LCI facelift, updated technology and mild hybrid'}
                ],
                'is_active': True
            },
            {
                'name': '6 Series',
                'body_style': 'Coupe/Convertible/Gran Coupe',
                'years': [
                    {'range': (2004, 2007), 'generation': 'E63', 'note': 'E63/E64 first generation pre-LCI'},
                    {'range': (2008, 2010), 'generation': 'E63 LCI', 'note': 'E63/E64 LCI facelift'},
                    {'range': (2011, 2014), 'generation': 'F12', 'note': 'F12/F13 second generation pre-LCI'},
                    {'range': (2015, 2018), 'generation': 'F12 LCI', 'note': 'F12/F13 LCI facelift'},
                    {'range': (2018, 2025), 'generation': 'G32', 'note': 'Third generation, Gran Turismo replacement'}
                ],
                'is_active': True
            },
            {
                'name': '7 Series',
                'body_style': 'Sedan',
                'years': [
                    {'range': (1995, 2001), 'generation': 'E38', 'note': 'Third generation, classic flagship'},
                    {'range': (2002, 2005), 'generation': 'E65', 'note': 'Fourth generation pre-LCI, first iDrive'},
                    {'range': (2006, 2008), 'generation': 'E65 LCI', 'note': 'E65 LCI facelift, updated iDrive'},
                    {'range': (2009, 2012), 'generation': 'F01', 'note': 'Fifth generation pre-LCI'},
                    {'range': (2013, 2015), 'generation': 'F01 LCI', 'note': 'F01 LCI facelift, updated technology'},
                    {'range': (2016, 2019), 'generation': 'G11', 'note': 'Sixth generation pre-LCI, CLAR platform'},
                    {'range': (2020, 2022), 'generation': 'G11 LCI', 'note': 'G11 LCI facelift, updated styling'},
                    {'range': (2023, 2025), 'generation': 'G70', 'note': 'Seventh generation, controversial large grille'}
                ],
                'is_active': True
            },
            {
                'name': '8 Series',
                'body_style': 'Coupe/Convertible/Gran Coupe',
                'years': [
                    {'range': (1990, 1999), 'generation': 'E31', 'note': 'Original 8 Series, V8/V12 grand tourer'},
                    {'range': (2019, 2025), 'generation': 'G14', 'note': 'Revived 8 Series, modern grand tourer'}
                ],
                'is_active': True
            },
            {
                'name': 'X3',
                'body_style': 'SUV',
                'years': [
                    {'range': (2004, 2006), 'generation': 'E83', 'note': 'E83 first generation pre-LCI'},
                    {'range': (2007, 2010), 'generation': 'E83 LCI', 'note': 'E83 LCI facelift, updated styling'},
                    {'range': (2011, 2014), 'generation': 'F25', 'note': 'F25 second generation pre-LCI'},
                    {'range': (2015, 2017), 'generation': 'F25 LCI', 'note': 'F25 LCI facelift'},
                    {'range': (2018, 2021), 'generation': 'G01', 'note': 'G01 third generation pre-LCI'},
                    {'range': (2022, 2025), 'generation': 'G01 LCI', 'note': 'G01 LCI facelift, current generation'}
                ],
                'is_active': True
            },
            {
                'name': 'X5',
                'body_style': 'SUV',
                'years': [
                    {'range': (2000, 2003), 'generation': 'E53', 'note': 'E53 first generation, BMW\'s first SUV'},
                    {'range': (2007, 2010), 'generation': 'E70', 'note': 'E70 second generation pre-LCI'},
                    {'range': (2011, 2013), 'generation': 'E70 LCI', 'note': 'E70 LCI facelift'},
                    {'range': (2014, 2017), 'generation': 'F15', 'note': 'F15 third generation pre-LCI'},
                    {'range': (2018, 2018), 'generation': 'F15 LCI', 'note': 'F15 LCI facelift, brief refresh'},
                    {'range': (2019, 2022), 'generation': 'G05', 'note': 'G05 fourth generation pre-LCI'},
                    {'range': (2023, 2025), 'generation': 'G05 LCI', 'note': 'G05 LCI facelift, current generation'}
                ],
                'is_active': True
            },
            # X1 (E84, F48, U11)
            {
                'name': 'X1',
                'body_style': 'SUV',
                'years': [
                    {'range': (2009, 2012), 'generation': 'E84', 'note': 'First generation pre-LCI'},
                    {'range': (2013, 2015), 'generation': 'E84 LCI', 'note': 'E84 LCI facelift'},
                    {'range': (2016, 2019), 'generation': 'F48', 'note': 'Second generation pre-LCI (FWD based)'},
                    {'range': (2020, 2022), 'generation': 'F48 LCI', 'note': 'F48 LCI facelift'},
                    {'range': (2023, 2025), 'generation': 'U11', 'note': 'Third generation, current model'}
                ],
                'is_active': True
            },
            # X2 (F39, U10)
            {
                'name': 'X2',
                'body_style': 'SUV Coupe',
                'years': [
                    {'range': (2018, 2020), 'generation': 'F39', 'note': 'First generation pre-LCI'},
                    {'range': (2021, 2023), 'generation': 'F39 LCI', 'note': 'F39 LCI facelift'},
                    {'range': (2024, 2025), 'generation': 'U10', 'note': 'Second generation, current model'}
                ],
                'is_active': True
            },
            # X4 (F26, G02)
            {
                'name': 'X4',
                'body_style': 'SUV Coupe',
                'years': [
                    {'range': (2014, 2018), 'generation': 'F26', 'note': 'First generation'},
                    {'range': (2019, 2021), 'generation': 'G02', 'note': 'Second generation pre-LCI'},
                    {'range': (2022, 2025), 'generation': 'G02 LCI', 'note': 'G02 LCI facelift, current model'}
                ],
                'is_active': True
            },
            # X6 (E71, F16, G06)
            {
                'name': 'X6',
                'body_style': 'SUV Coupe',
                'years': [
                    {'range': (2008, 2011), 'generation': 'E71', 'note': 'First generation pre-LCI'},
                    {'range': (2012, 2014), 'generation': 'E71 LCI', 'note': 'E71 LCI facelift'},
                    {'range': (2015, 2017), 'generation': 'F16', 'note': 'Second generation pre-LCI'},
                    {'range': (2018, 2019), 'generation': 'F16 LCI', 'note': 'F16 LCI facelift'},
                    {'range': (2020, 2022), 'generation': 'G06', 'note': 'Third generation pre-LCI'},
                    {'range': (2023, 2025), 'generation': 'G06 LCI', 'note': 'G06 LCI facelift, current model'}
                ],
                'is_active': True
            },
            # X7 (G07)
            {
                'name': 'X7',
                'body_style': 'Full-size SUV',
                'years': [
                    {'range': (2019, 2022), 'generation': 'G07', 'note': 'First generation pre-LCI'},
                    {'range': (2023, 2025), 'generation': 'G07 LCI', 'note': 'G07 LCI facelift, current model'}
                ],
                'is_active': True
            },
            # Z Series (Z4 E85/E86, E89, G29)
            {
                'name': 'Z4',
                'body_style': 'Roadster/Coupe',
                'years': [
                    {'range': (2002, 2005), 'generation': 'E85/E86', 'note': 'First generation Roadster/Coupe pre-LCI'},
                    {'range': (2006, 2008), 'generation': 'E85/E86 LCI', 'note': 'E85/E86 LCI facelift'},
                    {'range': (2009, 2012), 'generation': 'E89', 'note': 'Second generation pre-LCI (retractable hardtop)'},
                    {'range': (2013, 2016), 'generation': 'E89 LCI', 'note': 'E89 LCI facelift'},
                    {'range': (2019, 2025), 'generation': 'G29', 'note': 'Third generation, current model (soft top)'}
                ],
                'is_active': True
            },
            # i3 (I01)
            {
                'name': 'i3',
                'body_style': 'Hatchback (EV)',
                'years': [
                    {'range': (2014, 2017), 'generation': 'I01', 'note': 'First generation EV pre-LCI'},
                    {'range': (2018, 2022), 'generation': 'I01 LCI', 'note': 'I01 LCI facelift, larger battery options'}
                ],
                'is_active': False # Discontinued
            },
            # i8 (I12/I15)
            {
                'name': 'i8',
                'body_style': 'Coupe/Roadster (PHEV)',
                'years': [
                    {'range': (2014, 2017), 'generation': 'I12', 'note': 'First generation Coupe PHEV'},
                    {'range': (2018, 2020), 'generation': 'I12/I15 LCI', 'note': 'I12 Coupe / I15 Roadster LCI facelift'}
                ],
                'is_active': False # Discontinued
            },
        ]
        
        # Filter out discontinued models if not requested
        if not include_discontinued:
            bmw_models = [model for model in bmw_models if model.get('is_active', True)]
            self.stdout.write('Filtering to active models only')
        
        self.stdout.write(f'Processing {len(bmw_models)} BMW models...')
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for model_data in bmw_models:
            model_name = model_data['name']
            body_style = model_data['body_style']
            is_active = model_data['is_active']
            
            # Create the base model record
            if not dry_run:
                model_obj, created = Model.objects.get_or_create(
                    make=bmw_make,
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
                    if 'LCI' in generation:
                        gen_display = f" {generation} 🔄"
                    self.stdout.write(f'    {display_start}-{display_end}{gen_display}: {note}')
            
            self.stdout.write('')  # Blank line between models
        
        # Summary
        self.stdout.write('=' * 60)
        self.stdout.write('BMW MODELS SUMMARY (LCI REFRESH SUPPORT)')
        self.stdout.write('=' * 60)
        
        if not dry_run:
            self.stdout.write(f'✓ Created: {created_count} models')
            self.stdout.write(f'↻ Updated: {updated_count} models') 
            self.stdout.write(f'- Existed: {skipped_count} models')
            self.stdout.write(f'📊 Total: {created_count + updated_count + skipped_count} models processed')
        else:
            self.stdout.write(f'📊 Would process: {len(bmw_models)} models')
        
        # Show generation insights
        self.stdout.write('\n🔍 GENERATION INSIGHTS:')
        self.stdout.write('BMW Platform Evolution with LCI (Life Cycle Impulse) Refreshes:')
        self.stdout.write('• 3 Series: E46→E90/E90 LCI→F30/F30 LCI→G20/G20 LCI')
        self.stdout.write('• 5 Series: E39→E60/E60 LCI→F10/F10 LCI→G30/G30 LCI')
        self.stdout.write('• 7 Series: E38→E65/E65 LCI→F01/F01 LCI→G11/G11 LCI→G70')
        self.stdout.write('• X3: E83/E83 LCI→F25/F25 LCI→G01/G01 LCI')
        self.stdout.write('• X5: E53→E70/E70 LCI→F15/F15 LCI→G05/G05 LCI')
        
        self.stdout.write('\nLCI Refresh Impact:')
        self.stdout.write('• LCI Models: Significant styling, tech, sometimes powertrain updates')
        self.stdout.write('• Parts Compatibility: LCI refreshes often require different parts')
        self.stdout.write('• Technology Updates: iDrive systems, LED lighting, driver assistance')
        
        self.stdout.write('\n📋 NEXT STEPS:')
        self.stdout.write('1. Add engines: python manage.py add_bmw_engines')
        self.stdout.write('2. Add trims: python manage.py add_bmw_trims')
        self.stdout.write('3. Create vehicles: python manage.py create_bmw_vehicles')
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'\n🎉 Successfully processed {len(bmw_models)} BMW models with LCI generation support!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('\n⚠️  DRY RUN complete - run without --dry-run to save changes')
            )
