@echo off
echo ================================================================
echo CONSENSUS-BASED FITMENT SYSTEM - PHASE 1 IMPLEMENTATION
echo ================================================================
echo.
echo This script will:
echo 1. Create database migrations for new consensus models
echo 2. Apply migrations to database
echo 3. Create sample data for testing
echo 4. Test consensus processing
echo 5. Display results
echo.
pause

cd /d "C:\Users\Wildc\Documents\Programming\Parts Matrix\parts_interchange"

echo.
echo Step 1: Activating virtual environment...
call "..\venv\Scripts\activate.bat"

echo.
echo Step 2: Creating migrations for consensus models...
python manage.py makemigrations parts --name="add_consensus_fitment_models"

echo.
echo Step 3: Applying migrations...
python manage.py migrate

echo.
echo Step 4: Creating sample data and testing consensus processing...
python create_sample_consensus_data.py

echo.
echo Step 5: Testing management command...
python manage.py process_consensus_fitments --stats-only

echo.
echo ================================================================
echo PHASE 1 IMPLEMENTATION COMPLETE!
echo ================================================================
echo.
echo You can now:
echo 1. Access Django admin to review consensus fitments
echo 2. Use the management command: python manage.py process_consensus_fitments
echo 3. Begin implementing Phase 2 (API Enhancement)
echo.
echo Admin URL: http://localhost:8000/admin/
echo Admin Models: RawListingData, ConsensusFitment, ConflictingFitment
echo.
pause
