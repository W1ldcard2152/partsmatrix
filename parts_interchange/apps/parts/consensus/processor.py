from django.db import transaction, models
from django.utils import timezone
from decimal import Decimal
from collections import defaultdict
from typing import Dict, List, Tuple
import logging

from ..models import RawListingData, ConsensusFitment, ConflictingFitment

logger = logging.getLogger(__name__)


class FitmentConsensusProcessor:
    """Convert raw listing data (quarks) into consensus fitments (atoms)"""
    
    def __init__(self):
        self.min_listings_required = 2
        self.base_confidence = 20  # Base confidence percentage
        self.max_weight_bonus = 40  # Maximum weight bonus percentage
    
    def process_part_number(self, part_number: str) -> Dict:
        """Process all raw listings for a specific part number"""
        logger.info(f"Processing consensus for part number: {part_number}")
        
        raw_listings = RawListingData.objects.filter(part_number=part_number)
        
        if raw_listings.count() < self.min_listings_required:
            logger.info(f"Insufficient data points for {part_number}: {raw_listings.count()} < {self.min_listings_required}")
            return {'processed': 0, 'skipped': 1, 'reason': 'insufficient_data'}
        
        # Group listings by fitment signature
        fitment_groups = self.group_by_fitment_signature(raw_listings)
        
        processed_count = 0
        conflicts_created = 0
        
        # Calculate consensus for each group
        for signature, listings in fitment_groups.items():
            consensus_data = self.calculate_consensus(listings)
            
            with transaction.atomic():
                created, updated = self.update_or_create_consensus_fitment(
                    part_number, signature, consensus_data, listings
                )
                if created or updated:
                    processed_count += 1
        
        # Identify conflicts
        conflicts = self.identify_conflicts(part_number, fitment_groups)
        conflicts_created = len(conflicts)
        
        logger.info(f"Processed {processed_count} consensus fitments for {part_number}, identified {conflicts_created} conflicts")
        
        return {
            'processed': processed_count,
            'conflicts': conflicts_created,
            'total_groups': len(fitment_groups),
            'total_listings': raw_listings.count()
        }
    
    def group_by_fitment_signature(self, raw_listings) -> Dict[str, List]:
        """Group listings by unique vehicle fitment combination"""
        fitment_groups = defaultdict(list)
        
        for listing in raw_listings:
            signature = listing.get_fitment_signature()
            fitment_groups[signature].append(listing)
        
        return dict(fitment_groups)
    
    def calculate_consensus(self, listings: List[RawListingData]) -> Dict:
        """Calculate consensus metrics for a group of listings"""
        if not listings:
            return {}
        
        # Calculate total weight
        total_weight = sum(listing.calculate_quality_weight() for listing in listings)
        listing_count = len(listings)
        
        # Calculate confidence score
        confidence = self.calculate_confidence_score(listing_count, total_weight)
        
        # Determine status based on confidence
        status = self.determine_status(confidence)
        
        # Use first listing for vehicle details (they should all be the same in this group)
        first_listing = listings[0]
        
        return {
            'vehicle_year': first_listing.vehicle_year,
            'vehicle_make': first_listing.vehicle_make,
            'vehicle_model': first_listing.vehicle_model,
            'vehicle_trim': first_listing.vehicle_trim,
            'vehicle_engine': first_listing.vehicle_engine,
            'confidence_score': confidence,
            'supporting_listings_count': listing_count,
            'total_weight_score': total_weight,
            'status': status
        }
    
    def calculate_confidence_score(self, listing_count: int, total_weight: Decimal) -> Decimal:
        """Calculate confidence score based on listing count and weight"""
        # Base confidence
        confidence = Decimal(str(self.base_confidence))
        
        # Weight bonus (capped at max_weight_bonus)
        weight_bonus = min(float(total_weight) * 10, self.max_weight_bonus)
        confidence += Decimal(str(weight_bonus))
        
        # Listing count bonus
        count_bonus = min((listing_count - 1) * 15, 30)  # Up to 30% bonus for multiple listings
        confidence += Decimal(str(count_bonus))
        
        # Cap at 100
        return min(confidence, Decimal('100.00'))
    
    def determine_status(self, confidence: Decimal) -> str:
        """Determine fitment status based on confidence score"""
        confidence_float = float(confidence)
        
        if confidence_float >= 80:
            return 'HIGH_CONFIDENCE'
        elif confidence_float >= 60:
            return 'MEDIUM_CONFIDENCE'
        elif confidence_float >= 40:
            return 'LOW_CONFIDENCE'
        else:
            return 'NEEDS_REVIEW'
    
    def update_or_create_consensus_fitment(self, part_number: str, signature: str, 
                                         consensus_data: Dict, listings: List) -> Tuple[bool, bool]:
        """Update or create consensus fitment record"""
        if not consensus_data:
            return False, False
        
        try:
            consensus_fitment, created = ConsensusFitment.objects.update_or_create(
                part_number=part_number,
                vehicle_year=consensus_data['vehicle_year'],
                vehicle_make=consensus_data['vehicle_make'],
                vehicle_model=consensus_data['vehicle_model'],
                vehicle_trim=consensus_data['vehicle_trim'],
                vehicle_engine=consensus_data['vehicle_engine'],
                defaults={
                    'confidence_score': consensus_data['confidence_score'],
                    'supporting_listings_count': consensus_data['supporting_listings_count'],
                    'total_weight_score': consensus_data['total_weight_score'],
                    'status': consensus_data['status']
                }
            )
            
            # Update the many-to-many relationship
            consensus_fitment.supporting_raw_listings.set(listings)
            
            return created, not created
            
        except Exception as e:
            logger.error(f"Error creating/updating consensus fitment for {part_number}: {e}")
            return False, False
    
    def identify_conflicts(self, part_number: str, fitment_groups: Dict) -> List[str]:
        """Identify potential conflicts requiring manual review"""
        conflicts = []
        
        if len(fitment_groups) <= 1:
            return conflicts  # No conflicts possible
        
        # Check for suspicious patterns
        year_conflicts = self.check_year_conflicts(fitment_groups)
        platform_conflicts = self.check_platform_conflicts(fitment_groups)
        
        all_conflicts = year_conflicts + platform_conflicts
        
        if all_conflicts:
            self.create_conflict_record(part_number, fitment_groups, all_conflicts)
            conflicts.extend(all_conflicts)
        
        return conflicts
    
    def check_year_conflicts(self, fitment_groups: Dict) -> List[str]:
        """Check for conflicting year ranges"""
        conflicts = []
        years = []
        
        for signature, listings in fitment_groups.items():
            year = listings[0].vehicle_year
            years.append(year)
        
        # Flag if years span more than expected generation length
        if len(years) > 1:
            year_span = max(years) - min(years)
            if year_span > 8:  # Most generations are 6-8 years
                conflicts.append(f"Suspicious year range: {min(years)}-{max(years)} (span: {year_span} years)")
        
        return conflicts
    
    def check_platform_conflicts(self, fitment_groups: Dict) -> List[str]:
        """Check for conflicting platforms/models"""
        conflicts = []
        makes = set()
        models = set()
        
        for signature, listings in fitment_groups.items():
            makes.add(listings[0].vehicle_make)
            models.add(listings[0].vehicle_model)
        
        # Flag cross-manufacturer fitments (unusual but possible)
        if len(makes) > 1:
            conflicts.append(f"Cross-manufacturer fitment: {', '.join(makes)}")
        
        # Flag multiple models (may indicate part family)
        if len(models) > 3:
            conflicts.append(f"Multiple models: {', '.join(models)}")
        
        return conflicts
    
    def create_conflict_record(self, part_number: str, fitment_groups: Dict, conflicts: List[str]):
        """Create a conflict record for manual review"""
        conflict_description = "; ".join(conflicts)
        
        # Get all listings involved in the conflict
        all_listings = []
        for listings in fitment_groups.values():
            all_listings.extend(listings)
        
        try:
            with transaction.atomic():
                conflict_record, created = ConflictingFitment.objects.get_or_create(
                    part_number=part_number,
                    conflict_description=conflict_description,
                    defaults={'resolution_status': 'PENDING'}
                )
                
                if created:
                    conflict_record.conflicting_listings.set(all_listings)
                    logger.info(f"Created conflict record for {part_number}: {conflict_description}")
                
        except Exception as e:
            logger.error(f"Error creating conflict record for {part_number}: {e}")
    
    def process_all_new_data(self, min_listings: int = 2) -> Dict:
        """Process all part numbers with new raw data"""
        self.min_listings_required = min_listings
        
        # Find part numbers with sufficient raw data
        part_numbers_with_data = (
            RawListingData.objects
            .values('part_number')
            .annotate(listing_count=models.Count('id'))
            .filter(listing_count__gte=min_listings)
            .values_list('part_number', flat=True)
        )
        
        total_processed = 0
        total_conflicts = 0
        total_parts = len(part_numbers_with_data)
        
        logger.info(f"Processing {total_parts} part numbers with >= {min_listings} listings")
        
        for part_number in part_numbers_with_data:
            try:
                result = self.process_part_number(part_number)
                total_processed += result.get('processed', 0)
                total_conflicts += result.get('conflicts', 0)
            except Exception as e:
                logger.error(f"Error processing part number {part_number}: {e}")
        
        return {
            'total_parts_processed': total_parts,
            'total_fitments_processed': total_processed,
            'total_conflicts_identified': total_conflicts
        }
    
    def get_processing_stats(self) -> Dict:
        """Get overall processing statistics"""
        stats = {
            'raw_listings_total': RawListingData.objects.count(),
            'consensus_fitments_total': ConsensusFitment.objects.count(),
            'high_confidence_count': ConsensusFitment.objects.filter(status='HIGH_CONFIDENCE').count(),
            'medium_confidence_count': ConsensusFitment.objects.filter(status='MEDIUM_CONFIDENCE').count(),
            'low_confidence_count': ConsensusFitment.objects.filter(status='LOW_CONFIDENCE').count(),
            'needs_review_count': ConsensusFitment.objects.filter(status='NEEDS_REVIEW').count(),
            'pending_conflicts': ConflictingFitment.objects.filter(resolution_status='PENDING').count(),
            'unique_part_numbers': RawListingData.objects.values('part_number').distinct().count()
        }
        
        # Calculate percentages
        total_consensus = stats['consensus_fitments_total']
        if total_consensus > 0:
            stats['high_confidence_percentage'] = round((stats['high_confidence_count'] / total_consensus) * 100, 2)
            stats['production_ready_percentage'] = round((
                (stats['high_confidence_count'] + 
                 ConsensusFitment.objects.filter(status='VERIFIED').count()) / total_consensus
            ) * 100, 2)
        else:
            stats['high_confidence_percentage'] = 0
            stats['production_ready_percentage'] = 0
        
        return stats
