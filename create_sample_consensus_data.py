#!/usr/bin/env python
"""
Sample data creation script for testing the consensus-based fitment system.
This script creates sample RawListingData entries to test the consensus processing.
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta
import random
from pathlib import Path

# Setup Django paths like manage.py does
project_root = Path(__file__).resolve().parent
parts_interchange_dir = project_root / 'parts_interchange'
apps_dir = parts_interchange_dir / 'apps'
sys.path.insert(0, str(apps_dir))
sys.path.insert(0, str(parts_interchange_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parts_interchange.settings')
django.setup()

from apps.parts.models import RawListingData
from apps.parts.consensus.processor import FitmentConsensusProcessor


def create_sample_raw_listings():
    """Create sample raw listing data for testing consensus processing"""
    
    print("Creating sample raw listing data...")
    
    # Sample part numbers with different fitment scenarios
    sample_data = [
        # Part 1: Strong consensus scenario (4 agree, 1 differs)
        {
            'part_number': '1432255E',
            'scenarios': [
                # Strong consensus group
                {'count': 4, 'year': 2010, 'make': 'Ford', 'model': 'F-150', 'trim': 'XLT', 'engine': '4.6L V8'},
                # Outlier
                {'count': 1, 'year': 2010, 'make': 'Ford', 'model': 'F-150', 'trim': 'Regular Cab', 'engine': '4.6L V8'}
            ]
        },
        # Part 2: Medium confidence scenario (2 groups, similar weight)
        {
            'part_number': 'AC45821',
            'scenarios': [
                {'count': 3, 'year': 2008, 'make': 'Acura', 'model': 'TL', 'trim': 'Base', 'engine': '3.2L V6'},
                {'count': 2, 'year': 2009, 'make': 'Acura', 'model': 'TL', 'trim': 'Base', 'engine': '3.2L V6'}
            ]
        },
        # Part 3: High confidence scenario (6 listings all agree)
        {
            'part_number': 'GM12345A',
            'scenarios': [
                {'count': 6, 'year': 2005, 'make': 'Chevrolet', 'model': 'Malibu', 'trim': 'LS', 'engine': '2.2L I4'}
            ]
        },
        # Part 4: Conflict scenario (cross-manufacturer)
        {
            'part_number': 'UNIV789',
            'scenarios': [
                {'count': 2, 'year': 2007, 'make': 'Honda', 'model': 'Civic', 'trim': 'LX', 'engine': '1.8L I4'},
                {'count': 2, 'year': 2007, 'make': 'Toyota', 'model': 'Corolla', 'trim': 'S', 'engine': '1.8L I4'}
            ]
        },
        # Part 5: Year span conflict scenario
        {
            'part_number': 'SPAN999',
            'scenarios': [
                {'count': 2, 'year': 2000, 'make': 'Ford', 'model': 'Taurus', 'trim': 'SE', 'engine': '3.0L V6'},
                {'count': 2, 'year': 2015, 'make': 'Ford', 'model': 'Taurus', 'trim': 'SEL', 'engine': '3.5L V6'}
            ]
        }
    ]
    
    created_count = 0
    
    for part_data in sample_data:
        part_number = part_data['part_number']
        
        # Clear existing data for this part
        RawListingData.objects.filter(part_number=part_number).delete()
        
        for scenario in part_data['scenarios']:
            for i in range(scenario['count']):
                # Vary seller quality to test weighting
                seller_quality = random.choice([
                    {'feedback': 50, 'business': False, 'verified': False},
                    {'feedback': 500, 'business': False, 'verified': True},
                    {'feedback': 2000, 'business': True, 'verified': True},
                    {'feedback': 5000, 'business': True, 'verified': True}
                ])
                
                # Create listing with varied extraction dates
                extraction_date = datetime.now() - timedelta(days=random.randint(1, 30))
                
                listing = RawListingData.objects.create(
                    part_number=part_number,
                    vehicle_year=scenario['year'],
                    vehicle_make=scenario['make'],
                    vehicle_model=scenario['model'],
                    vehicle_trim=scenario['trim'],
                    vehicle_engine=scenario['engine'],
                    source_ebay_item_id=f"EB{random.randint(100000000, 999999999)}",
                    seller_feedback_count=seller_quality['feedback'],
                    seller_is_business=seller_quality['business'],
                    is_verified_seller=seller_quality['verified'],
                    listing_title=f"{part_number} {scenario['make']} {scenario['model']} {scenario['year']} AC Compressor",
                    listing_price=Decimal(str(random.randint(50, 300))),
                    has_oem_reference=random.choice([True, False]),
                    has_detailed_description=random.choice([True, False]),
                    extraction_date=extraction_date
                )
                created_count += 1
    
    print(f"Created {created_count} sample raw listings")
    return created_count


def test_consensus_processing():
    """Test the consensus processing on sample data"""
    
    print("\nTesting consensus processing...")
    
    processor = FitmentConsensusProcessor()
    
    # Get all unique part numbers
    part_numbers = RawListingData.objects.values_list('part_number', flat=True).distinct()
    
    for part_number in part_numbers:
        print(f"\nProcessing part number: {part_number}")
        
        # Show raw data summary
        raw_listings = RawListingData.objects.filter(part_number=part_number)
        print(f"  Raw listings: {raw_listings.count()}")
        
        # Process consensus
        result = processor.process_part_number(part_number)
        print(f"  Result: {result}")
    
    # Show overall stats
    print("\n" + "="*50)
    print("PROCESSING STATISTICS")
    print("="*50)
    stats = processor.get_processing_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")


def demonstrate_admin_integration():
    """Show how the data would appear in Django admin"""
    
    print("\n" + "="*50)
    print("ADMIN INTEGRATION DEMO")
    print("="*50)
    
    from apps.parts.models import ConsensusFitment, ConflictingFitment
    
    print(f"Raw Listings: {RawListingData.objects.count()}")
    print(f"Consensus Fitments: {ConsensusFitment.objects.count()}")
    print(f"Conflicting Fitments: {ConflictingFitment.objects.count()}")
    
    print("\nHigh Confidence Fitments:")
    high_confidence = ConsensusFitment.objects.filter(status='HIGH_CONFIDENCE')
    for fitment in high_confidence:
        print(f"  {fitment}")
    
    print("\nPending Conflicts:")
    conflicts = ConflictingFitment.objects.filter(resolution_status='PENDING')
    for conflict in conflicts:
        print(f"  {conflict}")


def main():
    """Main function to run the sample data creation and testing"""
    
    print("Consensus-Based Fitment System - Sample Data Creation")
    print("=" * 60)
    
    try:
        # Create sample data
        created_count = create_sample_raw_listings()
        
        # Test consensus processing
        test_consensus_processing()
        
        # Demonstrate admin integration
        demonstrate_admin_integration()
        
        print("\n" + "="*60)
        print("PHASE 1 IMPLEMENTATION COMPLETE!")
        print("="*60)
        print("\nNext steps:")
        print("1. Run Django migrations: python manage.py migrate")
        print("2. Access Django admin to review consensus fitments")
        print("3. Use management command: python manage.py process_consensus_fitments --stats-only")
        print("4. Begin Phase 2: API Enhancement (see roadmap)")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
