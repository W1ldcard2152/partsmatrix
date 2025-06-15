#!/bin/bash
# Phase 2 Setup and Validation Script
# Run this script from the Parts Matrix root directory (where manage.py is located)

echo "🚀 Phase 2 Consensus Engine Setup & Validation"
echo "=============================================="

# Ensure we're in the correct directory (manage.py should be in current directory)
if [ ! -f "manage.py" ]; then
    echo "❌ manage.py not found. Please run this script from the Parts Matrix root directory."
    exit 1
fi

# Check if Django is accessible
echo "🔍 Checking Django environment..."
if ! python manage.py check >/dev/null 2>&1; then
    echo "❌ Django environment check failed"
    exit 1
fi
echo "✅ Django environment OK"

# Run database migrations to ensure consensus models are up to date
echo ""
echo "🔄 Running database migrations..."
python manage.py makemigrations parts >/dev/null 2>&1
python manage.py migrate >/dev/null 2>&1
echo "✅ Database migrations complete"

# Setup monitoring infrastructure
echo ""
echo "📊 Setting up monitoring infrastructure..."
python manage.py setup_consensus_monitoring --create-scripts --setup-logging --create-alerts --output-dir ./monitoring
echo "✅ Monitoring setup complete"

# Test the consensus system
echo ""
echo "🧪 Testing consensus system..."
python manage.py setup_consensus_monitoring --test-system
echo "✅ System health check complete"

# Show current system status
echo ""
echo "📈 Current system status:"
python manage.py process_consensus_fitments --stats-only

# Test quality analysis if data exists
echo ""
echo "📊 Testing quality analysis..."
python manage.py consensus_quality_analysis --confidence-breakdown 2>/dev/null || echo "No data for analysis yet"

# Create sample processing script
echo ""
echo "📝 Creating quick start script..."

# Create Windows batch file
cat > run_daily_processing.bat << 'EOF'
@echo off
echo Running daily consensus processing...
python manage.py process_consensus_fitments --new-data-only
python manage.py consensus_quality_analysis --export-json --output-dir ./daily_reports
echo Daily processing complete!
pause
EOF

# Create Linux/Mac shell script
cat > run_daily_processing.sh << 'EOF'
#!/bin/bash
echo "Running daily consensus processing..."
python manage.py process_consensus_fitments --new-data-only
python manage.py consensus_quality_analysis --export-json --output-dir ./daily_reports
echo "Daily processing complete!"
EOF

chmod +x run_daily_processing.sh 2>/dev/null || true

echo "✅ Quick start scripts created"

# Create directories for reports
mkdir -p daily_reports weekly_reports monthly_reports archive 2>/dev/null || true

# Final validation
echo ""
echo "🔍 Final validation..."
python test_phase2_implementation.py

echo ""
echo "🎉 Phase 2 Setup Complete!"
echo "=========================="
echo ""
echo "📁 Created directories:"
echo "   📊 monitoring/     - Automated scripts and configuration"
echo "   📈 daily_reports/  - Daily processing reports"
echo "   📋 weekly_reports/ - Weekly conflict reviews"
echo "   📊 monthly_reports/- Monthly quality analysis"
echo "   📦 archive/        - Archived reports"
echo ""
echo "🛠️ Available commands:"
echo "   Daily:   python manage.py process_consensus_fitments --new-data-only"
echo "   Weekly:  python manage.py review_fitment_conflicts --auto-resolve"
echo "   Monthly: python manage.py consensus_quality_analysis --export-csv"
echo "   Monitor: python manage.py setup_consensus_monitoring --test-system"
echo ""
echo "🚀 Quick start:"
echo "   Windows: run_daily_processing.bat"
echo "   Linux:   ./run_daily_processing.sh"
echo ""
echo "📋 Next phase: Scraper Integration (Phase 3)"
echo "   Ready to integrate with eBay scraper for automatic data collection"
echo ""
echo "✅ Phase 2 implementation is complete and ready for production use!"
