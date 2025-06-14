@echo off
echo Testing Environment Variable Loading
echo ====================================

cd /d "C:\Users\Wildc\Documents\Programming\Parts Matrix"
call venv\Scripts\activate.bat
cd ebay_api

echo.
echo Testing environment variable loading...
python test_env_loading.py

echo.
echo ====================================
if %ERRORLEVEL% EQU 0 (
    echo Environment loading test completed!
    echo.
    echo If EBAY_APP_ID was found, you can now run:
    echo   python test_extractor.py
) else (
    echo Environment loading test failed!
)
echo.
pause
