# This goes in: parts_interchange/apps/vehicles/management/commands/add_audi_models.py

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.vehicles.models import Make, Model


class Command(BaseCommand):
    help = 'Add Audi vehicle models from 2000-2025 with generation data including .5 mid-cycle refreshes'

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
        
        # Get or verify Audi make exists
        try:
            if not dry_run:
                audi_make = Make.objects.get(name='Audi')
                self.stdout.write(f'✓ Found Audi make: {audi_make}')
            else:
                self.stdout.write('✓ Would use existing Audi make')
        except Make.DoesNotExist:
            self.stdout.write(self.style.ERROR('Audi make not found. Please run: python manage.py add_brands first'))
            return
        
        # Define Audi models with their year ranges and generations INCLUDING .5 refreshes
        audi_models = [
            # A-Series Sedans (Current Models)
            {
                'name': 'A3',
                'body_style': 'Sedan/Wagon/Convertible',
                'years': [
                    {'range': (1996, 2003), 'generation': '8L', 'note': 'First generation in US'},
                    {'range': (2006, 2013), 'generation': '8P', 'note': 'Return to US market'},
                    {'range': (2015, 2020), 'generation': '8V', 'note': 'Sedan added, e-tron variant'},
                    {'range': (2021, 2025), 'generation': '8Y', 'note': 'Current generation, mild hybrid standard'}
                ],
                'is_active': True
            },
            {
                'name': 'A4',
                'body_style': 'Sedan/Wagon',
                'years': [
                    {'range': (1996, 2001), 'generation': 'B5', 'note': 'First-gen quattro popularity'},
                    {'range': (2002, 2005), 'generation': 'B6', 'note': 'Second generation B6 platform'},
                    {'range': (2006, 2008), 'generation': 'B7', 'note': 'B7 mid-cycle refresh, updated styling and tech'},
                    {'range': (2009, 2012), 'generation': 'B8', 'note': 'Third generation B8 platform'},
                    {'range': (2013, 2016), 'generation': 'B8.5', 'note': 'B8.5 facelift, MMI update, LED lighting'},
                    {'range': (2017, 2020), 'generation': 'B9', 'note': 'Fourth generation B9 platform, MLB Evo'},
                    {'range': (2021, 2023), 'generation': 'B9.5', 'note': 'B9.5 facelift, updated infotainment and styling'},
                    {'range': (2024, 2025), 'generation': 'B10', 'note': 'Latest generation, electrified options'}
                ],
                'is_active': True
            },
            {
                'name': 'A5',
                'body_style': 'Coupe/Convertible/Sportback',
                'years': [
                    {'range': (2008, 2012), 'generation': 'B8', 'note': 'First A5, coupe/convertible'},
                    {'range': (2013, 2016), 'generation': 'B8.5', 'note': 'B8.5 facelift, updated styling and tech'},
                    {'range': (2017, 2020), 'generation': 'B9', 'note': 'Sportback added, mild hybrid available'},
                    {'range': (2021, 2025), 'generation': 'B9.5', 'note': 'B9.5 facelift, updated technology'}
                ],
                'is_active': True
            },
            {
                'name': 'A6',
                'body_style': 'Sedan/Wagon',
                'years': [
                    {'range': (1998, 2004), 'generation': 'C5', 'note': 'Avant wagon popular, allroad variant'},
                    {'range': (2005, 2008), 'generation': 'C6', 'note': 'Second generation C6 platform'},
                    {'range': (2009, 2011), 'generation': 'C6.5', 'note': 'C6.5 facelift, updated MMI and LED DRLs'},
                    {'range': (2012, 2014), 'generation': 'C7', 'note': 'Third generation C7 platform, MLB'},
                    {'range': (2015, 2018), 'generation': 'C7.5', 'note': 'C7.5 facelift, matrix LED headlights, updated tech'},
                    {'range': (2019, 2025), 'generation': 'C8', 'note': 'Mild hybrid standard, advanced tech'}
                ],
                'is_active': True
            },
            {
                'name': 'A7',
                'body_style': 'Sportback',
                'years': [
                    {'range': (2012, 2014), 'generation': 'C7', 'note': 'Four-door coupe design'},
                    {'range': (2015, 2018), 'generation': 'C7.5', 'note': 'C7.5 facelift, updated styling and tech'},
                    {'range': (2019, 2025), 'generation': 'C8', 'note': 'Mild hybrid, advanced driver assistance'}
                ],
                'is_active': True
            },
            {
                'name': 'A8',
                'body_style': 'Sedan',
                'years': [
                    {'range': (1997, 2003), 'generation': 'D2', 'note': 'Aluminum space frame construction'},
                    {'range': (2004, 2007), 'generation': 'D3', 'note': 'Second generation D3 platform'},
                    {'range': (2008, 2010), 'generation': 'D3.5', 'note': 'D3.5 facelift, updated styling and technology'},
                    {'range': (2011, 2013), 'generation': 'D4', 'note': 'Third generation D4 platform'},
                    {'range': (2014, 2017), 'generation': 'D4.5', 'note': 'D4.5 facelift, matrix LED standard, updated MMI'},
                    {'range': (2018, 2025), 'generation': 'D5', 'note': 'Level 3 automation, mild hybrid'}
                ],
                'is_active': True
            },
            
            # Q-Series SUVs (Current Models)
            {
                'name': 'Q3',
                'body_style': 'SUV',
                'years': [
                    {'range': (2015, 2018), 'generation': '8U', 'note': 'First Q3 in US market'},
                    {'range': (2019, 2025), 'generation': '8Y', 'note': 'Redesigned, more interior space'}
                ],
                'is_active': True
            },
            {
                'name': 'Q5',
                'body_style': 'SUV',
                'years': [
                    {'range': (2009, 2012), 'generation': '8R', 'note': 'First mid-size Audi SUV'},
                    {'range': (2013, 2017), 'generation': '8R.5', 'note': '8R.5 facelift, updated styling and tech'},
                    {'range': (2018, 2025), 'generation': '8Y', 'note': 'MLB platform, mild hybrid available'}
                ],
                'is_active': True
            },
            {
                'name': 'Q7',
                'body_style': 'SUV',
                'years': [
                    {'range': (2007, 2009), 'generation': '4L', 'note': 'First full-size Audi SUV'},
                    {'range': (2010, 2012), 'generation': '4L.5', 'note': '4L.5 facelift, updated styling and efficiency'},
                    {'range': (2013, 2015), 'generation': '4L.75', 'note': 'Final refresh before complete redesign'},
                    {'range': (2016, 2019), 'generation': '4M', 'note': 'MLB platform, lighter weight'},
                    {'range': (2020, 2025), 'generation': '4M.5', 'note': '4M.5 facelift, updated technology and mild hybrid standard'}
                ],
                'is_active': True
            },
            {
                'name': 'Q8',
                'body_style': 'SUV',
                'years': [
                    {'range': (2019, 2025), 'generation': '4M', 'note': 'Coupe SUV, flagship design'}
                ],
                'is_active': True
            },
            
            # Sports Cars with .5 refreshes
            {
                'name': 'TT',
                'body_style': 'Coupe/Convertible',
                'years': [
                    {'range': (2000, 2006), 'generation': '8N', 'note': 'First generation in US'},
                    {'range': (2008, 2010), 'generation': '8J', 'note': 'Second generation 8J platform'},
                    {'range': (2011, 2015), 'generation': '8J.5', 'note': '8J.5 facelift, updated styling and interior'},
                    {'range': (2016, 2018), 'generation': '8S', 'note': 'Third generation 8S platform, virtual cockpit'},
                    {'range': (2019, 2023), 'generation': '8S.5', 'note': '8S.5 facelift, updated styling before discontinuation'}
                ],
                'is_active': False,
                'discontinued': 2023
            },
            {
                'name': 'R8',
                'body_style': 'Sports Car',
                'years': [
                    {'range': (2008, 2012), 'generation': '42', 'note': 'First R8, V8 and V10 engines'},
                    {'range': (2013, 2015), 'generation': '42.5', 'note': '42.5 facelift, updated styling and performance'},
                    {'range': (2016, 2019), 'generation': '4S', 'note': 'V10 only, more aggressive design'},
                    {'range': (2020, 2023), 'generation': '4S.5', 'note': '4S.5 final updates before discontinuation'}
                ],
                'is_active': False,
                'discontinued': 2023
            },
            
            # S Models with .5 refreshes
            {
                'name': 'S4',
                'body_style': 'Sedan/Wagon',
                'years': [
                    {'range': (2000, 2003), 'generation': 'B5', 'note': 'Twin-turbo V6, B5 S4'},
                    {'range': (2004, 2005), 'generation': 'B6', 'note': 'V8 engine introduction, B6 S4'},
                    {'range': (2006, 2008), 'generation': 'B7', 'note': 'B7 S4, updated styling and tech'},
                    {'range': (2010, 2012), 'generation': 'B8', 'note': 'Supercharged V6, B8 S4'},
                    {'range': (2013, 2016), 'generation': 'B8.5', 'note': 'B8.5 S4, updated styling and tech'},
                    {'range': (2018, 2020), 'generation': 'B9', 'note': 'Turbo V6, mild hybrid, B9 S4'},
                    {'range': (2021, 2025), 'generation': 'B9.5', 'note': 'B9.5 S4, updated styling and technology'}
                ],
                'is_active': True
            },
            {
                'name': 'S5',
                'body_style': 'Coupe/Convertible/Sportback',
                'years': [
                    {'range': (2008, 2012), 'generation': 'B8', 'note': 'Supercharged V6, B8 S5'},
                    {'range': (2013, 2016), 'generation': 'B8.5', 'note': 'B8.5 S5, updated styling and tech'},
                    {'range': (2018, 2020), 'generation': 'B9', 'note': 'Turbo V6, mild hybrid, B9 S5'},
                    {'range': (2021, 2025), 'generation': 'B9.5', 'note': 'B9.5 S5, updated styling and technology'}
                ],
                'is_active': True
            },
            {
                'name': 'S6',
                'body_style': 'Sedan/Wagon',
                'years': [
                    {'range': (2002, 2004), 'generation': 'C5', 'note': 'V8 twin-turbo'},
                    {'range': (2007, 2011), 'generation': 'C6', 'note': 'V10 engine'},
                    {'range': (2013, 2014), 'generation': 'C7', 'note': 'Twin-turbo V8, first C7 S6'},
                    {'range': (2015, 2018), 'generation': 'C7.5', 'note': 'C7.5 S6, updated styling and tech'},
                    {'range': (2020, 2022), 'generation': 'C8', 'note': 'Mild hybrid V8, new S6'},
                    {'range': (2023, 2025), 'generation': 'C8.5', 'note': 'C8.5 S6, updated technology and styling'}
                ],
                'is_active': True
            },
            {
                'name': 'S7',
                'body_style': 'Sportback',
                'years': [
                    {'range': (2013, 2014), 'generation': 'C7', 'note': 'Twin-turbo V8, first S7'},
                    {'range': (2015, 2018), 'generation': 'C7.5', 'note': 'C7.5 S7, updated styling and tech'},
                    {'range': (2020, 2022), 'generation': 'C8', 'note': 'Mild hybrid V8, new S7'},
                    {'range': (2023, 2025), 'generation': 'C8.5', 'note': 'C8.5 S7, updated technology and styling'}
                ],
                'is_active': True
            },
            {
                'name': 'S8',
                'body_style': 'Sedan',
                'years': [
                    {'range': (2001, 2003), 'generation': 'D2', 'note': 'V8 twin-turbo'},
                    {'range': (2007, 2009), 'generation': 'D3', 'note': 'V10 engine'},
                    {'range': (2013, 2013), 'generation': 'D4', 'note': 'Twin-turbo V8, new S8'},
                    {'range': (2014, 2017), 'generation': 'D4.5', 'note': 'D4.5 S8, updated styling and tech'},
                    {'range': (2020, 2022), 'generation': 'D5', 'note': 'Mild hybrid V8, new S8'},
                    {'range': (2023, 2025), 'generation': 'D5.5', 'note': 'D5.5 S8, updated technology and performance'}
                ],
                'is_active': True
            },
            
            # SQ Models with .5 refreshes
            {
                'name': 'SQ5',
                'body_style': 'SUV',
                'years': [
                    {'range': (2014, 2015), 'generation': '8R', 'note': 'Supercharged V6, first SQ5'},
                    {'range': (2016, 2017), 'generation': '8R.5', 'note': '8R.5 SQ5, updated styling before redesign'},
                    {'range': (2018, 2021), 'generation': '8Y', 'note': 'Turbo V6, mild hybrid, new SQ5'},
                    {'range': (2022, 2025), 'generation': '8Y.5', 'note': '8Y.5 SQ5, updated technology and styling'}
                ],
                'is_active': True
            },
            {
                'name': 'SQ7',
                'body_style': 'SUV',
                'years': [
                    {'range': (2017, 2019), 'generation': '4M', 'note': 'Twin-turbo V8, mild hybrid, first SQ7'},
                    {'range': (2020, 2025), 'generation': '4M.5', 'note': '4M.5 SQ7, updated styling and technology'}
                ],
                'is_active': True
            },
            {
                'name': 'SQ8',
                'body_style': 'SUV',
                'years': [
                    {'range': (2020, 2022), 'generation': '4M', 'note': 'Twin-turbo V8, mild hybrid, first SQ8'},
                    {'range': (2023, 2025), 'generation': '4M.5', 'note': '4M.5 SQ8, updated styling and technology'}
                ],
                'is_active': True
            },
            
            # RS Models with .5 refreshes
            {
                'name': 'RS5',
                'body_style': 'Coupe/Convertible/Sportback',
                'years': [
                    {'range': (2013, 2014), 'generation': 'B8', 'note': 'Naturally aspirated V8, first RS5'},
                    {'range': (2015, 2015), 'generation': 'B8.5', 'note': 'B8.5 RS5, final year before hiatus'},
                    {'range': (2018, 2020), 'generation': 'B9', 'note': 'Twin-turbo V6, mild hybrid, new RS5'},
                    {'range': (2021, 2025), 'generation': 'B9.5', 'note': 'B9.5 RS5, updated styling and performance'}
                ],
                'is_active': True
            },
            {
                'name': 'RS6',
                'body_style': 'Wagon',
                'years': [
                    {'range': (2003, 2004), 'generation': 'C5', 'note': 'Twin-turbo V8, limited availability'},
                    {'range': (2020, 2022), 'generation': 'C8', 'note': 'Return to US, mild hybrid V8'},
                    {'range': (2023, 2025), 'generation': 'C8.5', 'note': 'C8.5 RS6, updated performance and technology'}
                ],
                'is_active': True
            },
            {
                'name': 'RS7',
                'body_style': 'Sportback',
                'years': [
                    {'range': (2014, 2014), 'generation': 'C7', 'note': 'Twin-turbo V8, first RS7'},
                    {'range': (2015, 2018), 'generation': 'C7.5', 'note': 'C7.5 RS7, updated styling and performance'},
                    {'range': (2020, 2022), 'generation': 'C8', 'note': 'Mild hybrid V8, new RS7'},
                    {'range': (2023, 2025), 'generation': 'C8.5', 'note': 'C8.5 RS7, updated performance and technology'}
                ],
                'is_active': True
            },
            {
                'name': 'RSQ8',
                'body_style': 'SUV',
                'years': [
                    {'range': (2020, 2022), 'generation': '4M', 'note': 'First RS SUV, twin-turbo V8'},
                    {'range': (2023, 2025), 'generation': '4M.5', 'note': '4M.5 RSQ8, updated performance and styling'}
                ],
                'is_active': True
            },
            
            # Electric Models (no .5 refreshes yet, too new)
            {
                'name': 'e-tron',
                'body_style': 'SUV',
                'years': [
                    {'range': (2019, 2025), 'generation': '', 'note': 'First all-electric Audi SUV'}
                ],
                'is_active': True
            },
            {
                'name': 'e-tron GT',
                'body_style': 'Sedan',
                'years': [
                    {'range': (2022, 2025), 'generation': '', 'note': 'Electric sports sedan, shared with Taycan'}
                ],
                'is_active': True
            }
        ]
        
        # Filter out discontinued models if not requested
        if not include_discontinued:
            audi_models = [model for model in audi_models if model.get('is_active', True)]
            self.stdout.write('Filtering to active models only')
        
        self.stdout.write(f'Processing {len(audi_models)} Audi models...')
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for model_data in audi_models:
            model_name = model_data['name']
            body_style = model_data['body_style']
            is_active = model_data['is_active']
            
            # Create the base model record
            if not dry_run:
                model_obj, created = Model.objects.get_or_create(
                    make=audi_make,
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
                    # Highlight .5 generations
                    if '.5' in generation:
                        gen_display = f" {generation} 🔄"
                    self.stdout.write(f'    {display_start}-{display_end}{gen_display}: {note}')
            
            # Show discontinuation info
            if 'discontinued' in model_data:
                self.stdout.write(f'    ⚠️  Discontinued: {model_data["discontinued"]}')
            
            self.stdout.write('')  # Blank line between models
        
        # Summary
        self.stdout.write('=' * 60)
        self.stdout.write('AUDI MODELS SUMMARY')
        self.stdout.write('=' * 60)
        
        if not dry_run:
            self.stdout.write(f'✓ Created: {created_count} models')
            self.stdout.write(f'↻ Updated: {updated_count} models') 
            self.stdout.write(f'- Existed: {skipped_count} models')
            self.stdout.write(f'📊 Total: {created_count + updated_count + skipped_count} models processed')
        else:
            self.stdout.write(f'📊 Would process: {len(audi_models)} models')
        
        # Show generation insights
        self.stdout.write('\\n🔍 GENERATION INSIGHTS:')
        self.stdout.write('Audi Platform Evolution with Mid-Cycle Refreshes (.5 Models):')
        self.stdout.write('• A4: B5→B6→B7→B8/B8.5→B9/B9.5→B10 (major refreshes every 3-4 years)')
        self.stdout.write('• A6: C5→C6/C6.5→C7/C7.5→C8/C8.5 (significant .5 updates)')
        self.stdout.write('• A8: D2→D3/D3.5→D4/D4.5→D5/D5.5 (flagship tech in refreshes)')
        self.stdout.write('• TT: 8N→8J/8J.5→8S/8S.5 (styling and tech updates)')
        self.stdout.write('• Q7: 4L/4L.5/4L.75→4M/4M.5 (multiple refreshes before redesign)')
        
        self.stdout.write('\\nMid-Cycle Refresh Impact:')
        self.stdout.write('• .5 Models: Significant styling, technology, and sometimes powertrain updates')
        self.stdout.write('• Parts Compatibility: .5 refreshes often require different parts (lights, bumpers, electronics)')
        self.stdout.write('• Technology Updates: MMI systems, virtual cockpit, LED lighting packages')
        self.stdout.write('• Performance Models: S/RS variants often get more significant .5 updates')
        
        self.stdout.write('\\nKey .5 Refresh Examples:')
        self.stdout.write('• B8.5 A4/S4 (2013): New MMI, LED DRLs, updated interior')
        self.stdout.write('• C7.5 A6/A7 (2015): Matrix LED headlights, virtual cockpit')
        self.stdout.write('• D4.5 A8 (2014): Matrix LED standard, updated MMI Touch')
        self.stdout.write('• 4L.5 Q7 (2010): Updated styling, efficiency improvements')
        
        # Next steps
        self.stdout.write('\\n📋 NEXT STEPS:')
        self.stdout.write('1. Run migrations: python manage.py makemigrations && python manage.py migrate')
        self.stdout.write('2. Add engines: python manage.py add_audi_engines')
        self.stdout.write('3. Add trims: python manage.py add_audi_trims')
        self.stdout.write('4. Create vehicles: python manage.py create_audi_vehicles')
        self.stdout.write('5. Note: .5 generation vehicles will have separate part fitments')
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'\\n🎉 Successfully processed {len(audi_models)} Audi models with .5 generation support!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('\\n⚠️  DRY RUN complete - run without --dry-run to save changes')
            )
