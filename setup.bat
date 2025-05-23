@echo off
REM Parts Interchange Database Setup Script for Windows
REM This script sets up the development environment

echo === Parts Interchange Database Setup ===

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✓ Python is available

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo ✓ Virtual environment created
) else (
    echo ✓ Virtual environment exists
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo Installing Python dependencies...
if exist "requirements\dev.txt" (
    pip install -r requirements\dev.txt
    echo ✓ Dependencies installed
) else (
    echo Error: requirements\dev.txt not found
    pause
    exit /b 1
)

REM Copy environment file if it doesn't exist
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env"
        echo ✓ Environment file created from template
        echo ⚠️  Please edit .env file with your database credentials
    ) else (
        echo Warning: .env.example not found
    )
) else (
    echo ✓ Environment file exists
)

REM Navigate to Django project directory
cd parts_interchange

REM Check if PostgreSQL is available
psql --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  PostgreSQL not found. Please install PostgreSQL first.
    echo   Download from: https://www.postgresql.org/download/windows/
) else (
    echo ✓ PostgreSQL is available
    
    REM Offer to create database
    set /p create_db="Create database 'parts_interchange_db'? (y/n): "
    if /i "%create_db%"=="y" (
        createdb parts_interchange_db 2>nul
        if errorlevel 1 (
            echo ⚠️  Database might already exist or creation failed
        ) else (
            echo ✓ Database created
        )
    )
)

REM Run Django migrations
echo Running database migrations...
python manage.py makemigrations
python manage.py migrate

if errorlevel 1 (
    echo ⚠️  Migration failed. Please check database connection.
) else (
    echo ✓ Database migrations completed
)

REM Create superuser
set /p create_superuser="Create Django superuser? (y/n): "
if /i "%create_superuser%"=="y" (
    python manage.py createsuperuser
)

REM Initialize basic data
set /p init_data="Initialize basic data (manufacturers, categories)? (y/n): "
if /i "%init_data%"=="y" (
    python manage.py init_basic_data
    echo ✓ Basic data initialized
)

REM Generate sample data
set /p sample_data="Generate and import sample data? (y/n): "
if /i "%sample_data%"=="y" (
    cd ..\scripts
    python generate_sample_data.py
    cd ..\parts_interchange
    
    REM Import sample data
    python manage.py import_csv ..\scripts\sample_parts.csv --type parts
    python manage.py import_csv ..\scripts\sample_vehicles.csv --type vehicles
    python manage.py import_csv ..\scripts\sample_fitments.csv --type fitments
    
    echo ✓ Sample data imported
)

echo.
echo === Setup Complete! ===
echo.
echo To start the development server:
echo   cd parts_interchange
echo   venv\Scripts\activate.bat
echo   python manage.py runserver
echo.
echo Then visit:
echo   http://localhost:8000/           - Home page
echo   http://localhost:8000/admin/     - Admin interface
echo   http://localhost:8000/api/       - API endpoints
echo.
echo API Documentation available at: http://localhost:8000/api/
echo.
pause
