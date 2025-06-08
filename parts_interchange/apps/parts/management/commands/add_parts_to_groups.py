from django.core.management.base import BaseCommand
from django.db import transaction, models
from apps.parts.models import Part, PartGroup, PartGroupMembership


class Command(BaseCommand):
    help = 'Add existing parts to appropriate part groups based on matching criteria'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without making changes'
        )
        parser.add_argument(
            '--part-group',
            type=str,
            help='Add parts to specific part group only'
        )
        parser.add_argument(
            '--auto-assign',
            action='store_true',
            help='Automatically assign parts based on name/category matching'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        part_group_filter = options['part_group']
        auto_assign = options['auto_assign']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No data will be saved'))
        
        # Manual part assignments based on existing parts data
        part_assignments = [
            # Alternator assignments
            {
                'part_group': '12V 100-150A Alternators',
                'parts_criteria': {
                    'category_names': ['Alternator', 'Engine/Engine Bay Accessories'],
                    'name_contains': ['alternator'],
                    'exclude_names': ['high output', '200a', '200 amp', 'heavy duty']
                },
                'compatibility_level': 'COMPATIBLE',
                'installation_notes': 'Verify amperage rating and connector type before installation'
            },
            {
                'part_group': '12V 150-200A High Output Alternators',
                'parts_criteria': {
                    'category_names': ['Alternator', 'Engine/Engine Bay Accessories'],
                    'name_contains': ['alternator'],
                    'include_names': ['high output', '150a', '160a', '180a', '200a', 'heavy duty']
                },
                'compatibility_level': 'COMPATIBLE',
                'installation_notes': 'High output alternator - verify electrical system capacity'
            },
            
            # Starter assignments
            {
                'part_group': 'Standard 12V Starters - Gear Reduction',
                'parts_criteria': {
                    'category_names': ['Starter Motor', 'Engine/Engine Bay Accessories'],
                    'name_contains': ['starter'],
                    'exclude_names': ['direct drive', 'heavy duty']
                },
                'compatibility_level': 'COMPATIBLE',
                'installation_notes': 'Modern gear reduction starter - verify starter bolt pattern'
            },
            {
                'part_group': 'Standard 12V Starters - Direct Drive',
                'parts_criteria': {
                    'category_names': ['Starter Motor', 'Engine/Engine Bay Accessories'],
                    'name_contains': ['starter'],
                    'include_names': ['direct drive', 'heavy duty']
                },
                'compatibility_level': 'COMPATIBLE',
                'installation_notes': 'Traditional direct drive starter - heavier but robust'
            },
            
            # Engine assignments
            {
                'part_group': 'LS Engine Family - Long Blocks',
                'parts_criteria': {
                    'category_names': ['Engine', 'Complete Engine Assembly'],
                    'name_contains': ['ls1', 'ls2', 'ls3', 'ls6', 'lsa', 'ls9', 'lt1', 'lt4'],
                    'exclude_names': ['head', 'manifold', 'pan']
                },
                'compatibility_level': 'IDENTICAL',
                'installation_notes': 'LS family engines share many components and mounting patterns'
            },
            {
                'part_group': 'Small Block Chevy (SBC) - Traditional',
                'parts_criteria': {
                    'category_names': ['Engine', 'Complete Engine Assembly'],
                    'name_contains': ['350', '305', '327', '283', 'small block'],
                    'exclude_names': ['ls', 'lt', 'head', 'manifold']
                },
                'compatibility_level': 'COMPATIBLE',
                'installation_notes': 'Traditional SBC - verify year and specific variant'
            },
            {
                'part_group': 'Ford Modular V8 Engines',
                'parts_criteria': {
                    'category_names': ['Engine', 'Complete Engine Assembly'],
                    'name_contains': ['4.6', '5.0', '5.4', '5.8', 'modular', 'coyote'],
                    'exclude_names': ['head', 'manifold', 'pan']
                },
                'compatibility_level': 'COMPATIBLE',
                'installation_notes': 'Ford modular family - verify 2V/3V/4V variant'
            },
            
            # Transmission assignments
            {
                'part_group': '4L60E/4L65E/4L70E Automatic Transmissions',
                'parts_criteria': {
                    'category_names': ['Transmission', 'Automatic'],
                    'name_contains': ['4l60e', '4l65e', '4l70e']
                },
                'compatibility_level': 'IDENTICAL',
                'installation_notes': '4L60E family - verify year and torque capacity'
            },
            {
                'part_group': 'T56/TR6060 Manual Transmissions',
                'parts_criteria': {
                    'category_names': ['Transmission', 'Manual'],
                    'name_contains': ['t56', 'tr6060']
                },
                'compatibility_level': 'COMPATIBLE',
                'installation_notes': 'T56 family - verify bellhousing pattern and shifter location'
            },
            
            # Brake assignments
            {
                'part_group': 'Standard Single Piston Brake Calipers',
                'parts_criteria': {
                    'category_names': ['Brake Caliper', 'Wheels, Tires, & Brakes'],
                    'name_contains': ['caliper'],
                    'exclude_names': ['brembo', 'multi', 'performance', '4 piston', '6 piston']
                },
                'compatibility_level': 'COMPATIBLE',
                'installation_notes': 'Standard caliper - verify rotor diameter and mounting pattern'
            },
            {
                'part_group': 'Multi-Piston Performance Brake Calipers',
                'parts_criteria': {
                    'category_names': ['Brake Caliper', 'Wheels, Tires, & Brakes'],
                    'name_contains': ['caliper'],
                    'include_names': ['brembo', 'multi', 'performance', '4 piston', '6 piston']
                },
                'compatibility_level': 'CONDITIONAL',
                'installation_notes': 'Performance caliper - may require rotor and brake line modifications'
            },
            
            # Suspension assignments
            {
                'part_group': 'MacPherson Strut Assemblies - Compact Cars',
                'parts_criteria': {
                    'category_names': ['Struts', 'Steering & Suspension'],
                    'name_contains': ['strut'],
                    'exclude_names': ['rear', 'shock']
                },
                'compatibility_level': 'COMPATIBLE',
                'installation_notes': 'MacPherson strut - verify spring rate and mounting points'
            },
            {
                'part_group': 'Coil-Over Shock Assemblies - Trucks/SUVs',
                'parts_criteria': {
                    'category_names': ['Shocks', 'Steering & Suspension'],
                    'name_contains': ['shock', 'coil over'],
                    'exclude_names': ['strut']
                },
                'compatibility_level': 'COMPATIBLE',
                'installation_notes': 'Coil-over shock - verify spring rate and travel'
            }
        ]
        
        # Filter assignments if specific part group requested
        if part_group_filter:
            part_assignments = [pa for pa in part_assignments if part_group_filter.lower() in pa['part_group'].lower()]
            self.stdout.write(f'Filtering to assignments for "{part_group_filter}"')
        
        self.stdout.write(f'Processing {len(part_assignments)} part assignment rules...')
        
        total_assigned = 0
        total_skipped = 0
        
        for assignment in part_assignments:
            part_group_name = assignment['part_group']
            criteria = assignment['parts_criteria']
            compatibility = assignment['compatibility_level']
            notes = assignment['installation_notes']
            
            try:
                if not dry_run:
                    # Get the part group
                    try:
                        part_group = PartGroup.objects.get(name=part_group_name)
                    except PartGroup.DoesNotExist:
                        self.stdout.write(f'  Warning: Part group "{part_group_name}" not found')
                        total_skipped += 1
                        continue
                else:
                    self.stdout.write(f'📦 Part Group: {part_group_name}')
                
                # Build query for matching parts
                parts_query = Part.objects.filter(is_active=True)
                
                # Filter by categories
                if 'category_names' in criteria:
                    parts_query = parts_query.filter(category__name__in=criteria['category_names'])
                
                # Filter by name contains
                if 'name_contains' in criteria:
                    for term in criteria['name_contains']:
                        parts_query = parts_query.filter(name__icontains=term)
                
                # Include specific names
                if 'include_names' in criteria:
                    include_filter = None
                    for term in criteria['include_names']:
                        if include_filter is None:
                            include_filter = models.Q(name__icontains=term)
                        else:
                            include_filter |= models.Q(name__icontains=term)
                    if include_filter:
                        parts_query = parts_query.filter(include_filter)
                
                # Exclude specific names
                if 'exclude_names' in criteria:
                    for term in criteria['exclude_names']:
                        parts_query = parts_query.exclude(name__icontains=term)
                
                # Get matching parts
                matching_parts = parts_query.select_related('manufacturer', 'category')
                part_count = matching_parts.count()
                
                self.stdout.write(f'  Found {part_count} matching parts')
                
                if part_count > 0:
                    assigned_count = 0
                    
                    for part in matching_parts:
                        if not dry_run:
                            # Check if already assigned to this group
                            existing = PartGroupMembership.objects.filter(
                                part=part, part_group=part_group
                            ).exists()
                            
                            if not existing:
                                PartGroupMembership.objects.create(
                                    part=part,
                                    part_group=part_group,
                                    compatibility_level=compatibility,
                                    installation_notes=notes,
                                    is_verified=False,
                                    created_by='auto-assignment'
                                )
                                assigned_count += 1
                        else:
                            assigned_count += 1
                            # Show first few examples
                            if assigned_count <= 3:
                                self.stdout.write(f'    → {part.manufacturer.abbreviation}-{part.part_number}: {part.name}')
                    
                    self.stdout.write(f'  ✓ Assigned {assigned_count} parts to {part_group_name}')
                    self.stdout.write(f'    Compatibility: {compatibility}')
                    self.stdout.write(f'    Notes: {notes}')
                    total_assigned += assigned_count
                else:
                    self.stdout.write(f'  - No matching parts found')
                    total_skipped += 1
                
                self.stdout.write('')  # Blank line
                
            except Exception as e:
                self.stdout.write(f'  Error processing {part_group_name}: {e}')
                total_skipped += 1
        
        # Auto-assignment based on simple pattern matching
        if auto_assign:
            self.stdout.write('\n🤖 AUTO-ASSIGNMENT MODE')
            self.stdout.write('Attempting to assign remaining parts...')
            
            # Simple auto-assignment rules
            auto_rules = [
                {'pattern': 'alternator', 'group': '12V 100-150A Alternators'},
                {'pattern': 'starter', 'group': 'Standard 12V Starters - Gear Reduction'},
                {'pattern': 'caliper', 'group': 'Standard Single Piston Brake Calipers'},
                {'pattern': 'strut', 'group': 'MacPherson Strut Assemblies - Compact Cars'},
            ]
            
            for rule in auto_rules:
                if not dry_run:
                    try:
                        part_group = PartGroup.objects.get(name=rule['group'])
                        unassigned_parts = Part.objects.filter(
                            name__icontains=rule['pattern'],
                            is_active=True,
                            part_group_memberships__isnull=True
                        )
                        
                        auto_assigned = 0
                        for part in unassigned_parts[:10]:  # Limit to 10 per rule
                            PartGroupMembership.objects.create(
                                part=part,
                                part_group=part_group,
                                compatibility_level='COMPATIBLE',
                                installation_notes='Auto-assigned based on name pattern',
                                is_verified=False,
                                created_by='auto-assignment'
                            )
                            auto_assigned += 1
                        
                        if auto_assigned > 0:
                            self.stdout.write(f'  ✓ Auto-assigned {auto_assigned} "{rule["pattern"]}" parts')
                            total_assigned += auto_assigned
                    
                    except PartGroup.DoesNotExist:
                        continue
        
        # Summary
        self.stdout.write('=' * 60)
        self.stdout.write('PART ASSIGNMENT SUMMARY')
        self.stdout.write('=' * 60)
        
        if not dry_run:
            self.stdout.write(f'✓ Assigned: {total_assigned} parts to groups')
            self.stdout.write(f'- Skipped: {total_skipped} assignments')
        else:
            self.stdout.write(f'📊 Would assign: {total_assigned} parts to groups')
        
        # Next steps
        self.stdout.write('\n📋 NEXT STEPS:')
        self.stdout.write('1. Review assignments: /admin/parts/partgroupmembership/')
        self.stdout.write('2. Verify compatibility: python manage.py verify_part_groups')
        self.stdout.write('3. Test junkyard search: python manage.py test_junkyard_search')
        
        # Usage examples
        self.stdout.write('\n💡 JUNKYARD SEARCH EXAMPLES:')
        self.stdout.write('"Need alternator for 2010 Chevy Silverado"')
        self.stdout.write('→ Shows all alternators in "12V 100-150A Alternators" group')
        self.stdout.write('→ Lists compatibility level and installation notes')
        self.stdout.write('→ Includes parts from Ford, Toyota, Honda, etc. that fit')
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'\n🎉 Successfully assigned {total_assigned} parts to groups!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('\n⚠️  DRY RUN complete - run without --dry-run to save changes')
            )
