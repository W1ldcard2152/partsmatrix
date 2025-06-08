@echo off
echo === Parts Interchange Database - Starting with Render ===

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo ✅ Connected to Render PostgreSQL successfully!
echo Database: parts_interchange_db
echo Host: dpg-d0oipuemcj7s73d7fvr0-a.ohio-postgres.render.com

REM Stay in root directory where manage.py is located
echo.
echo Running Django setup from root directory...

REM Run migrations
echo 📊 Running database migrations...
python manage.py migrate

if errorlevel 1 (
    echo ❌ Migration failed
    pause
    exit /b 1
)

echo ✅ Migrations completed successfully!

REM Check if we need basic data
echo.
set /p init_data="Initialize basic data (manufacturers, categories)? (y/n): "
if /i "%init_data%"=="y" (
    echo 📦 Initializing basic data...
    python manage.py init_basic_data
    echo ✅ Basic data initialized
)

REM Offer to create superuser
echo.
set /p create_superuser="Create Django superuser for admin access? (y/n): "
if /i "%create_superuser%"=="y" (
    echo 👤 Creating superuser...
    python manage.py createsuperuser
    echo ✅ Superuser created
)

echo.
echo 🚀 === READY TO LAUNCH! ===
echo.
echo Your Parts Interchange Database is ready!
echo.
echo To start the server:
echo   python manage.py runserver
echo.
echo Then visit:
echo   http://localhost:8000/           - Home page
echo   http://localhost:8000/admin/     - Admin interface (if superuser created)
echo   http://localhost:8000/api/       - API endpoints
echo.
echo 📊 Database: Render PostgreSQL (parts_interchange_db)
echo 🔒 Secure cloud hosting with remote access
echo 💰 Cost: $7/month for professional-grade database
echo.
pause
