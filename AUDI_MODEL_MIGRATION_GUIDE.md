# Audi Model Structure Migration Guide

## Overview
This guide helps you migrate from the old structure (where S4, RS7, SQ5 etc. were trims) to the new corrected structure (where they are separate models).

## Problem with Old Structure
- **A4** (model) with **S4** (trim) → S4 couldn't have its own Premium Plus/Prestige options
- **A7** (model) with **RS7** (trim) → RS7 couldn't have multiple trim levels
- **Q5** (model) with **SQ5** (trim) → SQ5 couldn't have its own configurations

## New Corrected Structure
- **A4** (model) → Premium/Premium Plus/Prestige (trims)
- **S4** (separate model) → Premium Plus/Prestige (trims)
- **RS7** (separate model) → Premium Plus/Prestige (trims)
- **SQ5** (separate model) → Premium Plus/Prestige (trims)

## Migration Steps

### Step 1: Backup Your Data
```bash
# Create a backup before making changes
python manage.py dumpdata vehicles > vehicles_backup.json
python manage.py dumpdata fitments > fitments_backup.json
```

### Step 2: Check Existing Data
```bash
# See what Vehicle records currently exist
python manage.py shell
>>> from apps.vehicles.models import Vehicle
>>> Vehicle.objects.filter(make__name='Audi').values('model__name', 'trim__name').distinct()
```

### Step 3: Run the Corrected Commands
```bash
# 1. First, create the corrected trim structure
python manage.py add_audi_trims_corrected --dry-run
python manage.py add_audi_trims_corrected

# 2. Ensure all S/RS models exist (they should from your existing add_audi_models.py)
python manage.py add_audi_models --dry-run
python manage.py add_audi_models

# 3. Create vehicles with the corrected structure
python manage.py create_audi_vehicles_corrected --dry-run
python manage.py create_audi_vehicles_corrected
```

### Step 4: Clean Up Old Incorrect Records (Optional)
If you have existing Vehicle records that need to be updated:

```python
# Django shell script to migrate existing records
from apps.vehicles.models import Vehicle, Model, Trim, Make

# Example: Move S4 from A4 trim to S4 model
audi = Make.objects.get(name='Audi')
a4_model = Model.objects.get(make=audi, name='A4')
s4_model = Model.objects.get(make=audi, name='S4')
s4_trim = Trim.objects.get(name='S4')

# Find vehicles that are A4 model with S4 trim (incorrect structure)
incorrect_s4_vehicles = Vehicle.objects.filter(
    make=audi,
    model=a4_model,
    trim=s4_trim
)

# Move them to S4 model with appropriate trim
for vehicle in incorrect_s4_vehicles:
    # Determine appropriate trim for the S4 model
    new_trim = Trim.objects.get(name='Premium Plus')  # or 'Prestige'
    
    # Update or create new vehicle record
    Vehicle.objects.get_or_create(
        year=vehicle.year,
        make=audi,
        model=s4_model,
        generation=vehicle.generation,
        trim=new_trim,
        engine=vehicle.engine,
        defaults={
            'transmission_type': vehicle.transmission_type,
            'drivetrain': vehicle.drivetrain,
            'is_active': vehicle.is_active,
            'notes': vehicle.notes
        }
    )

# Delete the old incorrect records
incorrect_s4_vehicles.delete()
```

### Step 5: Update Fitment Records
If you have existing Fitment records, you may need to update them:

```python
from apps.fitments.models import Fitment

# Example: Update fitments that were pointing to A4+S4 trim to point to S4 model
s4_fitments = Fitment.objects.filter(
    vehicle__make__name='Audi',
    vehicle__model__name='A4',
    vehicle__trim__name='S4'
)

# Update each fitment to point to the S4 model instead
for fitment in s4_fitments:
    # Find the equivalent S4 model vehicle
    s4_vehicle = Vehicle.objects.get(
        year=fitment.vehicle.year,
        make__name='Audi',
        model__name='S4',
        generation=fitment.vehicle.generation,
        engine=fitment.vehicle.engine
    )
    
    # Update the fitment
    fitment.vehicle = s4_vehicle
    fitment.save()
```

### Step 6: Verification
```python
# Verify the migration worked correctly
from apps.vehicles.models import Vehicle

# Check that S4 is now a separate model with its own trims
s4_vehicles = Vehicle.objects.filter(
    make__name='Audi',
    model__name='S4'
).values('year', 'trim__name', 'engine__name')

print("S4 Vehicles (should have Premium Plus/Prestige trims):")
for v in s4_vehicles:
    print(f"  {v['year']} S4 {v['trim__name']} {v['engine__name']}")

# Check that A4 no longer has S4 as a trim
a4_with_s4_trim = Vehicle.objects.filter(
    make__name='Audi',
    model__name='A4',
    trim__name='S4'
)
print(f"A4 vehicles with S4 trim (should be 0): {a4_with_s4_trim.count()}")
```

## Models That Need Migration

