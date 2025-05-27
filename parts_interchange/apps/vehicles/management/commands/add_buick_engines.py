from django.core.management.base import BaseCommand
from django.db import transaction
from apps.vehicles.models import Engine


class Command(BaseCommand):
    help = 'Add Buick engines from 2000-2025 with detailed specifications'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without making changes'
        )
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='Update existing engine records with new data'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        update_existing = options['update_existing']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No data will be saved'))
        
        # Buick engines by generation and model years
        buick_engines = [
            # I3 Engines
            {
                'name': '1.2L I3 LIH Turbo',
                'displacement': 1.2,
                'cylinders': 3,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 137,
                'torque': 162,
                'engine_code': 'LIH',
                'models': ['Encore GX'],
                'years': '2020-2025',
                'notes': 'Smallest engine for Encore GX'
            },
            {
                'name': '1.3L I3 L3T Turbo',
                'displacement': 1.3,
                'cylinders': 3,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 155,
                'torque': 174,
                'engine_code': 'L3T',
                'models': ['Encore GX'],
                'years': '2020-2025',
                'notes': 'Larger 3-cylinder for Encore GX'
            },
            
            # I4 Engines
            {
                'name': '1.4L I4 LUJ Turbo',
                'displacement': 1.4,
                'cylinders': 4,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 138,
                'torque': 148,
                'engine_code': 'LUJ',
                'models': ['Encore'],
                'years': '2013-2016',
                'notes': 'Turbocharged 4-cylinder for Encore'
            },
            {
                'name': '1.4L I4 LE2 Turbo',
                'displacement': 1.4,
                'cylinders': 4,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 153,
                'torque': 177,
                'engine_code': 'LE2',
                'models': ['Encore'],
                'years': '2017-2022',
                'notes': 'Updated turbocharged 4-cylinder for Encore'
            },
            {
                'name': '1.6L I4 LWC Turbo',
                'displacement': 1.6,
                'cylinders': 4,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 200,
                'torque': 207,
                'engine_code': 'LWC',
                'models': ['Cascada'],
                'years': '2016-2019',
                'notes': 'Turbocharged 4-cylinder for Cascada'
            },
            {
                'name': '2.0L I4 LHU Turbo',
                'displacement': 2.0,
                'cylinders': 4,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 220,
                'torque': 258,
                'engine_code': 'LHU',
                'models': ['Regal'],
                'years': '2011-2013',
                'notes': 'Turbocharged 4-cylinder for Regal'
            },
            {
                'name': '2.0L I4 LTG Turbo',
                'displacement': 2.0,
                'cylinders': 4,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 259,
                'torque': 295,
                'engine_code': 'LTG',
                'models': ['Regal', 'Verano', 'Envision'],
                'years': '2014-2020',
                'notes': 'Higher output turbocharged 4-cylinder'
            },
            {
                'name': '2.0L I4 LSY Turbo',
                'displacement': 2.0,
                'cylinders': 4,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 228,
                'torque': 258,
                'engine_code': 'LSY',
                'models': ['Envision'],
                'years': '2021-2025',
                'notes': 'Latest turbocharged 4-cylinder for Envision'
            },
            {
                'name': '2.4L I4 LEA',
                'displacement': 2.4,
                'cylinders': 4,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 180,
                'torque': 171,
                'engine_code': 'LEA',
                'models': ['Verano', 'Regal'],
                'years': '2011-2017',
                'notes': 'Naturally aspirated 4-cylinder'
            },
            {
                'name': '2.4L I4 LAF',
                'displacement': 2.4,
                'cylinders': 4,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 182,
                'torque': 172,
                'engine_code': 'LAF',
                'models': ['LaCrosse', 'Regal'],
                'years': '2010-2016',
                'notes': 'Naturally aspirated 4-cylinder with eAssist'
            },
            {
                'name': '2.5L I4 LCV',
                'displacement': 2.5,
                'cylinders': 4,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 194,
                'torque': 187,
                'engine_code': 'LCV',
                'models': ['LaCrosse', 'Envision'],
                'years': '2016-2020',
                'notes': 'Naturally aspirated 4-cylinder'
            },
            {
                'name': '3.1L V6 LG8',
                'displacement': 3.1,
                'cylinders': 6,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 175,
                'torque': 195,
                'engine_code': 'LG8',
                'models': ['Century'],
                'years': '2000-2005',
                'notes': 'Naturally aspirated V6'
            },
            {
                'name': '3.4L V6 LA1',
                'displacement': 3.4,
                'cylinders': 6,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 185,
                'torque': 210,
                'engine_code': 'LA1',
                'models': ['Rendezvous'],
                'years': '2002-2007',
                'notes': 'Naturally aspirated V6'
            },
            {
                'name': '3.5L V6 LX9',
                'displacement': 3.5,
                'cylinders': 6,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 200,
                'torque': 220,
                'engine_code': 'LX9',
                'models': ['Terraza'],
                'years': '2005-2007',
                'notes': 'Naturally aspirated V6'
            },
            {
                'name': '3.6L V6 LY7',
                'displacement': 3.6,
                'cylinders': 6,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 240,
                'torque': 223,
                'engine_code': 'LY7',
                'models': ['LaCrosse', 'Rendezvous'],
                'years': '2005-2009',
                'notes': 'Naturally aspirated V6'
            },
            {
                'name': '3.6L V6 LLT',
                'displacement': 3.6,
                'cylinders': 6,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 280,
                'torque': 259,
                'engine_code': 'LLT',
                'models': ['LaCrosse', 'Enclave'],
                'years': '2009-2012',
                'notes': 'Naturally aspirated V6 with direct injection'
            },
            {
                'name': '3.6L V6 LFX',
                'displacement': 3.6,
                'cylinders': 6,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 304,
                'torque': 264,
                'engine_code': 'LFX',
                'models': ['LaCrosse', 'Enclave'],
                'years': '2012-2017',
                'notes': 'Updated naturally aspirated V6 with direct injection'
            },
            {
                'name': '3.6L V6 LGX',
                'displacement': 3.6,
                'cylinders': 6,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 310,
                'torque': 282,
                'engine_code': 'LGX',
                'models': ['Enclave', 'LaCrosse'],
                'years': '2017-2025',
                'notes': 'Latest naturally aspirated V6'
            },
            {
                'name': '3.8L V6 L36',
                'displacement': 3.8,
                'cylinders': 6,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 205,
                'torque': 230,
                'engine_code': 'L36',
                'models': ['LaCrosse', 'Lucerne', 'LeSabre', 'Park Avenue'],
                'years': '2000-2009',
                'notes': 'Naturally aspirated V6, very common GM engine'
            },
            {
                'name': '3.8L V6 L67 Supercharged',
                'displacement': 3.8,
                'cylinders': 6,
                'fuel_type': 'GAS',
                'aspiration': 'SC',
                'horsepower': 240,
                'torque': 280,
                'engine_code': 'L67',
                'models': ['Park Avenue'],
                'years': '2000-2005',
                'notes': 'Supercharged V6'
            },
            {
                'name': '3.9L V6 LZ9',
                'displacement': 3.9,
                'cylinders': 6,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 240,
                'torque': 240,
                'engine_code': 'LZ9',
                'models': ['Terraza'],
                'years': '2006-2007',
                'notes': 'Naturally aspirated V6'
            },
            
            # I6 Engines
            {
                'name': '4.2L I6 LL8',
                'displacement': 4.2,
                'cylinders': 6,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 275,
                'torque': 275,
                'engine_code': 'LL8',
                'models': ['Rainier'],
                'years': '2004-2007',
                'notes': 'Naturally aspirated I6 for SUVs'
            },
            
            # V8 Engines
            {
                'name': '4.6L V8 LH2',
                'displacement': 4.6,
                'cylinders': 8,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 275,
                'torque': 295,
                'engine_code': 'LH2',
                'models': ['Lucerne'],
                'years': '2006-2011',
                'notes': 'Northstar V8 engine'
            },
            {
                'name': '5.3L V8 LM4',
                'displacement': 5.3,
                'cylinders': 8,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 290,
                'torque': 325,
                'engine_code': 'LM4',
                'models': ['Rainier'],
                'years': '2004-2007',
                'notes': 'Naturally aspirated V8 for SUVs'
            }
        ]
        
        self.stdout.write(f'Processing {len(buick_engines)} Buick engines...')
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for engine_data in buick_engines:
            engine_name = engine_data['name']
            
            if not dry_run:
                # Check if engine already exists
                existing_engines = Engine.objects.filter(name=engine_name)
                
                if existing_engines.exists():
                    if update_existing:
                        engine_obj = existing_engines.first()
                        # Update fields
                        engine_obj.displacement = engine_data.get('displacement')
                        engine_obj.cylinders = engine_data.get('cylinders')
                        engine_obj.fuel_type = engine_data['fuel_type']
                        # Only update aspiration if it's not None
                        if engine_data.get('aspiration') is not None:
                            engine_obj.aspiration = engine_data['aspiration']
                        engine_obj.horsepower = engine_data.get('horsepower')
                        engine_obj.torque = engine_data.get('torque')
                        engine_obj.engine_code = engine_data['engine_code']
                        engine_obj.save()
                        updated_count += 1
                        status = '↻ UPDATED'
                    else:
                        skipped_count += 1
                        status = '- EXISTS'
                else:
                    # Create new engine
                    engine_kwargs = {
                        'name': engine_name,
                        'displacement': engine_data.get('displacement'),
                        'cylinders': engine_data.get('cylinders'),
                        'fuel_type': engine_data['fuel_type'],
                        'horsepower': engine_data.get('horsepower'),
                        'torque': engine_data.get('torque'),
                        'engine_code': engine_data['engine_code']
                    }
                    
                    # Only set aspiration if it's not None
                    if engine_data.get('aspiration') is not None:
                        engine_kwargs['aspiration'] = engine_data['aspiration']
                    
                    Engine.objects.create(**engine_kwargs)
                    created_count += 1
                    status = '✓ CREATED'
            else:
                status = '? DRY RUN'
            
            # Display engine info
            disp_str = f"{engine_data.get('displacement', 'Electric')}L" if engine_data.get('displacement') else "Electric"
            cyl_str = f"{engine_data.get('cylinders', 'E')}-Cyl" if engine_data.get('cylinders') else "Electric"
            hp_str = f"{engine_data.get('horsepower', '?')}hp" if engine_data.get('horsepower') else ""
            
            self.stdout.write(f'{status} {engine_name}')
            self.stdout.write(f'    {disp_str} {cyl_str} | {hp_str} | {engine_data["engine_code"]}')
            self.stdout.write(f'    Models: {", ".join(engine_data["models"][:3])}{"..." if len(engine_data["models"]) > 3 else ""}')
            self.stdout.write(f'    Years: {engine_data["years"]} | {engine_data["notes"]}')
            self.stdout.write('')  # Blank line
        
        # Summary
        self.stdout.write('=' * 60)
        self.stdout.write('BUICK ENGINES SUMMARY')
        self.stdout.write('=' * 60)
        
        if not dry_run:
            self.stdout.write(f'✓ Created: {created_count} engines')
            self.stdout.write(f'↻ Updated: {updated_count} engines')
            self.stdout.write(f'- Existed: {skipped_count} engines')
            self.stdout.write(f'📊 Total: {created_count + updated_count + skipped_count} engines processed')
        else:
            self.stdout.write(f'📊 Would process: {len(buick_engines)} engines')
        
        # Engine insights
        self.stdout.write('\n🔍 ENGINE INSIGHTS:')
        self.stdout.write('Buick Engine Evolution:')
        self.stdout.write('• Early 2000s: Focus on naturally aspirated V6s (3.1L, 3.4L, 3.8L)')
        self.stdout.write('• Mid 2000s: Introduction of 3.6L V6 (LY7, LLT, LFX, LGX) and some V8s (4.6L, 5.3L)')
        self.stdout.write('• 2010s: Shift towards smaller displacement turbocharged I4s (1.4L, 1.6L, 2.0L)')
        self.stdout.write('• Current: Continued use of 3.6L V6 and modern turbocharged I3/I4 engines')
        
        self.stdout.write('\nKey Buick Engine Families:')
        self.stdout.write('• 3.8L V6 (L36/L67): Workhorse engine, very common in older models')
        self.stdout.write('• 3.6L V6 (LLT/LFX/LGX): Modern V6, widely used in larger models like Enclave and LaCrosse')
        self.stdout.write('• 2.0L Turbo I4 (LTG/LSY): Performance and efficiency option in Regal and Envision')
        self.stdout.write('• 1.X L Turbo I3/I4: Smaller, efficient engines for compact SUVs like Encore/Encore GX')
        
        self.stdout.write('\nPowertrain Trends:')
        self.stdout.write('• Downsizing: Smaller engines with turbocharging for efficiency')
        self.stdout.write('• V6 Dominance: Historically, V6 engines were the core of Buick lineup')
        self.stdout.write('• SUV Focus: Current engine lineup heavily favors SUVs')
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'\n🎉 Successfully processed {len(buick_engines)} Buick engines!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('\n⚠️  DRY RUN complete - run without --dry-run to save changes')
            )
