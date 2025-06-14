@echo off
echo eBay Parts Extractor for Acura AC Compressors
echo ============================================
echo.

REM Check if we're in the right directory
if not exist "ebay_parts_extractor.py" (
    echo Error: Please run this from the ebay_api directory
    echo Expected to find ebay_parts_extractor.py
    pause
    exit /b 1
)

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python first.
    pause
    exit /b 1
)

REM Check for .env file
if not exist ".env" (
    echo Warning: .env file not found
    echo Please create .env file with your EBAY_APP_ID
    echo You can copy .env.example and modify it
    echo.
)

REM Check environment variable
if "%EBAY_APP_ID%"=="" (
    echo Error: EBAY_APP_ID environment variable not set
    echo.
    echo Please either:
    echo 1. Set environment variable: set EBAY_APP_ID=your-app-id-here
    echo 2. Create .env file with: EBAY_APP_ID=your-app-id-here
    echo.
    pause
    exit /b 1
)

echo Starting eBay parts extraction...
echo Using App ID: %EBAY_APP_ID:~0,10%...
echo.

REM Run the extractor
python ebay_parts_extractor.py

echo.
echo Extraction complete!
echo Check the generated JSON and CSV files for results.
echo.
pause
