@echo off
REM Build script for Render deployment (Windows version for local testing)

echo Starting build process...

REM Install Python dependencies
echo Installing dependencies...
pip install -r requirements\prod.txt

REM Navigate to Django project directory
cd parts_interchange

REM Collect static files
echo Collecting static files...
python manage.py collectstatic --no-input

REM Run database migrations
echo Running database migrations...
python manage.py migrate

REM Create superuser if it doesn't exist (optional - commented out for security)
REM echo Creating superuser...
REM python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'your-secure-password') if not User.objects.filter(username='admin').exists() else print('Superuser already exists')"

REM Initialize basic data (optional)
REM echo Initializing basic data...
REM python manage.py init_basic_data 2>nul || echo Basic data initialization failed or already exists

echo Build completed successfully!
pause