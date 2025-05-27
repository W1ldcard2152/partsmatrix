# This goes in: parts_interchange/apps/parts/management/commands/add_manufacturers.py

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.parts.models import Manufacturer


class Command(BaseCommand):
    help = 'Add comprehensive automotive manufacturers organized by region and market segment'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without making changes'
        )
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='Update existing manufacturer records with new data'
        )
        parser.add_argument(
            '--region',
            type=str,
            choices=['domestic', 'import', 'performance', 'commercial', 'all'],
            default='all',
            help='Filter manufacturers by region/type (default: all)'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        update_existing = options['update_existing']
        region_filter = options['region']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No data will be saved'))
        
        # Comprehensive automotive manufacturers by region and type
        manufacturers = [
            # Domestic OEM Manufacturers
            {
                'name': 'General Motors',
                'abbreviation': 'GM',
                'country': 'USA',
                'region': 'domestic',
                'type': 'OEM',
                'brands': 'Chevrolet, GMC, Cadillac, Buick',
                'specialty': 'Full line domestic manufacturer'
            },
            {
                'name': 'Ford Motor Company',
                'abbreviation': 'FORD',
                'country': 'USA',
                'region': 'domestic',
                'type': 'OEM',
                'brands': 'Ford, Lincoln, Mercury (discontinued)',
                'specialty': 'Full line domestic manufacturer'
            },
            {
                'name': 'Stellantis',
                'abbreviation': 'STLA',
                'country': 'USA/Europe',
                'region': 'domestic',
                'type': 'OEM',
                'brands': 'Chrysler, Dodge, Jeep, Ram, Plymouth (discontinued)',
                'specialty': 'Merged FCA and PSA Group'
            },
            {
                'name': 'Tesla',
                'abbreviation': 'TSLA',
                'country': 'USA',
                'region': 'domestic',
                'type': 'EV OEM',
                'brands': 'Tesla',
                'specialty': 'Electric vehicle manufacturer'
            },
            
            # Import OEM Manufacturers - Japanese
            {
                'name': 'Toyota Motor Corporation',
                'abbreviation': 'TOYOTA',
                'country': 'Japan',
                'region': 'import',
                'type': 'OEM',
                'brands': 'Toyota, Lexus, Scion (discontinued)',
                'specialty': 'Reliability and fuel efficiency leader'
            },
            {
                'name': 'Honda Motor Company',
                'abbreviation': 'HONDA',
                'country': 'Japan',
                'region': 'import',
                'type': 'OEM',
                'brands': 'Honda, Acura',
                'specialty': 'Engineering excellence and VTEC technology'
            },
            {
                'name': 'Nissan Motor Company',
                'abbreviation': 'NISSAN',
                'country': 'Japan',
                'region': 'import',
                'type': 'OEM',
                'brands': 'Nissan, Infiniti, Datsun (vintage)',
                'specialty': 'Performance and innovation (GT-R, Z-cars)'
            },
            {
                'name': 'Mazda Motor Corporation',
                'abbreviation': 'MAZDA',
                'country': 'Japan',
                'region': 'import',
                'type': 'OEM',
                'brands': 'Mazda',
                'specialty': 'Rotary engines, SkyActiv technology'
            },
            {
                'name': 'Subaru Corporation',
                'abbreviation': 'SUBARU',
                'country': 'Japan',
                'region': 'import',
                'type': 'OEM',
                'brands': 'Subaru',
                'specialty': 'All-wheel drive, boxer engines'
            },
            {
                'name': 'Mitsubishi Motors',
                'abbreviation': 'MITSU',
                'country': 'Japan',
                'region': 'import',
                'type': 'OEM',
                'brands': 'Mitsubishi',
                'specialty': 'Evolution performance line, 4WD systems'
            },
            
            # Import OEM Manufacturers - European
            {
                'name': 'BMW Group',
                'abbreviation': 'BMW',
                'country': 'Germany',
                'region': 'import',
                'type': 'Luxury OEM',
                'brands': 'BMW, Mini, Rolls-Royce',
                'specialty': 'Ultimate driving machine, inline-6 engines'
            },
            {
                'name': 'Mercedes-Benz Group',
                'abbreviation': 'MB',
                'country': 'Germany',
                'region': 'import',
                'type': 'Luxury OEM',
                'brands': 'Mercedes-Benz, AMG, Smart',
                'specialty': 'Luxury and engineering excellence'
            },
            {
                'name': 'Audi AG',
                'abbreviation': 'AUDI',
                'country': 'Germany',
                'region': 'import',
                'type': 'Luxury OEM',
                'brands': 'Audi',
                'specialty': 'Quattro AWD, TFSI engines, luxury performance'
            },
            {
                'name': 'Porsche AG',
                'abbreviation': 'PORSCHE',
                'country': 'Germany',
                'region': 'import',
                'type': 'Performance OEM',
                'brands': 'Porsche',
                'specialty': 'Sports cars, flat-6 engines, racing heritage'
            },
            {
                'name': 'Volkswagen AG',
                'abbreviation': 'VW',
                'country': 'Germany',
                'region': 'import',
                'type': 'OEM',
                'brands': 'Volkswagen, Bentley, Bugatti, Lamborghini',
                'specialty': 'People\'s car, TSI/TDI engines'
            },
            {
                'name': 'Volvo Cars',
                'abbreviation': 'VOLVO',
                'country': 'Sweden',
                'region': 'import',
                'type': 'Luxury OEM',
                'brands': 'Volvo',
                'specialty': 'Safety innovation, T5/T6 engines'
            },
            
            # Import OEM Manufacturers - Korean
            {
                'name': 'Hyundai Motor Company',
                'abbreviation': 'HYUNDAI',
                'country': 'South Korea',
                'region': 'import',
                'type': 'OEM',
                'brands': 'Hyundai, Genesis',
                'specialty': 'Value and warranty, N performance division'
            },
            {
                'name': 'Kia Corporation',
                'abbreviation': 'KIA',
                'country': 'South Korea',
                'region': 'import',
                'type': 'OEM',
                'brands': 'Kia',
                'specialty': 'Design and value, Stinger GT performance'
            },
            
            # Performance/Specialty Manufacturers
            {
                'name': 'Saleen Automotive',
                'abbreviation': 'SALEEN',
                'country': 'USA',
                'region': 'performance',
                'type': 'Performance Modifier',
                'brands': 'Saleen',
                'specialty': 'Ford Mustang and supercar modifications'
            },
            {
                'name': 'Shelby American',
                'abbreviation': 'SHELBY',
                'country': 'USA',
                'region': 'performance',
                'type': 'Performance Modifier',
                'brands': 'Shelby',
                'specialty': 'Ford performance modifications, Cobra heritage'
            },
            {
                'name': 'Hennessey Performance',
                'abbreviation': 'HPE',
                'country': 'USA',
                'region': 'performance',
                'type': 'Performance Modifier',
                'brands': 'Hennessey',
                'specialty': 'Extreme performance modifications, Venom series'
            },
            {
                'name': 'Roush Performance',
                'abbreviation': 'ROUSH',
                'country': 'USA',
                'region': 'performance',
                'type': 'Performance Modifier',
                'brands': 'Roush',
                'specialty': 'Ford performance, NASCAR technology'
            },
            
            # Aftermarket Parts Manufacturers
            {
                'name': 'Bosch',
                'abbreviation': 'BOSCH',
                'country': 'Germany',
                'region': 'aftermarket',
                'type': 'OE Supplier/Aftermarket',
                'brands': 'Bosch',
                'specialty': 'Fuel injection, ignition, braking systems'
            },
            {
                'name': 'Denso Corporation',
                'abbreviation': 'DENSO',
                'country': 'Japan',
                'region': 'aftermarket',
                'type': 'OE Supplier/Aftermarket',
                'brands': 'Denso',
                'specialty': 'Electrical components, HVAC, fuel systems'
            },
            {
                'name': 'Delphi Technologies',
                'abbreviation': 'DELPHI',
                'country': 'UK',
                'region': 'aftermarket',
                'type': 'OE Supplier/Aftermarket',
                'brands': 'Delphi',
                'specialty': 'Electrical systems, fuel injection, diagnostics'
            },
            {
                'name': 'NGK Spark Plugs',
                'abbreviation': 'NGK',
                'country': 'Japan',
                'region': 'aftermarket',
                'type': 'Specialist',
                'brands': 'NGK, NTK',
                'specialty': 'Spark plugs, ignition coils, oxygen sensors'
            },
            {
                'name': 'Champion Auto Parts',
                'abbreviation': 'CHAMPION',
                'country': 'USA',
                'region': 'aftermarket',
                'type': 'Specialist',
                'brands': 'Champion',
                'specialty': 'Spark plugs, wipers, filters'
            },
            {
                'name': 'AC Delco',
                'abbreviation': 'ACDELCO',
                'country': 'USA',
                'region': 'aftermarket',
                'type': 'OE Supplier/Aftermarket',
                'brands': 'AC Delco',
                'specialty': 'GM OE parts and aftermarket components'
            },
            {
                'name': 'Motorcraft',
                'abbreviation': 'MCRAFT',
                'country': 'USA',
                'region': 'aftermarket',
                'type': 'OE Supplier',
                'brands': 'Motorcraft',
                'specialty': 'Ford OE parts and service components'
            },
            {
                'name': 'Mopar',
                'abbreviation': 'MOPAR',
                'country': 'USA',
                'region': 'aftermarket',
                'type': 'OE Supplier',
                'brands': 'Mopar',
                'specialty': 'Chrysler/Dodge/Jeep/Ram OE and performance parts'
            },
            
            # Brake Specialists
            {
                'name': 'Brembo SpA',
                'abbreviation': 'BREMBO',
                'country': 'Italy',
                'region': 'performance',
                'type': 'Brake Specialist',
                'brands': 'Brembo',
                'specialty': 'High-performance brake systems, racing heritage'
            },
            {
                'name': 'Wilwood Engineering',
                'abbreviation': 'WILWOOD',
                'country': 'USA',
                'region': 'performance',
                'type': 'Brake Specialist',
                'brands': 'Wilwood',
                'specialty': 'Racing and performance brake systems'
            },
            {
                'name': 'StopTech',
                'abbreviation': 'STOPTECH',
                'country': 'USA',
                'region': 'performance',
                'type': 'Brake Specialist',
                'brands': 'StopTech',
                'specialty': 'Performance brake systems and rotors'
            },
            
            # Suspension Specialists
            {
                'name': 'Bilstein',
                'abbreviation': 'BILSTEIN',
                'country': 'Germany',
                'region': 'performance',
                'type': 'Suspension Specialist',
                'brands': 'Bilstein',
                'specialty': 'Monotube shock absorbers, racing suspension'
            },
            {
                'name': 'KYB Corporation',
                'abbreviation': 'KYB',
                'country': 'Japan',
                'region': 'aftermarket',
                'type': 'Suspension Specialist',
                'brands': 'KYB',
                'specialty': 'OE and aftermarket shock absorbers, struts'
            },
            {
                'name': 'Monroe Tenneco',
                'abbreviation': 'MONROE',
                'country': 'USA',
                'region': 'aftermarket',
                'type': 'Suspension Specialist',
                'brands': 'Monroe, Gabriel',
                'specialty': 'Aftermarket shock absorbers and struts'
            },
            {
                'name': 'Eibach Springs',
                'abbreviation': 'EIBACH',
                'country': 'Germany',
                'region': 'performance',
                'type': 'Suspension Specialist',
                'brands': 'Eibach',
                'specialty': 'Performance springs and suspension components'
            },
            
            # Engine Performance Specialists
            {
                'name': 'Holley Performance',
                'abbreviation': 'HOLLEY',
                'country': 'USA',
                'region': 'performance',
                'type': 'Engine Performance',
                'brands': 'Holley, Sniper, Terminator',
                'specialty': 'Carburetors, fuel injection, engine management'
            },
            {
                'name': 'Edelbrock Corporation',
                'abbreviation': 'EDELBROCK',
                'country': 'USA',
                'region': 'performance',
                'type': 'Engine Performance',
                'brands': 'Edelbrock',
                'specialty': 'Intake manifolds, carburetors, cylinder heads'
            },
            {
                'name': 'K&N Engineering',
                'abbreviation': 'KN',
                'country': 'USA',
                'region': 'performance',
                'type': 'Air Filtration',
                'brands': 'K&N',
                'specialty': 'High-flow air filters and intake systems'
            },
            {
                'name': 'Flowmaster',
                'abbreviation': 'FLOWMASTER',
                'country': 'USA',
                'region': 'performance',
                'type': 'Exhaust Specialist',
                'brands': 'Flowmaster',
                'specialty': 'Performance exhaust systems and mufflers'
            },
            {
                'name': 'Borla Performance',
                'abbreviation': 'BORLA',
                'country': 'USA',
                'region': 'performance',
                'type': 'Exhaust Specialist',
                'brands': 'Borla',
                'specialty': 'Stainless steel performance exhaust systems'
            },
            
            # Turbo/Forced Induction Specialists
            {
                'name': 'Garrett Motion',
                'abbreviation': 'GARRETT',
                'country': 'Switzerland',
                'region': 'performance',
                'type': 'Turbo Specialist',
                'brands': 'Garrett, Honeywell',
                'specialty': 'Turbochargers and forced induction systems'
            },
            {
                'name': 'BorgWarner',
                'abbreviation': 'BW',
                'country': 'USA',
                'region': 'performance',
                'type': 'Turbo Specialist',
                'brands': 'BorgWarner, EFR',
                'specialty': 'Turbochargers, transfer cases, timing systems'
            },
            {
                'name': 'Precision Turbo',
                'abbreviation': 'PTE',
                'country': 'USA',
                'region': 'performance',
                'type': 'Turbo Specialist',
                'brands': 'Precision Turbo',
                'specialty': 'Aftermarket turbochargers and intercoolers'
            },
            
            # Commercial/Heavy Duty
            {
                'name': 'Cummins Inc',
                'abbreviation': 'CUMMINS',
                'country': 'USA',
                'region': 'commercial',
                'type': 'Engine Manufacturer',
                'brands': 'Cummins',
                'specialty': 'Diesel engines, commercial and industrial power'
            },
            {
                'name': 'Caterpillar Inc',
                'abbreviation': 'CAT',
                'country': 'USA',
                'region': 'commercial',
                'type': 'Engine Manufacturer',
                'brands': 'Caterpillar',
                'specialty': 'Heavy equipment, diesel engines, industrial'
            },
            {
                'name': 'Allison Transmission',
                'abbreviation': 'ALLISON',
                'country': 'USA',
                'region': 'commercial',
                'type': 'Transmission Specialist',
                'brands': 'Allison',
                'specialty': 'Automatic transmissions for commercial vehicles'
            },
            
            # Classic/Restoration Specialists
            {
                'name': 'Year One',
                'abbreviation': 'YEAR1',
                'country': 'USA',
                'region': 'classic',
                'type': 'Classic Parts',
                'brands': 'Year One',
                'specialty': 'GM muscle car restoration parts 1962-1972'
            },
            {
                'name': 'NPD (National Parts Depot)',
                'abbreviation': 'NPD',
                'country': 'USA',
                'region': 'classic',
                'type': 'Classic Parts',
                'brands': 'NPD',
                'specialty': 'Ford Mustang and classic Ford restoration'
            },
            {
                'name': 'Classic Industries',
                'abbreviation': 'CLASSIC',
                'country': 'USA',
                'region': 'classic',
                'type': 'Classic Parts',
                'brands': 'Classic Industries',
                'specialty': 'Camaro, Chevelle, Nova restoration parts'
            },
            
            # Remanufacturing Specialists
            {
                'name': 'Cardone Industries',
                'abbreviation': 'CARDONE',
                'country': 'USA',
                'region': 'aftermarket',
                'type': 'Remanufacturer',
                'brands': 'Cardone, A1 Cardone',
                'specialty': 'Remanufactured automotive components'
            },
            {
                'name': 'Remy International',
                'abbreviation': 'REMY',
                'country': 'USA',
                'region': 'aftermarket',
                'type': 'Remanufacturer',
                'brands': 'Remy',
                'specialty': 'Remanufactured starters, alternators, motors'
            }
        ]
        
        # Filter manufacturers by region if specified
        if region_filter != 'all':
            manufacturers = [m for m in manufacturers if m['region'] == region_filter]
            self.stdout.write(f'Filtering to {region_filter} manufacturers only')
        
        self.stdout.write(f'Processing {len(manufacturers)} manufacturers...')
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for mfr_data in manufacturers:
            mfr_name = mfr_data['name']
            abbreviation = mfr_data['abbreviation']
            country = mfr_data['country']
            
            if not dry_run:
                # Check if manufacturer already exists
                existing_mfrs = Manufacturer.objects.filter(name=mfr_name)
                
                if existing_mfrs.exists():
                    if update_existing:
                        mfr_obj = existing_mfrs.first()
                        # Update fields
                        mfr_obj.abbreviation = abbreviation
                        mfr_obj.country = country
                        mfr_obj.save()
                        updated_count += 1
                        status = '↻ UPDATED'
                    else:
                        skipped_count += 1
                        status = '- EXISTS'
                else:
                    # Create new manufacturer
                    Manufacturer.objects.create(
                        name=mfr_name,
                        abbreviation=abbreviation,
                        country=country
                    )
                    created_count += 1
                    status = '✓ CREATED'
            else:
                status = '? DRY RUN'
            
            # Display manufacturer info
            self.stdout.write(f'{status} {mfr_name} ({abbreviation})')
            self.stdout.write(f'    Country: {country} | Region: {mfr_data["region"].title()} | Type: {mfr_data["type"]}')
            self.stdout.write(f'    Brands: {mfr_data["brands"]}')
            self.stdout.write(f'    Specialty: {mfr_data["specialty"]}')
            self.stdout.write('')  # Blank line
        
        # Summary
        self.stdout.write('=' * 60)
        self.stdout.write('MANUFACTURERS SUMMARY')
        self.stdout.write('=' * 60)
        
        if not dry_run:
            self.stdout.write(f'✓ Created: {created_count} manufacturers')
            self.stdout.write(f'↻ Updated: {updated_count} manufacturers')
            self.stdout.write(f'- Existed: {skipped_count} manufacturers')
            self.stdout.write(f'📊 Total: {created_count + updated_count + skipped_count} manufacturers processed')
        else:
            self.stdout.write(f'📊 Would process: {len(manufacturers)} manufacturers')
        
        # Regional breakdown
        self.stdout.write('\n🌍 REGIONAL BREAKDOWN:')
        region_counts = {}
        for mfr in manufacturers:
            region = mfr['region']
            region_counts[region] = region_counts.get(region, 0) + 1
        
        for region, count in sorted(region_counts.items()):
            self.stdout.write(f'• {region.title()}: {count} manufacturers')
        
        # Type breakdown
        self.stdout.write('\n🏭 TYPE BREAKDOWN:')
        type_counts = {}
        for mfr in manufacturers:
            mfr_type = mfr['type']
            type_counts[mfr_type] = type_counts.get(mfr_type, 0) + 1
        
        for mfr_type, count in sorted(type_counts.items()):
            self.stdout.write(f'• {mfr_type}: {count} manufacturers')
        
        # Usage examples
        self.stdout.write('\n💡 USAGE EXAMPLES:')
        self.stdout.write('Filter by region:')
        self.stdout.write('• python manage.py add_manufacturers --region domestic')
        self.stdout.write('• python manage.py add_manufacturers --region import')
        self.stdout.write('• python manage.py add_manufacturers --region performance')
        
        self.stdout.write('\nAPI queries:')
        self.stdout.write('• All GM parts: /api/parts/?manufacturer__abbreviation=GM')
        self.stdout.write('• Performance manufacturers: /api/manufacturers/?name__contains=Performance')
        self.stdout.write('• German manufacturers: /api/manufacturers/?country=Germany')
        
        # Next steps
        self.stdout.write('\n📋 NEXT STEPS:')
        self.stdout.write('1. ✅ Part categories created')
        self.stdout.write('2. ✅ Manufacturers populated')
        self.stdout.write('3. 🔄 Add parts: python manage.py add_parts --manufacturer [name]')
        self.stdout.write('4. 🔄 Create interchange groups: python manage.py add_interchange_groups')
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'\n🎉 Successfully processed {len(manufacturers)} manufacturers!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('\n⚠️  DRY RUN complete - run without --dry-run to save changes')
            )
