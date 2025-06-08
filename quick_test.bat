@echo off
echo Parts Interchange Database - Quick Fix and Test
echo ================================================

REM Activate virtual environment
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found at venv\Scripts\activate.bat
    echo Please ensure you're in the correct directory
    pause
    exit /b 1
)

echo.
echo Step 1: Testing Django setup and imports...
python verify_setup.py

if errorlevel 1 (
    echo.
    echo ❌ Setup verification failed!
    echo Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo Step 2: Testing database connection...
cd parts_interchange
python manage.py test_db

if errorlevel 1 (
    echo.
    echo ❌ Database connection failed!
    echo Trying to run migrations...
    python manage.py migrate
)

echo.
echo Step 3: Running Django system check...
python manage.py check

if errorlevel 1 (
    echo.
    echo ❌ Django system check failed!
    pause
    exit /b 1
)

echo.
echo ✅ All tests passed! You can now run the server.
echo.
echo To start the development server:
echo   python manage.py runserver
echo.
echo Then visit: http://localhost:8000/
echo.
pause
