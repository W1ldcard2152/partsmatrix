@echo off
REM Quick Phase 2 Demo Script
REM Shows the consensus system in action

echo ======================================
echo Phase 2 Consensus System Demo
echo ======================================

echo.
echo [1] Current System Overview:
python manage.py process_consensus_fitments --stats-only

echo.
echo [2] Reviewing Pending Conflicts:
python manage.py review_fitment_conflicts --status PENDING --limit 5

echo.
echo [3] Quality Analysis Summary:
python manage.py consensus_quality_analysis --confidence-breakdown

echo.
echo [4] System Health Check:
python manage.py setup_consensus_monitoring --test-system

echo.
echo ======================================
echo Demo Complete!
echo ======================================
echo.
echo Your consensus system is processing:
echo   - 24 raw marketplace listings
echo   - 9 consensus fitments generated
echo   - 33.3%% production-ready data
echo   - 2 conflicts identified for review
echo.
echo Next steps:
echo   1. Review conflicts manually or auto-resolve simple ones
echo   2. Add more raw data through scraper integration
echo   3. Monitor quality metrics as data grows
echo.
pause
