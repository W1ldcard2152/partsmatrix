@echo off
echo === Testing Improved Acura Parts Import ===

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Change to Django project directory
cd parts_interchange

echo.
echo 🧪 Running DRY RUN first to test parsing...
python manage.py import_acura_parts ..\acura_parts_data.txt --dry-run

echo.
echo ==========================================
set /p continue="Continue with actual import? (y/n): "

if /i "%continue%"=="y" (
    echo.
    echo 🚀 Running actual import...
    python manage.py import_acura_parts ..\acura_parts_data.txt
    
    echo.
    echo 📊 Checking what was created...
    python manage.py shell -c "
from apps.parts.models import Part, Manufacturer
from apps.vehicles.models import Vehicle, Make, Model
from apps.fitments.models import Fitment

print('=== DATABASE STATUS ===')
print(f'Parts: {Part.objects.count()}')
print(f'Vehicles: {Vehicle.objects.count()}')
print(f'Fitments: {Fitment.objects.count()}')
print()

# Show the AC Line part if it exists
ac_line = Part.objects.filter(name__icontains='AC Line').first()
if ac_line:
    print(f'AC Line Part: {ac_line}')
    print(f'Fitments: {ac_line.fitments.count()}')
    for fitment in ac_line.fitments.all()[:5]:
        print(f'  → {fitment.vehicle}')
else:
    print('AC Line part not found')
"
    
    echo.
    echo 🎉 Import completed! Check the results above.
) else (
    echo Import cancelled.
)

echo.
pause
