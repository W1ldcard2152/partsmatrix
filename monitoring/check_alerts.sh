#!/bin/bash
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
