# This goes in: parts_interchange/apps/vehicles/management/commands/add_bmw_engines.py

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.vehicles.models import Engine


class Command(BaseCommand):
    help = 'Add BMW engines from 2000-2025 with detailed specifications'

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
        
        # BMW engines by generation and model years
        bmw_engines = [
            # N Series Naturally Aspirated Engines (2000s-2010s)
            {
                'name': '2.0L I4 N46',
                'displacement': 2.0,
                'cylinders': 4,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 150,
                'torque': 148,
                'engine_code': 'N46B20',
                'models': ['1 Series E87', '3 Series E46', 'X3 E83'],
                'years': '2004-2011',
                'notes': 'Naturally aspirated 4-cylinder, Valvetronic'
            },
            {
                'name': '2.5L I6 N52',
                'displacement': 2.5,
                'cylinders': 6,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 218,
                'torque': 185,
                'engine_code': 'N52B25',
                'models': ['3 Series E90', '5 Series E60', 'X3 E83'],
                'years': '2005-2013',
                'notes': 'Magnesium/aluminum construction, last naturally aspirated BMW I6'
            },
            {
                'name': '3.0L I6 N52',
                'displacement': 3.0,
                'cylinders': 6,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 255,
                'torque': 220,
                'engine_code': 'N52B30',
                'models': ['3 Series E90', '5 Series E60', 'X3 E83', 'X5 E70'],
                'years': '2005-2013',
                'notes': 'Most common N52, smooth and reliable naturally aspirated I6'
            },
            {
                'name': '3.0L I6 N53',
                'displacement': 3.0,
                'cylinders': 6,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 272,
                'torque': 236,
                'engine_code': 'N53B30',
                'models': ['3 Series E90', '5 Series E60', '7 Series F01'],
                'years': '2007-2012',
                'notes': 'Direct injection naturally aspirated, Europe mainly'
            },
            {
                'name': '4.4L V8 N62',
                'displacement': 4.4,
                'cylinders': 8,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 325,
                'torque': 330,
                'engine_code': 'N62B44',
                'models': ['5 Series E60', '6 Series E63', '7 Series E65', 'X5 E53'],
                'years': '2003-2010',
                'notes': 'Naturally aspirated V8, Valvetronic and Double-VANOS'
            },
            
            # N Series Turbocharged Engines
            {
                'name': '2.0L I4 N20 Turbo',
                'displacement': 2.0,
                'cylinders': 4,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 241,
                'torque': 258,
                'engine_code': 'N20B20',
                'models': ['3 Series F30', '4 Series F32', '5 Series F10'],
                'years': '2011-2016',
                'notes': 'First turbo 4-cylinder in modern BMW, twin-scroll turbo'
            },
            {
                'name': '3.0L I6 N54 Twin-Turbo',
                'displacement': 3.0,
                'cylinders': 6,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 300,
                'torque': 300,
                'engine_code': 'N54B30',
                'models': ['3 Series E90', '5 Series E60', '7 Series F01', 'X6 E71'],
                'years': '2006-2016',
                'notes': 'Twin-turbo I6, high performance potential, tuner favorite'
            },
            {
                'name': '3.0L I6 N55 Single-Turbo',
                'displacement': 3.0,
                'cylinders': 6,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 306,
                'torque': 295,
                'engine_code': 'N55B30',
                'models': ['3 Series F30', '4 Series F32', '5 Series F10', 'X3 F25', 'X5 F15'],
                'years': '2009-2016',
                'notes': 'Single twin-scroll turbo, replaced N54 for better emissions'
            },
            
            # B Series Modern Turbocharged Engines (2014+)
            {
                'name': '2.0L I4 B46 Turbo',
                'displacement': 2.0,
                'cylinders': 4,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 248,
                'torque': 258,
                'engine_code': 'B46B20',
                'models': ['3 Series G20', '4 Series G22', 'X3 G01', 'X4 G02'],
                'years': '2016-2025',
                'notes': 'Current base turbo engine, modular B-series architecture'
            },
            {
                'name': '2.0L I4 B48 Turbo',
                'displacement': 2.0,
                'cylinders': 4,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 255,
                'torque': 295,
                'engine_code': 'B48B20',
                'models': ['3 Series G20', '4 Series G22', '5 Series G30', 'X3 G01'],
                'years': '2014-2025',
                'notes': 'Higher output B-series, twin-scroll turbo with mild hybrid'
            },
            {
                'name': '3.0L I6 B58 Single-Turbo',
                'displacement': 3.0,
                'cylinders': 6,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 335,
                'torque': 330,
                'engine_code': 'B58B30',
                'models': ['3 Series G20', '4 Series G22', '5 Series G30', 'X3 G01', 'X5 G05'],
                'years': '2015-2025',
                'notes': 'Current BMW I6 turbo, excellent balance of power and efficiency'
            },
            {
                'name': '3.0L I6 B58 High Output',
                'displacement': 3.0,
                'cylinders': 6,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 382,
                'torque': 369,
                'engine_code': 'B58B30O1',
                'models': ['M340i', 'M440i', 'X3 M40i', 'X5 M50i'],
                'years': '2019-2025',
                'notes': 'Higher tune of B58, M Performance models'
            },
            
            # S Series M Division Engines
            {
                'name': '3.0L I6 S55 Twin-Turbo',
                'displacement': 3.0,
                'cylinders': 6,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 425,
                'torque': 406,
                'engine_code': 'S55B30',
                'models': ['M3 F80', 'M4 F82', 'M2 Competition F87'],
                'years': '2014-2020',
                'notes': 'M Division twin-turbo I6, replaced naturally aspirated V8'
            },
            {
                'name': '3.0L I6 S58 Twin-Turbo',
                'displacement': 3.0,
                'cylinders': 6,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 473,
                'torque': 406,
                'engine_code': 'S58B30',
                'models': ['M3 G80', 'M4 G82', 'X3 M F97', 'X4 M F98'],
                'years': '2019-2025',
                'notes': 'Latest M Division I6, most powerful BMW 6-cylinder'
            },
            
            # V8 Engines (N/S Series)
            {
                'name': '4.8L V8 N62',
                'displacement': 4.8,
                'cylinders': 8,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 360,
                'torque': 360,
                'engine_code': 'N62B48',
                'models': ['5 Series E60', '6 Series E63', '7 Series E65', 'X5 E70'],
                'years': '2005-2010',
                'notes': 'Larger displacement naturally aspirated V8'
            },
            {
                'name': '4.4L V8 N63 Twin-Turbo',
                'displacement': 4.4,
                'cylinders': 8,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 400,
                'torque': 450,
                'engine_code': 'N63B44',
                'models': ['5 Series F10', '7 Series F01', 'X5 F15', 'X6 F16'],
                'years': '2008-2016',
                'notes': 'First generation twin-turbo V8, hot-V design'
            },
            {
                'name': '4.4L V8 N63TU Twin-Turbo',
                'displacement': 4.4,
                'cylinders': 8,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 445,
                'torque': 480,
                'engine_code': 'N63B44TU',
                'models': ['5 Series G30', '7 Series G11', 'X5 G05', 'X6 G06', 'X7 G07'],
                'years': '2016-2025',
                'notes': 'Updated N63 with reliability improvements'
            },
            {
                'name': '4.4L V8 S63 Twin-Turbo',
                'displacement': 4.4,
                'cylinders': 8,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 560,
                'torque': 500,
                'engine_code': 'S63B44',
                'models': ['M5 F10', 'M6 F12', 'X5 M F85', 'X6 M F86'],
                'years': '2011-2017',
                'notes': 'M Division high-performance V8'
            },
            {
                'name': '4.4L V8 S63TU Twin-Turbo',
                'displacement': 4.4,
                'cylinders': 8,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 617,
                'torque': 553,
                'engine_code': 'S63B44TU',
                'models': ['M5 F90', 'M8 F91', 'X5 M F95', 'X6 M F96'],
                'years': '2017-2025',
                'notes': 'Latest M Division V8, most powerful BMW engine'
            },
            
            # V10 and V12 Engines (Limited Production)
            {
                'name': '5.0L V10 S85',
                'displacement': 5.0,
                'cylinders': 10,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 507,
                'torque': 384,
                'engine_code': 'S85B50',
                'models': ['M5 E60', 'M6 E63'],
                'years': '2005-2010',
                'notes': 'Formula 1-derived V10, naturally aspirated high-revving'
            },
            {
                'name': '6.0L V12 N73',
                'displacement': 6.0,
                'cylinders': 12,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 438,
                'torque': 444,
                'engine_code': 'N73B60',
                'models': ['7 Series E65', '8 Series E31'],
                'years': '2002-2012',
                'notes': 'Naturally aspirated V12 flagship engine'
            },
            {
                'name': '6.0L V12 N74 Twin-Turbo',
                'displacement': 6.0,
                'cylinders': 12,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 535,
                'torque': 550,
                'engine_code': 'N74B60',
                'models': ['7 Series F01', '8 Series G14'],
                'years': '2009-2025',
                'notes': 'Twin-turbo V12, ultimate luxury power'
            },
            {
                'name': '6.6L V12 N74 Twin-Turbo',
                'displacement': 6.6,
                'cylinders': 12,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 601,
                'torque': 590,
                'engine_code': 'N74B66',
                'models': ['M760i G11'],
                'years': '2016-2022',
                'notes': 'Higher displacement N74 for M Performance V12'
            },
            
            # Diesel Engines (Europe/Limited US)
            {
                'name': '2.0L I4 N47 Turbo Diesel',
                'displacement': 2.0,
                'cylinders': 4,
                'fuel_type': 'DSL',
                'aspiration': 'TC',
                'horsepower': 177,
                'torque': 258,
                'engine_code': 'N47D20',
                'models': ['3 Series E90', '5 Series F10', 'X3 E83'],
                'years': '2007-2014',
                'notes': 'Common rail diesel, Europe and limited US market'
            },
            {
                'name': '2.0L I4 B47 Turbo Diesel',
                'displacement': 2.0,
                'cylinders': 4,
                'fuel_type': 'DSL',
                'aspiration': 'TC',
                'horsepower': 190,
                'torque': 295,
                'engine_code': 'B47D20',
                'models': ['1 Series F20', '2 Series F22', '3 Series F30', '4 Series F32', '5 Series G30', 'X1 F48', 'X3 G01'],
                'years': '2014-2025',
                'notes': 'Modular B-series diesel, replaced N47'
            },
            {
                'name': '3.0L I6 N57 Turbo Diesel',
                'displacement': 3.0,
                'cylinders': 6,
                'fuel_type': 'DSL',
                'aspiration': 'TC',
                'horsepower': 258,
                'torque': 413,
                'engine_code': 'N57D30',
                'models': ['5 Series F10', '7 Series F01', 'X5 F15', 'X6 F16'],
                'years': '2008-2018',
                'notes': 'BMW I6 diesel, high torque output'
            },
            {
                'name': '3.0L I6 B57 Turbo Diesel',
                'displacement': 3.0,
                'cylinders': 6,
                'fuel_type': 'DSL',
                'aspiration': 'TC',
                'horsepower': 265,
                'torque': 457,
                'engine_code': 'B57D30',
                'models': ['5 Series G30', '7 Series G11', 'X5 G05', 'X7 G07'],
                'years': '2015-2025',
                'notes': 'Modular B-series diesel, replaced N57, often with mild hybrid'
            },
            
            # Hybrid Powertrains
            {
                'name': '2.0L I4 B46 Hybrid',
                'displacement': 2.0,
                'cylinders': 4,
                'fuel_type': 'HYB',
                'aspiration': 'TC',
                'horsepower': 241,  # System total
                'torque': 295,
                'engine_code': 'B46B20 + eDrive',
                'models': ['3 Series G20 330e', '5 Series G30 530e'],
                'years': '2019-2025',
                'notes': 'Plug-in hybrid system, electric range ~20 miles'
            },
            {
                'name': '3.0L I6 B58 Hybrid',
                'displacement': 3.0,
                'cylinders': 6,
                'fuel_type': 'HYB',
                'aspiration': 'TC',
                'horsepower': 389,  # System total
                'torque': 443,
                'engine_code': 'B58B30 + eDrive',
                'models': ['5 Series G30 545e', '7 Series G11 745e', 'X5 G05 xDrive45e'],
                'years': '2019-2025',
                'notes': 'Performance plug-in hybrid, longer electric range'
            },
            
            # Electric Powertrains (i Series)
            {
                'name': 'eDrive40 Single Motor Electric',
                'displacement': None,
                'cylinders': None,
                'fuel_type': 'ELC',
                'aspiration': None,
                'horsepower': 335,
                'torque': 317,
                'engine_code': 'eDrive40',
                'models': ['i4 G26', 'i5 G60', 'iX1 U11'],
                'years': '2021-2025',
                'notes': 'Single rear motor, balanced performance and range'
            },
            {
                'name': 'eDrive50 Dual Motor Electric',
                'displacement': None,
                'cylinders': None,
                'fuel_type': 'ELC',
                'aspiration': None,
                'horsepower': 516,
                'torque': 564,
                'engine_code': 'eDrive50',
                'models': ['iX G09', 'i4 G26', 'i5 G60', 'i7 G70'],
                'years': '2021-2025',
                'notes': 'Dual motor AWD, higher performance and range'
            },
            {
                'name': 'eDrive60 Dual Motor Electric',
                'displacement': None,
                'cylinders': None,
                'fuel_type': 'ELC',
                'aspiration': None,
                'horsepower': 590,
                'torque': 586,
                'engine_code': 'eDrive60',
                'models': ['i7 G70', 'iX G09'],
                'years': '2022-2025',
                'notes': 'High-performance dual motor, flagship electric models'
            },
            {
                'name': 'eDrive M60 Dual Motor Electric',
                'displacement': None,
                'cylinders': None,
                'fuel_type': 'ELC',
                'aspiration': None,
                'horsepower': 610,
                'torque': 811,
                'engine_code': 'eDrive M60',
                'models': ['iX M60', 'i4 M50', 'i5 M60'],
                'years': '2022-2025',
                'notes': 'M Performance electric, highest output'
            },
            {
                'name': 'eDrive M70 Dual Motor Electric',
                'displacement': None,
                'cylinders': None,
                'fuel_type': 'ELC',
                'aspiration': None,
                'horsepower': 650, # Approximate, based on i7 M70
                'torque': 749, # Approximate, based on i7 M70
                'engine_code': 'eDrive M70',
                'models': ['i7 M70 G70'],
                'years': '2023-2025',
                'notes': 'High-performance electric for flagship M models'
            },
            
            # Special/Limited Edition Engines
            {
                'name': '3.2L I6 S54',
                'displacement': 3.2,
                'cylinders': 6,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 333,
                'torque': 262,
                'engine_code': 'S54B32',
                'models': ['M3 E46', 'Z4 M E85/E86'],
                'years': '2000-2008',
                'notes': 'High-revving naturally aspirated I6, individual throttle bodies'
            },
            {
                'name': '5.0L V8 S62',
                'displacement': 5.0,
                'cylinders': 8,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 394,
                'torque': 369,
                'engine_code': 'S62B50',
                'models': ['M5 E39', 'Z8 E52'],
                'years': '1998-2003',
                'notes': 'Naturally aspirated V8, individual throttle bodies'
            },
            {
                'name': '4.0L V8 S65 High-Rev',
                'displacement': 4.0,
                'cylinders': 8,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 414,
                'torque': 295,
                'engine_code': 'S65B40',
                'models': ['M3 E90', 'M3 E92', 'M3 E93'],
                'years': '2007-2013',
                'notes': 'High-revving naturally aspirated V8, 8400 RPM redline'
            },
            {
                'name': '1.5L I3 B38 Turbo',
                'displacement': 1.5,
                'cylinders': 3,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 136,
                'torque': 162,
                'engine_code': 'B38B15',
                'models': ['2 Series Active Tourer', '1 Series F20', 'X1 F48'],
                'years': '2014-2025',
                'notes': '3-cylinder turbo, used in various FWD models'
            },
            {
                'name': '1.5L I3 B38 Hybrid',
                'displacement': 1.5,
                'cylinders': 3,
                'fuel_type': 'HYB',
                'aspiration': 'TC',
                'horsepower': 220, # System total for i8, 225xe
                'torque': 280,
                'engine_code': 'B38B15 + eDrive',
                'models': ['i8 I12', '2 Series Active Tourer 225xe'],
                'years': '2014-2020',
                'notes': '3-cylinder turbo combined with electric motor for hybrid applications'
            }
        ]
        
        self.stdout.write(f'Processing {len(bmw_engines)} BMW engines...')
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for engine_data in bmw_engines:
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
            cyl_str = f"V{engine_data.get('cylinders', 'E')}" if engine_data.get('cylinders') else "Electric"
            hp_str = f"{engine_data.get('horsepower', '?')}hp" if engine_data.get('horsepower') else ""
            
            self.stdout.write(f'{status} {engine_name}')
            self.stdout.write(f'    {disp_str} {cyl_str} | {hp_str} | {engine_data["engine_code"]}')
            self.stdout.write(f'    Models: {", ".join(engine_data["models"][:3])}{"..." if len(engine_data["models"]) > 3 else ""}')
            self.stdout.write(f'    Years: {engine_data["years"]} | {engine_data["notes"]}')
            self.stdout.write('')  # Blank line
        
        # Summary
        self.stdout.write('=' * 60)
        self.stdout.write('BMW ENGINES SUMMARY')
        self.stdout.write('=' * 60)
        
        if not dry_run:
            self.stdout.write(f'✓ Created: {created_count} engines')
            self.stdout.write(f'↻ Updated: {updated_count} engines')
            self.stdout.write(f'- Existed: {skipped_count} engines')
            self.stdout.write(f'📊 Total: {created_count + updated_count + skipped_count} engines processed')
        else:
            self.stdout.write(f'📊 Would process: {len(bmw_engines)} engines')
        
        # Engine insights
        self.stdout.write('\n🔍 ENGINE INSIGHTS:')
        self.stdout.write('BMW Engine Evolution:')
        self.stdout.write('• N-Series (2000-2015): N52 NA I6 → N54/N55 Turbo I6 → N20 Turbo I4')
        self.stdout.write('• B-Series (2014+): B46/B48 Turbo I4 → B58 Turbo I6 (current)')
        self.stdout.write('• S-Series M: S85 V10 → S65 V8 → S55/S58 Turbo I6 → S63 V8')
        self.stdout.write('• V12 Flagship: N73 NA → N74 Twin-Turbo (7/8 Series)')
        
        self.stdout.write('\nKey BMW Engine Families:')
        self.stdout.write('• B58: Current turbo I6 (335-382hp), excellent tuning potential')
        self.stdout.write('• N55: Previous single-turbo I6 (306hp), reliable workhorse')
        self.stdout.write('• N54: Twin-turbo I6 (300hp), tuner favorite but reliability issues')
        self.stdout.write('• S58: Latest M I6 (473hp), most powerful BMW 6-cylinder')
        self.stdout.write('• S63TU: Current M V8 (617hp), flagship performance')
        
        self.stdout.write('\nPowertrain Evolution:')
        self.stdout.write('• 2000-2012: Naturally aspirated era (N52, S85 V10)')
        self.stdout.write('• 2006-2016: Turbo transition (N54, N55, N20)')
        self.stdout.write('• 2014+: Modern turbo era (B-series, mild hybrid)')
        self.stdout.write('• 2019+: Electrification (plug-in hybrid, pure electric)')
        
        self.stdout.write('\nCurrent Hierarchy (2025):')
        self.stdout.write('• Entry: B46/B48 2.0L Turbo I4 (248-255hp)')
        self.stdout.write('• Volume: B58 3.0L Turbo I6 (335-382hp)')
        self.stdout.write('• Performance: S58 3.0L Twin-Turbo I6 (473hp)')
        self.stdout.write('• Ultimate: S63TU 4.4L Twin-Turbo V8 (617hp)')
        self.stdout.write('• Flagship: N74 6.0L Twin-Turbo V12 (535hp)')
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'\n🎉 Successfully processed {len(bmw_engines)} BMW engines!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('\n⚠️  DRY RUN complete - run without --dry-run to save changes')
            )
