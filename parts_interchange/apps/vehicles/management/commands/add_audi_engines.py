# This goes in: parts_interchange/apps/vehicles/management/commands/add_audi_engines.py

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.vehicles.models import Engine


class Command(BaseCommand):
    help = 'Add Audi engines from 2000-2025 with detailed specifications'

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
        
        # Audi engines by generation and model years
        # Note: These are filter identifiers, not actual part numbers
        audi_engines = [
            # TFSI Turbo Engines (Current Era 2005+)
            {
                'name': '1.4L I4 TFSI Turbo',
                'displacement': 1.4,
                'cylinders': 4,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 150,
                'torque': 184,
                'engine_code': 'EA211',
                'models': ['A3 8Y base'],
                'years': '2021-2025',
                'notes': 'Miller cycle, mild hybrid standard'
            },
            {
                'name': '1.8L I4 TFSI Turbo',
                'displacement': 1.8,
                'cylinders': 4,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 170,
                'torque': 199,
                'engine_code': 'EA888 Gen 2',
                'models': ['A3 8P', 'A4 B8', 'TT 8J'],
                'years': '2009-2015',
                'notes': 'Second generation EA888, direct injection'
            },
            {
                'name': '2.0L I4 TFSI Turbo',
                'displacement': 2.0,
                'cylinders': 4,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 201,
                'torque': 236,
                'engine_code': 'EA888 Gen 3',
                'models': ['A3 8V', 'A4 B9', 'A5 B9', 'Q3 8Y', 'Q5 8Y'],
                'years': '2015-2025',
                'notes': 'Current base turbo engine, mild hybrid available'
            },
            {
                'name': '2.0L I4 TFSI Turbo High Output',
                'displacement': 2.0,
                'cylinders': 4,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 245,
                'torque': 273,
                'engine_code': 'EA888 Gen 3B',
                'models': ['S3 8Y', 'TT 8S'],
                'years': '2016-2025',
                'notes': 'Higher output tune, performance applications'
            },
            {
                'name': '2.5L I5 TFSI Turbo',
                'displacement': 2.5,
                'cylinders': 5,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 394,
                'torque': 354,
                'engine_code': 'DAZA',
                'models': ['RS3 8Y', 'TT RS 8S'],
                'years': '2017-2025',
                'notes': 'Iconic 5-cylinder sound, RS model exclusive'
            },
            
            # V6 TFSI Engines
            {
                'name': '3.0L V6 TFSI Turbo',
                'displacement': 3.0,
                'cylinders': 6,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 335,
                'torque': 369,
                'engine_code': 'EA839',
                'models': ['A4 S4 B9', 'A5 S5 B9', 'Q5 SQ5 8Y'],
                'years': '2018-2025',
                'notes': 'Replaced supercharged V6, mild hybrid'
            },
            {
                'name': '3.0L V6 TFSI Supercharged',
                'displacement': 3.0,
                'cylinders': 6,
                'fuel_type': 'GAS',
                'aspiration': 'SC',
                'horsepower': 333,
                'torque': 325,
                'engine_code': 'CGXC',
                'models': ['A4 S4 B8', 'A5 S5 B8', 'A6 C7', 'A7 C7'],
                'years': '2010-2017',
                'notes': 'Supercharged era before turbo return'
            },
            {
                'name': '2.9L V6 TFSI Twin-Turbo',
                'displacement': 2.9,
                'cylinders': 6,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 444,
                'torque': 443,
                'engine_code': 'EA839 evo',
                'models': ['RS4 B9', 'RS5 B9'],
                'years': '2018-2025',
                'notes': 'RS-specific tune, mild hybrid'
            },
            
            # V8 TFSI Engines
            {
                'name': '4.0L V8 TFSI Twin-Turbo',
                'displacement': 4.0,
                'cylinders': 8,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 444,
                'torque': 443,
                'engine_code': 'EA825',
                'models': ['A6 S6 C8', 'A7 S7 C8', 'A8 S8 D5'],
                'years': '2019-2025',
                'notes': 'Mild hybrid standard, cylinder deactivation'
            },
            {
                'name': '4.0L V8 TFSI Twin-Turbo High Output',
                'displacement': 4.0,
                'cylinders': 8,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 591,
                'torque': 590,
                'engine_code': 'EA825 evo',
                'models': ['RS6 C8', 'RS7 C8', 'RSQ8 4M'],
                'years': '2020-2025',
                'notes': 'RS-specific tune, anti-lag system'
            },
            
            # Older Twin-Turbo Engines
            {
                'name': '2.7L V6 Twin-Turbo',
                'displacement': 2.7,
                'cylinders': 6,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 250,
                'torque': 258,
                'engine_code': 'APJ/AZB',
                'models': ['S4 B5'],
                'years': '2000-2002',
                'notes': 'Bi-turbo V6, iconic B5 S4 engine'
            },
            {
                'name': '4.2L V8 Twin-Turbo',
                'displacement': 4.2,
                'cylinders': 8,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 450,
                'torque': 413,
                'engine_code': 'BCY',
                'models': ['RS6 C5'],
                'years': '2003-2004',
                'notes': 'Bi-turbo V8, first generation RS6'
            },
            
            # Older Naturally Aspirated Engines (2000-2005 era)
            {
                'name': '1.8L I4 Turbo',
                'displacement': 1.8,
                'cylinders': 4,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 150,
                'torque': 155,
                'engine_code': 'AWM/AMU',
                'models': ['A3 8L', 'A4 B6', 'TT 8N'],
                'years': '2000-2008',
                'notes': 'Original 1.8T, port injection'
            },
            {
                'name': '2.0L I4 FSI',
                'displacement': 2.0,
                'cylinders': 4,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 150,
                'torque': 140,
                'engine_code': 'BPY',
                'models': ['A3 8P', 'A4 B7'],
                'years': '2006-2008',
                'notes': 'First direct injection, naturally aspirated'
            },
            {
                'name': '3.2L V6 FSI',
                'displacement': 3.2,
                'cylinders': 6,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 255,
                'torque': 243,
                'engine_code': 'BKH',
                'models': ['A3 8P V6', 'A4 B7 V6', 'TT 8J V6'],
                'years': '2006-2012',
                'notes': 'Direct injection V6, quattro standard'
            },
            
            # V8 Engines (S/RS Models)
            {
                'name': '4.2L V8 FSI',
                'displacement': 4.2,
                'cylinders': 8,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 350,
                'torque': 302,
                'engine_code': 'BNS',
                'models': ['S4 B6/B7', 'S5 B8', 'A8 D3'],
                'years': '2004-2011',
                'notes': 'Naturally aspirated V8, characteristic sound'
            },
            {
                'name': '5.2L V10 FSI',
                'displacement': 5.2,
                'cylinders': 10,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 525,
                'torque': 391,
                'engine_code': 'BUJ',
                'models': ['R8 42 V10', 'S6 C6', 'S8 D3'],
                'years': '2007-2015',
                'notes': 'Lamborghini-derived V10'
            },
            {
                'name': '4.2L V8 FSI R8',
                'displacement': 4.2,
                'cylinders': 8,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 420,
                'torque': 317,
                'engine_code': 'BYH',
                'models': ['R8 42 V8'],
                'years': '2008-2012',
                'notes': 'R8-specific V8, dry sump lubrication'
            },
            
            # Diesel Engines (TDI)
            {
                'name': '2.0L I4 TDI Turbo',
                'displacement': 2.0,
                'cylinders': 4,
                'fuel_type': 'DSL',
                'aspiration': 'TC',
                'horsepower': 140,
                'torque': 236,
                'engine_code': 'CJAA',
                'models': ['A3 8P TDI', 'A4 B8 TDI', 'Q5 8R TDI'],
                'years': '2009-2015',
                'notes': 'Common rail diesel, discontinued in US after dieselgate'
            },
            {
                'name': '3.0L V6 TDI Turbo',
                'displacement': 3.0,
                'cylinders': 6,
                'fuel_type': 'DSL',
                'aspiration': 'TC',
                'horsepower': 240,
                'torque': 428,
                'engine_code': 'CATA',
                'models': ['A6 C7 TDI', 'A7 C7 TDI', 'A8 D4 TDI', 'Q7 4L TDI'],
                'years': '2011-2015',
                'notes': 'V6 diesel, high torque output'
            },
            
            # Hybrid and Electric Powertrains
            {
                'name': '2.0L I4 TFSI Hybrid',
                'displacement': 2.0,
                'cylinders': 4,
                'fuel_type': 'HYB',
                'aspiration': 'TC',
                'horsepower': 362,  # System total
                'torque': 369,
                'engine_code': 'EA888 + Motor',
                'models': ['A6 C8 TFSI e', 'A7 C7 e-tron', 'A8 D5 TFSI e'],
                'years': '2019-2025',
                'notes': 'Plug-in hybrid system, electric range ~25 miles'
            },
            {
                'name': '3.0L V6 TFSI Hybrid',
                'displacement': 3.0,
                'cylinders': 6,
                'fuel_type': 'HYB',
                'aspiration': 'TC',
                'horsepower': 443,  # System total
                'torque': 516,
                'engine_code': 'EA839 + Motor',
                'models': ['A8 D5 60 TFSI e'],
                'years': '2019-2025',
                'notes': 'Premium plug-in hybrid, long electric range'
            },
            {
                'name': 'Dual Motor Electric',
                'displacement': None,
                'cylinders': None,
                'fuel_type': 'ELC',
                'aspiration': None,
                'horsepower': 402,  # System total
                'torque': 490,
                'engine_code': 'Electric AWD',
                'models': ['e-tron 55'],
                'years': '2019-2025',
                'notes': 'Dual motor setup, ~250 mile range'
            },
            {
                'name': 'Triple Motor Electric',
                'displacement': None,
                'cylinders': None,
                'fuel_type': 'ELC',
                'aspiration': None,
                'horsepower': 469,  # System total
                'torque': 464,
                'engine_code': 'Electric Performance',
                'models': ['e-tron GT', 'RS e-tron GT'],
                'years': '2022-2025',
                'notes': 'Performance electric, shared with Porsche Taycan'
            },
            {
                'name': 'Single Motor Electric',
                'displacement': None,
                'cylinders': None,
                'fuel_type': 'ELC',
                'aspiration': None,
                'horsepower': 265,
                'torque': 339,
                'engine_code': 'Electric RWD',
                'models': ['Q4 e-tron 40'],
                'years': '2022-2025',
                'notes': 'Rear-wheel drive electric, entry e-tron'
            },
            {
                'name': 'Dual Motor Electric Compact',
                'displacement': None,
                'cylinders': None,
                'fuel_type': 'ELC',
                'aspiration': None,
                'horsepower': 265,
                'torque': 339,
                'engine_code': 'Electric AWD Compact',
                'models': ['Q4 e-tron 50'],
                'years': '2022-2025',
                'notes': 'All-wheel drive electric, compact SUV'
            },
            
            # Performance Engine Variants (additional power levels)
            {
                'name': '2.0L I4 TFSI Turbo 45 TFSI',
                'displacement': 2.0,
                'cylinders': 4,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 245,
                'torque': 273,
                'engine_code': 'EA888 Gen 3B',
                'models': ['A4 45 TFSI', 'A5 45 TFSI', 'Q5 45 TFSI'],
                'years': '2017-2025',
                'notes': 'Mid-level power tune'
            },
            {
                'name': '3.0L V6 TFSI Turbo 55 TFSI',
                'displacement': 3.0,
                'cylinders': 6,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 362,
                'torque': 369,
                'engine_code': 'EA839',
                'models': ['A6 55 TFSI', 'A7 55 TFSI', 'A8 55 TFSI'],
                'years': '2018-2025',
                'notes': 'Premium V6 power level'
            },
            
            # Special Edition Engines
            {
                'name': '2.5L I5 TFSI Turbo RS Performance',
                'displacement': 2.5,
                'cylinders': 5,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 401,
                'torque': 354,
                'engine_code': 'DAZA+',
                'models': ['RS3 Performance'],
                'years': '2022-2025',
                'notes': 'Limited edition higher output'
            },
            {
                'name': '4.0L V8 TFSI Twin-Turbo RS Performance',
                'displacement': 4.0,
                'cylinders': 8,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 630,
                'torque': 627,
                'engine_code': 'EA825 evo+',
                'models': ['RS6 Performance', 'RS7 Performance'],
                'years': '2023-2025',
                'notes': 'Ultimate RS power level'
            }
        ]
        
        self.stdout.write(f'Processing {len(audi_engines)} Audi engines...')
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for engine_data in audi_engines:
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
                    
                    # Only set aspiration if it's not None (let model default handle None case)
                    if engine_data.get('aspiration') is not None:
                        engine_kwargs['aspiration'] = engine_data['aspiration']
                    
                    Engine.objects.create(**engine_kwargs)
                    created_count += 1
                    status = '✓ CREATED'
            else:
                status = '? DRY RUN'
            
            # Display engine info
            disp_str = f"{engine_data.get('displacement', 'Electric')}L" if engine_data.get('displacement') else "Electric"
            cyl_str = f"V{engine_data.get('cylinders', 'E')}" if engine_data.get('cylinders') else "Electric"
            hp_str = f"{engine_data.get('horsepower', '?')}hp" if engine_data.get('horsepower') else ""
            
            self.stdout.write(f'{status} {engine_name}')
            self.stdout.write(f'    {disp_str} {cyl_str} | {hp_str} | {engine_data["engine_code"]}')
            self.stdout.write(f'    Models: {", ".join(engine_data["models"])}')
            self.stdout.write(f'    Years: {engine_data["years"]} | {engine_data["notes"]}')
            self.stdout.write('')  # Blank line
        
        # Summary
        self.stdout.write('=' * 60)
        self.stdout.write('AUDI ENGINES SUMMARY')
        self.stdout.write('=' * 60)
        
        if not dry_run:
            self.stdout.write(f'✓ Created: {created_count} engines')
            self.stdout.write(f'↻ Updated: {updated_count} engines')
            self.stdout.write(f'- Existed: {skipped_count} engines')
            self.stdout.write(f'📊 Total: {created_count + updated_count + skipped_count} engines processed')
        else:
            self.stdout.write(f'📊 Would process: {len(audi_engines)} engines')
        
        # Engine insights
        self.stdout.write('\\n🔍 ENGINE INSIGHTS:')
        self.stdout.write('Audi Engine Families:')
        self.stdout.write('• EA888: 1.8L-2.0L TFSI (2009-present) - Most common')
        self.stdout.write('• EA839: 3.0L V6 TFSI (2016-present) - Current V6')
        self.stdout.write('• EA825: 4.0L V8 TFSI (2019-present) - Current V8')
        self.stdout.write('• DAZA: 2.5L I5 TFSI (2017-present) - RS models')
        
        self.stdout.write('\\nPower Evolution:')
        self.stdout.write('• 2000-2005: NA engines (1.8T transition period)')
        self.stdout.write('• 2006-2010: FSI direct injection introduction')
        self.stdout.write('• 2010-2017: TFSI turbo + supercharged V6 era')
        self.stdout.write('• 2018+: All turbo, mild hybrid integration')
        self.stdout.write('• 2019+: Electric powertrains (e-tron lineup)')
        
        self.stdout.write('\\nCurrent Hierarchy:')
        self.stdout.write('• Entry: 1.4L TFSI (mild hybrid)')
        self.stdout.write('• Volume: 2.0L TFSI (201-245hp variants)')
        self.stdout.write('• Performance: 3.0L V6 TFSI (335hp), 2.9L V6 (444hp)')
        self.stdout.write('• Ultimate: 4.0L V8 TFSI (444-630hp), 2.5L I5 (394-401hp)')
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'\\n🎉 Successfully processed {len(audi_engines)} Audi engines!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('\\n⚠️  DRY RUN complete - run without --dry-run to save changes')
            )
