@echo off
echo === Setting up Local PostgreSQL Database ===

REM Check if PostgreSQL is available
psql --version >nul 2>&1
if errorlevel 1 (
    echo ❌ PostgreSQL not found. Please install PostgreSQL first.
    echo    Download from: https://www.postgresql.org/download/windows/
    pause
    exit /b 1
)

echo ✅ PostgreSQL is available

REM Create database
echo Creating database 'parts_interchange_db'...
createdb -U postgres parts_interchange_db 2>nul
if errorlevel 1 (
    echo ⚠️  Database might already exist or creation failed
    echo    This is OK if the database already exists
) else (
    echo ✅ Database created successfully
)

echo.
echo === Database Setup Complete! ===
echo.
echo Your local database is ready. You can now run:
echo   python manage.py migrate
echo   python manage.py runserver
echo.
pause
