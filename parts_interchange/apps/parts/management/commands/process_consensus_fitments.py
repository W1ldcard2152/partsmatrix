from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from apps.parts.models import RawListingData, ConsensusFitment, ConflictingFitment
from apps.parts.consensus.processor import FitmentConsensusProcessor
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Process raw listing data into consensus fitments'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--part-number', 
            help='Process specific part number'
        )
        parser.add_argument(
            '--all', 
            action='store_true', 
            help='Process all parts with new data'
        )
        parser.add_argument(
            '--new-data-only',
            action='store_true',
            help='Process only parts with new raw data since last update'
        )
        parser.add_argument(
            '--min-listings', 
            type=int, 
            default=2, 
            help='Minimum listings required (default: 2)'
        )
        parser.add_argument(
            '--dry-run', 
            action='store_true', 
            help='Show what would be processed without making changes'
        )
        parser.add_argument(
            '--verbose', 
            action='store_true', 
            help='Enable verbose output'
        )
        parser.add_argument(
            '--stats-only', 
            action='store_true', 
            help='Only show current processing statistics'
        )
    
    def handle(self, *args, **options):
        if options['verbose']:
            logging.basicConfig(level=logging.INFO)
        
        processor = FitmentConsensusProcessor()
        
        # Show stats only
        if options['stats_only']:
            self.show_stats(processor)
            return
        
        # Dry run information
        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )
        
        try:
            if options['part_number']:
                self.process_single_part(processor, options['part_number'], options)
            elif options['all']:
                self.process_all_parts(processor, options)
            elif options['new_data_only']:
                self.process_new_data_only(processor, options)
            else:
                self.stdout.write(
                    self.style.ERROR('Must specify --part-number, --all, or --new-data-only')
                )
                return
                
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('\\nProcessing interrupted by user')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during processing: {e}')
            )
            raise CommandError(f'Processing failed: {e}')
    
    def process_single_part(self, processor, part_number, options):
        """Process a single part number"""
        self.stdout.write(f'Processing part number: {part_number}')
        
        # Check if part number exists
        raw_count = RawListingData.objects.filter(part_number=part_number).count()
        if raw_count == 0:
            self.stdout.write(
                self.style.WARNING(f'No raw listings found for part number: {part_number}')
            )
            return
        
        self.stdout.write(f'Found {raw_count} raw listings for {part_number}')
        
        if options['dry_run']:
            self.show_dry_run_info(part_number, raw_count, options['min_listings'])
            return
        
        # Process the part
        result = processor.process_part_number(part_number)
        
        # Show results
        self.stdout.write(
            self.style.SUCCESS(
                f'Processed {result["processed"]} consensus fitments, '
                f'identified {result["conflicts"]} conflicts'
            )
        )
        
        if result.get('reason') == 'insufficient_data':
            self.stdout.write(
                self.style.WARNING(
                    f'Skipped due to insufficient data: {raw_count} < {options["min_listings"]}'
                )
            )
    
    def process_all_parts(self, processor, options):
        """Process all parts with sufficient data"""
        min_listings = options['min_listings']
        
        # Get candidate part numbers
        from django.db import models
        candidate_parts = (
            RawListingData.objects
            .values('part_number')
            .annotate(listing_count=models.Count('id'))
            .filter(listing_count__gte=min_listings)
        )
        
        total_candidates = len(candidate_parts)
        self.stdout.write(f'Found {total_candidates} part numbers with >= {min_listings} listings')
        
        if total_candidates == 0:
            self.stdout.write(
                self.style.WARNING('No part numbers meet the minimum listing requirement')
            )
            return
        
        if options['dry_run']:
            self.show_batch_dry_run_info(candidate_parts, min_listings)
            return
        
        # Process all candidates
        self.stdout.write('Starting batch processing...')
        
        result = processor.process_all_new_data(min_listings)
        
        # Show summary
        self.stdout.write(
            self.style.SUCCESS(
                f'Batch processing complete:\n'
                f'  Parts processed: {result["total_parts_processed"]}\n'
                f'  Fitments created/updated: {result["total_fitments_processed"]}\n'
                f'  Conflicts identified: {result["total_conflicts_identified"]}'
            )
        )
        
        # Show updated stats
        self.show_stats(processor)
    
    def process_new_data_only(self, processor, options):
        """Process only parts with new raw data since last consensus update"""
        min_listings = options['min_listings']
        
        # Find parts with raw data newer than their last consensus update
        from django.db import models
        from django.db.models import Max, Count
        
        # Get parts with recent raw data
        recent_raw_parts = (
            RawListingData.objects
            .values('part_number')
            .annotate(
                listing_count=Count('id'),
                latest_raw=Max('extraction_date')
            )
            .filter(listing_count__gte=min_listings)
        )
        
        # Find which parts need updating
        candidates = []
        for part_data in recent_raw_parts:
            part_number = part_data['part_number']
            latest_raw = part_data['latest_raw']
            
            # Check if consensus data exists and when it was last updated
            latest_consensus = (
                ConsensusFitment.objects
                .filter(part_number=part_number)
                .aggregate(latest_update=Max('last_updated'))
            )['latest_update']
            
            # Include if no consensus exists or raw data is newer
            if not latest_consensus or latest_raw > latest_consensus:
                candidates.append(part_number)
        
        total_candidates = len(candidates)
        self.stdout.write(f'Found {total_candidates} part numbers with new data to process')
        
        if total_candidates == 0:
            self.stdout.write(
                self.style.WARNING('No parts found with new data requiring processing')
            )
            return
        
        if options['dry_run']:
            self.stdout.write('\nParts that would be processed:')
            for part_number in candidates[:10]:  # Show first 10
                self.stdout.write(f'  {part_number}')
            if total_candidates > 10:
                self.stdout.write(f'  ... and {total_candidates - 10} more')
            return
        
        # Process candidates
        self.stdout.write('Starting new data processing...')
        
        processed = 0
        total_conflicts = 0
        
        for part_number in candidates:
            try:
                result = processor.process_part_number(part_number)
                processed += result.get('processed', 0)
                total_conflicts += result.get('conflicts', 0)
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing {part_number}: {e}')
                )
        
        # Show summary
        self.stdout.write(
            self.style.SUCCESS(
                f'New data processing complete:\n'
                f'  Parts with new data: {total_candidates}\n'
                f'  Fitments processed: {processed}\n'
                f'  Conflicts identified: {total_conflicts}'
            )
        )
        
        # Show updated stats
        self.show_stats(processor)
    
    def show_dry_run_info(self, part_number, raw_count, min_listings):
        """Show what would happen for a single part in dry run mode"""
        from collections import defaultdict
        
        raw_listings = RawListingData.objects.filter(part_number=part_number)
        
        # Group by fitment signature
        fitment_groups = defaultdict(list)
        for listing in raw_listings:
            signature = listing.get_fitment_signature()
            fitment_groups[signature].append(listing)
        
        self.stdout.write(f'\nDry run analysis for {part_number}:')
        self.stdout.write(f'  Raw listings: {raw_count}')
        self.stdout.write(f'  Unique fitment signatures: {len(fitment_groups)}')
        
        if raw_count < min_listings:
            self.stdout.write(
                self.style.WARNING(f'  Would be SKIPPED (< {min_listings} minimum)')
            )
            return
        
        for signature, listings in fitment_groups.items():
            year, make, model, trim, engine = signature.split('|')
            listing_count = len(listings)
            total_weight = sum(listing.calculate_quality_weight() for listing in listings)
            
            self.stdout.write(f'  Group: {year} {make} {model}')
            self.stdout.write(f'    Listings: {listing_count}')
            self.stdout.write(f'    Total weight: {total_weight:.2f}')
    
    def show_batch_dry_run_info(self, candidate_parts, min_listings):
        """Show batch processing dry run information"""
        self.stdout.write(f'\nBatch dry run analysis:')
        self.stdout.write(f'  Minimum listings required: {min_listings}')
        self.stdout.write(f'  Candidate part numbers: {len(candidate_parts)}')
        
        # Show distribution
        distribution = {}
        for part_data in candidate_parts:
            count = part_data['listing_count']
            range_key = f'{(count // 5) * 5}-{(count // 5) * 5 + 4}'
            distribution[range_key] = distribution.get(range_key, 0) + 1
        
        self.stdout.write('  Listing count distribution:')
        for range_key, part_count in sorted(distribution.items()):
            self.stdout.write(f'    {range_key} listings: {part_count} parts')
    
    def show_stats(self, processor):
        """Show current processing statistics"""
        stats = processor.get_processing_stats()
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write('CONSENSUS PROCESSING STATISTICS')
        self.stdout.write('='*50)
        
        # Raw data stats
        self.stdout.write(f'Raw Listings: {stats["raw_listings_total"]:,}')
        self.stdout.write(f'Unique Part Numbers: {stats["unique_part_numbers"]:,}')
        
        # Consensus stats
        self.stdout.write(f'\nConsensus Fitments: {stats["consensus_fitments_total"]:,}')
        self.stdout.write(f'  High Confidence: {stats["high_confidence_count"]:,} ({stats["high_confidence_percentage"]}%)')
        self.stdout.write(f'  Medium Confidence: {stats["medium_confidence_count"]:,}')
        self.stdout.write(f'  Low Confidence: {stats["low_confidence_count"]:,}')
        self.stdout.write(f'  Needs Review: {stats["needs_review_count"]:,}')
        
        # Conflict stats
        self.stdout.write(f'\nPending Conflicts: {stats["pending_conflicts"]:,}')
        
        # Quality metrics
        self.stdout.write(f'\nQuality Metrics:')
        self.stdout.write(f'  Production Ready: {stats["production_ready_percentage"]}%')
        
        if stats['raw_listings_total'] > 0:
            processing_rate = (stats['consensus_fitments_total'] / stats['raw_listings_total']) * 100
            self.stdout.write(f'  Processing Rate: {processing_rate:.1f}%')
        
        self.stdout.write('='*50)
