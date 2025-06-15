#!/bin/bash
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
