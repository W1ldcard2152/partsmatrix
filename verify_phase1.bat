@echo off
echo ================================================================
echo CONSENSUS-BASED FITMENT SYSTEM - PHASE 1 VERIFICATION
echo ================================================================
echo.

cd /d "C:\Users\Wildc\Documents\Programming\Parts Matrix"

echo Step 1: Activating virtual environment...
call "venv\Scripts\activate.bat"

echo.
echo Step 2: Creating migrations for consensus models...
python manage.py makemigrations parts --name="add_consensus_fitment_models"

echo.
echo Step 3: Applying migrations...
python manage.py migrate

echo.
echo Step 4: Testing consensus models...
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parts_interchange.settings')
import django
django.setup()
from apps.parts.models import RawListingData, ConsensusFitment, ConflictingFitment
print('✓ All consensus models imported successfully!')
print(f'RawListingData table: {RawListingData._meta.db_table}')
print(f'ConsensusFitment table: {ConsensusFitment._meta.db_table}')
print(f'ConflictingFitment table: {ConflictingFitment._meta.db_table}')
"

echo.
echo Step 5: Testing management command...
python manage.py process_consensus_fitments --stats-only

echo.
echo ================================================================
echo PHASE 1 VERIFICATION COMPLETE!
echo ================================================================
pause
