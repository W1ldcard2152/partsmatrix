#!/bin/bash

# Parts Interchange Database Setup Script
# This script sets up the development environment

echo "=== Parts Interchange Database Setup ==="

# Check if Python 3.8+ is available
python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+')
if (( $(echo "$python_version < 3.8" | bc -l) )); then
    echo "Error: Python 3.8 or higher is required. Current version: $python_version"
    exit 1
fi

echo "✓ Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing Python dependencies..."
if [ -f "requirements/dev.txt" ]; then
    pip install -r requirements/dev.txt
else
    echo "Error: requirements/dev.txt not found"
    exit 1
fi

echo "✓ Dependencies installed"

# Copy environment file if it doesn't exist
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✓ Environment file created from template"
        echo "⚠️  Please edit .env file with your database credentials"
    else
        echo "Warning: .env.example not found"
    fi
else
    echo "✓ Environment file exists"
fi

# Navigate to Django project directory
cd parts_interchange

# Check if PostgreSQL is available
if command -v psql &> /dev/null; then
    echo "✓ PostgreSQL is available"
    
    # Offer to create database
    read -p "Create database 'parts_interchange_db'? (y/n): " create_db
    if [ "$create_db" = "y" ]; then
        createdb parts_interchange_db 2>/dev/null
        if [ $? -eq 0 ]; then
            echo "✓ Database created"
        else
            echo "⚠️  Database might already exist or creation failed"
        fi
    fi
else
    echo "⚠️  PostgreSQL not found. Please install PostgreSQL first."
    echo "   Ubuntu/Debian: sudo apt install postgresql postgresql-contrib"
    echo "   macOS: brew install postgresql"
    echo "   Windows: Download from https://www.postgresql.org/download/"
fi

# Run Django migrations
echo "Running database migrations..."
python manage.py makemigrations
python manage.py migrate

if [ $? -eq 0 ]; then
    echo "✓ Database migrations completed"
else
    echo "⚠️  Migration failed. Please check database connection."
fi

# Create superuser
read -p "Create Django superuser? (y/n): " create_superuser
if [ "$create_superuser" = "y" ]; then
    python manage.py createsuperuser
fi

# Initialize basic data
read -p "Initialize basic data (manufacturers, categories)? (y/n): " init_data
if [ "$init_data" = "y" ]; then
    python manage.py init_basic_data
    echo "✓ Basic data initialized"
fi

# Generate sample data
read -p "Generate and import sample data? (y/n): " sample_data
if [ "$sample_data" = "y" ]; then
    cd ../scripts
    python generate_sample_data.py
    cd ../parts_interchange
    
    # Import sample data
    python manage.py import_csv ../scripts/sample_parts.csv --type parts
    python manage.py import_csv ../scripts/sample_vehicles.csv --type vehicles
    python manage.py import_csv ../scripts/sample_fitments.csv --type fitments
    
    echo "✓ Sample data imported"
fi

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "To start the development server:"
echo "  cd parts_interchange"
echo "  source ../venv/bin/activate"
echo "  python manage.py runserver"
echo ""
echo "Then visit:"
echo "  http://localhost:8000/           - Home page"
echo "  http://localhost:8000/admin/     - Admin interface"
echo "  http://localhost:8000/api/       - API endpoints"
echo ""
echo "API Documentation available at: http://localhost:8000/api/"
