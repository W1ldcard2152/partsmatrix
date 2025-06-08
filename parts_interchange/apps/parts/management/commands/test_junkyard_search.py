from django.core.management.base import BaseCommand
from django.db import models
from apps.parts.models import Part, PartGroup, PartGroupMembership
from apps.vehicles.models import Vehicle
from apps.fitments.models import Fitment


class Command(BaseCommand):
    help = 'Test junkyard search functionality using part groups'

    def add_arguments(self, parser):
        parser.add_argument(
            '--vehicle',
            type=str,
            help='Search for parts that fit specific vehicle (format: "year make model")'
        )
        parser.add_argument(
            '--part-type',
            type=str,
            help='Search for specific part type (e.g., "alternator", "starter")'
        )
        parser.add_argument(
            '--part-group',
            type=str,
            help='Search within specific part group'
        )
        parser.add_argument(
            '--show-all',
            action='store_true',
            help='Show all compatible parts, not just best matches'
        )

    def handle(self, *args, **options):
        vehicle_search = options['vehicle']
        part_type = options['part_type']
        part_group_name = options['part_group']
        show_all = options['show_all']
        
        self.stdout.write(self.style.SUCCESS('🔍 JUNKYARD SEARCH SYSTEM TEST'))
        self.stdout.write('=' * 60)
        
        # Scenario 1: Vehicle-based search
        if vehicle_search:
            self.test_vehicle_search(vehicle_search, part_type, show_all)
        
        # Scenario 2: Part group search
        elif part_group_name:
            self.test_part_group_search(part_group_name, show_all)
        
        # Scenario 3: Part type search
        elif part_type:
            self.test_part_type_search(part_type, show_all)
        
        # Default: Run all test scenarios
        else:
            self.run_all_test_scenarios()
    
    def test_vehicle_search(self, vehicle_search, part_type=None, show_all=False):
        """Test: 'I need a [part] for [vehicle]'"""
        self.stdout.write(f'\n🚗 VEHICLE SEARCH: "{vehicle_search}"')
        
        # Parse vehicle search (simple implementation)
        parts = vehicle_search.split()
        if len(parts) >= 3:
            year = parts[0]
            make = parts[1]
            model = ' '.join(parts[2:])
        else:
            self.stdout.write('❌ Please use format: "year make model"')
            return
        
        # Find matching vehicles
        vehicles = Vehicle.objects.filter(
            year=year,
            make__name__icontains=make,
            model__name__icontains=model
        ).select_related('make', 'model', 'trim', 'engine')
        
        if not vehicles.exists():
            self.stdout.write(f'❌ No vehicles found matching "{vehicle_search}"')
            return
        
        self.stdout.write(f'✓ Found {vehicles.count()} matching vehicles:')
        for vehicle in vehicles[:3]:  # Show first 3
            self.stdout.write(f'  • {vehicle}')
        
        # Find parts that fit these vehicles
        if part_type:
            # Specific part type requested
            fitments = Fitment.objects.filter(
                vehicle__in=vehicles,
                part__name__icontains=part_type
            ).select_related('part__manufacturer', 'part__category')
            
            self.stdout.write(f'\n🔧 {part_type.upper()} parts that fit:')
        else:
            # All parts
            fitments = Fitment.objects.filter(
                vehicle__in=vehicles
            ).select_related('part__manufacturer', 'part__category')
            
            self.stdout.write(f'\n🔧 All parts that fit:')
        
        if not fitments.exists():
            self.stdout.write('❌ No direct fitments found')
            return
        
        # Group by part groups for interchange search
        part_groups_found = set()
        direct_parts = []
        
        for fitment in fitments:
            direct_parts.append(fitment.part)
            # Find part groups this part belongs to
            memberships = PartGroupMembership.objects.filter(
                part=fitment.part
            ).select_related('part_group')
            
            for membership in memberships:
                part_groups_found.add(membership.part_group)
        
        self.stdout.write(f'✓ Found {len(direct_parts)} direct-fit parts')
        self.stdout.write(f'✓ Found {len(part_groups_found)} part groups with compatible parts')
        
        # Show part group compatibility
        for part_group in part_groups_found:
            self.show_part_group_details(part_group, show_all)
    
    def test_part_group_search(self, part_group_name, show_all=False):
        """Test: Show all parts in a specific part group"""
        self.stdout.write(f'\n📦 PART GROUP SEARCH: "{part_group_name}"')
        
        try:
            part_group = PartGroup.objects.get(name__icontains=part_group_name)
            self.show_part_group_details(part_group, show_all)
        except PartGroup.DoesNotExist:
            # Try partial match
            part_groups = PartGroup.objects.filter(name__icontains=part_group_name)
            if part_groups.exists():
                self.stdout.write(f'✓ Found {part_groups.count()} matching part groups:')
                for pg in part_groups:
                    self.show_part_group_details(pg, show_all)
            else:
                self.stdout.write(f'❌ No part groups found matching "{part_group_name}"')
    
    def test_part_type_search(self, part_type, show_all=False):
        """Test: Show all part groups for a part type"""
        self.stdout.write(f'\n🔍 PART TYPE SEARCH: "{part_type}"')
        
        # Find part groups that might contain this part type
        part_groups = PartGroup.objects.filter(
            models.Q(name__icontains=part_type) |
            models.Q(description__icontains=part_type) |
            models.Q(category__name__icontains=part_type)
        )
        
        if part_groups.exists():
            self.stdout.write(f'✓ Found {part_groups.count()} relevant part groups:')
            for part_group in part_groups:
                self.show_part_group_details(part_group, show_all)
        else:
            self.stdout.write(f'❌ No part groups found for "{part_type}"')
    
    def show_part_group_details(self, part_group, show_all=False):
        """Display detailed information about a part group"""
        self.stdout.write(f'\n📦 {part_group.name}')
        self.stdout.write(f'   Category: {part_group.category.name}')
        self.stdout.write(f'   Description: {part_group.description}')
        
        # Technical specs
        specs = []
        if part_group.voltage:
            specs.append(f'{part_group.voltage}V')
        if part_group.amperage:
            specs.append(f'{part_group.amperage}A')
        if part_group.wattage:
            specs.append(f'{part_group.wattage}W')
        if specs:
            self.stdout.write(f'   Specifications: {" | ".join(specs)}')
        
        if part_group.mounting_pattern:
            self.stdout.write(f'   Mounting: {part_group.mounting_pattern}')
        if part_group.connector_type:
            self.stdout.write(f'   Connector: {part_group.connector_type}')
        
        # Get parts in this group
        memberships = PartGroupMembership.objects.filter(
            part_group=part_group
        ).select_related('part__manufacturer', 'part__category').annotate(
            fitment_count=models.Count('part__fitments')
        ).order_by('compatibility_level', '-fitment_count')
        
        if not memberships.exists():
            self.stdout.write('   ❌ No parts assigned to this group yet')
            return
        
        self.stdout.write(f'   ✓ {memberships.count()} parts in group:')
        
        # Group by compatibility level
        by_compatibility = {}
        for membership in memberships:
            level = membership.compatibility_level
            if level not in by_compatibility:
                by_compatibility[level] = []
            by_compatibility[level].append(membership)
        
        # Show each compatibility level
        for level in ['IDENTICAL', 'COMPATIBLE', 'CONDITIONAL']:
            if level in by_compatibility:
                parts_list = by_compatibility[level]
                self.stdout.write(f'\n   🔧 {level} COMPATIBILITY ({len(parts_list)} parts):')
                
                # Show limited or all parts based on show_all flag
                display_count = len(parts_list) if show_all else min(5, len(parts_list))
                
                for i, membership in enumerate(parts_list[:display_count]):
                    part = membership.part
                    fitments = membership.fitment_count
                    
                    # Format part info
                    part_info = f'{part.manufacturer.abbreviation}-{part.part_number}'
                    vehicle_info = f'({fitments} vehicles)' if fitments > 0 else '(no fitments)'
                    
                    self.stdout.write(f'     • {part_info}: {part.name} {vehicle_info}')
                    
                    if membership.installation_notes:
                        self.stdout.write(f'       Note: {membership.installation_notes}')
                    
                    if membership.year_restriction:
                        self.stdout.write(f'       Years: {membership.year_restriction}')
                    
                    if membership.application_restriction:
                        self.stdout.write(f'       Restriction: {membership.application_restriction}')
                
                if not show_all and len(parts_list) > 5:
                    self.stdout.write(f'     ... and {len(parts_list) - 5} more (use --show-all)')
    
    def run_all_test_scenarios(self):
        """Run comprehensive test scenarios"""
        self.stdout.write('\n🧪 RUNNING ALL TEST SCENARIOS')
        
        # Scenario 1: Junkyard customer needs alternator
        self.stdout.write('\n' + '='*60)
        self.stdout.write('📋 SCENARIO 1: Customer needs alternator for 2010 Chevy Silverado')
        self.test_vehicle_search('2010 Chevrolet Silverado', 'alternator')
        
        # Scenario 2: Show all alternators available
        self.stdout.write('\n' + '='*60)
        self.stdout.write('📋 SCENARIO 2: Show all alternator part groups')
        self.test_part_type_search('alternator')
        
        # Scenario 3: LS engine compatibility
        self.stdout.write('\n' + '='*60)
        self.stdout.write('📋 SCENARIO 3: LS engine interchange possibilities')
        self.test_part_group_search('LS Engine Family')
        
        # Scenario 4: Brake caliper search
        self.stdout.write('\n' + '='*60)
        self.stdout.write('📋 SCENARIO 4: Find brake calipers for any vehicle')
        self.test_part_type_search('brake caliper')
        
        # Scenario 5: Show database statistics
        self.stdout.write('\n' + '='*60)
        self.stdout.write('📋 SCENARIO 5: Database Statistics')
        self.show_database_stats()
        
        # Summary and recommendations
        self.stdout.write('\n' + '='*60)
        self.stdout.write('📊 TEST SUMMARY & RECOMMENDATIONS')
        self.stdout.write('='*60)
        
        self.stdout.write('\n✅ WHAT WORKS:')
        self.stdout.write('• Part groups enable "what else fits" functionality')
        self.stdout.write('• Compatibility levels help users make informed decisions')
        self.stdout.write('• Technical specifications ensure proper fitment')
        self.stdout.write('• Installation notes prevent compatibility issues')
        
        self.stdout.write('\n🚧 AREAS FOR IMPROVEMENT:')
        self.stdout.write('• Need more parts assigned to groups')
        self.stdout.write('• Vehicle fitment data could be expanded')
        self.stdout.write('• Verification process for compatibility claims')
        self.stdout.write('• User interface for junkyard workers')
        
        self.stdout.write('\n🎯 NEXT STEPS:')
        self.stdout.write('1. Add more real parts data')
        self.stdout.write('2. Verify part group assignments')
        self.stdout.write('3. Create web interface for searches')
        self.stdout.write('4. Add pricing and availability data')
        
    def show_database_stats(self):
        """Show current database statistics"""
        from apps.parts.models import Manufacturer
        from apps.vehicles.models import Make
        
        # Parts statistics
        total_parts = Part.objects.count()
        active_parts = Part.objects.filter(is_active=True).count()
        parts_in_groups = PartGroupMembership.objects.values('part').distinct().count()
        
        # Part groups statistics
        total_groups = PartGroup.objects.count()
        active_groups = PartGroup.objects.filter(is_active=True).count()
        
        # Vehicle statistics
        total_vehicles = Vehicle.objects.count()
        total_makes = Make.objects.count()
        
        # Fitment statistics
        total_fitments = Fitment.objects.count()
        verified_fitments = Fitment.objects.filter(is_verified=True).count()
        
        self.stdout.write('\n📊 CURRENT DATABASE STATUS:')
        self.stdout.write(f'   Parts: {active_parts:,} active / {total_parts:,} total')
        self.stdout.write(f'   Parts in Groups: {parts_in_groups:,} ({parts_in_groups/max(active_parts,1)*100:.1f}%)')
        self.stdout.write(f'   Part Groups: {active_groups:,} active / {total_groups:,} total')
        self.stdout.write(f'   Vehicles: {total_vehicles:,} total across {total_makes:,} makes')
        self.stdout.write(f'   Fitments: {verified_fitments:,} verified / {total_fitments:,} total')
        
        # Show top part groups by size
        top_groups = PartGroup.objects.annotate(
            part_count=models.Count('memberships')
        ).order_by('-part_count')[:5]
        
        if top_groups.exists():
            self.stdout.write('\n🏆 TOP PART GROUPS BY SIZE:')
            for i, group in enumerate(top_groups, 1):
                self.stdout.write(f'   {i}. {group.name}: {group.part_count} parts')
        
        # Show categories with most part groups
        from apps.parts.models import PartCategory
        top_categories = PartCategory.objects.annotate(
            group_count=models.Count('part_groups')
        ).order_by('-group_count')[:5]
        
        if top_categories.exists():
            self.stdout.write('\n📂 CATEGORIES WITH MOST PART GROUPS:')
            for i, category in enumerate(top_categories, 1):
                if category.group_count > 0:
                    self.stdout.write(f'   {i}. {category.name}: {category.group_count} groups')
        
        # Compatibility level distribution
        compatibility_stats = PartGroupMembership.objects.values('compatibility_level').annotate(
            count=models.Count('id')
        ).order_by('-count')
        
        if compatibility_stats.exists():
            self.stdout.write('\n🔧 COMPATIBILITY LEVEL DISTRIBUTION:')
            for stat in compatibility_stats:
                level = stat['compatibility_level']
                count = stat['count']
                self.stdout.write(f'   {level}: {count:,} assignments')
