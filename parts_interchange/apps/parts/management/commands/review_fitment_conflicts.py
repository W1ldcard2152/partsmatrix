from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from django.db.models import Count, Q
from apps.parts.models import ConflictingFitment, RawListingData, ConsensusFitment
import csv
import os
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Review and manage fitment conflicts needing manual attention'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--status',
            choices=['PENDING', 'RESOLVED', 'DISMISSED'],
            default='PENDING',
            help='Filter conflicts by resolution status'
        )
        parser.add_argument(
            '--generate-report',
            action='store_true',
            help='Generate CSV report of conflicts'
        )
        parser.add_argument(
            '--auto-resolve',
            action='store_true',
            help='Attempt automatic resolution of simple conflicts'
        )
        parser.add_argument(
            '--part-number',
            help='Review conflicts for specific part number'
        )
        parser.add_argument(
            '--age-days',
            type=int,
            help='Filter conflicts older than N days'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Limit number of conflicts to review (default: 50)'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output'
        )
    
    def handle(self, *args, **options):
        if options['verbose']:
            logging.basicConfig(level=logging.INFO)
        
        try:
            if options['generate_report']:
                self.generate_conflict_report(options)
            elif options['auto_resolve']:
                self.auto_resolve_conflicts(options)
            else:
                self.review_conflicts(options)
                
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('\nConflict review interrupted by user')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during conflict review: {e}')
            )
            raise CommandError(f'Conflict review failed: {e}')
    
    def review_conflicts(self, options):
        """Review conflicts based on filters"""
        conflicts = self.get_filtered_conflicts(options)
        
        if not conflicts.exists():
            self.stdout.write(
                self.style.WARNING('No conflicts found matching the criteria')
            )
            return
        
        total_conflicts = conflicts.count()
        self.stdout.write(f'Found {total_conflicts} conflicts to review')
        
        # Show summary statistics
        self.show_conflict_summary(conflicts)
        
        # Review each conflict
        for i, conflict in enumerate(conflicts[:options['limit']], 1):
            self.stdout.write(f'\n--- Conflict {i}/{min(options["limit"], total_conflicts)} ---')
            self.display_conflict_details(conflict)
            
            if options['verbose']:
                self.display_conflicting_listings(conflict)
    
    def get_filtered_conflicts(self, options):
        """Get conflicts based on filter criteria"""
        conflicts = ConflictingFitment.objects.filter(
            resolution_status=options['status']
        )
        
        if options['part_number']:
            conflicts = conflicts.filter(part_number=options['part_number'])
        
        if options['age_days']:
            cutoff_date = timezone.now() - timedelta(days=options['age_days'])
            conflicts = conflicts.filter(created_date__lte=cutoff_date)
        
        return conflicts.order_by('-created_date')
    
    def show_conflict_summary(self, conflicts):
        """Show summary statistics for conflicts"""
        # Count by part number
        part_conflicts = (
            conflicts.values('part_number')
            .annotate(conflict_count=Count('id'))
            .order_by('-conflict_count')[:10]
        )
        
        self.stdout.write('\nTop 10 parts with most conflicts:')
        for part_data in part_conflicts:
            self.stdout.write(
                f'  {part_data["part_number"]}: {part_data["conflict_count"]} conflicts'
            )
        
        # Count by conflict type
        conflict_types = {}
        for conflict in conflicts:
            description = conflict.conflict_description
            if 'year range' in description.lower():
                conflict_types['Year Range'] = conflict_types.get('Year Range', 0) + 1
            elif 'cross-manufacturer' in description.lower():
                conflict_types['Cross-Manufacturer'] = conflict_types.get('Cross-Manufacturer', 0) + 1
            elif 'multiple models' in description.lower():
                conflict_types['Multiple Models'] = conflict_types.get('Multiple Models', 0) + 1
            else:
                conflict_types['Other'] = conflict_types.get('Other', 0) + 1
        
        self.stdout.write('\nConflict types:')
        for conflict_type, count in conflict_types.items():
            self.stdout.write(f'  {conflict_type}: {count}')
    
    def display_conflict_details(self, conflict):
        """Display detailed information about a conflict"""
        self.stdout.write(f'Part Number: {conflict.part_number}')
        self.stdout.write(f'Conflict: {conflict.conflict_description}')
        self.stdout.write(f'Created: {conflict.created_date.strftime("%Y-%m-%d %H:%M")}')
        self.stdout.write(f'Status: {conflict.resolution_status}')
        self.stdout.write(f'Conflicting Listings: {conflict.conflicting_listings.count()}')
        
        if conflict.resolution_notes:
            self.stdout.write(f'Notes: {conflict.resolution_notes}')
    
    def display_conflicting_listings(self, conflict):
        """Display details of conflicting listings"""
        listings = conflict.conflicting_listings.all()
        
        self.stdout.write('\nConflicting Listings:')
        for listing in listings:
            weight = listing.calculate_quality_weight()
            self.stdout.write(
                f'  {listing.vehicle_year} {listing.vehicle_make} {listing.vehicle_model} '
                f'(Weight: {weight:.2f}, Seller: {"Business" if listing.seller_is_business else "Individual"})'
            )
    
    def auto_resolve_conflicts(self, options):
        """Attempt automatic resolution of simple conflicts"""
        conflicts = self.get_filtered_conflicts(options)
        
        resolved_count = 0
        dismissed_count = 0
        
        self.stdout.write('Attempting automatic conflict resolution...')
        
        for conflict in conflicts:
            resolution = self.analyze_conflict_for_auto_resolution(conflict)
            
            if resolution['action'] == 'resolve':
                with transaction.atomic():
                    conflict.resolution_status = 'RESOLVED'
                    conflict.resolved_date = timezone.now()
                    conflict.resolved_by = 'auto-resolver'
                    conflict.resolution_notes = resolution['notes']
                    conflict.save()
                    resolved_count += 1
                    
                    if options['verbose']:
                        self.stdout.write(f'  RESOLVED: {conflict.part_number} - {resolution["notes"]}')
            
            elif resolution['action'] == 'dismiss':
                with transaction.atomic():
                    conflict.resolution_status = 'DISMISSED'
                    conflict.resolved_date = timezone.now()
                    conflict.resolved_by = 'auto-resolver'
                    conflict.resolution_notes = resolution['notes']
                    conflict.save()
                    dismissed_count += 1
                    
                    if options['verbose']:
                        self.stdout.write(f'  DISMISSED: {conflict.part_number} - {resolution["notes"]}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Auto-resolution complete: {resolved_count} resolved, {dismissed_count} dismissed'
            )
        )
    
    def analyze_conflict_for_auto_resolution(self, conflict):
        """Analyze conflict to determine if it can be auto-resolved"""
        listings = conflict.conflicting_listings.all()
        
        # Check for false positive year conflicts (consecutive years)
        if 'year range' in conflict.conflict_description.lower():
            years = sorted([listing.vehicle_year for listing in listings])
            if len(years) == 2 and abs(years[1] - years[0]) <= 1:
                return {
                    'action': 'dismiss',
                    'notes': f'Consecutive years {years[0]}-{years[1]} are likely same generation'
                }
        
        # Check for trim variations (same base model)
        if len(set(listing.vehicle_make for listing in listings)) == 1:
            models = set(listing.vehicle_model for listing in listings)
            if len(models) == 1:
                trims = [listing.vehicle_trim for listing in listings if listing.vehicle_trim]
                if len(trims) > 1:
                    return {
                        'action': 'resolve',
                        'notes': f'Trim variations for same model: {", ".join(trims)}'
                    }
        
        # Check for single outlier with low weight
        if len(listings) >= 3:
            weights = [listing.calculate_quality_weight() for listing in listings]
            min_weight = min(weights)
            avg_weight = sum(weights) / len(weights)
            
            if min_weight < avg_weight * 0.5:  # Outlier is less than half average weight
                return {
                    'action': 'resolve',
                    'notes': f'Low quality outlier detected (weight: {min_weight:.2f} vs avg: {avg_weight:.2f})'
                }
        
        return {'action': 'manual', 'notes': 'Requires manual review'}
    
    def generate_conflict_report(self, options):
        """Generate CSV report of conflicts"""
        conflicts = self.get_filtered_conflicts(options)
        
        if not conflicts.exists():
            self.stdout.write(
                self.style.WARNING('No conflicts found to report')
            )
            return
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'conflict_report_{options["status"].lower()}_{timestamp}.csv'
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'part_number', 'conflict_description', 'created_date',
                'resolution_status', 'conflicting_listings_count',
                'listing_details', 'age_days'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for conflict in conflicts:
                # Get listing details
                listings = conflict.conflicting_listings.all()
                listing_details = '; '.join([
                    f'{l.vehicle_year} {l.vehicle_make} {l.vehicle_model} '
                    f'(Weight: {l.calculate_quality_weight():.2f})'
                    for l in listings
                ])
                
                # Calculate age
                age_days = (timezone.now() - conflict.created_date).days
                
                writer.writerow({
                    'part_number': conflict.part_number,
                    'conflict_description': conflict.conflict_description,
                    'created_date': conflict.created_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'resolution_status': conflict.resolution_status,
                    'conflicting_listings_count': conflict.conflicting_listings.count(),
                    'listing_details': listing_details,
                    'age_days': age_days
                })
        
        self.stdout.write(
            self.style.SUCCESS(f'Conflict report generated: {filename}')
        )
        
        # Show summary
        total_conflicts = conflicts.count()
        avg_age = sum((timezone.now() - c.created_date).days for c in conflicts) / total_conflicts if total_conflicts > 0 else 0
        
        self.stdout.write(f'\nReport Summary:')
        self.stdout.write(f'  Total conflicts: {total_conflicts}')
        self.stdout.write(f'  Average age: {avg_age:.1f} days')
        self.stdout.write(f'  Status: {options["status"]}')
