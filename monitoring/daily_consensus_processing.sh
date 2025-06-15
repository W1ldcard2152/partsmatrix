#!/bin/bash
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
