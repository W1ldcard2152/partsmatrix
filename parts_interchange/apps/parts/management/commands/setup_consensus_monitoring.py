from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db import models
from apps.parts.models import RawListingData, ConsensusFitment, ConflictingFitment
from decimal import Decimal
import os
import json
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Set up monitoring and alerting for consensus-based fitment system'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--create-scripts',
            action='store_true',
            help='Create monitoring shell scripts'
        )
        parser.add_argument(
            '--setup-logging',
            action='store_true',
            help='Configure enhanced logging for consensus processing'
        )
        parser.add_argument(
            '--create-alerts',
            action='store_true',
            help='Create alert threshold configuration'
        )
        parser.add_argument(
            '--test-system',
            action='store_true',
            help='Run comprehensive system health check'
        )
        parser.add_argument(
            '--output-dir',
            default='./monitoring',
            help='Output directory for monitoring files'
        )
    
    def handle(self, *args, **options):
        try:
            # Create monitoring directory
            os.makedirs(options['output_dir'], exist_ok=True)
            
            if options['create_scripts']:
                self.create_monitoring_scripts(options['output_dir'])
            
            if options['setup_logging']:
                self.setup_enhanced_logging(options['output_dir'])
            
            if options['create_alerts']:
                self.create_alert_configuration(options['output_dir'])
            
            if options['test_system']:
                self.run_system_health_check()
            
            # Always show current system status
            self.show_system_status()
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error setting up monitoring: {e}')
            )
            raise CommandError(f'Monitoring setup failed: {e}')
    
    def create_monitoring_scripts(self, output_dir):
        """Create monitoring shell scripts"""
        # Daily processing script
        daily_script = """#!/bin/bash
# Daily Consensus Processing Script
# Run this script daily to process new raw listings

echo "Starting daily consensus processing..."
echo "Timestamp: $(date)"

# Process new raw listings
python manage.py process_consensus_fitments --all --min-listings 2

# Generate daily stats
python manage.py consensus_quality_analysis --export-json --output-dir ./daily_reports

# Check for critical issues
python manage.py setup_consensus_monitoring --test-system

echo "Daily processing complete: $(date)"
"""
        
        weekly_script = """#!/bin/bash
# Weekly Consensus Review Script
# Run this script weekly for conflict review and cleanup

echo "Starting weekly consensus review..."
echo "Timestamp: $(date)"

# Review pending conflicts
python manage.py review_fitment_conflicts --status PENDING --generate-report

# Attempt auto-resolution of simple conflicts
python manage.py review_fitment_conflicts --auto-resolve

# Generate comprehensive quality report
python manage.py consensus_quality_analysis --confidence-breakdown --part-coverage --quality-trends --export-csv

echo "Weekly review complete: $(date)"
"""
        
        monthly_script = """#!/bin/bash
# Monthly Consensus Analysis Script
# Run this script monthly for comprehensive analysis

echo "Starting monthly consensus analysis..."
echo "Timestamp: $(date)"

# Full quality analysis with all options
python manage.py consensus_quality_analysis \\
    --confidence-breakdown \\
    --part-coverage \\
    --quality-trends \\
    --days-back 90 \\
    --export-csv \\
    --export-json \\
    --output-dir ./monthly_reports

# Archive old conflict reports
find ./consensus_reports -name "*.csv" -mtime +90 -exec mv {} ./archive/ \\;

echo "Monthly analysis complete: $(date)"
"""
        
        # Write scripts
        scripts = [
            ('daily_consensus_processing.sh', daily_script),
            ('weekly_consensus_review.sh', weekly_script),
            ('monthly_consensus_analysis.sh', monthly_script)
        ]
        
        for script_name, script_content in scripts:
            script_path = os.path.join(output_dir, script_name)
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            # Make executable (Unix/Linux)
            try:
                os.chmod(script_path, 0o755)
            except:
                pass  # Windows doesn't support chmod
        
        self.stdout.write(
            self.style.SUCCESS(f'Monitoring scripts created in {output_dir}/')
        )
    
    def setup_enhanced_logging(self, output_dir):
        """Setup enhanced logging configuration"""
        logging_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'verbose': {
                    'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
                    'style': '{',
                },
                'simple': {
                    'format': '{levelname} {message}',
                    'style': '{',
                },
                'consensus': {
                    'format': '[CONSENSUS] {asctime} {levelname} {module}: {message}',
                    'style': '{',
                }
            },
            'handlers': {
                'consensus_file': {
                    'level': 'INFO',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': os.path.join(output_dir, 'consensus_processing.log'),
                    'maxBytes': 10485760,  # 10MB
                    'backupCount': 5,
                    'formatter': 'consensus',
                },
                'consensus_error': {
                    'level': 'ERROR',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': os.path.join(output_dir, 'consensus_errors.log'),
                    'maxBytes': 5242880,  # 5MB
                    'backupCount': 3,
                    'formatter': 'verbose',
                },
                'console': {
                    'level': 'WARNING',
                    'class': 'logging.StreamHandler',
                    'formatter': 'simple',
                }
            },
            'loggers': {
                'apps.parts.consensus': {
                    'handlers': ['consensus_file', 'consensus_error', 'console'],
                    'level': 'INFO',
                    'propagate': False,
                },
                'apps.parts.management.commands.process_consensus_fitments': {
                    'handlers': ['consensus_file', 'consensus_error'],
                    'level': 'INFO',
                    'propagate': False,
                }
            }
        }
        
        # Write logging configuration
        config_path = os.path.join(output_dir, 'consensus_logging.json')
        with open(config_path, 'w') as f:
            json.dump(logging_config, f, indent=2)
        
        # Create log analysis script
        log_analysis_script = """#!/bin/bash
# Log Analysis Script
# Analyze consensus processing logs for issues

echo "Consensus Processing Log Analysis"
echo "================================"

LOG_DIR="./monitoring"
CONSENSUS_LOG="$LOG_DIR/consensus_processing.log"
ERROR_LOG="$LOG_DIR/consensus_errors.log"

if [ -f "$CONSENSUS_LOG" ]; then
    echo "Recent processing activity:"
    tail -20 "$CONSENSUS_LOG"
    echo ""
    
    echo "Processing summary (last 24 hours):"
    grep "$(date --date='1 day ago' '+%Y-%m-%d')" "$CONSENSUS_LOG" | wc -l
    echo "log entries found"
    echo ""
fi

if [ -f "$ERROR_LOG" ]; then
    echo "Recent errors:"
    tail -10 "$ERROR_LOG"
    echo ""
    
    ERROR_COUNT=$(grep "$(date '+%Y-%m-%d')" "$ERROR_LOG" | wc -l)
    echo "Errors today: $ERROR_COUNT"
    
    if [ "$ERROR_COUNT" -gt 10 ]; then
        echo "WARNING: High error count detected!"
    fi
fi

echo "Analysis complete: $(date)"
"""
        
        # Write log analysis script
        script_path = os.path.join(output_dir, 'analyze_logs.sh')
        with open(script_path, 'w') as f:
            f.write(log_analysis_script)
        
        try:
            os.chmod(script_path, 0o755)
        except:
            pass
        
        self.stdout.write(
            self.style.SUCCESS(f'Enhanced logging configuration created in {output_dir}/')
        )
    
    def create_alert_configuration(self, output_dir):
        """Create alert threshold configuration"""
        alert_config = {
            'thresholds': {
                'critical': {
                    'pending_conflicts_age_days': 30,
                    'processing_failure_rate_percent': 20,
                    'low_confidence_rate_percent': 50,
                    'raw_data_staleness_days': 7
                },
                'warning': {
                    'pending_conflicts_age_days': 14,
                    'processing_failure_rate_percent': 10,
                    'low_confidence_rate_percent': 30,
                    'raw_data_staleness_days': 3
                }
            },
            'notification_settings': {
                'email_alerts': False,
                'log_alerts': True,
                'console_alerts': True
            },
            'monitoring_intervals': {
                'system_health_check_hours': 24,
                'conflict_review_days': 7,
                'quality_analysis_days': 30
            }
        }
        
        # Write alert configuration
        config_path = os.path.join(output_dir, 'alert_thresholds.json')
        with open(config_path, 'w') as f:
            json.dump(alert_config, f, indent=2)
        
        # Create alert checking script
        alert_script = """#!/bin/bash
# Alert Checking Script
# Check system against alert thresholds

echo "Consensus System Alert Check"
echo "============================"

# Check if Django is available
if ! python -c "import django" 2>/dev/null; then
    echo "CRITICAL: Django not available"
    exit 1
fi

# Run system health check
python manage.py setup_consensus_monitoring --test-system > /tmp/health_check.log 2>&1

if [ $? -ne 0 ]; then
    echo "CRITICAL: System health check failed"
    cat /tmp/health_check.log
    exit 1
fi

echo "System health check passed"

# Check for old pending conflicts
CONFLICT_COUNT=$(python manage.py review_fitment_conflicts --status PENDING --age-days 14 | grep "Found" | awk '{print $2}')

if [ "$CONFLICT_COUNT" -gt 50 ]; then
    echo "WARNING: $CONFLICT_COUNT old pending conflicts found"
fi

echo "Alert check complete: $(date)"
"""
        
        script_path = os.path.join(output_dir, 'check_alerts.sh')
        with open(script_path, 'w') as f:
            f.write(alert_script)
        
        try:
            os.chmod(script_path, 0o755)
        except:
            pass
        
        self.stdout.write(
            self.style.SUCCESS(f'Alert configuration created in {output_dir}/')
        )
    
    def run_system_health_check(self):
        """Run comprehensive system health check"""
        self.stdout.write('Running consensus system health check...')
        
        issues = []
        warnings = []
        
        # Check data availability
        raw_count = RawListingData.objects.count()
        consensus_count = ConsensusFitment.objects.count()
        
        if raw_count == 0:
            issues.append('No raw listing data found')
        elif raw_count < 100:
            warnings.append(f'Low raw data count: {raw_count}')
        
        # Check recent data
        from datetime import timedelta
        recent_cutoff = timezone.now() - timedelta(days=7)
        recent_raw = RawListingData.objects.filter(extraction_date__gte=recent_cutoff).count()
        
        if recent_raw == 0:
            issues.append('No recent raw data (last 7 days)')
        elif recent_raw < 10:
            warnings.append(f'Low recent data: {recent_raw} listings in last 7 days')
        
        # Check processing rate
        if raw_count > 0:
            processing_rate = (consensus_count / raw_count) * 100
            if processing_rate < 10:
                issues.append(f'Low processing rate: {processing_rate:.1f}%')
            elif processing_rate < 30:
                warnings.append(f'Moderate processing rate: {processing_rate:.1f}%')
        
        # Check pending conflicts
        old_conflicts = ConflictingFitment.objects.filter(
            resolution_status='PENDING',
            created_date__lt=timezone.now() - timedelta(days=30)
        ).count()
        
        if old_conflicts > 100:
            issues.append(f'Too many old conflicts: {old_conflicts}')
        elif old_conflicts > 50:
            warnings.append(f'Many old conflicts: {old_conflicts}')
        
        # Check confidence distribution
        if consensus_count > 0:
            low_confidence = ConsensusFitment.objects.filter(confidence_score__lt=40).count()
            low_confidence_rate = (low_confidence / consensus_count) * 100
            
            if low_confidence_rate > 50:
                issues.append(f'High low-confidence rate: {low_confidence_rate:.1f}%')
            elif low_confidence_rate > 30:
                warnings.append(f'Moderate low-confidence rate: {low_confidence_rate:.1f}%')
        
        # Display results
        if issues:
            self.stdout.write(self.style.ERROR('CRITICAL ISSUES FOUND:'))
            for issue in issues:
                self.stdout.write(self.style.ERROR(f'  ❌ {issue}'))
        
        if warnings:
            self.stdout.write(self.style.WARNING('WARNINGS:'))
            for warning in warnings:
                self.stdout.write(self.style.WARNING(f'  ⚠️  {warning}'))
        
        if not issues and not warnings:
            self.stdout.write(self.style.SUCCESS('✅ System health check passed - no issues found'))
        
        return len(issues) == 0  # Return True if no critical issues
    
    def show_system_status(self):
        """Show current system status"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write('CONSENSUS SYSTEM STATUS')
        self.stdout.write('='*50)
        
        # Basic counts
        raw_count = RawListingData.objects.count()
        consensus_count = ConsensusFitment.objects.count()
        conflict_count = ConflictingFitment.objects.filter(resolution_status='PENDING').count()
        
        self.stdout.write(f'Raw Listings: {raw_count:,}')
        self.stdout.write(f'Consensus Fitments: {consensus_count:,}')
        self.stdout.write(f'Pending Conflicts: {conflict_count:,}')
        
        # Recent activity
        from datetime import timedelta
        recent_cutoff = timezone.now() - timedelta(days=7)
        recent_raw = RawListingData.objects.filter(extraction_date__gte=recent_cutoff).count()
        recent_consensus = ConsensusFitment.objects.filter(last_updated__gte=recent_cutoff).count()
        
        self.stdout.write(f'\nRecent Activity (7 days):')
        self.stdout.write(f'  New Raw Listings: {recent_raw:,}')
        self.stdout.write(f'  Updated Consensus: {recent_consensus:,}')
        
        # Quality metrics
        if consensus_count > 0:
            high_confidence = ConsensusFitment.objects.filter(confidence_score__gte=80).count()
            high_confidence_rate = (high_confidence / consensus_count) * 100
            
            production_ready = ConsensusFitment.objects.filter(
                models.Q(status='HIGH_CONFIDENCE') | models.Q(status='VERIFIED')
            ).count()
            production_rate = (production_ready / consensus_count) * 100
            
            self.stdout.write(f'\nQuality Metrics:')
            self.stdout.write(f'  High Confidence (80%+): {high_confidence_rate:.1f}%')
            self.stdout.write(f'  Production Ready: {production_rate:.1f}%')
        
        # Processing efficiency
        if raw_count > 0:
            processing_rate = (consensus_count / raw_count) * 100
            self.stdout.write(f'  Processing Efficiency: {processing_rate:.1f}%')
        
        self.stdout.write('\nMonitoring Status: ✅ Active')
        self.stdout.write(f'Last Check: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}')
        
        self.stdout.write('='*50)
