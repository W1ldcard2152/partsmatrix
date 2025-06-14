@echo off
echo Testing eBay Extractor Django Import Fix
echo ========================================

cd /d "C:\Users\Wildc\Documents\Programming\Parts Matrix\ebay_api"

echo.
echo Running Django import test...
python test_django_import.py

echo.
echo =========================================
echo If the Django import test passed, you can now run:
echo python test_extractor.py
echo.
pause
