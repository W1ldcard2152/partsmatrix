@echo off
REM Simple script to run the migration fix

echo === Parts Matrix Migration Fix ===
echo.

cd /d "C:\Users\Wildc\Documents\Programming\Parts Matrix"

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Run the migration fix
echo Running migration fix script...
python fix_migrations.py

REM Check if successful
if %ERRORLEVEL% EQU 0 (
    echo.
    echo === SUCCESS ===
    echo Migrations completed successfully!
    echo You can now run your Django commands.
) else (
    echo.
    echo === MANUAL FIX NEEDED ===
    echo The automatic fix didn't work. Try these commands:
    echo.
    echo 1. cd parts_interchange
    echo 2. python manage.py migrate --fake parts 0002_add_performance_indexes
    echo 3. python manage.py migrate
)

echo.
pause
