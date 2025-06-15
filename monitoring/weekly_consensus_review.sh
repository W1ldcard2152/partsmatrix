#!/bin/bash
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
