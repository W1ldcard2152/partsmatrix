#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit  # Exit on error

echo "Starting build process..."

# Install Python dependencies
echo "Installing dependencies..."
pip install -r requirements/prod.txt

# Navigate to Django project directory
cd parts_interchange

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Run database migrations
echo "Running database migrations..."
python manage.py migrate

# Create superuser if it doesn't exist (optional - commented out for security)
# echo "Creating superuser..."
# python manage.py shell -c "
# from django.contrib.auth import get_user_model
# User = get_user_model()
# if not User.objects.filter(username='admin').exists():
#     User.objects.create_superuser('admin', 'admin@example.com', 'your-secure-password')
#     print('Superuser created')
# else:
#     print('Superuser already exists')
# "

# Initialize basic data (optional)
# echo "Initializing basic data..."
# python manage.py init_basic_data || echo "Basic data initialization failed or already exists"

echo "Build completed successfully!"