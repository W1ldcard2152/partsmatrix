# Automotive Parts Interchange Database

A comprehensive Django-based system for managing automotive parts fitment data, providing API endpoints for parts interchange lookups.

## 🚀 Features

- **Parts Management**: Store manufacturer part numbers with detailed specifications
- **Vehicle Database**: Year/Make/Model/Trim/Engine format following eBay standards
- **Fitment Relationships**: Link parts to compatible vehicles with precision data
- **Interchange Groups**: Manage functionally equivalent parts across manufacturers
- **RESTful API**: Full API access for external integrations
- **Admin Interface**: Django admin for easy data management
- **Bulk Import**: CSV import capabilities for large datasets

## 🏗️ Architecture

- **Backend**: Django 4.2 with Django REST Framework
- **Database**: PostgreSQL with optimized queries
- **Authentication**: Token-based API authentication
- **Documentation**: Auto-generated API documentation
- **Deployment**: Ready for cloud deployment (Render, Heroku, etc.)

## 📋 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Parts\ Matrix
   ```

2. **Run setup script**
   ```bash
   # Windows
   setup.bat
   
   # Linux/Mac
   ./setup.sh
   ```

3. **Start development server**
   ```bash
   cd parts_interchange
   python manage.py runserver
   ```

4. **Access the application**
   - Home: http://localhost:8000/
   - Admin: http://localhost:8000/admin/
   - API: http://localhost:8000/api/

### Cloud Deployment

For production deployment on Render, see [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) for detailed instructions.

## 🗄️ Database Schema

### Core Models

- **Manufacturer**: GM, Ford, Toyota, etc.
- **PartCategory**: Engine, Transmission, Suspension, etc.
- **Part**: Individual part numbers with specifications
- **Make/Model/Engine/Trim**: Vehicle specifications
- **Vehicle**: Complete vehicle definitions
- **Fitment**: Part-to-vehicle compatibility relationships

### Key Relationships

```
Manufacturer → Parts → Fitments ← Vehicles ← Make/Model/Engine
            ↓
      InterchangeGroups
```

## 🔌 API Endpoints

### Core Resources
- `GET /api/parts/` - List all parts
- `GET /api/vehicles/` - List all vehicles  
- `GET /api/fitments/` - List all fitments
- `GET /api/manufacturers/` - List manufacturers

### Lookup Endpoints
- `GET /api/lookup/part-fitments/{part_id}/` - Get vehicles for a part
- `GET /api/lookup/vehicle-parts/{vehicle_id}/` - Get parts for a vehicle
- `GET /api/lookup/interchange/{part_number}/` - Get interchange parts

### Search Endpoints
- `GET /api/search/parts/?part_number=ABC123` - Search parts
- `GET /api/search/vehicles/?year=2020&make=Ford` - Search vehicles
- `GET /api/search/fitments/?part_number=ABC123` - Search fitments

### Statistics
- `GET /api/stats/` - Database statistics and metrics

## 📊 Sample Data

The system includes sample data generators for testing:

```bash
cd scripts
python generate_sample_data.py
cd ../parts_interchange
python manage.py import_csv ../scripts/sample_parts.csv --type parts
python manage.py import_csv ../scripts/sample_vehicles.csv --type vehicles  
python manage.py import_csv ../scripts/sample_fitments.csv --type fitments
```

## 🔧 Configuration

### Environment Variables

Key configuration options (see `.env.example`):

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/db
# or individual settings
DB_NAME=parts_interchange_db
DB_USER=postgres
DB_PASSWORD=your_password

# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com

# API
CORS_ALLOWED_ORIGINS=https://your-frontend.com
```

### Local Development
- Copy `.env.example` to `.env`
- Update database credentials
- Set `DEBUG=True` for development

### Production Deployment
- Set `DEBUG=False`
- Configure `DATABASE_URL`
- Set proper `ALLOWED_HOSTS`
- Configure static file serving

## 🧪 Testing

Run the test suite:

```bash
cd parts_interchange
python -m pytest
```

With coverage:

```bash
python -m pytest --cov=apps
```

## 📁 Project Structure

```
Parts Matrix/
├── parts_interchange/          # Main Django project
│   ├── apps/                  # Django applications
│   │   ├── api/              # REST API endpoints
│   │   ├── parts/            # Parts management
│   │   ├── vehicles/         # Vehicle management
│   │   └── fitments/         # Fitment relationships
│   ├── parts_interchange/    # Project settings
│   ├── templates/            # HTML templates
│   └── static/              # Static files
├── requirements/             # Python dependencies
├── scripts/                 # Utility scripts
├── build.sh                # Deployment build script
└── README.md               # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📈 Roadmap

- [ ] Advanced search filters
- [ ] Bulk edit capabilities
- [ ] Data validation improvements
- [ ] Performance optimizations
- [ ] Mobile-responsive admin interface
- [ ] Export functionality
- [ ] Integration with external catalogs

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- Check the [deployment guide](RENDER_DEPLOYMENT.md) for setup help
- Review API documentation at `/api/` endpoint
- Open GitHub issues for bugs or feature requests

## 🏷️ Version

Current version: 1.0.0

Built with Django 4.2, PostgreSQL, and Django REST Framework.