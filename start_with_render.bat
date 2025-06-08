@echo off
echo === Parts Interchange Database - Render Connection ===

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Test connection
echo Testing Render database connection...
python test_render_connection.py

if errorlevel 1 (
    echo ❌ Connection test failed
    pause
    exit /b 1
)

echo.
echo ✅ Connection test passed! Starting Django setup...

REM Navigate to Django project
cd parts_interchange

REM Run migrations
echo Running database migrations...
python manage.py migrate

REM Check if we need basic data
echo.
set /p init_data="Initialize basic data (manufacturers, categories)? (y/n): "
if /i "%init_data%"=="y" (
    python manage.py init_basic_data
    echo ✅ Basic data initialized
)

echo.
echo === Ready to start server! ===
echo Run: python manage.py runserver
echo Then visit: http://localhost:8000/
echo.
pause
