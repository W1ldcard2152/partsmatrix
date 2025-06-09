@echo off
echo === Testing Acura Parts Import ===

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the test
python test_acura_import.py

pause
