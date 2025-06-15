from django.core.management.base import BaseCommand, CommandError
from django.db import models
from django.utils import timezone
from apps.parts.models import RawListingData, ConsensusFitment, ConflictingFitment
from decimal import Decimal
import csv
import json
import os
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Generate comprehensive consensus data quality analysis reports'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--export-csv',
            action='store_true',
            help='Export analysis to CSV files'
        )
        parser.add_argument(
            '--export-json',
            action='store_true',
            help='Export analysis to JSON file'
        )
        parser.add_argument(
            '--confidence-breakdown',
            action='store_true',
            help='Show detailed confidence score breakdown'
        )
        parser.add_argument(
            '--part-coverage',
            action='store_true',
            help='Analyze part number coverage rates'
        )
        parser.add_argument(
            '--quality-trends',
            action='store_true',
            help='Show quality trends over time'
        )
        parser.add_argument(
            '--days-back',
            type=int,
            default=30,
            help='Number of days to analyze for trends (default: 30)'
        )
        parser.add_argument(
            '--min-listings',
            type=int,
            default=2,
            help='Minimum listings required for analysis (default: 2)'
        )
        parser.add_argument(
            '--output-dir',
            default='./consensus_reports',
            help='Output directory for reports'
        )
    
    def handle(self, *args, **options):
        try:
            # Create output directory
            os.makedirs(options['output_dir'], exist_ok=True)
            
            # Generate analysis
            analysis_data = self.generate_comprehensive_analysis(options)
            
            # Display console output
            self.display_analysis_summary(analysis_data)
            
            if options['confidence_breakdown']:
                self.display_confidence_breakdown(analysis_data)
            
            if options['part_coverage']:
                self.display_part_coverage(analysis_data)
            
            if options['quality_trends']:
                self.display_quality_trends(analysis_data, options['days_back'])
            
            # Export data
            if options['export_csv']:
                self.export_to_csv(analysis_data, options['output_dir'])
            
            if options['export_json']:
                self.export_to_json(analysis_data, options['output_dir'])
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during quality analysis: {e}')
            )
            raise CommandError(f'Quality analysis failed: {e}')
    
    def generate_comprehensive_analysis(self, options):
        """Generate comprehensive data quality analysis"""
        analysis = {
            'generation_time': timezone.now(),
            'parameters': {
                'days_back': options['days_back'],
                'min_listings': options['min_listings']
            }
        }
        
        # Basic counts
        analysis['raw_data'] = self.analyze_raw_data(options)
        analysis['consensus_data'] = self.analyze_consensus_data(options)
        analysis['conflicts'] = self.analyze_conflicts(options)
        analysis['coverage'] = self.analyze_coverage(options)
        analysis['quality_metrics'] = self.calculate_quality_metrics(options)
        analysis['trends'] = self.analyze_trends(options['days_back'])
        
        return analysis
    
    def analyze_raw_data(self, options):
        """Analyze raw listing data"""
        total_raw = RawListingData.objects.count()
        
        # Data quality indicators
        verified_sellers = RawListingData.objects.filter(is_verified_seller=True).count()
        business_sellers = RawListingData.objects.filter(seller_is_business=True).count()
        has_oem_ref = RawListingData.objects.filter(has_oem_reference=True).count()
        detailed_desc = RawListingData.objects.filter(has_detailed_description=True).count()
        
        # Recent data (last 30 days)
        recent_cutoff = timezone.now() - timedelta(days=30)
        recent_raw = RawListingData.objects.filter(extraction_date__gte=recent_cutoff).count()
        
        # Part number distribution
        part_distribution = (
            RawListingData.objects
            .values('part_number')
            .annotate(listing_count=models.Count('id'))
            .order_by('-listing_count')
        )
        
        # Calculate distribution stats
        listing_counts = [item['listing_count'] for item in part_distribution]
        
        return {
            'total_listings': total_raw,
            'unique_part_numbers': part_distribution.count(),
            'recent_listings_30_days': recent_raw,
            'quality_indicators': {
                'verified_sellers': verified_sellers,
                'verified_sellers_percentage': (verified_sellers / total_raw * 100) if total_raw > 0 else 0,
                'business_sellers': business_sellers,
                'business_sellers_percentage': (business_sellers / total_raw * 100) if total_raw > 0 else 0,
                'has_oem_reference': has_oem_ref,
                'oem_reference_percentage': (has_oem_ref / total_raw * 100) if total_raw > 0 else 0,
                'detailed_description': detailed_desc,
                'detailed_desc_percentage': (detailed_desc / total_raw * 100) if total_raw > 0 else 0
            },
            'listing_distribution': {
                'max_listings_per_part': max(listing_counts) if listing_counts else 0,
                'min_listings_per_part': min(listing_counts) if listing_counts else 0,
                'avg_listings_per_part': sum(listing_counts) / len(listing_counts) if listing_counts else 0,
                'parts_with_single_listing': sum(1 for count in listing_counts if count == 1),
                'parts_with_multiple_listings': sum(1 for count in listing_counts if count > 1)
            }
        }
    
    def analyze_consensus_data(self, options):
        """Analyze consensus fitment data"""
        total_consensus = ConsensusFitment.objects.count()
        
        # Status distribution
        status_counts = {}
        for status_choice in ConsensusFitment.STATUS_CHOICES:
            status = status_choice[0]
            count = ConsensusFitment.objects.filter(status=status).count()
            status_counts[status] = {
                'count': count,
                'percentage': (count / total_consensus * 100) if total_consensus > 0 else 0,
                'description': status_choice[1]
            }
        
        # Confidence score distribution
        confidence_ranges = [
            ('90-100', 90, 100),
            ('80-89', 80, 89),
            ('70-79', 70, 79),
            ('60-69', 60, 69),
            ('50-59', 50, 59),
            ('40-49', 40, 49),
            ('30-39', 30, 39),
            ('20-29', 20, 29),
            ('0-19', 0, 19)
        ]
        
        confidence_distribution = {}
        for range_name, min_conf, max_conf in confidence_ranges:
            count = ConsensusFitment.objects.filter(
                confidence_score__gte=min_conf,
                confidence_score__lte=max_conf
            ).count()
            confidence_distribution[range_name] = {
                'count': count,
                'percentage': (count / total_consensus * 100) if total_consensus > 0 else 0
            }
        
        # Supporting listings analysis
        support_stats = ConsensusFitment.objects.aggregate(
            avg_supporting_listings=models.Avg('supporting_listings_count'),
            max_supporting_listings=models.Max('supporting_listings_count'),
            min_supporting_listings=models.Min('supporting_listings_count')
        )
        
        # Production readiness
        production_ready = ConsensusFitment.objects.filter(
            models.Q(status='HIGH_CONFIDENCE') | models.Q(status='VERIFIED'),
            confidence_score__gte=80
        ).count()
        
        return {
            'total_consensus_fitments': total_consensus,
            'status_distribution': status_counts,
            'confidence_distribution': confidence_distribution,
            'supporting_listings_stats': support_stats,
            'production_ready': {
                'count': production_ready,
                'percentage': (production_ready / total_consensus * 100) if total_consensus > 0 else 0
            }
        }
    
    def analyze_conflicts(self, options):
        """Analyze conflict data"""
        total_conflicts = ConflictingFitment.objects.count()
        pending_conflicts = ConflictingFitment.objects.filter(resolution_status='PENDING').count()
        resolved_conflicts = ConflictingFitment.objects.filter(resolution_status='RESOLVED').count()
        dismissed_conflicts = ConflictingFitment.objects.filter(resolution_status='DISMISSED').count()
        
        # Age analysis
        current_time = timezone.now()
        age_ranges = [
            ('0-7 days', 0, 7),
            ('8-30 days', 8, 30),
            ('31-90 days', 31, 90),
            ('90+ days', 91, 999999)
        ]
        
        age_distribution = {}
        for range_name, min_days, max_days in age_ranges:
            min_date = current_time - timedelta(days=max_days)
            max_date = current_time - timedelta(days=min_days)
            
            count = ConflictingFitment.objects.filter(
                created_date__gte=min_date,
                created_date__lte=max_date,
                resolution_status='PENDING'
            ).count()
            
            age_distribution[range_name] = count
        
        # Resolution rate
        total_resolved = resolved_conflicts + dismissed_conflicts
        resolution_rate = (total_resolved / total_conflicts * 100) if total_conflicts > 0 else 0
        
        return {
            'total_conflicts': total_conflicts,
            'pending_conflicts': pending_conflicts,
            'resolved_conflicts': resolved_conflicts,
            'dismissed_conflicts': dismissed_conflicts,
            'resolution_rate_percentage': resolution_rate,
            'pending_age_distribution': age_distribution
        }
    
    def analyze_coverage(self, options):
        """Analyze data coverage and processing rates"""
        total_raw_parts = RawListingData.objects.values('part_number').distinct().count()
        consensus_parts = ConsensusFitment.objects.values('part_number').distinct().count()
        
        # Parts with sufficient data for processing
        eligible_parts = (
            RawListingData.objects
            .values('part_number')
            .annotate(listing_count=models.Count('id'))
            .filter(listing_count__gte=options['min_listings'])
            .count()
        )
        
        # Processing coverage
        processing_rate = (consensus_parts / eligible_parts * 100) if eligible_parts > 0 else 0
        overall_coverage = (consensus_parts / total_raw_parts * 100) if total_raw_parts > 0 else 0
        
        return {
            'total_raw_part_numbers': total_raw_parts,
            'processed_part_numbers': consensus_parts,
            'eligible_for_processing': eligible_parts,
            'processing_rate_percentage': processing_rate,
            'overall_coverage_percentage': overall_coverage,
            'unprocessed_parts': eligible_parts - consensus_parts
        }
    
    def calculate_quality_metrics(self, options):
        """Calculate overall quality metrics"""
        total_raw = RawListingData.objects.count()
        total_consensus = ConsensusFitment.objects.count()
        
        # Data efficiency
        data_efficiency = (total_consensus / total_raw * 100) if total_raw > 0 else 0
        
        # Average confidence score
        avg_confidence = ConsensusFitment.objects.aggregate(
            avg_confidence=models.Avg('confidence_score')
        )['avg_confidence'] or 0
        
        # High quality percentage
        high_quality = ConsensusFitment.objects.filter(confidence_score__gte=80).count()
        high_quality_percentage = (high_quality / total_consensus * 100) if total_consensus > 0 else 0
        
        # Average weight per listing
        total_weight = sum(listing.calculate_quality_weight() for listing in RawListingData.objects.all())
        avg_weight = total_weight / total_raw if total_raw > 0 else 0
        
        return {
            'data_efficiency_percentage': data_efficiency,
            'average_confidence_score': float(avg_confidence),
            'high_quality_percentage': high_quality_percentage,
            'average_listing_weight': float(avg_weight)
        }
    
    def analyze_trends(self, days_back):
        """Analyze quality trends over time"""
        try:
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Daily trends
            daily_trends = []
            for i in range(days_back):
                day_start = start_date + timedelta(days=i)
                day_end = day_start + timedelta(days=1)
                
                try:
                    raw_count = RawListingData.objects.filter(
                        extraction_date__gte=day_start,
                        extraction_date__lt=day_end
                    ).count()
                    
                    consensus_count = ConsensusFitment.objects.filter(
                        last_updated__gte=day_start,
                        last_updated__lt=day_end
                    ).count()
                    
                    daily_trends.append({
                        'date': day_start.strftime('%Y-%m-%d'),
                        'raw_listings': raw_count,
                        'consensus_fitments': consensus_count
                    })
                except Exception as e:
                    # Skip days with invalid dates
                    daily_trends.append({
                        'date': day_start.strftime('%Y-%m-%d'),
                        'raw_listings': 0,
                        'consensus_fitments': 0
                    })
            
            return {
                'daily_trends': daily_trends,
                'trend_period_days': days_back,
                'total_raw_in_period': sum(day['raw_listings'] for day in daily_trends),
                'total_consensus_in_period': sum(day['consensus_fitments'] for day in daily_trends)
            }
        except Exception as e:
            # Return empty trends if there's an error
            return {
                'daily_trends': [],
                'trend_period_days': days_back,
                'total_raw_in_period': 0,
                'total_consensus_in_period': 0
            }
    
    def display_analysis_summary(self, analysis):
        """Display summary analysis to console"""
        self.stdout.write('='*60)
        self.stdout.write('CONSENSUS DATA QUALITY ANALYSIS REPORT')
        self.stdout.write('='*60)
        self.stdout.write(f'Generated: {analysis["generation_time"].strftime("%Y-%m-%d %H:%M:%S")}')
        self.stdout.write('')
        
        # Raw data summary
        raw = analysis['raw_data']
        self.stdout.write('RAW DATA SUMMARY:')
        self.stdout.write(f'  Total Listings: {raw["total_listings"]:,}')
        self.stdout.write(f'  Unique Part Numbers: {raw["unique_part_numbers"]:,}')
        self.stdout.write(f'  Recent (30 days): {raw["recent_listings_30_days"]:,}')
        self.stdout.write(f'  Business Sellers: {raw["quality_indicators"]["business_sellers_percentage"]:.1f}%')
        self.stdout.write(f'  OEM References: {raw["quality_indicators"]["oem_reference_percentage"]:.1f}%')
        self.stdout.write('')
        
        # Consensus data summary
        consensus = analysis['consensus_data']
        self.stdout.write('CONSENSUS DATA SUMMARY:')
        self.stdout.write(f'  Total Consensus Fitments: {consensus["total_consensus_fitments"]:,}')
        self.stdout.write(f'  Production Ready: {consensus["production_ready"]["percentage"]:.1f}%')
        self.stdout.write('  Status Distribution:')
        for status, data in consensus['status_distribution'].items():
            self.stdout.write(f'    {status}: {data["count"]:,} ({data["percentage"]:.1f}%)')
        self.stdout.write('')
        
        # Conflicts summary
        conflicts = analysis['conflicts']
        self.stdout.write('CONFLICTS SUMMARY:')
        self.stdout.write(f'  Total Conflicts: {conflicts["total_conflicts"]:,}')
        self.stdout.write(f'  Pending: {conflicts["pending_conflicts"]:,}')
        self.stdout.write(f'  Resolution Rate: {conflicts["resolution_rate_percentage"]:.1f}%')
        self.stdout.write('')
        
        # Coverage summary
        coverage = analysis['coverage']
        self.stdout.write('COVERAGE SUMMARY:')
        self.stdout.write(f'  Processing Rate: {coverage["processing_rate_percentage"]:.1f}%')
        self.stdout.write(f'  Overall Coverage: {coverage["overall_coverage_percentage"]:.1f}%')
        self.stdout.write(f'  Unprocessed Parts: {coverage["unprocessed_parts"]:,}')
        self.stdout.write('')
        
        # Quality metrics
        quality = analysis['quality_metrics']
        self.stdout.write('QUALITY METRICS:')
        self.stdout.write(f'  Data Efficiency: {quality["data_efficiency_percentage"]:.1f}%')
        self.stdout.write(f'  Average Confidence: {quality["average_confidence_score"]:.1f}')
        self.stdout.write(f'  High Quality Rate: {quality["high_quality_percentage"]:.1f}%')
        self.stdout.write(f'  Average Listing Weight: {quality["average_listing_weight"]:.2f}')
        
        self.stdout.write('='*60)
    
    def display_confidence_breakdown(self, analysis):
        """Display detailed confidence score breakdown"""
        self.stdout.write('\nCONFIDENCE SCORE BREAKDOWN:')
        self.stdout.write('-'*40)
        
        confidence_dist = analysis['consensus_data']['confidence_distribution']
        for range_name, data in confidence_dist.items():
            if data['count'] > 0:
                self.stdout.write(f'  {range_name}%: {data["count"]:,} ({data["percentage"]:.1f}%)')
    
    def display_part_coverage(self, analysis):
        """Display part coverage analysis"""
        self.stdout.write('\nPART COVERAGE ANALYSIS:')
        self.stdout.write('-'*40)
        
        raw = analysis['raw_data']
        coverage = analysis['coverage']
        
        self.stdout.write(f'  Parts with Single Listing: {raw["listing_distribution"]["parts_with_single_listing"]:,}')
        self.stdout.write(f'  Parts with Multiple Listings: {raw["listing_distribution"]["parts_with_multiple_listings"]:,}')
        self.stdout.write(f'  Average Listings per Part: {raw["listing_distribution"]["avg_listings_per_part"]:.1f}')
        self.stdout.write(f'  Max Listings for One Part: {raw["listing_distribution"]["max_listings_per_part"]:,}')
    
    def display_quality_trends(self, analysis, days_back):
        """Display quality trends"""
        self.stdout.write(f'\nQUALITY TRENDS (Last {days_back} days):')
        self.stdout.write('-'*50)
        
        trends = analysis['trends']
        recent_days = trends['daily_trends'][-7:]  # Show last 7 days
        
        for day_data in recent_days:
            self.stdout.write(
                f'  {day_data["date"]}: Raw={day_data["raw_listings"]:,}, '
                f'Consensus={day_data["consensus_fitments"]:,}'
            )
        
        self.stdout.write(f'\nPeriod Totals:')
        self.stdout.write(f'  Raw Listings: {trends["total_raw_in_period"]:,}')
        self.stdout.write(f'  Consensus Fitments: {trends["total_consensus_in_period"]:,}')
    
    def export_to_csv(self, analysis, output_dir):
        """Export analysis to CSV files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Export confidence distribution
        confidence_file = os.path.join(output_dir, f'confidence_distribution_{timestamp}.csv')
        with open(confidence_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Confidence Range', 'Count', 'Percentage'])
            
            for range_name, data in analysis['consensus_data']['confidence_distribution'].items():
                writer.writerow([range_name, data['count'], data['percentage']])
        
        # Export daily trends
        trends_file = os.path.join(output_dir, f'daily_trends_{timestamp}.csv')
        with open(trends_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Date', 'Raw Listings', 'Consensus Fitments'])
            
            for day_data in analysis['trends']['daily_trends']:
                writer.writerow([day_data['date'], day_data['raw_listings'], day_data['consensus_fitments']])
        
        # Export summary statistics
        summary_file = os.path.join(output_dir, f'summary_stats_{timestamp}.csv')
        with open(summary_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Metric', 'Value'])
            
            # Flatten key metrics for CSV export
            metrics = [
                ('Total Raw Listings', analysis['raw_data']['total_listings']),
                ('Total Consensus Fitments', analysis['consensus_data']['total_consensus_fitments']),
                ('Processing Rate %', analysis['coverage']['processing_rate_percentage']),
                ('Production Ready %', analysis['consensus_data']['production_ready']['percentage']),
                ('Average Confidence', analysis['quality_metrics']['average_confidence_score']),
                ('Pending Conflicts', analysis['conflicts']['pending_conflicts']),
                ('Resolution Rate %', analysis['conflicts']['resolution_rate_percentage'])
            ]
            
            for metric, value in metrics:
                writer.writerow([metric, value])
        
        self.stdout.write(
            self.style.SUCCESS(f'CSV reports exported to {output_dir}/')
        )
    
    def export_to_json(self, analysis, output_dir):
        """Export analysis to JSON file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.join(output_dir, f'consensus_analysis_{timestamp}.json')
        
        # Convert datetime objects to strings for JSON serialization
        analysis_copy = analysis.copy()
        analysis_copy['generation_time'] = analysis['generation_time'].isoformat()
        
        with open(filename, 'w') as jsonfile:
            json.dump(analysis_copy, jsonfile, indent=2, default=str)
        
        self.stdout.write(
            self.style.SUCCESS(f'JSON report exported: {filename}')
        )
