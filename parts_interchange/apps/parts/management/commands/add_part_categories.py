# This goes in: parts_interchange/apps/parts/management/commands/add_part_categories.py

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.parts.models import PartCategory, Manufacturer


class Command(BaseCommand):
    help = 'Add comprehensive automotive part categories organized by system and function'

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
        parser.add_argument(
            '--include-specialized',
            action='store_true',
            default=True,
            help='Include specialized categories for performance/racing (default: True)'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        update_existing = options['update_existing']
        include_specialized = options['include_specialized']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No data will be saved'))
        
        # Comprehensive automotive part categories organized by system
        part_categories = [
            {
                'name': 'Door Components & Glass',
                'description': 'Components related to vehicle doors and glass.',
                'system': 'Body',
                'level': 'Major Component',
                'examples': 'Door panels, window glass, door handles',
                'subcategories': [
                    {'name': 'Door Panel', 'description': 'Interior and exterior door panels.', 'system': 'Body', 'level': 'Component', 'examples': 'Front door panel, rear door panel', 'parent': 'Door Components & Glass'},
                    {'name': 'Window Glass', 'description': 'Glass for vehicle windows.', 'system': 'Body', 'level': 'Component', 'examples': 'Door window glass, rear quarter glass', 'parent': 'Door Components & Glass'},
                    {'name': 'Vent/Quarter Glass', 'description': 'Fixed or movable vent and quarter glass.', 'system': 'Body', 'level': 'Component', 'examples': 'Rear quarter window, vent window', 'parent': 'Door Components & Glass'},
                    {'name': 'Window Regulator/Motor', 'description': 'Mechanism for raising and lowering windows.', 'system': 'Electrical', 'level': 'Component', 'examples': 'Power window motor, manual window regulator', 'parent': 'Door Components & Glass'},
                    {'name': 'Door Latch Actuator', 'description': 'Mechanism for locking and unlocking doors.', 'system': 'Electrical', 'level': 'Component', 'examples': 'Door lock actuator, power door latch', 'parent': 'Door Components & Glass'},
                    {'name': 'Exterior Door Handle', 'description': 'Outside door handles for vehicle entry.', 'system': 'Body', 'level': 'Component', 'examples': 'Front exterior door handle, rear exterior door handle', 'parent': 'Door Components & Glass'},
                    {'name': 'Interior Door Handle', 'description': 'Inside door handles for vehicle exit.', 'system': 'Interior', 'level': 'Component', 'examples': 'Front interior door handle, rear interior door handle', 'parent': 'Door Components & Glass'},
                    {'name': 'Speaker', 'description': 'Audio speakers located in doors.', 'system': 'Infotainment', 'level': 'Component', 'examples': 'Door speaker, tweeter', 'parent': 'Door Components & Glass'},
                    {'name': 'Sunroof Glass', 'description': 'Glass panel for sunroofs.', 'system': 'Body', 'level': 'Component', 'examples': 'Sliding sunroof glass, panoramic roof glass', 'parent': 'Door Components & Glass'},
                    {'name': 'Other Door Component/Glass Part', 'description': 'Miscellaneous door or glass related parts.', 'system': 'Body', 'level': 'Component', 'examples': 'Door hinge, door check strap', 'parent': 'Door Components & Glass'},
                ]
            },
            {
                'name': 'Interior',
                'description': 'General interior components of the vehicle.',
                'system': 'Interior',
                'level': 'Major Component',
                'examples': 'Seats, dashboard, floor mats',
                'subcategories': [
                    {'name': 'Cargo Cover', 'description': 'Cover for the cargo area.', 'system': 'Interior', 'level': 'Component', 'examples': 'Retractable cargo cover, rigid cargo cover', 'parent': 'Interior'},
                    {'name': 'Defroster Vent Panel', 'description': 'Panel for defroster vents.', 'system': 'Interior', 'level': 'Component', 'examples': 'Dashboard defroster vent, rear defroster vent', 'parent': 'Interior'},
                    {'name': 'Dash Pad/Top Panel', 'description': 'Top surface of the dashboard.', 'system': 'Interior', 'level': 'Component', 'examples': 'Dashboard top cover, dash pad', 'parent': 'Interior'},
                    {'name': 'Dash Assembly', 'description': 'Complete dashboard assembly.', 'system': 'Interior', 'level': 'Component', 'examples': 'Full dashboard assembly, instrument panel', 'parent': 'Interior'},
                    {'name': 'Instrument Cluster/Speedometer', 'description': 'Display for vehicle speed and other information.', 'system': 'Electrical', 'level': 'Component', 'examples': 'Digital instrument cluster, analog speedometer', 'parent': 'Interior'},
                    {'name': 'Rearview Mirror', 'description': 'Interior mirror for rear visibility.', 'system': 'Interior', 'level': 'Component', 'examples': 'Auto-dimming rearview mirror, manual rearview mirror', 'parent': 'Interior'},
                    {'name': 'Steering Wheel', 'description': 'Steering control for the vehicle.', 'system': 'Steering', 'level': 'Component', 'examples': 'Leather steering wheel, heated steering wheel', 'parent': 'Interior'},
                    {'name': 'Armrest', 'description': 'Rest for the arm, often integrated into seats or consoles.', 'system': 'Interior', 'level': 'Component', 'examples': 'Center console armrest, door panel armrest', 'parent': 'Interior'},
                    {'name': 'Floor Mats', 'description': 'Protective mats for the vehicle floor.', 'system': 'Interior', 'level': 'Component', 'examples': 'All-weather floor mats, carpet floor mats', 'parent': 'Interior'},
                    {'name': 'Glove Box', 'description': 'Storage compartment in the dashboard.', 'system': 'Interior', 'level': 'Component', 'examples': 'Glove box assembly, glove box door', 'parent': 'Interior'},
                    {
                        'name': 'Console',
                        'description': 'Central console units and parts.',
                        'system': 'Interior',
                        'level': 'Component',
                        'examples': 'Center console, overhead console',
                        'parent': 'Interior',
                        'subcategories': [
                            {'name': 'Front Center Consoles & Parts', 'description': 'Front console units and components.', 'system': 'Interior', 'level': 'Sub-Component', 'examples': 'Front console lid, front console insert', 'parent': 'Console'},
                            {'name': 'Rear Center Consoles & Parts', 'description': 'Rear console units and components.', 'system': 'Interior', 'level': 'Sub-Component', 'examples': 'Rear console armrest, rear console storage', 'parent': 'Console'},
                            {'name': 'Overhead Consoles & Dome Lights', 'description': 'Overhead console units and dome lights.', 'system': 'Interior', 'level': 'Sub-Component', 'examples': 'Overhead console with sunroof controls, dome light assembly', 'parent': 'Console'},
                            {'name': 'Other Console Part', 'description': 'Miscellaneous console parts.', 'system': 'Interior', 'level': 'Sub-Component', 'examples': 'Console trim, console bracket', 'parent': 'Console'},
                        ]
                    },
                    {'name': 'Seat Belt', 'description': 'Safety restraint system.', 'system': 'Safety', 'level': 'Component', 'examples': 'Front seat belt, rear seat belt buckle', 'parent': 'Interior'},
                    {'name': 'Shifter', 'description': 'Gear shifter assembly.', 'system': 'Drivetrain', 'level': 'Component', 'examples': 'Automatic shifter, manual shifter knob', 'parent': 'Interior'},
                    {'name': 'Brake/Clutch Pedal', 'description': 'Pedals for braking and clutch operation.', 'system': 'Brakes', 'level': 'Component', 'examples': 'Brake pedal assembly, clutch pedal pad', 'parent': 'Interior'},
                    {'name': 'Gas/Accelerator Pedal', 'description': 'Pedal for controlling engine speed.', 'system': 'Engine', 'level': 'Component', 'examples': 'Accelerator pedal sensor, gas pedal assembly', 'parent': 'Interior'},
                    {'name': 'Other Interior Part', 'description': 'Miscellaneous interior parts.', 'system': 'Interior', 'level': 'Component', 'examples': 'Interior trim piece, headliner', 'parent': 'Interior'},
                ]
            },
            {
                'name': 'Electrical (Interior)',
                'description': 'Electrical components located within the vehicle interior.',
                'system': 'Electrical',
                'level': 'Major Component',
                'examples': 'Clockspring, door switches, interior fuse box',
                'subcategories': [
                    {'name': 'Clockspring (Steering Wheel/Airbag Wiring)', 'description': 'Wiring for steering wheel controls and airbag.', 'system': 'Electrical', 'level': 'Component', 'examples': 'Steering wheel clockspring, airbag clockspring', 'parent': 'Electrical (Interior)'},
                    {'name': 'Door Switches (Lock/Window)', 'description': 'Switches for door locks and windows.', 'system': 'Electrical', 'level': 'Component', 'examples': 'Power window switch, door lock switch', 'parent': 'Electrical (Interior)'},
                    {'name': 'Cabin/Interior Fuse Box', 'description': 'Fuse box located in the cabin.', 'system': 'Electrical', 'level': 'Component', 'examples': 'Interior fuse panel, cabin fuse block', 'parent': 'Electrical (Interior)'},
                    {'name': 'Ignition Switch', 'description': 'Switch for starting the vehicle.', 'system': 'Electrical', 'level': 'Component', 'examples': 'Key ignition switch, push-button start switch', 'parent': 'Electrical (Interior)'},
                    {'name': 'Headlight Switch', 'description': 'Switch for controlling headlights.', 'system': 'Electrical', 'level': 'Component', 'examples': 'Headlight dimmer switch, automatic headlight switch', 'parent': 'Electrical (Interior)'},
                    {'name': 'Switch Panel', 'description': 'Panel containing multiple switches.', 'system': 'Electrical', 'level': 'Component', 'examples': 'Dashboard switch panel, center console switch panel', 'parent': 'Electrical (Interior)'},
                    {'name': 'Sunroof Motor', 'description': 'Motor for operating the sunroof.', 'system': 'Electrical', 'level': 'Component', 'examples': 'Sunroof tilt motor, sunroof slide motor', 'parent': 'Electrical (Interior)'},
                    {'name': 'Instrument Cluster/Speedometer', 'description': 'Display for vehicle speed and other information.', 'system': 'Electrical', 'level': 'Component', 'examples': 'Digital instrument cluster, analog speedometer', 'parent': 'Electrical (Interior)'},
                    {'name': 'Other Interior Electrical Part', 'description': 'Miscellaneous interior electrical parts.', 'system': 'Electrical', 'level': 'Component', 'examples': 'Interior light switch, power outlet', 'parent': 'Electrical (Interior)'},
                ]
            },
            {
                'name': 'Radio/Infotainment',
                'description': 'Components for vehicle audio and infotainment systems.',
                'system': 'Infotainment',
                'level': 'Major Component',
                'examples': 'Radio receiver, amplifier, speakers',
                'subcategories': [
                    {'name': 'Radio Receiver/CD-Player', 'description': 'Unit for receiving radio signals and playing CDs.', 'system': 'Infotainment', 'level': 'Component', 'examples': 'AM/FM radio, CD player head unit', 'parent': 'Radio/Infotainment'},
                    {'name': 'Radio/Infotainment Faceplate', 'description': 'Front panel of the radio or infotainment unit.', 'system': 'Infotainment', 'level': 'Component', 'examples': 'Touchscreen faceplate, button panel', 'parent': 'Radio/Infotainment'},
                    {'name': 'Amplifier', 'description': 'Device for boosting audio signals.', 'system': 'Infotainment', 'level': 'Component', 'examples': 'Audio amplifier, subwoofer amplifier', 'parent': 'Radio/Infotainment'},
                    {'name': 'Speaker', 'description': 'Audio output devices.', 'system': 'Infotainment', 'level': 'Component', 'examples': 'Door speaker, dashboard speaker', 'parent': 'Radio/Infotainment'},
                    {'name': 'Other Radio/Infotainment Part', 'description': 'Miscellaneous radio or infotainment parts.', 'system': 'Infotainment', 'level': 'Component', 'examples': 'Antenna, wiring harness', 'parent': 'Radio/Infotainment'},
                ]
            },
            {
                'name': 'Electrical (Exterior/Engine/Drivetrain)',
                'description': 'Electrical components located outside the cabin, in the engine bay, or related to the drivetrain.',
                'system': 'Electrical',
                'level': 'Major Component',
                'examples': 'Battery, alternator, engine fuse box',
                'subcategories': [
                    {'name': 'Battery', 'description': 'Vehicle battery for electrical power.', 'system': 'Electrical', 'level': 'Component', 'examples': '12V car battery, hybrid battery pack', 'parent': 'Electrical (Exterior/Engine/Drivetrain)'},
                    {'name': 'Alternator', 'description': 'Generates electrical power for the vehicle.', 'system': 'Electrical', 'level': 'Component', 'examples': 'Engine alternator, generator', 'parent': 'Electrical (Exterior/Engine/Drivetrain)'},
                    {'name': 'Exterior Camera/Projector', 'description': 'Cameras or projectors for exterior viewing or lighting.', 'system': 'Electrical', 'level': 'Component', 'examples': 'Backup camera, headlight projector', 'parent': 'Electrical (Exterior/Engine/Drivetrain)'},
                    {'name': 'Engine Fuse Box', 'description': 'Fuse box located in the engine bay.', 'system': 'Electrical', 'level': 'Component', 'examples': 'Under-hood fuse box, engine compartment fuse block', 'parent': 'Electrical (Exterior/Engine/Drivetrain)'},
                    {
                        'name': 'Computer',
                        'description': 'Electronic control modules and computers.',
                        'system': 'Electronics',
                        'level': 'Component',
                        'examples': 'Engine computer, ABS module',
                        'parent': 'Electrical (Exterior/Engine/Drivetrain)',
                        'subcategories': [
                            {'name': 'Engine Computer/Powertrain Control Module', 'description': 'Controls engine and powertrain functions.', 'system': 'Electronics', 'level': 'Sub-Component', 'examples': 'ECM, PCM', 'parent': 'Computer'},
                            {'name': 'ABS Module', 'description': 'Controls anti-lock braking system.', 'system': 'Electronics', 'level': 'Sub-Component', 'examples': 'ABS control unit, brake module', 'parent': 'Computer'},
                            {'name': 'Transmission/Drivetrain Module', 'description': 'Controls transmission and drivetrain functions.', 'system': 'Electronics', 'level': 'Sub-Component', 'examples': 'TCM, transfer case control module', 'parent': 'Computer'},
                            {'name': 'Body Control Module', 'description': 'Controls various body electrical functions.', 'system': 'Electronics', 'level': 'Sub-Component', 'examples': 'BCM, central electric module', 'parent': 'Computer'},
                            {'name': 'Communication Module (Bluetooth, Onstar, etc.)', 'description': 'Modules for communication systems.', 'system': 'Electronics', 'level': 'Sub-Component', 'examples': 'Bluetooth module, telematics control unit', 'parent': 'Computer'},
                            {'name': 'Driver Assist Module', 'description': 'Modules for driver assistance systems.', 'system': 'Electronics', 'level': 'Sub-Component', 'examples': 'Lane keep assist module, adaptive cruise control module', 'parent': 'Computer'},
                            {'name': 'Suspension Module (Yaw rate, roll, etc.)', 'description': 'Modules for suspension and stability control.', 'system': 'Electronics', 'level': 'Sub-Component', 'examples': 'Air suspension control module, yaw rate sensor', 'parent': 'Computer'},
                            {'name': 'Theft-Locking Module', 'description': 'Modules for vehicle security and locking.', 'system': 'Electronics', 'level': 'Sub-Component', 'examples': 'Immobilizer module, central locking module', 'parent': 'Computer'},
                            {'name': 'Other Computer/Module', 'description': 'Miscellaneous electronic control units.', 'system': 'Electronics', 'level': 'Sub-Component', 'examples': 'Navigation module, climate control module', 'parent': 'Computer'},
                        ]
                    },
                    {'name': 'Heater/AC Controller', 'description': 'Control unit for heating and air conditioning.', 'system': 'HVAC', 'level': 'Component', 'examples': 'Climate control panel, AC switch', 'parent': 'Electrical (Exterior/Engine/Drivetrain)'},
                    {'name': 'Starter Motor', 'description': 'Motor for starting the engine.', 'system': 'Electrical', 'level': 'Component', 'examples': 'Engine starter, starter solenoid', 'parent': 'Electrical (Exterior/Engine/Drivetrain)'},
                ]
            },
            {
                'name': 'Exterior',
                'description': 'External body and trim components.',
                'system': 'Body',
                'level': 'Major Component',
                'examples': 'Wiper motors, side mirrors, bumpers',
                'subcategories': [
                    {
                        'name': 'Wiper Motors & Arms',
                        'description': 'Components for windshield and rear window wipers.',
                        'system': 'Body',
                        'level': 'Component',
                        'examples': 'Front wiper motor, rear wiper arm',
                        'parent': 'Exterior',
                        'subcategories': [
                            {'name': 'Front Wiper Motor', 'description': 'Motor for front windshield wipers.', 'system': 'Electrical', 'level': 'Sub-Component', 'examples': 'Windshield wiper motor, front wiper assembly', 'parent': 'Wiper Motors & Arms'},
                            {'name': 'Rear Wiper Motor', 'description': 'Motor for rear window wiper.', 'system': 'Electrical', 'level': 'Sub-Component', 'examples': 'Rear hatch wiper motor, rear wiper assembly', 'parent': 'Wiper Motors & Arms'},
                            {'name': 'Front Wiper Arm', 'description': 'Arm for front windshield wipers.', 'system': 'Body', 'level': 'Sub-Component', 'examples': 'Driver side wiper arm, passenger side wiper arm', 'parent': 'Wiper Motors & Arms'},
                            {'name': 'Rear Wiper Arm', 'description': 'Arm for rear window wiper.', 'system': 'Body', 'level': 'Sub-Component', 'examples': 'Rear hatch wiper arm, rear window wiper arm', 'parent': 'Wiper Motors & Arms'},
                            {'name': 'Other Wiper Part', 'description': 'Miscellaneous wiper system parts.', 'system': 'Body', 'level': 'Sub-Component', 'examples': 'Wiper blade, wiper linkage', 'parent': 'Wiper Motors & Arms'},
                        ]
                    },
                    {'name': 'Side View Door Mirror', 'description': 'Exterior mirrors for side and rear visibility.', 'system': 'Body', 'level': 'Component', 'examples': 'Driver side mirror, passenger side mirror', 'parent': 'Exterior'},
                    {'name': 'Running Board', 'description': 'Step for easier entry and exit.', 'system': 'Body', 'level': 'Component', 'examples': 'Side step, nerf bar', 'parent': 'Exterior'},
                    {'name': 'Luggage/Roof Rack', 'description': 'System for carrying luggage on the roof.', 'system': 'Body', 'level': 'Component', 'examples': 'Roof rack cross bars, luggage carrier', 'parent': 'Exterior'},
                    {
                        'name': 'Bumpers & Parts',
                        'description': 'Front and rear bumper assemblies and components.',
                        'system': 'Body',
                        'level': 'Component',
                        'examples': 'Front bumper cover, rear bumper reinforcement',
                        'parent': 'Exterior',
                        'subcategories': [
                            {'name': 'Front Bumper', 'description': 'Front bumper assembly.', 'system': 'Body', 'level': 'Sub-Component', 'examples': 'Front bumper cover, front bumper assembly', 'parent': 'Bumpers & Parts'},
                            {'name': 'Rear Bumper', 'description': 'Rear bumper assembly.', 'system': 'Body', 'level': 'Sub-Component', 'examples': 'Rear bumper cover, rear bumper assembly', 'parent': 'Bumpers & Parts'},
                            {'name': 'Front Bumper Reinforcements', 'description': 'Reinforcement for the front bumper.', 'system': 'Body', 'level': 'Sub-Component', 'examples': 'Front bumper impact bar, front bumper absorber', 'parent': 'Bumpers & Parts'},
                            {'name': 'Rear Bumper Reinforcement', 'description': 'Reinforcement for the rear bumper.', 'system': 'Body', 'level': 'Sub-Component', 'examples': 'Rear bumper impact bar, rear bumper absorber', 'parent': 'Bumpers & Parts'},
                            {'name': 'Bumper End Caps/Shocks', 'description': 'End caps and energy absorbers for bumpers.', 'system': 'Body', 'level': 'Sub-Component', 'examples': 'Bumper end cap, bumper shock absorber', 'parent': 'Bumpers & Parts'},
                            {'name': 'Other Bumper Part', 'description': 'Miscellaneous bumper parts.', 'system': 'Body', 'level': 'Sub-Component', 'examples': 'Bumper bracket, bumper trim', 'parent': 'Bumpers & Parts'},
                        ]
                    },
                    {'name': 'Grille', 'description': 'Front grille assembly.', 'system': 'Body', 'level': 'Component', 'examples': 'Front grille, grille insert', 'parent': 'Exterior'},
                    {'name': 'Header Panel/Radiator Core Support', 'description': 'Panel supporting the radiator and front end.', 'system': 'Body', 'level': 'Component', 'examples': 'Radiator support, header panel', 'parent': 'Exterior'},
                    {
                        'name': 'Hood',
                        'description': 'Engine hood and related components.',
                        'system': 'Body',
                        'level': 'Component',
                        'examples': 'Hood panel, hood latch',
                        'parent': 'Exterior',
                        'subcategories': [
                            {'name': 'Hood', 'description': 'Main hood panel.', 'system': 'Body', 'level': 'Sub-Component', 'examples': 'Engine hood, hood panel', 'parent': 'Hood'},
                            {'name': 'Hood Latch', 'description': 'Mechanism for securing the hood.', 'system': 'Body', 'level': 'Sub-Component', 'examples': 'Hood latch assembly, hood release cable', 'parent': 'Hood'},
                            {'name': 'Hood Hinge', 'description': 'Hinge for opening and closing the hood.', 'system': 'Body', 'level': 'Sub-Component', 'examples': 'Left hood hinge, right hood hinge', 'parent': 'Hood'},
                            {'name': 'Hood Emblem', 'description': 'Emblem or badge on the hood.', 'system': 'Body', 'level': 'Sub-Component', 'examples': 'Brand emblem, hood ornament', 'parent': 'Hood'},
                            {'name': 'Other Hood Part', 'description': 'Miscellaneous hood parts.', 'system': 'Body', 'level': 'Sub-Component', 'examples': 'Hood prop rod, hood insulation', 'parent': 'Hood'},
                        ]
                    },
                    {
                        'name': 'Fenders & Parts',
                        'description': 'Fender panels and related components.',
                        'system': 'Body',
                        'level': 'Component',
                        'examples': 'Front fender, fender liner',
                        'parent': 'Exterior',
                        'subcategories': [
                            {'name': 'Fender', 'description': 'Main fender panel.', 'system': 'Body', 'level': 'Sub-Component', 'examples': 'Front fender, rear fender', 'parent': 'Fenders & Parts'},
                            {'name': 'Fender Liner', 'description': 'Liner inside the fender well.', 'system': 'Body', 'level': 'Sub-Component', 'examples': 'Front fender liner, rear fender liner', 'parent': 'Fenders & Parts'},
                            {'name': 'Fender Moulding/Overfender/Trim', 'description': 'Moulding or trim for fenders.', 'system': 'Body', 'level': 'Sub-Component', 'examples': 'Fender flare, fender trim', 'parent': 'Fenders & Parts'},
                            {'name': 'Other Fender Part', 'description': 'Miscellaneous fender parts.', 'system': 'Body', 'level': 'Sub-Component', 'examples': 'Fender bracket, fender vent', 'parent': 'Fenders & Parts'},
                        ]
                    },
                    {'name': 'Engine Cradle/Subframe', 'description': 'Support structure for the engine and suspension.', 'system': 'Chassis', 'level': 'Component', 'examples': 'Front subframe, engine crossmember', 'parent': 'Exterior'},
                    {
                        'name': 'Convertible Top Parts',
                        'description': 'Components for convertible tops.',
                        'system': 'Body',
                        'level': 'Component',
                        'examples': 'Convertible top fabric, convertible top motor',
                        'parent': 'Exterior',
                        'subcategories': [
                            {'name': 'Convertible Top', 'description': 'Fabric or hardtop convertible roof.', 'system': 'Body', 'level': 'Sub-Component', 'examples': 'Soft top, retractable hardtop', 'parent': 'Convertible Top Parts'},
                            {'name': 'Convertible Top Motor/Pump', 'description': 'Motor or pump for operating the convertible top.', 'system': 'Electrical', 'level': 'Sub-Component', 'examples': 'Hydraulic pump, electric motor', 'parent': 'Convertible Top Parts'},
                            {'name': 'Convertible Top Module/Computer', 'description': 'Control module for the convertible top.', 'system': 'Electronics', 'level': 'Sub-Component', 'examples': 'Convertible top control unit, roof module', 'parent': 'Convertible Top Parts'},
                            {'name': 'Convertible Flaps/Trim', 'description': 'Flaps or trim pieces for convertible tops.', 'system': 'Body', 'level': 'Sub-Component', 'examples': 'Convertible top flap, trim strip', 'parent': 'Convertible Top Parts'},
                            {'name': 'Other Convertible Part', 'description': 'Miscellaneous convertible top parts.', 'system': 'Body', 'level': 'Sub-Component', 'examples': 'Convertible top weatherstrip, convertible top latch', 'parent': 'Convertible Top Parts'},
                        ]
                    },
                    {'name': 'Other Exterior Part', 'description': 'Miscellaneous exterior parts.', 'system': 'Body', 'level': 'Component', 'examples': 'Body molding, emblem', 'parent': 'Exterior'},
                ]
            },
            {
                'name': 'Engine',
                'description': 'Core engine components.',
                'system': 'Powertrain',
                'level': 'Major Component',
                'examples': 'Complete engine, ignition coil, cylinder head',
                'subcategories': [
                    {'name': 'Complete Engine Assembly', 'description': 'Entire engine unit.', 'system': 'Powertrain', 'level': 'Component', 'examples': 'Long block, short block', 'parent': 'Engine'},
                    {'name': 'Ignition Coil', 'description': 'Component for igniting fuel.', 'system': 'Electrical', 'level': 'Component', 'examples': 'Spark plug coil, ignition coil pack', 'parent': 'Engine'},
                    {'name': 'Air Injection Pump/Secondary Air Pump', 'description': 'Pump for emissions control.', 'system': 'Emissions', 'level': 'Component', 'examples': 'Smog pump, secondary air injection pump', 'parent': 'Engine'},
                    {'name': 'Camshaft', 'description': 'Controls valve timing.', 'system': 'Powertrain', 'level': 'Component', 'examples': 'Intake camshaft, exhaust camshaft', 'parent': 'Engine'},
                    {'name': 'Cam Phaser/VVT Actuator', 'description': 'Adjusts camshaft timing.', 'system': 'Powertrain', 'level': 'Component', 'examples': 'VVT solenoid, cam phaser', 'parent': 'Engine'},
                    {'name': 'Crankshaft', 'description': 'Converts reciprocating motion to rotational motion.', 'system': 'Powertrain', 'level': 'Component', 'examples': 'Engine crankshaft, main bearing', 'parent': 'Engine'},
                    {'name': 'Cylinder Head', 'description': 'Top part of the engine cylinder.', 'system': 'Powertrain', 'level': 'Component', 'examples': 'Engine cylinder head, cylinder head gasket', 'parent': 'Engine'},
                    {'name': 'Connecting Rod & Piston', 'description': 'Connects piston to crankshaft.', 'system': 'Powertrain', 'level': 'Component', 'examples': 'Piston assembly, connecting rod bearing', 'parent': 'Engine'},
                    {'name': 'Oil Pan', 'description': 'Reservoir for engine oil.', 'system': 'Lubrication', 'level': 'Component', 'examples': 'Engine oil pan, oil drain plug', 'parent': 'Engine'},
                    {'name': 'Oil Pump', 'description': 'Circulates engine oil.', 'system': 'Lubrication', 'level': 'Component', 'examples': 'Engine oil pump, oil pump screen', 'parent': 'Engine'},
                    {'name': 'Engine/Cylinder Block', 'description': 'Main structural component of the engine.', 'system': 'Powertrain', 'level': 'Component', 'examples': 'Engine block, cylinder sleeve', 'parent': 'Engine'},
                    {'name': 'Flywheel/Flexplate', 'description': 'Connects engine to transmission.', 'system': 'Powertrain', 'level': 'Component', 'examples': 'Engine flywheel, flexplate', 'parent': 'Engine'},
                    {'name': 'Valvetrain Parts', 'description': 'Components controlling valve operation.', 'system': 'Powertrain', 'level': 'Component', 'examples': 'Valve spring, rocker arm', 'parent': 'Engine'},
                    {'name': 'Harmonic Balancer', 'description': 'Reduces engine vibrations.', 'system': 'Powertrain', 'level': 'Component', 'examples': 'Crankshaft pulley, vibration damper', 'parent': 'Engine'},
                    {'name': 'Turbocharger/Supercharger', 'description': 'Boosts engine power.', 'system': 'Air Intake', 'level': 'Component', 'examples': 'Turbo assembly, supercharger unit', 'parent': 'Engine'},
                    {'name': 'Valve Cover', 'description': 'Covers the valvetrain.', 'system': 'Powertrain', 'level': 'Component', 'examples': 'Engine valve cover, valve cover gasket', 'parent': 'Engine'},
                    {'name': 'Water Pump', 'description': 'Circulates coolant through the engine.', 'system': 'Cooling', 'level': 'Component', 'examples': 'Engine water pump, coolant pump', 'parent': 'Engine'},
                    {'name': 'Other Engine Part', 'description': 'Miscellaneous engine parts.', 'system': 'Powertrain', 'level': 'Component', 'examples': 'Engine mount, timing chain', 'parent': 'Engine'},
                ]
            },
            {
                'name': 'Intake, Exhaust, & Fuel',
                'description': 'Components for air intake, exhaust, and fuel delivery systems.',
                'system': 'Engine Systems',
                'level': 'Major Component',
                'examples': 'Muffler, intake manifold, fuel pump',
                'subcategories': [
                    {'name': 'Muffler', 'description': 'Reduces exhaust noise.', 'system': 'Exhaust', 'level': 'Component', 'examples': 'Exhaust muffler, resonator', 'parent': 'Intake, Exhaust, & Fuel'},
                    {'name': 'Resonator', 'description': 'Reduces exhaust noise and drone.', 'system': 'Exhaust', 'level': 'Component', 'examples': 'Exhaust resonator, mid-pipe resonator', 'parent': 'Intake, Exhaust, & Fuel'},
                    {'name': 'Exhaust Manifold', 'description': 'Collects exhaust gases from cylinders.', 'system': 'Exhaust', 'level': 'Component', 'examples': 'Header, exhaust manifold gasket', 'parent': 'Intake, Exhaust, & Fuel'},
                    {'name': 'Intake Manifold', 'description': 'Distributes air to engine cylinders.', 'system': 'Air Intake', 'level': 'Component', 'examples': 'Engine intake manifold, intake manifold gasket', 'parent': 'Intake, Exhaust, & Fuel'},
                    {'name': 'Throttle Body', 'description': 'Controls airflow into the engine.', 'system': 'Air Intake', 'level': 'Component', 'examples': 'Electronic throttle body, mechanical throttle body', 'parent': 'Intake, Exhaust, & Fuel'},
                    {'name': 'Air Intake Tube/Resonator', 'description': 'Tube connecting air cleaner to throttle body.', 'system': 'Air Intake', 'level': 'Component', 'examples': 'Air intake hose, intake resonator', 'parent': 'Intake, Exhaust, & Fuel'},
                    {'name': 'Air Cleaner', 'description': 'Filters air entering the engine.', 'system': 'Air Intake', 'level': 'Component', 'examples': 'Air filter box, air filter element', 'parent': 'Intake, Exhaust, & Fuel'},
                    {'name': 'Air Shutter/Splitter/Guide', 'description': 'Directs airflow for cooling or aerodynamics.', 'system': 'Body', 'level': 'Component', 'examples': 'Active grille shutter, air guide', 'parent': 'Intake, Exhaust, & Fuel'},
                    {'name': 'Mass Air Meter', 'description': 'Measures air mass entering the engine.', 'system': 'Electrical', 'level': 'Component', 'examples': 'MAF sensor, mass airflow sensor', 'parent': 'Intake, Exhaust, & Fuel'},
                    {'name': 'Evaporator/Charcoal Vapor Canister', 'description': 'Part of the evaporative emissions system.', 'system': 'Emissions', 'level': 'Component', 'examples': 'EVAP canister, charcoal canister', 'parent': 'Intake, Exhaust, & Fuel'},
                    {'name': 'Fuel/Water Separator', 'description': 'Separates water from fuel.', 'system': 'Fuel', 'level': 'Component', 'examples': 'Diesel fuel filter, water separator', 'parent': 'Intake, Exhaust, & Fuel'},
                    {'name': 'Fuel/Gas Cap', 'description': 'Seals the fuel tank opening.', 'system': 'Fuel', 'level': 'Component', 'examples': 'Gas cap, fuel filler cap', 'parent': 'Intake, Exhaust, & Fuel'},
                    {
                        'name': 'Fuel Pump',
                        'description': 'Pumps fuel from tank to engine.',
                        'system': 'Fuel',
                        'level': 'Component',
                        'examples': 'Electric fuel pump, mechanical fuel pump',
                        'parent': 'Intake, Exhaust, & Fuel',
                        'subcategories': [
                            {'name': 'Low Pressure (In Tank)', 'description': 'Fuel pump located in the fuel tank.', 'system': 'Fuel', 'level': 'Sub-Component', 'examples': 'In-tank fuel pump, fuel sender unit', 'parent': 'Fuel Pump'},
                            {'name': 'High Pressure (Engine Driven)', 'description': 'Fuel pump driven by the engine for direct injection.', 'system': 'Fuel', 'level': 'Sub-Component', 'examples': 'HPFP, direct injection fuel pump', 'parent': 'Fuel Pump'},
                            {'name': 'Other Fuel Pump', 'description': 'Miscellaneous fuel pump parts.', 'system': 'Fuel', 'level': 'Sub-Component', 'examples': 'Fuel pump relay, fuel pump module', 'parent': 'Fuel Pump'},
                        ]
                    },
                    {'name': 'Fuel Line', 'description': 'Carries fuel throughout the vehicle.', 'system': 'Fuel', 'level': 'Component', 'examples': 'Fuel supply line, fuel return line', 'parent': 'Intake, Exhaust, & Fuel'},
                    {'name': 'Fuel Rail', 'description': 'Distributes fuel to injectors.', 'system': 'Fuel', 'level': 'Component', 'examples': 'Fuel injector rail, common rail', 'parent': 'Intake, Exhaust, & Fuel'},
                    {'name': 'Fuel Injector', 'description': 'Sprays fuel into engine.', 'system': 'Fuel', 'level': 'Component', 'examples': 'Gasoline fuel injector, diesel injector', 'parent': 'Intake, Exhaust, & Fuel'},
                    {'name': 'Other Intake Part', 'description': 'Miscellaneous intake system parts.', 'system': 'Air Intake', 'level': 'Component', 'examples': 'Intake hose, air duct', 'parent': 'Intake, Exhaust, & Fuel'},
                    {'name': 'Other Exhaust Part', 'description': 'Miscellaneous exhaust system parts.', 'system': 'Exhaust', 'level': 'Component', 'examples': 'Exhaust hanger, exhaust clamp', 'parent': 'Intake, Exhaust, & Fuel'},
                    {'name': 'Other Fuel Part', 'description': 'Miscellaneous fuel system parts.', 'system': 'Fuel', 'level': 'Component', 'examples': 'Fuel filter, fuel pressure regulator', 'parent': 'Intake, Exhaust, & Fuel'},
                ]
            },
            {
                'name': 'Engine/Engine Bay Accessories',
                'description': 'Accessories located in the engine bay.',
                'system': 'Engine Systems',
                'level': 'Major Component',
                'examples': 'Alternator, A/C compressor, radiator',
                'subcategories': [
                    {'name': 'Alternator', 'description': 'Generates electrical power for the vehicle.', 'system': 'Electrical', 'level': 'Component', 'examples': 'Engine alternator, generator', 'parent': 'Engine/Engine Bay Accessories'},
                    {'name': 'Battery', 'description': 'Vehicle battery for electrical power.', 'system': 'Electrical', 'level': 'Component', 'examples': '12V car battery, hybrid battery pack', 'parent': 'Engine/Engine Bay Accessories'},
                    {'name': 'A/C Compressor', 'description': 'Compresses refrigerant for air conditioning.', 'system': 'HVAC', 'level': 'Component', 'examples': 'AC compressor, AC clutch', 'parent': 'Engine/Engine Bay Accessories'},
                    {'name': 'Engine Cooling Fan (Electric)', 'description': 'Electric fan for engine cooling.', 'system': 'Cooling', 'level': 'Component', 'examples': 'Radiator fan, condenser fan', 'parent': 'Engine/Engine Bay Accessories'},
                    {'name': 'Engine Driven Fans, Clutches, & Fan Shrouds', 'description': 'Engine-driven cooling fans and related components.', 'system': 'Cooling', 'level': 'Component', 'examples': 'Fan clutch, fan blade, fan shroud', 'parent': 'Engine/Engine Bay Accessories'},
                    {'name': 'Washer Bottle', 'description': 'Reservoir for windshield washer fluid.', 'system': 'Body', 'level': 'Component', 'examples': 'Windshield washer reservoir, washer fluid tank', 'parent': 'Engine/Engine Bay Accessories'},
                    {'name': 'Starter Motor', 'description': 'Motor for starting the engine.', 'system': 'Electrical', 'level': 'Component', 'examples': 'Engine starter, starter solenoid', 'parent': 'Engine/Engine Bay Accessories'},
                    {'name': 'Engine Cradle/Subframe', 'description': 'Support structure for the engine and suspension.', 'system': 'Chassis', 'level': 'Component', 'examples': 'Front subframe, engine crossmember', 'parent': 'Engine/Engine Bay Accessories'},
                    {'name': 'Battery Tray', 'description': 'Tray for holding the vehicle battery.', 'system': 'Electrical', 'level': 'Component', 'examples': 'Battery holder, battery box', 'parent': 'Engine/Engine Bay Accessories'},
                    {
                        'name': 'Radiators & Coolers',
                        'description': 'Heat exchangers for various fluids.',
                        'system': 'Cooling',
                        'level': 'Component',
                        'examples': 'Engine radiator, AC condenser',
                        'parent': 'Engine/Engine Bay Accessories',
                        'subcategories': [
                            {'name': 'Radiator', 'description': 'Cools engine coolant.', 'system': 'Cooling', 'level': 'Sub-Component', 'examples': 'Engine radiator, coolant radiator', 'parent': 'Radiators & Coolers'},
                            {'name': 'A/C Condenser', 'description': 'Cools refrigerant in AC system.', 'system': 'HVAC', 'level': 'Sub-Component', 'examples': 'AC condenser, air conditioning condenser', 'parent': 'Radiators & Coolers'},
                            {'name': 'Intercooler', 'description': 'Cools compressed air from turbo/supercharger.', 'system': 'Air Intake', 'level': 'Sub-Component', 'examples': 'Turbo intercooler, charge air cooler', 'parent': 'Radiators & Coolers'},
                            {'name': 'Engine Oil Cooler', 'description': 'Cools engine oil.', 'system': 'Lubrication', 'level': 'Sub-Component', 'examples': 'Oil cooler, engine oil heat exchanger', 'parent': 'Radiators & Coolers'},
                            {'name': 'Transmission Oil Cooler', 'description': 'Cools transmission fluid.', 'system': 'Drivetrain', 'level': 'Sub-Component', 'examples': 'Transmission cooler, ATF cooler', 'parent': 'Radiators & Coolers'},
                            {'name': 'Power Steering Cooler', 'description': 'Cools power steering fluid.', 'system': 'Steering', 'level': 'Sub-Component', 'examples': 'Power steering fluid cooler, PS cooler', 'parent': 'Radiators & Coolers'},
                            {'name': 'Other Cooler', 'description': 'Miscellaneous fluid coolers.', 'system': 'Cooling', 'level': 'Sub-Component', 'examples': 'Fuel cooler, differential cooler', 'parent': 'Radiators & Coolers'},
                        ]
                    },
                    {'name': 'Other Engine Accessory Part', 'description': 'Miscellaneous engine bay accessories.', 'system': 'Engine Systems', 'level': 'Component', 'examples': 'Power steering pump, serpentine belt', 'parent': 'Engine/Engine Bay Accessories'},
                ]
            },
            {
                'name': 'Transmission & Drivetrain',
                'description': 'Components for power transmission to the wheels.',
                'system': 'Drivetrain',
                'level': 'Major Component',
                'examples': 'Transmission, transfer case, axle',
                'subcategories': [
                    {'name': 'Transmission', 'description': 'Transmits power from engine to wheels.', 'system': 'Drivetrain', 'level': 'Component', 'examples': 'Automatic transmission, manual transmission', 'parent': 'Transmission & Drivetrain'},
                    {'name': 'Transfer Case', 'description': 'Distributes power in 4WD/AWD vehicles.', 'system': 'Drivetrain', 'level': 'Component', 'examples': '4x4 transfer case, AWD transfer case', 'parent': 'Transmission & Drivetrain'},
                    {'name': 'Torque Converter', 'description': 'Connects engine to automatic transmission.', 'system': 'Drivetrain', 'level': 'Component', 'examples': 'Automatic transmission torque converter, lock-up torque converter', 'parent': 'Transmission & Drivetrain'},
                    {'name': 'Front Carrier/Differential/Axle', 'description': 'Front differential and axle assembly.', 'system': 'Drivetrain', 'level': 'Component', 'examples': 'Front differential, front axle shaft', 'parent': 'Transmission & Drivetrain'},
                    {'name': 'Rear Carrier/Differential/Axle', 'description': 'Rear differential and axle assembly.', 'system': 'Drivetrain', 'level': 'Component', 'examples': 'Rear differential, rear axle shaft', 'parent': 'Transmission & Drivetrain'},
                    {'name': 'Axle/Half/Drive/Prop Shaft', 'description': 'Shafts transmitting power to wheels or differentials.', 'system': 'Drivetrain', 'level': 'Component', 'examples': 'CV axle, driveshaft, propeller shaft', 'parent': 'Transmission & Drivetrain'},
                    {'name': 'Front Driveshaft', 'description': 'Driveshaft for front-wheel drive or front axle.', 'system': 'Drivetrain', 'level': 'Component', 'examples': 'Front propeller shaft, front CV driveshaft', 'parent': 'Transmission & Drivetrain'},
                    {'name': 'Rear Driveshaft', 'description': 'Driveshaft for rear-wheel drive or rear axle.', 'system': 'Drivetrain', 'level': 'Component', 'examples': 'Rear propeller shaft, rear CV driveshaft', 'parent': 'Transmission & Drivetrain'},
                    {'name': 'Other Transmission/Drivetrain part', 'description': 'Miscellaneous transmission or drivetrain parts.', 'system': 'Drivetrain', 'level': 'Component', 'examples': 'Transmission mount, differential cover', 'parent': 'Transmission & Drivetrain'},
                ]
            },
            {
                'name': 'Steering & Suspension',
                'description': 'Components for vehicle steering and suspension.',
                'system': 'Chassis',
                'level': 'Major Component',
                'examples': 'Steering wheel, strut, control arm',
                'subcategories': [
                    {'name': 'Steering Wheel', 'description': 'Steering control for the vehicle.', 'system': 'Steering', 'level': 'Component', 'examples': 'Leather steering wheel, heated steering wheel', 'parent': 'Steering & Suspension'},
                    {'name': 'Steering Column', 'description': 'Column connecting steering wheel to steering gear.', 'system': 'Steering', 'level': 'Component', 'examples': 'Tilt steering column, telescopic steering column', 'parent': 'Steering & Suspension'},
                    {'name': 'Steering Column Intermediate Link', 'description': 'Link connecting steering column to steering rack.', 'system': 'Steering', 'level': 'Component', 'examples': 'Steering shaft, universal joint', 'parent': 'Steering & Suspension'},
                    {'name': 'Steering Rack/Gear', 'description': 'Converts steering wheel input to wheel movement.', 'system': 'Steering', 'level': 'Component', 'examples': 'Power steering rack, manual steering gear', 'parent': 'Steering & Suspension'},
                    {'name': 'Engine Cradle/Subframe', 'description': 'Support structure for the engine and suspension.', 'system': 'Chassis', 'level': 'Component', 'examples': 'Front subframe, engine crossmember', 'parent': 'Steering & Suspension'},
                    {'name': 'Coil Spring', 'description': 'Spring for suspension system.', 'system': 'Suspension', 'level': 'Component', 'examples': 'Front coil spring, rear coil spring', 'parent': 'Steering & Suspension'},
                    {'name': 'Strut (Loaded Shock)', 'description': 'Combines shock absorber and coil spring.', 'system': 'Suspension', 'level': 'Component', 'examples': 'Front strut assembly, rear strut', 'parent': 'Steering & Suspension'},
                    {'name': 'Steering Knuckle/Hub', 'description': 'Connects wheel to suspension.', 'system': 'Suspension', 'level': 'Component', 'examples': 'Front steering knuckle, wheel hub assembly', 'parent': 'Steering & Suspension'},
                    {
                        'name': 'Control Arms',
                        'description': 'Links connecting suspension to chassis.',
                        'system': 'Suspension',
                        'level': 'Component',
                        'examples': 'Upper control arm, lower control arm',
                        'parent': 'Steering & Suspension',
                        'subcategories': [
                            {'name': 'Front Upper', 'description': 'Upper control arm for front suspension.', 'system': 'Suspension', 'level': 'Sub-Component', 'examples': 'Front upper control arm, upper A-arm', 'parent': 'Control Arms'},
                            {'name': 'Front Lower', 'description': 'Lower control arm for front suspension.', 'system': 'Suspension', 'level': 'Sub-Component', 'examples': 'Front lower control arm, lower A-arm', 'parent': 'Control Arms'},
                            {'name': 'Rear Upper', 'description': 'Upper control arm for rear suspension.', 'system': 'Suspension', 'level': 'Sub-Component', 'examples': 'Rear upper control arm, rear upper link', 'parent': 'Control Arms'},
                            {'name': 'Rear Lower', 'description': 'Lower control arm for rear suspension.', 'system': 'Suspension', 'level': 'Sub-Component', 'examples': 'Rear lower control arm, rear lower link', 'parent': 'Control Arms'},
                        ]
                    },
                    {'name': 'Stabilizer Bar/Sway bar', 'description': 'Reduces body roll during cornering.', 'system': 'Suspension', 'level': 'Component', 'examples': 'Front sway bar, rear stabilizer bar', 'parent': 'Steering & Suspension'},
                    {'name': 'Strut Tower Brace', 'description': 'Stiffens chassis for improved handling.', 'system': 'Suspension', 'level': 'Component', 'examples': 'Front strut brace, rear strut bar', 'parent': 'Steering & Suspension'},
                    {'name': 'Air Suspension Compressor', 'description': 'Compressor for air suspension systems.', 'system': 'Suspension', 'level': 'Component', 'examples': 'Air ride compressor, air suspension pump', 'parent': 'Steering & Suspension'},
                    {'name': 'Other Steering/Suspension Part', 'description': 'Miscellaneous steering or suspension parts.', 'system': 'Chassis', 'level': 'Component', 'examples': 'Tie rod end, ball joint', 'parent': 'Steering & Suspension'},
                ]
            },
            {
                'name': 'Lights and Lamps',
                'description': 'Exterior lighting components.',
                'system': 'Lighting',
                'level': 'Major Component',
                'examples': 'Headlight, tail light, fog light',
                'subcategories': [
                    {'name': 'Headlight', 'description': 'Front lighting for illumination.', 'system': 'Lighting', 'level': 'Component', 'examples': 'Halogen headlight, LED headlight', 'parent': 'Lights and Lamps'},
                    {'name': 'Tail Light', 'description': 'Rear lighting for visibility and braking.', 'system': 'Lighting', 'level': 'Component', 'examples': 'LED tail light, brake light assembly', 'parent': 'Lights and Lamps'},
                    {'name': 'Fog/Driving Light', 'description': 'Auxiliary lights for adverse conditions.', 'system': 'Lighting', 'level': 'Component', 'examples': 'Front fog light, driving lamp', 'parent': 'Lights and Lamps'},
                    {'name': '3rd Brake Light', 'description': 'Center high-mounted stop lamp.', 'system': 'Lighting', 'level': 'Component', 'examples': 'CHMSL, high-mount stop light', 'parent': 'Lights and Lamps'},
                    {'name': 'Trunk Finish Panel', 'description': 'Panel around the trunk opening, often with lights.', 'system': 'Body', 'level': 'Component', 'examples': 'Trunk lid trim panel, rear garnish', 'parent': 'Lights and Lamps'},
                    {'name': 'Rear Lamp/Backup Light', 'description': 'Rear lights for reverse and general illumination.', 'system': 'Lighting', 'level': 'Component', 'examples': 'Reverse light, rear marker light', 'parent': 'Lights and Lamps'},
                    {'name': 'Other Light/Lamp Part', 'description': 'Miscellaneous lighting components.', 'system': 'Lighting', 'level': 'Component', 'examples': 'Light bulb, wiring harness', 'parent': 'Lights and Lamps'},
                ]
            },
            {
                'name': 'Wheels, Tires, & Brakes',
                'description': 'Components for wheels, tires, and braking system.',
                'system': 'Wheels/Brakes',
                'level': 'Major Component',
                'examples': 'Brake caliper, tire, wheel',
                'subcategories': [
                    {'name': 'Anti-Lock Brake Pump', 'description': 'Pump for the anti-lock braking system.', 'system': 'Brakes', 'level': 'Component', 'examples': 'ABS pump, hydraulic control unit', 'parent': 'Wheels, Tires, & Brakes'},
                    {'name': 'Spare Tire/Roadside Kit', 'description': 'Spare tire and emergency roadside tools.', 'system': 'Wheels/Brakes', 'level': 'Component', 'examples': 'Compact spare tire, jack kit', 'parent': 'Wheels, Tires, & Brakes'},
                    {'name': 'Brake Caliper', 'description': 'Houses brake pads and pistons.', 'system': 'Brakes', 'level': 'Component', 'examples': 'Front brake caliper, rear brake caliper', 'parent': 'Wheels, Tires, & Brakes'},
                    {'name': 'Tire', 'description': 'Rubber component providing traction.', 'system': 'Wheels/Brakes', 'level': 'Component', 'examples': 'All-season tire, summer tire', 'parent': 'Wheels, Tires, & Brakes'},
                    {'name': 'Wheel', 'description': 'Rim for mounting the tire.', 'system': 'Wheels/Brakes', 'level': 'Component', 'examples': 'Alloy wheel, steel wheel', 'parent': 'Wheels, Tires, & Brakes'},
                    {'name': 'Hub Cap/Center Cap', 'description': 'Decorative cover for wheel hub.', 'system': 'Wheels/Brakes', 'level': 'Component', 'examples': 'Wheel hub cap, center cap', 'parent': 'Wheels, Tires, & Brakes'},
                    {'name': 'Brake Master Cylinder', 'description': 'Generates hydraulic pressure for brakes.', 'system': 'Brakes', 'level': 'Component', 'examples': 'Master cylinder, brake fluid reservoir', 'parent': 'Wheels, Tires, & Brakes'},
                    {'name': 'Brake Booster', 'description': 'Assists in brake pedal effort.', 'system': 'Brakes', 'level': 'Component', 'examples': 'Vacuum brake booster, hydraulic brake booster', 'parent': 'Wheels, Tires, & Brakes'},
                    {'name': 'Other Wheel/Tire/Brake Part', 'description': 'Miscellaneous wheel, tire, or brake parts.', 'system': 'Wheels/Brakes', 'level': 'Component', 'examples': 'Brake pad, brake rotor', 'parent': 'Wheels, Tires, & Brakes'},
                ]
            },
            {
                'name': 'Misc.',
                'description': 'Miscellaneous parts not fitting into other categories.',
                'system': 'Miscellaneous',
                'level': 'Major Component',
                'examples': 'Key fob, owner’s manual, towing parts',
                'subcategories': [
                    {'name': 'Key Fob', 'description': 'Remote keyless entry device.', 'system': 'Electrical', 'level': 'Component', 'examples': 'Smart key, remote start fob', 'parent': 'Misc.'},
                    {'name': 'Owner’s Manual', 'description': 'Vehicle owner’s handbook.', 'system': 'Documentation', 'level': 'Component', 'examples': 'Service manual, user guide', 'parent': 'Misc.'},
                    {'name': 'Plow Parts', 'description': 'Components for snow plows.', 'system': 'Specialized', 'level': 'Component', 'examples': 'Snow plow blade, plow mount', 'parent': 'Misc.'},
                    {'name': 'Towing Parts', 'description': 'Components for towing.', 'system': 'Specialized', 'level': 'Component', 'examples': 'Trailer hitch, tow ball', 'parent': 'Misc.'},
                    {'name': 'Other Misc. Part', 'description': 'Any other miscellaneous part.', 'system': 'Miscellaneous', 'level': 'Component', 'examples': 'License plate frame, car cover', 'parent': 'Misc.'},
                ]
            },
        ]
        
        # Filter out specialized categories if not requested
        if not include_specialized:
            part_categories = [cat for cat in part_categories if not cat.get('specialized', False)]
            self.stdout.write('Filtering to standard categories only')
        
        self.stdout.write(f'Processing part categories...')
        
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

            self.stdout.write(f'{status} {category_name}')
            self.stdout.write(f'    {description}')
            if parent_category_obj:
                self.stdout.write(f'    Parent: {parent_category_obj.name}')
            self.stdout.write(f'    System: {system} | Level: {level}')
            self.stdout.write(f'    Examples: {examples}')
            if category_data.get('specialized'):
                self.stdout.write(f'    🏁 SPECIALIZED CATEGORY')
            self.stdout.write('')  # Blank line

            if 'subcategories' in category_data and category_obj:
                for sub_category_data in category_data['subcategories']:
                    _create_category(sub_category_data, category_obj)

        for category_data in part_categories:
            _create_category(category_data)
        
        # Summary
        self.stdout.write('=' * 60)
        self.stdout.write('PART CATEGORIES SUMMARY')
        self.stdout.write('=' * 60)
        
        if not dry_run:
            self.stdout.write(f'✓ Created: {created_count} categories')
            self.stdout.write(f'↻ Updated: {updated_count} categories')
            self.stdout.write(f'- Existed: {skipped_count} categories')
            self.stdout.write(f'📊 Total: {created_count + updated_count + skipped_count} categories processed')
        else:
            self.stdout.write(f'📊 Would create: {created_count} categories')
            self.stdout.write(f'📊 Would update: {updated_count} categories')
            self.stdout.write(f'📊 Would skip: {skipped_count} categories')
            self.stdout.write(f'📊 Total: {created_count + updated_count + skipped_count} categories would be processed')
        
        # System breakdown insights (simplified for new structure)
        self.stdout.write('\n🔍 CATEGORY BREAKDOWN BY SYSTEM (Top-level only):')
        
        system_counts = {}
        for category in part_categories:
            system = category.get('system', 'General')
            system_counts[system] = system_counts.get(system, 0) + 1
        
        for system, count in sorted(system_counts.items()):
            self.stdout.write(f'• {system}: {count} top-level categories')
        
        # Level breakdown (simplified for new structure)
        self.stdout.write('\n📊 CATEGORY LEVELS (Top-level only):')
        level_counts = {}
        for category in part_categories:
            level = category.get('level', 'Major Component')
            level_counts[level] = level_counts.get(level, 0) + 1
        
        for level, count in sorted(level_counts.items()):
            self.stdout.write(f'• {level}: {count} top-level categories')
        
        # Usage examples
        self.stdout.write('\n💡 USAGE EXAMPLES:')
        self.stdout.write('Create parts with categories:')
        self.stdout.write('1. python manage.py add_parts --category "Alternator"')
        self.stdout.write('2. python manage.py add_parts --category "Door Panel"') 
        self.stdout.write('3. python manage.py add_parts --category "Brake Caliper"')
        
        self.stdout.write('\nQuery parts by category:')
        self.stdout.write('• All engine parts: /api/parts/?category__name__in=Engine,Complete Engine Assembly,Ignition Coil')
        self.stdout.write('• All brake components: /api/parts/?category__name__startswith=Brake')
        self.stdout.write('• Parts in "Door Components & Glass" and its subcategories: /api/parts/?category__name__in=Door Components & Glass,Door Panel,Window Glass')
        
        # Next steps
        self.stdout.write('\n📋 NEXT STEPS:')
        self.stdout.write('1. Add manufacturers: python manage.py add_manufacturers')
        self.stdout.write('2. Add parts: python manage.py add_parts --category [category_name]')
        self.stdout.write('3. Create fitments: python manage.py create_fitments')
        self.stdout.write('4. Import data: python manage.py import_csv [file.csv]')
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'\n🎉 Successfully processed {created_count + updated_count + skipped_count} part categories!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('\n⚠️  DRY RUN complete - run without --dry-run to save changes')
            )
