# This goes in: parts_interchange/apps/parts/management/commands/add_part_categories.py

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.parts.models import PartCategory, Manufacturer


class Command(BaseCommand):
    help = 'Add comprehensive automotive part categories - Major systems at top level for optimal UX'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without making changes'
        )
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='Update existing category records with new data'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        update_existing = options['update_existing']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No data will be saved'))
        
        # Major automotive systems at top level - Optimized for user experience and freemium model
        part_categories = [
            # ========================================
            # POWERTRAIN SYSTEMS (Front and Center)
            # ========================================
            {
                'name': 'Engine',
                'description': 'Complete engines and core engine components.',
                'system': 'Powertrain',
                'level': 'Major System',
                'examples': 'Complete engine, cylinder head, crankshaft, pistons',
                'subcategories': [
                    {'name': 'Complete Engine Assembly', 'description': 'Entire engine unit ready for installation.', 'examples': 'Long block, short block, crate engine'},
                    {'name': 'Engine Block/Cylinder Block', 'description': 'Main structural component of the engine.', 'examples': 'Engine block, cylinder sleeve, deck surface'},
                    {'name': 'Cylinder Head', 'description': 'Top part of the engine containing valves and combustion chambers.', 'examples': 'Cylinder head assembly, bare cylinder head, head gasket'},
                    {'name': 'Crankshaft', 'description': 'Converts reciprocating motion to rotational motion.', 'examples': 'Forged crankshaft, cast crankshaft, main bearings'},
                    {'name': 'Camshaft', 'description': 'Controls valve timing and lift.', 'examples': 'Intake camshaft, exhaust camshaft, cam bearings'},
                    {'name': 'Pistons & Connecting Rods', 'description': 'Components that transfer combustion force to crankshaft.', 'examples': 'Piston assembly, connecting rod, rod bearings'},
                    {'name': 'Valvetrain Components', 'description': 'Parts controlling valve operation.', 'examples': 'Valve springs, rocker arms, pushrods, lifters'},
                    {'name': 'Timing Components', 'description': 'Components that synchronize engine timing.', 'examples': 'Timing chain, timing belt, timing gears, guides'},
                    {'name': 'Oil System', 'description': 'Engine lubrication system components.', 'examples': 'Oil pump, oil pan, oil pickup, oil filter housing'},
                    {'name': 'Cooling System', 'description': 'Engine cooling components.', 'examples': 'Water pump, thermostat, coolant hoses, freeze plugs'},
                    {'name': 'Ignition System', 'description': 'Components for fuel ignition.', 'examples': 'Ignition coils, spark plugs, distributor, ignition module'},
                    {'name': 'Engine Covers & Housings', 'description': 'Protective covers and housings.', 'examples': 'Valve covers, timing covers, oil pan, bell housing'},
                    {'name': 'Engine Mounts', 'description': 'Components securing engine to chassis.', 'examples': 'Motor mounts, transmission mounts, torque struts'},
                    {'name': 'Forced Induction', 'description': 'Turbochargers and superchargers.', 'examples': 'Turbocharger, supercharger, intercooler, wastegate'},
                    {'name': 'Other Engine Components', 'description': 'Miscellaneous engine parts.', 'examples': 'Harmonic balancer, flywheel, flexplate, engine sensors'},
                ]
            },
            {
                'name': 'Intake, Exhaust & Fuel',
                'description': 'Air intake, exhaust, and fuel delivery systems.',
                'system': 'Engine Support',
                'level': 'Major System',
                'examples': 'Intake manifold, exhaust manifold, fuel pump, muffler',
                'subcategories': [
                    {'name': 'Air Intake System', 'description': 'Components delivering air to the engine.', 'examples': 'Air filter, intake manifold, throttle body, MAF sensor'},
                    {'name': 'Fuel Delivery System', 'description': 'Components delivering fuel to the engine.', 'examples': 'Fuel pump, fuel injectors, fuel rail, fuel filter'},
                    {'name': 'Exhaust System', 'description': 'Components removing exhaust gases.', 'examples': 'Exhaust manifold, catalytic converter, muffler, exhaust pipe'},
                    {'name': 'Fuel Tank & Storage', 'description': 'Fuel storage and related components.', 'examples': 'Fuel tank, fuel sending unit, fuel cap, fuel door'},
                    {'name': 'Carburetor System', 'description': 'Carburetor and related components (classic vehicles).', 'examples': 'Carburetor, choke, accelerator pump, fuel bowl'},
                ]
            },
            {
                'name': 'Transmission & Drivetrain',
                'description': 'Power transmission components from engine to wheels.',
                'system': 'Drivetrain',
                'level': 'Major System',
                'examples': 'Transmission, differential, driveshaft, CV axles',
                'subcategories': [
                    {'name': 'Automatic Transmission', 'description': 'Automatic transmission components.', 'examples': 'Complete transmission, torque converter, valve body, solenoids'},
                    {'name': 'Manual Transmission', 'description': 'Manual transmission components.', 'examples': 'Manual transmission, clutch assembly, flywheel, shifter'},
                    {'name': 'Transfer Case', 'description': '4WD/AWD transfer case components.', 'examples': 'Transfer case assembly, shift motor, chain, output shaft'},
                    {'name': 'Differential', 'description': 'Front and rear differential components.', 'examples': 'Differential assembly, ring and pinion, carrier, axle shafts'},
                    {'name': 'Driveshafts & CV Axles', 'description': 'Power transmission shafts.', 'examples': 'Driveshaft, CV axle, U-joints, CV joints'},
                    {'name': 'Clutch System', 'description': 'Manual transmission clutch components.', 'examples': 'Clutch disc, pressure plate, release bearing, slave cylinder'},
                ]
            },
            
            # ========================================
            # CHASSIS SYSTEMS
            # ========================================
            {
                'name': 'Steering & Suspension',
                'description': 'Vehicle steering and suspension components.',
                'system': 'Chassis',
                'level': 'Major System',
                'examples': 'Steering rack, struts, control arms, sway bars',
                'subcategories': [
                    {'name': 'Steering System', 'description': 'Components for vehicle steering.', 'examples': 'Steering rack, power steering pump, tie rods, steering wheel'},
                    {'name': 'Front Suspension', 'description': 'Front suspension components.', 'examples': 'Struts, control arms, ball joints, coil springs'},
                    {'name': 'Rear Suspension', 'description': 'Rear suspension components.', 'examples': 'Shocks, leaf springs, trailing arms, panhard bar'},
                    {'name': 'Stabilizer System', 'description': 'Anti-roll bar components.', 'examples': 'Sway bars, end links, bushings, brackets'},
                    {'name': 'Air Suspension', 'description': 'Air ride suspension components.', 'examples': 'Air bags, compressor, air lines, height sensors'},
                ]
            },
            {
                'name': 'Wheels, Tires & Brakes',
                'description': 'Wheel, tire, and braking system components.',
                'system': 'Chassis',
                'level': 'Major System',
                'examples': 'Brake calipers, rotors, wheels, tires',
                'subcategories': [
                    {'name': 'Brake System', 'description': 'Vehicle braking components.', 'examples': 'Brake calipers, rotors, pads, master cylinder, brake lines'},
                    {'name': 'ABS & Traction Control', 'description': 'Anti-lock brake and traction control.', 'examples': 'ABS module, wheel speed sensors, brake booster'},
                    {'name': 'Wheels & Tires', 'description': 'Wheels and tire components.', 'examples': 'Alloy wheels, steel wheels, tires, TPMS sensors'},
                    {'name': 'Wheel Hardware', 'description': 'Wheel mounting hardware.', 'examples': 'Lug nuts, wheel studs, hub caps, center caps'},
                ]
            },
            
            # ========================================
            # NEW MAJOR SYSTEMS (Your A/C Line Goes Here!)
            # ========================================
            {
                'name': 'HVAC & Climate Control',
                'description': 'Heating, ventilation, and air conditioning components.',
                'system': 'Climate',
                'level': 'Major System',
                'examples': 'A/C compressor, heater core, A/C lines, blower motor',
                'freemium_value': 'HIGH',  # Great for subscription model
                'subcategories': [
                    {'name': 'A/C System Components', 'description': 'Air conditioning system parts.', 'examples': 'A/C compressor, condenser, evaporator, expansion valve'},
                    {'name': 'A/C Lines & Hoses', 'description': 'Refrigerant lines and hoses. ⭐ THIS IS WHERE YOUR A/C LINE GOES!', 'examples': 'High pressure line, low pressure line, suction hose, discharge hose'},
                    {'name': 'Heating System', 'description': 'Vehicle heating components.', 'examples': 'Heater core, heater control valve, heater hoses'},
                    {'name': 'Ventilation System', 'description': 'Air circulation components.', 'examples': 'Blower motor, cabin air filter, ductwork, vents'},
                    {'name': 'Climate Control Electronics', 'description': 'HVAC control modules and sensors.', 'examples': 'Climate control module, temperature sensors, blend door actuators'},
                    {'name': 'Refrigerant & Fluids', 'description': 'HVAC system fluids.', 'examples': 'R-134a refrigerant, R-1234yf refrigerant, A/C oil'},
                ]
            },
            {
                'name': 'Electrical Systems',
                'description': 'Vehicle electrical and electronic components.',
                'system': 'Electrical',
                'level': 'Major System',
                'examples': 'Alternator, battery, wiring harnesses, control modules',
                'subcategories': [
                    {'name': 'Charging System', 'description': 'Battery charging components.', 'examples': 'Alternator, battery, voltage regulator, charge cables'},
                    {'name': 'Starting System', 'description': 'Engine starting components.', 'examples': 'Starter motor, ignition switch, neutral safety switch'},
                    {'name': 'Control Modules', 'description': 'Electronic control units.', 'examples': 'ECM, PCM, BCM, ABS module, transmission control module'},
                    {'name': 'Wiring & Connectors', 'description': 'Vehicle wiring systems.', 'examples': 'Wiring harnesses, connectors, fuse boxes, relays'},
                    {'name': 'Sensors', 'description': 'Vehicle sensors and switches.', 'examples': 'Oxygen sensors, MAP sensors, temperature sensors, switches'},
                ]
            },
            {
                'name': 'Emissions Control',
                'description': 'Emissions control and pollution reduction systems.',
                'system': 'Emissions',
                'level': 'Major System',
                'examples': 'Catalytic converter, EGR valve, PCV system, oxygen sensors',
                'subcategories': [
                    {'name': 'Exhaust Treatment', 'description': 'Exhaust emissions treatment.', 'examples': 'Catalytic converter, DPF, SCR system, muffler'},
                    {'name': 'EGR System', 'description': 'Exhaust gas recirculation components.', 'examples': 'EGR valve, EGR cooler, EGR tube, vacuum lines'},
                    {'name': 'EVAP System', 'description': 'Evaporative emissions control.', 'examples': 'Charcoal canister, EVAP solenoids, fuel vapor lines'},
                    {'name': 'PCV System', 'description': 'Positive crankcase ventilation.', 'examples': 'PCV valve, breather hose, oil separator'},
                    {'name': 'Air Injection System', 'description': 'Secondary air injection for emissions.', 'examples': 'Air pump, check valves, air injection tubes'},
                ]
            },
            {
                'name': 'Safety Systems',
                'description': 'Vehicle safety and security systems.',
                'system': 'Safety',
                'level': 'Major System',
                'examples': 'Airbags, seat belts, ABS, security system',
                'subcategories': [
                    {'name': 'Airbag System', 'description': 'Airbag components and sensors.', 'examples': 'Airbag modules, crash sensors, clockspring, airbag computer'},
                    {'name': 'Seat Belt System', 'description': 'Seat belt and restraint components.', 'examples': 'Seat belts, pretensioners, buckles, retractors'},
                    {'name': 'Security System', 'description': 'Vehicle security components.', 'examples': 'Alarm system, immobilizer, keyless entry, door locks'},
                    {'name': 'Driver Assistance', 'description': 'Modern driver assistance features.', 'examples': 'Backup camera, parking sensors, lane assist, collision avoidance'},
                ]
            },
            
            # ========================================
            # CONSUMABLES & MAINTENANCE (Freemium Gold!)
            # ========================================
            {
                'name': 'Fluids & Consumables',
                'description': 'Vehicle fluids, oils, and consumable maintenance items.',
                'system': 'Maintenance',
                'level': 'Major System',
                'examples': 'Engine oil, transmission fluid, brake fluid, coolant',
                'freemium_value': 'ULTRA_HIGH',  # This is where the money is!
                'subcategories': [
                    {'name': 'Engine Fluids', 'description': 'Engine-related fluids and specifications.', 'examples': '5W-30 oil, 0W-20 oil, coolant, oil additives'},
                    {'name': 'Transmission Fluids', 'description': 'Transmission and drivetrain fluids.', 'examples': 'ATF, manual trans fluid, differential oil, transfer case fluid'},
                    {'name': 'Brake & Hydraulic Fluids', 'description': 'Brake and hydraulic system fluids.', 'examples': 'DOT 3 brake fluid, DOT 4, power steering fluid, clutch fluid'},
                    {'name': 'Specialty Fluids', 'description': 'Specialized vehicle fluids.', 'examples': 'Windshield washer fluid, A/C refrigerant, fuel additives'},
                    {'name': 'Maintenance Items', 'description': 'Regular maintenance consumables.', 'examples': 'Spark plugs, belts, hoses, fuses, bulbs'},
                ]
            },
            {
                'name': 'Filters',
                'description': 'Vehicle filtration components.',
                'system': 'Filtration',
                'level': 'Major System',
                'examples': 'Air filter, oil filter, fuel filter, cabin filter',
                'freemium_value': 'HIGH',  # Another subscription goldmine
                'subcategories': [
                    {'name': 'Engine Filters', 'description': 'Engine-related filters.', 'examples': 'Air filter, oil filter, PCV breather'},
                    {'name': 'Fuel Filters', 'description': 'Fuel system filtration.', 'examples': 'Fuel filter, fuel strainer, water separator'},
                    {'name': 'Cabin Filters', 'description': 'Interior air filtration.', 'examples': 'Cabin air filter, HEPA filter, activated carbon filter'},
                    {'name': 'Transmission Filters', 'description': 'Transmission and drivetrain filters.', 'examples': 'Transmission filter, differential breather'},
                ]
            },
            {
                'name': 'Gaskets, Seals & Hardware',
                'description': 'Sealing components and fastener hardware.',
                'system': 'Sealing',
                'level': 'Major System',
                'examples': 'Head gasket, weatherstripping, bolts, clips',
                'subcategories': [
                    {'name': 'Engine Gaskets & Seals', 'description': 'Engine sealing components.', 'examples': 'Head gasket, valve cover gasket, oil seals, timing cover gasket'},
                    {'name': 'Transmission Seals', 'description': 'Transmission and drivetrain seals.', 'examples': 'Output shaft seal, input shaft seal, differential seals'},
                    {'name': 'Body Seals & Weatherstripping', 'description': 'Body sealing components.', 'examples': 'Door seals, window seals, trunk seals, sunroof seals'},
                    {'name': 'Hardware & Fasteners', 'description': 'Bolts, clips, and fastening hardware.', 'examples': 'Engine bolts, body clips, trim fasteners, specialty hardware'},
                ]
            },
            {
                'name': 'Hybrid & Electric Vehicle',
                'description': 'Hybrid and electric vehicle specific components.',
                'system': 'Electric Vehicle',
                'level': 'Major System',
                'examples': 'Electric motor, battery pack, inverter, charging port',
                'subcategories': [
                    {'name': 'Electric Drive System', 'description': 'Electric propulsion components.', 'examples': 'Electric motor, inverter, DC-DC converter, electric transmission'},
                    {'name': 'Battery System', 'description': 'High voltage battery components.', 'examples': 'Battery pack, battery modules, BMS, cooling system'},
                    {'name': 'Charging System', 'description': 'Vehicle charging components.', 'examples': 'Charging port, onboard charger, charging cables, charging controller'},
                    {'name': 'Hybrid System', 'description': 'Hybrid-specific components.', 'examples': 'Hybrid battery, regenerative braking, electric water pump'},
                ]
            },
            
            # ========================================
            # BODY & EXTERIOR SYSTEMS
            # ========================================
            {
                'name': 'Body & Exterior',
                'description': 'Vehicle body panels, exterior trim, and accessories.',
                'system': 'Body',
                'level': 'Major System',
                'examples': 'Doors, fenders, bumpers, mirrors, trim',
                'subcategories': [
                    {'name': 'Body Panels', 'description': 'Main structural body panels.', 'examples': 'Doors, fenders, quarter panels, roof panels'},
                    {'name': 'Bumpers & Impact', 'description': 'Bumper assemblies and impact protection.', 'examples': 'Front bumper, rear bumper, impact absorbers, reinforcements'},
                    {'name': 'Hood & Trunk', 'description': 'Hood and trunk components.', 'examples': 'Hood, trunk lid, hinges, latches, gas struts'},
                    {'name': 'Exterior Trim & Molding', 'description': 'Exterior decorative and functional trim.', 'examples': 'Body molding, trim strips, emblems, badges'},
                    {'name': 'Mirrors & Glass', 'description': 'Exterior mirrors and glass components.', 'examples': 'Side mirrors, door glass, windshield, rear glass'},
                    {'name': 'Wipers & Washers', 'description': 'Windshield wiper and washer system.', 'examples': 'Wiper motors, wiper arms, washer reservoir, nozzles'},
                ]
            },
            {
                'name': 'Door Components & Glass',
                'description': 'Door assemblies, windows, and related hardware.',
                'system': 'Body',
                'level': 'Major System',
                'examples': 'Door panels, window glass, door handles, locks',
                'subcategories': [
                    {'name': 'Door Assemblies', 'description': 'Complete door units and shells.', 'examples': 'Door shell, door frame, door skin'},
                    {'name': 'Door Hardware', 'description': 'Interior and exterior door hardware.', 'examples': 'Door handles, lock cylinders, hinges, check straps'},
                    {'name': 'Window Systems', 'description': 'Door window and regulator components.', 'examples': 'Door glass, window regulators, window motors, window channels'},
                    {'name': 'Door Panels & Trim', 'description': 'Interior door panels and trim pieces.', 'examples': 'Door panels, armrests, door speakers, trim pieces'},
                ]
            },
            {
                'name': 'Lighting & Visibility',
                'description': 'Vehicle lighting and visibility components.',
                'system': 'Lighting',
                'level': 'Major System',
                'examples': 'Headlights, tail lights, turn signals, fog lights',
                'subcategories': [
                    {'name': 'Exterior Lighting', 'description': 'External vehicle lighting.', 'examples': 'Headlights, tail lights, turn signals, marker lights'},
                    {'name': 'Interior Lighting', 'description': 'Interior cabin lighting.', 'examples': 'Dome lights, courtesy lights, dashboard lights, accent lighting'},
                    {'name': 'Specialty Lighting', 'description': 'Fog lights and auxiliary lighting.', 'examples': 'Fog lights, driving lights, work lights, light bars'},
                    {'name': 'Bulbs & LEDs', 'description': 'Replacement bulbs and LED components.', 'examples': 'Halogen bulbs, LED bulbs, HID bulbs, flasher relays'},
                ]
            },
            
            # ========================================
            # INTERIOR & COMFORT SYSTEMS
            # ========================================
            {
                'name': 'Interior',
                'description': 'Interior components, seating, and cabin accessories.',
                'system': 'Interior',
                'level': 'Major System',
                'examples': 'Seats, dashboard, console, trim panels',
                'subcategories': [
                    {'name': 'Seating', 'description': 'Vehicle seats and components.', 'examples': 'Front seats, rear seats, seat motors, seat heaters'},
                    {'name': 'Dashboard & Instrument Panel', 'description': 'Dashboard components and gauges.', 'examples': 'Dashboard assembly, instrument cluster, gauge panels'},
                    {'name': 'Center Console', 'description': 'Center console and storage components.', 'examples': 'Console assembly, cup holders, storage bins, armrests'},
                    {'name': 'Interior Trim', 'description': 'Interior trim panels and accessories.', 'examples': 'Pillar trim, headliner, floor mats, cargo liners'},
                    {'name': 'Pedals & Controls', 'description': 'Pedals and interior controls.', 'examples': 'Brake pedal, gas pedal, shifter, parking brake'},
                ]
            },
            {
                'name': 'Infotainment & Electronics',
                'description': 'Audio, navigation, and entertainment systems.',
                'system': 'Electronics',
                'level': 'Major System',
                'examples': 'Radio, speakers, navigation, USB ports',
                'subcategories': [
                    {'name': 'Audio System', 'description': 'Vehicle audio components.', 'examples': 'Radio head unit, amplifiers, speakers, subwoofers'},
                    {'name': 'Navigation & Display', 'description': 'Navigation and display systems.', 'examples': 'GPS navigation, touch screens, display modules'},
                    {'name': 'Connectivity', 'description': 'Vehicle connectivity features.', 'examples': 'Bluetooth modules, USB ports, wireless charging, antennas'},
                    {'name': 'Entertainment Accessories', 'description': 'Entertainment and convenience features.', 'examples': 'DVD players, rear seat entertainment, gaming systems'},
                ]
            },
            
            # ========================================
            # TOOLS & MISCELLANEOUS
            # ========================================
            {
                'name': 'Tools & Equipment',
                'description': 'Automotive tools, equipment, and miscellaneous items.',
                'system': 'Tools',
                'level': 'Major System',
                'examples': 'Jack, tire iron, emergency kit, towing equipment',
                'subcategories': [
                    {'name': 'Emergency Equipment', 'description': 'Emergency and roadside equipment.', 'examples': 'Jack, lug wrench, spare tire, emergency kit'},
                    {'name': 'Towing & Hauling', 'description': 'Towing and cargo equipment.', 'examples': 'Trailer hitch, tow bar, cargo carriers, tie-downs'},
                    {'name': 'Maintenance Tools', 'description': 'Vehicle maintenance tools.', 'examples': 'Oil change tools, diagnostic equipment, specialty tools'},
                    {'name': 'Accessories', 'description': 'Vehicle accessories and add-ons.', 'examples': 'Floor mats, car covers, organizers, phone mounts'},
                ]
            },
        ]
        
        self.stdout.write(f'Processing {len(part_categories)} major automotive systems...')
        
        created_count = 0
        updated_count = 0
        skipped_count = 0

        @transaction.atomic
        def _create_category(category_data, parent_category_obj=None):
            nonlocal created_count, updated_count, skipped_count
            category_name = category_data['name']
            description = category_data['description']
            system = category_data.get('system', 'General')
            level = category_data.get('level', 'Component')
            examples = category_data.get('examples', '')
            
            if not dry_run:
                existing_category = PartCategory.objects.filter(name=category_name).first()
                
                if existing_category:
                    if update_existing:
                        # Update fields if different
                        if (existing_category.description != description or
                            existing_category.parent_category != parent_category_obj):
                            existing_category.description = description
                            existing_category.parent_category = parent_category_obj
                            existing_category.save()
                            updated_count += 1
                            status = '↻ UPDATED'
                        else:
                            skipped_count += 1
                            status = '- EXISTS'
                        category_obj = existing_category
                    else:
                        skipped_count += 1
                        status = '- EXISTS'
                        category_obj = existing_category
                else:
                    category_obj = PartCategory.objects.create(
                        name=category_name,
                        description=description,
                        parent_category=parent_category_obj
                    )
                    created_count += 1
                    status = '✓ CREATED'
            else:
                status = '? DRY RUN'
                category_obj = None # No object created in dry run

            # Display with freemium indicators
            freemium_indicator = ""
            if category_data.get('freemium_value') == 'ULTRA_HIGH':
                freemium_indicator = " 💰💰💰 FREEMIUM GOLDMINE!"
            elif category_data.get('freemium_value') == 'HIGH':
                freemium_indicator = " 💰💰 HIGH FREEMIUM VALUE"

            self.stdout.write(f'{status} {category_name}{freemium_indicator}')
            self.stdout.write(f'    {description}')
            if parent_category_obj:
                self.stdout.write(f'    Parent: {parent_category_obj.name}')
            self.stdout.write(f'    System: {system} | Level: {level}')
            self.stdout.write(f'    Examples: {examples}')
            self.stdout.write('')  # Blank line

            # Process subcategories
            if 'subcategories' in category_data and category_obj:
                for sub_category_data in category_data['subcategories']:
                    # Add parent reference and process
                    sub_category_data['parent'] = category_name
                    _create_category(sub_category_data, category_obj)

        # Process all categories
        for category_data in part_categories:
            _create_category(category_data)
        
        # Summary
        self.stdout.write('=' * 70)
        self.stdout.write('🎉 AUTOMOTIVE PARTS CATEGORIES - SUMMARY REPORT')
        self.stdout.write('=' * 70)
        
        if not dry_run:
            self.stdout.write(f'✅ Created: {created_count} categories')
            self.stdout.write(f'🔄 Updated: {updated_count} categories')
            self.stdout.write(f'⏭️  Existed: {skipped_count} categories')
            self.stdout.write(f'📊 Total: {created_count + updated_count + skipped_count} categories processed')
        else:
            self.stdout.write(f'📊 Would process: {len(part_categories)} major systems')
        
        # Freemium model insights
        self.stdout.write('\n💰 FREEMIUM MODEL INSIGHTS:')
        self.stdout.write('🏆 ULTRA HIGH VALUE: Fluids & Consumables (oil specs, fluid types)')
        self.stdout.write('🥈 HIGH VALUE: Filters, HVAC components (maintenance items)')
        self.stdout.write('🥉 GOOD VALUE: Safety systems, electrical components')
        
        # System breakdown
        self.stdout.write('\n🔧 MAJOR SYSTEMS BREAKDOWN:')
        self.stdout.write('🚗 Powertrain: Engine (FRONT & CENTER), Transmission, Intake/Exhaust')
        self.stdout.write('🛞 Chassis: Steering, Suspension, Brakes, Wheels')
        self.stdout.write('❄️  Climate: HVAC (YOUR A/C LINE HOME!), Emissions, Safety')
        self.stdout.write('🔌 Electrical: Unified electrical systems, Hybrid/EV')
        self.stdout.write('🏠 Body: Exterior, Interior, Doors, Lighting')
        self.stdout.write('⚙️  Maintenance: Fluids, Filters, Gaskets, Tools')
        
        # A/C Line solution
        self.stdout.write('\n❄️  A/C LINE SOLUTION:')
        self.stdout.write('✅ Your A/C line now belongs in:')
        self.stdout.write('   📁 HVAC & Climate Control > A/C Lines & Hoses')
        self.stdout.write('   🎯 Perfect fit for high-pressure and low-pressure A/C lines!')
        
        # Usage examples for your A/C line
        self.stdout.write('\n💡 A/C LINE CATEGORIZATION EXAMPLES:')
        self.stdout.write('🔸 High Pressure A/C Line → HVAC & Climate Control > A/C Lines & Hoses')
        self.stdout.write('🔸 Low Pressure A/C Line → HVAC & Climate Control > A/C Lines & Hoses')
        self.stdout.write('🔸 A/C Suction Hose → HVAC & Climate Control > A/C Lines & Hoses')
        self.stdout.write('🔸 A/C Discharge Hose → HVAC & Climate Control > A/C Lines & Hoses')
        
        # Next steps
        self.stdout.write('\n📋 NEXT STEPS TO SUCCESS:')
        self.stdout.write('1. ✅ Categories are ready - you can now add your A/C line!')
        self.stdout.write('2. 🏭 Add manufacturers: python manage.py add_manufacturers')
        self.stdout.write('3. 🔧 Add your first part with A/C Lines & Hoses category')
        self.stdout.write('4. 💰 Focus on Fluids & Consumables for freemium revenue')
        self.stdout.write('5. 📊 Build fitment database for subscriber value')
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'\n🚀 SUCCESS! {len(part_categories)} major automotive systems ready for action!')
            )
            self.stdout.write(
                self.style.SUCCESS('Your A/C line now has a perfect home in HVAC & Climate Control! 🎉')
            )
        else:
            self.stdout.write(
                self.style.WARNING('\n⚠️  DRY RUN complete - run without --dry-run to save changes')
            )