### Performance Models Now Separate:
- **S3** (was A3 trim) → Now separate model
- **RS3** (was A3 trim) → Now separate model  
- **S4** (was A4 trim) → Now separate model
- **S5** (was A5 trim) → Now separate model
- **RS5** (was A5 trim) → Now separate model
- **S6** (was A6 trim) → Now separate model
- **S7** (was A7 trim) → Now separate model
- **RS7** (was A7 trim) → Now separate model
- **S8** (was A8 trim) → Now separate model
- **SQ5** (was Q5 trim) → Now separate model
- **SQ7** (was Q7 trim) → Now separate model
- **SQ8** (was Q8 trim) → Now separate model
- **RSQ8** (was Q8 trim) → Now separate model
- **TTS** (was TT trim) → Now separate model
- **TT RS** (was TT trim) → Now separate model

### Trim Structure for Each Model Type:

**A-Models (A3, A4, A5, A6, A7, A8):**
- Premium
- Premium Plus  
- Prestige
- Engine designations (30 TFSI, 35 TFSI, 40 TFSI, 45 TFSI, 50 TFSI, 55 TFSI)

**S-Models (S3, S4, S5, S6, S7, S8):**
- Premium Plus
- Prestige
- Special packages (Competition, Dynamic, Black Edition)

**Q-Models (Q3, Q5, Q7, Q8):**
- Premium
- Premium Plus
- Prestige
- Hybrid trims (50 TFSI e, 55 TFSI e)

**SQ-Models (SQ5, SQ7, SQ8):**
- Premium Plus
- Prestige
- Performance packages

**RS-Models (RS3, RS5, RS6, RS7, RSQ8):**
- Premium Plus
- Prestige  
- Competition
- Performance

**TT Models:**
- TT: Base, Sport, Competition
- TTS: Premium Plus, Prestige
- TT RS: Premium Plus, Prestige

**R8 Models:**
- V8, V10, V10 Plus, Performance, Decennium

## Benefits of New Structure

### 1. **Accurate Parts Fitment**
```
OLD: Part fits "A4 with S4 trim" (confusing)
NEW: Part fits "S4 model" (clear)
```

### 2. **Better Inventory Management**
```
OLD: A4 parts mixed with S4 parts
NEW: S4 parts clearly separated from A4 parts
```

### 3. **Improved Customer Experience**
```
OLD: Customer searches for "S4" but finds it under A4 trims
NEW: Customer searches for "S4" and finds dedicated S4 model
```

### 4. **Database Queries**
```python
# OLD (confusing):
Vehicle.objects.filter(model__name='A4', trim__name='S4')

# NEW (clear):
Vehicle.objects.filter(model__name='S4')
```

### 5. **Reporting and Analytics**
```
OLD: S4 sales mixed with A4 data
NEW: S4 gets its own sales tracking and analysis
```

## Testing Your Migration

### 1. Test Vehicle Creation
```bash
# Should create S4 as separate model with Premium Plus trim
python manage.py create_audi_vehicles_corrected --models "S4" --years "2020-2022" --dry-run
```

### 2. Test Admin Interface
- Go to Django Admin → Vehicles → Vehicle
- Filter by Make: Audi, Model: S4
- Should see S4 vehicles with Premium Plus/Prestige trims

### 3. Test API Queries
```bash
# Should return S4 as separate model
curl http://localhost:8000/api/vehicles/?make__name=Audi&model__name=S4
```

### 4. Test Parts Fitment
```python
# Should be able to create fitments specifically for S4 model
from apps.fitments.models import Fitment
from apps.vehicles.models import Vehicle
from apps.parts.models import Part

s4_vehicle = Vehicle.objects.filter(model__name='S4').first()
some_part = Part.objects.first()

fitment = Fitment.objects.create(
    part=some_part,
    vehicle=s4_vehicle,
    notes="Fits S4 model specifically"
)
```

## Troubleshooting

### Problem: "Model 'S4' not found"
**Solution:** Run `python manage.py add_audi_models` first to ensure all S/RS models exist

### Problem: "Trim 'Premium Plus' not found"  
**Solution:** Run `python manage.py add_audi_trims_corrected` to create proper trim structure

### Problem: Duplicate vehicle records
**Solution:** Check for existing records and use `get_or_create()` instead of `create()`

### Problem: Fitments pointing to wrong vehicles
**Solution:** Run the fitment migration script in Step 5 above

## Rollback Plan

If you need to rollback:

```bash
# Restore from backup
python manage.py loaddata vehicles_backup.json
python manage.py loaddata fitments_backup.json
```

## Final Checklist

- [ ] Backup created
- [ ] Corrected trims added
- [ ] S/RS models exist as separate models  
- [ ] Vehicles created with correct model/trim structure
- [ ] Old incorrect records cleaned up
- [ ] Fitments updated to point to correct models
- [ ] Admin interface tested
- [ ] API queries tested
- [ ] Parts fitment tested

---

**Result:** You now have a clean, logical structure where:
- **A4 Premium Plus** = A4 model with Premium Plus trim
- **S4 Prestige** = S4 model with Prestige trim  
- **RS7 Premium Plus** = RS7 model with Premium Plus trim

This makes much more sense for parts fitment, inventory management, and customer experience!
