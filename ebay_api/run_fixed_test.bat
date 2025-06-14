@echo off
echo eBay Extractor - Fix and Test Script
echo ====================================

cd /d "C:\Users\Wildc\Documents\Programming\Parts Matrix"

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Changing to eBay API directory...
cd ebay_api

echo.
echo Running comprehensive test...
python comprehensive_test.py

echo.
echo ====================================
echo Test complete!
echo.
echo If all tests passed, you can now run:
echo   python test_extractor.py
echo   python ebay_parts_extractor.py
echo.
pause
