@echo off
echo === Testing Smart Parser Setup ===

set PYTHONPATH=%PYTHONPATH%;%CD%

REM Make sure we have categories
echo Checking for A/C categories...
python manage.py shell -c "from apps.parts.models import PartCategory; print('A/C Categories:', [c.name for c in PartCategory.objects.filter(name__icontains='A/C')])"

REM Make sure we have Acura manufacturer
echo Checking for Acura manufacturer...
python manage.py shell -c "from apps.parts.models import Manufacturer; print('Acura:', Manufacturer.objects.filter(name__icontains='Acura').exists())"

REM Start the server
echo.
echo Starting Django server...
echo Visit: http://localhost:8000/smart-parser/
echo.
python manage.py runserver
