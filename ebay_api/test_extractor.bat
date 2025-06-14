@echo off
echo eBay Parts Extractor - Test Suite
echo =================================
echo.

REM Check if we're in the right directory
if not exist "test_extractor.py" (
    echo Error: Please run this from the ebay_api directory
    echo Expected to find test_extractor.py
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

echo Running eBay extractor tests...
echo This will validate your setup before making API calls.
echo.

REM Run the test
python test_extractor.py

echo.
pause
