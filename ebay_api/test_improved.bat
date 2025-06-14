@echo off
echo Testing Improved eBay Extractor Patterns
echo =========================================

cd /d "C:\Users\Wildc\Documents\Programming\Parts Matrix"
call venv\Scripts\activate.bat
cd ebay_api

echo.
echo Testing improved pattern extraction...
python test_improved_patterns.py

echo.
echo =========================================
echo Pattern test complete!
echo.
echo You can now run the original test with:
echo   python test_extractor.py
echo.
pause
