#!/bin/bash
# Monthly Consensus Analysis Script
# Run this script monthly for comprehensive analysis

echo "Starting monthly consensus analysis..."
echo "Timestamp: $(date)"

# Full quality analysis with all options
python manage.py consensus_quality_analysis \
    --confidence-breakdown \
    --part-coverage \
    --quality-trends \
    --days-back 90 \
    --export-csv \
    --export-json \
    --output-dir ./monthly_reports

# Archive old conflict reports
find ./consensus_reports -name "*.csv" -mtime +90 -exec mv {} ./archive/ \;

echo "Monthly analysis complete: $(date)"
