# This goes in: parts_interchange/apps/vehicles/management/commands/add_acura_engines.py

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.vehicles.models import Engine


class Command(BaseCommand):
    help = 'Add Acura engines from 2000-2025 with detailed specifications'

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
        
        # Acura engines by generation and model years
        acura_engines = [
            # TL Engines
            {
                'name': '2.5L I5 SOHC',
                'displacement': 2.5,
                'cylinders': 5,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 176,
                'torque': 170,
                'engine_code': 'G25A4',
                'models': ['TL Gen 2'],
                'years': '1999-2003',
                'notes': 'Inline-5 from Vigor, unique to early TL'
            },
            
            # ILX Engines (missing from original list)
            {
                'name': '2.0L I4 SOHC i-VTEC',
                'displacement': 2.0,
                'cylinders': 4,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 150,
                'torque': 140,
                'engine_code': 'R20A3',
                'models': ['ILX Gen 1'],
                'years': '2013-2015',
                'notes': 'Base ILX engine, Civic-derived'
            },
            {
                'name': '1.5L I4 Hybrid',
                'displacement': 1.5,
                'cylinders': 4,
                'fuel_type': 'HYB',
                'aspiration': 'NA',
                'horsepower': 111,  # System total
                'torque': 127,
                'engine_code': 'LDA2',
                'models': ['ILX Gen 1 Hybrid'],
                'years': '2013-2015',
                'notes': 'IMA hybrid system'
            },
            {
                'name': '2.4L I4 DOHC i-VTEC',
                'displacement': 2.4,
                'cylinders': 4,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 201,
                'torque': 180,
                'engine_code': 'K24W7',
                'models': ['ILX Gen 2'],
                'years': '2016-2022',
                'notes': 'Updated engine for Gen 2 refresh'
            },
            {
                'name': '3.2L V6 SOHC VTEC',
                'displacement': 3.2,
                'cylinders': 6,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 225,
                'torque': 216,
                'engine_code': 'J32A1',
                'models': ['TL Gen 2', 'CL Gen 2'],
                'years': '1999-2003',
                'notes': 'First VTEC V6 in TL line'
            },
            {
                'name': '3.2L V6 SOHC VTEC',
                'displacement': 3.2,
                'cylinders': 6,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 270,
                'torque': 238,
                'engine_code': 'J32A3',
                'models': ['TL Gen 3'],
                'years': '2004-2008',
                'notes': 'Higher output for Gen 3 redesign'
            },
            {
                'name': '3.7L V6 SOHC VTEC',
                'displacement': 3.7,
                'cylinders': 6,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 305,
                'torque': 273,
                'engine_code': 'J37A4',
                'models': ['TL Gen 4'],
                'years': '2009-2014',
                'notes': 'Largest NA V6 in TL history'
            },
            
            # TLX Engines
            {
                'name': '2.4L I4 DOHC i-VTEC',
                'displacement': 2.4,
                'cylinders': 4,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 206,
                'torque': 182,
                'engine_code': 'K24W7',
                'models': ['TLX Gen 1'],
                'years': '2015-2020',
                'notes': 'Earth Dreams engine, DCT transmission'
            },
            {
                'name': '3.5L V6 SOHC i-VTEC',
                'displacement': 3.5,
                'cylinders': 6,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 290,
                'torque': 267,
                'engine_code': 'J35Y6',
                'models': ['TLX Gen 1'],
                'years': '2015-2020',
                'notes': 'SH-AWD available, 9-speed automatic'
            },
            {
                'name': '2.0L I4 DOHC VTEC Turbo',
                'displacement': 2.0,
                'cylinders': 4,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 272,
                'torque': 280,
                'engine_code': 'K20C4',
                'models': ['TLX Gen 2', 'Integra Gen 5'],
                'years': '2021-2025',
                'notes': 'New turbo 4-cylinder, 10-speed automatic'
            },
            {
                'name': '3.0L V6 DOHC VTEC Turbo',
                'displacement': 3.0,
                'cylinders': 6,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 355,
                'torque': 354,
                'engine_code': 'J30A1',
                'models': ['TLX Gen 2 Type S'],
                'years': '2021-2025',
                'notes': 'Twin-scroll turbo, Type S exclusive'
            },
            
            # MDX Engines
            {
                'name': '3.5L V6 SOHC VTEC',
                'displacement': 3.5,
                'cylinders': 6,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 265,
                'torque': 253,
                'engine_code': 'J35A5',
                'models': ['MDX Gen 1'],
                'years': '2001-2006',
                'notes': 'First Acura SUV engine, SH-AWD standard'
            },
            {
                'name': '3.7L V6 SOHC VTEC',
                'displacement': 3.7,
                'cylinders': 6,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 300,
                'torque': 270,
                'engine_code': 'J37A1',
                'models': ['MDX Gen 2'],
                'years': '2007-2013',
                'notes': 'More powerful for larger Gen 2'
            },
            {
                'name': '3.5L V6 SOHC i-VTEC',
                'displacement': 3.5,
                'cylinders': 6,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 290,
                'torque': 267,
                'engine_code': 'J35Y4',
                'models': ['MDX Gen 3'],
                'years': '2014-2020',
                'notes': 'Earth Dreams technology, 9-speed auto'
            },
            {
                'name': '3.5L V6 SOHC i-VTEC Hybrid',
                'displacement': 3.5,
                'cylinders': 6,
                'fuel_type': 'HYB',
                'aspiration': 'NA',
                'horsepower': 321,  # System total
                'torque': 289,
                'engine_code': 'J35Y5',
                'models': ['MDX Gen 3 Hybrid'],
                'years': '2017-2020',
                'notes': 'Sport Hybrid SH-AWD, 3-motor system'
            },
            {
                'name': '3.5L V6 DOHC VTEC Turbo',
                'displacement': 3.5,
                'cylinders': 6,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 355,
                'torque': 354,
                'engine_code': 'J35A8',
                'models': ['MDX Gen 4', 'MDX Gen 4 Type S'],
                'years': '2021-2025',
                'notes': 'Turbo V6, Type S gets 355hp tune'
            },
            
            # RDX Engines
            {
                'name': '2.3L I4 DOHC VTEC Turbo',
                'displacement': 2.3,
                'cylinders': 4,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 240,
                'torque': 260,
                'engine_code': 'K23A1',
                'models': ['RDX Gen 1'],
                'years': '2007-2012',
                'notes': 'First turbo Acura SUV, SH-AWD'
            },
            {
                'name': '3.5L V6 SOHC i-VTEC',
                'displacement': 3.5,
                'cylinders': 6,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 273,
                'torque': 251,
                'engine_code': 'J35Z2',
                'models': ['RDX Gen 2'],
                'years': '2013-2018',
                'notes': 'Switch to V6, AWD became optional'
            },
            {
                'name': '2.0L I4 DOHC VTEC Turbo',
                'displacement': 2.0,
                'cylinders': 4,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 272,
                'torque': 280,
                'engine_code': 'K20C1',
                'models': ['RDX Gen 3'],
                'years': '2019-2025',
                'notes': 'Back to turbo 4, 10-speed automatic'
            },
            
            # Integra Engines
            {
                'name': '1.8L I4 DOHC VTEC',
                'displacement': 1.8,
                'cylinders': 4,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 140,
                'torque': 127,
                'engine_code': 'B18B1',
                'models': ['Integra Gen 3'],
                'years': '1994-2001',
                'notes': 'Base engine, LS/RS models'
            },
            {
                'name': '1.8L I4 DOHC VTEC',
                'displacement': 1.8,
                'cylinders': 4,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 170,
                'torque': 128,
                'engine_code': 'B18C1',
                'models': ['Integra Gen 3 GS-R'],
                'years': '1994-2001',
                'notes': 'Higher output VTEC, GS-R model'
            },
            {
                'name': '1.8L I4 DOHC VTEC',
                'displacement': 1.8,
                'cylinders': 4,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 195,
                'torque': 130,
                'engine_code': 'B18C5',
                'models': ['Integra Gen 3 Type R'],
                'years': '1997-2001',
                'notes': 'Highest output, Type R exclusive'
            },
            {
                'name': '1.5L I4 DOHC VTEC Turbo',
                'displacement': 1.5,
                'cylinders': 4,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 200,
                'torque': 192,
                'engine_code': 'L15C7',
                'models': ['Integra Gen 5'],
                'years': '2023-2025',
                'notes': 'New turbo engine, CVT or 6-speed manual'
            },
            {
                'name': '2.0L I4 DOHC VTEC Turbo',
                'displacement': 2.0,
                'cylinders': 4,
                'fuel_type': 'GAS',
                'aspiration': 'TC',
                'horsepower': 320,
                'torque': 310,
                'engine_code': 'K20C1',
                'models': ['Integra Gen 5 Type S'],
                'years': '2024-2025',
                'notes': 'High performance turbo, Type S exclusive'
            },
            
            # Other Models (abbreviated for key engines)
            {
                'name': '2.0L I4 DOHC i-VTEC',
                'displacement': 2.0,
                'cylinders': 4,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 160,
                'torque': 141,
                'engine_code': 'K20A3',
                'models': ['RSX'],
                'years': '2002-2006',
                'notes': 'Base RSX engine'
            },
            {
                'name': '2.0L I4 DOHC i-VTEC',
                'displacement': 2.0,
                'cylinders': 4,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 210,
                'torque': 143,
                'engine_code': 'K20A2',
                'models': ['RSX Type-S'],
                'years': '2002-2006',
                'notes': 'High-output i-VTEC, Type-S only'
            },
            {
                'name': '2.4L I4 DOHC i-VTEC',
                'displacement': 2.4,
                'cylinders': 4,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 201,
                'torque': 172,
                'engine_code': 'K24Z7',
                'models': ['TSX Gen 1', 'TSX Gen 2'],
                'years': '2004-2014',
                'notes': 'European Accord engine'
            },
            {
                'name': '3.5L V6 SOHC VTEC',
                'displacement': 3.5,
                'cylinders': 6,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 280,
                'torque': 254,
                'engine_code': 'J35Z6',
                'models': ['TSX Gen 2 V6'],
                'years': '2010-2014',
                'notes': 'V6 option added to TSX'
            },
            {
                'name': '3.0L V6 SOHC VTEC',
                'displacement': 3.0,
                'cylinders': 6,
                'fuel_type': 'GAS',
                'aspiration': 'NA',
                'horsepower': 250,
                'torque': 233,
                'engine_code': 'C30A1',
                'models': ['NSX Gen 1'],
                'years': '1991-2005',
                'notes': 'All-aluminum, mid-engine'
            },
            {
                'name': '3.5L V6 DOHC VTEC Hybrid',
                'displacement': 3.5,
                'cylinders': 6,
                'fuel_type': 'HYB',
                'aspiration': 'TC',
                'horsepower': 573,  # System total
                'torque': 476,
                'engine_code': 'JNC1',
                'models': ['NSX Gen 2'],
                'years': '2016-2022',
                'notes': 'Twin-turbo hybrid, 3-motor system'
            },
        ]
        
        self.stdout.write(f'Processing {len(acura_engines)} Acura engines...')
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for engine_data in acura_engines:
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
                    Engine.objects.create(
                        name=engine_name,
                        displacement=engine_data.get('displacement'),
                        cylinders=engine_data.get('cylinders'),
                        fuel_type=engine_data['fuel_type'],
                        aspiration=engine_data['aspiration'],
                        horsepower=engine_data.get('horsepower'),
                        torque=engine_data.get('torque'),
                        engine_code=engine_data['engine_code']
                    )
                    created_count += 1
                    status = '✓ CREATED'
            else:
                status = '? DRY RUN'
            
            # Display engine info
            disp_str = f"{engine_data.get('displacement', '?')}L" if engine_data.get('displacement') else ""
            cyl_str = f"V{engine_data.get('cylinders', '?')}" if engine_data.get('cylinders') else ""
            hp_str = f"{engine_data.get('horsepower', '?')}hp" if engine_data.get('horsepower') else ""
            
            self.stdout.write(f'{status} {engine_name}')
            self.stdout.write(f'    {disp_str} {cyl_str} | {hp_str} | {engine_data["engine_code"]}')
            self.stdout.write(f'    Models: {", ".join(engine_data["models"])}')
            self.stdout.write(f'    Years: {engine_data["years"]} | {engine_data["notes"]}')
            self.stdout.write('')  # Blank line
        
        # Summary
        self.stdout.write('=' * 60)
        self.stdout.write('ACURA ENGINES SUMMARY')
        self.stdout.write('=' * 60)
        
        if not dry_run:
            self.stdout.write(f'✓ Created: {created_count} engines')
            self.stdout.write(f'↻ Updated: {updated_count} engines')
            self.stdout.write(f'- Existed: {skipped_count} engines')
            self.stdout.write(f'📊 Total: {created_count + updated_count + skipped_count} engines processed')
        else:
            self.stdout.write(f'📊 Would process: {len(acura_engines)} engines')
        
        # Engine insights
        self.stdout.write('\\n🔍 ENGINE INSIGHTS:')
        self.stdout.write('Key Acura Engine Families:')
        self.stdout.write('• J-Series V6: 2.5L-3.7L (1998-2020) - Most common')
        self.stdout.write('• K-Series I4: 1.5L-2.4L (2002-present) - Current turbo era')  
        self.stdout.write('• B-Series I4: 1.8L (1994-2001) - Classic VTEC')
        self.stdout.write('• Hybrid Systems: NSX, MDX (2016-present)')
        
        self.stdout.write('\\nTurbo Evolution:')
        self.stdout.write('• 2007: First turbo (RDX 2.3L)')
        self.stdout.write('• 2013-2018: NA V6 era')
        self.stdout.write('• 2019+: Return to turbo (2.0L, 3.0L)')
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'\\n🎉 Successfully processed {len(acura_engines)} Acura engines!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('\\n⚠️  DRY RUN complete - run without --dry-run to save changes')
            )
