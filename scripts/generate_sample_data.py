#!/usr/bin/env python3
"""
Generate sample CSV files for testing the parts interchange database
"""

import csv
import os
from datetime import datetime


def create_sample_manufacturers_csv():
    """Create sample manufacturers CSV"""
    data = [
        ['manufacturer', 'manufacturer_name', 'part_number', 'name', 'category', 'description', 'weight', 'dimensions'],
        ['GM', 'General Motors', '12345678', 'LS1 Long Block Engine', 'Engine', 'Complete LS1 5.7L V8 Engine Assembly', '450.0', '30x25x28'],
        ['GM', 'General Motors', '12345679', 'LS1 Short Block', 'Engine', 'LS1 5.7L Short Block without heads', '350.0', '30x25x20'],
        ['GM', 'General Motors', '12345680', 'LS1 Cylinder Head - Left', 'Engine', 'LS1 Left Side Cylinder Head', '45.0', '15x8x6'],
        ['GM', 'General Motors', '12345681', 'LS1 Cylinder Head - Right', 'Engine', 'LS1 Right Side Cylinder Head', '45.0', '15x8x6'],
        ['GM', 'General Motors', '24237113', '4L60E Transmission', 'Transmission', '4L60E 4-Speed Automatic Transmission', '180.0', '36x18x14'],
        ['GM', 'General Motors', '12341234', 'T56 Manual Transmission', 'Transmission', 'T56 6-Speed Manual Transmission', '125.0', '24x16x14'],
        ['FORD', 'Ford Motor Company', 'F150-302', '5.0L Windsor Block', 'Engine', 'Ford 302 Windsor Small Block', '400.0', '28x22x24'],
        ['FORD', 'Ford Motor Company', 'F150-351', '351W Long Block', 'Engine', 'Ford 351 Windsor Complete Engine', '480.0', '30x24x28'],
        ['FORD', 'Ford Motor Company', 'C4-AUTO', 'C4 Automatic', 'Transmission', 'Ford C4 3-Speed Automatic', '130.0', '28x16x12'],
        ['CHRYSLER', 'Chrysler Corporation', '318-BLOCK', '318 LA Small Block', 'Engine', 'Chrysler 318 LA Engine Block', '380.0', '28x22x24'],
        ['CHRYSLER', 'Chrysler Corporation', '340-HEAD', '340 Cylinder Head', 'Engine', 'Chrysler 340 Cylinder Head', '55.0', '16x9x7'],
        ['TOYOTA', 'Toyota Motor Corporation', '2JZ-ENGINE', '2JZ-GTE Engine', 'Engine', 'Toyota 2JZ-GTE Twin Turbo Inline-6', '320.0', '26x20x22'],
        ['HONDA', 'Honda Motor Company', 'B18C-TYPE-R', 'B18C Type-R Engine', 'Engine', 'Honda B18C Type-R VTEC Engine', '280.0', '24x18x20'],
    ]
    
    with open('sample_parts.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(data)
    
    print("Created sample_parts.csv")


def create_sample_vehicles_csv():
    """Create sample vehicles CSV"""
    data = [
        ['year', 'make', 'model', 'trim', 'engine', 'body_style', 'transmission_type', 'drivetrain', 'displacement', 'cylinders', 'fuel_type', 'engine_code'],
        [1997, 'Chevrolet', 'Camaro', 'Z28', 'LS1 5.7L V8', 'Coupe', 'AUTO', 'RWD', 5.7, 8, 'GAS', 'LS1'],
        [1998, 'Chevrolet', 'Camaro', 'Z28', 'LS1 5.7L V8', 'Coupe', 'AUTO', 'RWD', 5.7, 8, 'GAS', 'LS1'],
        [1998, 'Chevrolet', 'Camaro', 'Z28', 'LS1 5.7L V8', 'Coupe', 'MANUAL', 'RWD', 5.7, 8, 'GAS', 'LS1'],
        [1999, 'Chevrolet', 'Camaro', 'Z28', 'LS1 5.7L V8', 'Coupe', 'AUTO', 'RWD', 5.7, 8, 'GAS', 'LS1'],
        [1999, 'Chevrolet', 'Camaro', 'Z28', 'LS1 5.7L V8', 'Coupe', 'MANUAL', 'RWD', 5.7, 8, 'GAS', 'LS1'],
        [2000, 'Chevrolet', 'Camaro', 'Z28', 'LS1 5.7L V8', 'Coupe', 'AUTO', 'RWD', 5.7, 8, 'GAS', 'LS1'],
        [2001, 'Chevrolet', 'Camaro', 'Z28', 'LS1 5.7L V8', 'Coupe', 'AUTO', 'RWD', 5.7, 8, 'GAS', 'LS1'],
        [2002, 'Chevrolet', 'Camaro', 'Z28', 'LS1 5.7L V8', 'Coupe', 'AUTO', 'RWD', 5.7, 8, 'GAS', 'LS1'],
        [1997, 'Chevrolet', 'Corvette', 'Base', 'LS1 5.7L V8', 'Coupe', 'AUTO', 'RWD', 5.7, 8, 'GAS', 'LS1'],
        [1998, 'Chevrolet', 'Corvette', 'Base', 'LS1 5.7L V8', 'Coupe', 'MANUAL', 'RWD', 5.7, 8, 'GAS', 'LS1'],
        [1999, 'Chevrolet', 'Corvette', 'Base', 'LS1 5.7L V8', 'Coupe', 'AUTO', 'RWD', 5.7, 8, 'GAS', 'LS1'],
        [1985, 'Ford', 'Mustang', 'GT', '5.0L Windsor V8', 'Coupe', 'AUTO', 'RWD', 5.0, 8, 'GAS', '302W'],
        [1986, 'Ford', 'Mustang', 'GT', '5.0L Windsor V8', 'Coupe', 'MANUAL', 'RWD', 5.0, 8, 'GAS', '302W'],
        [1987, 'Ford', 'Mustang', 'GT', '5.0L Windsor V8', 'Coupe', 'AUTO', 'RWD', 5.0, 8, 'GAS', '302W'],
        [1970, 'Plymouth', 'Cuda', '340', '340 LA V8', 'Coupe', 'MANUAL', 'RWD', 5.6, 8, 'GAS', '340LA'],
        [1993, 'Toyota', 'Supra', 'Turbo', '2JZ-GTE I6', 'Coupe', 'MANUAL', 'RWD', 3.0, 6, 'GAS', '2JZ-GTE'],
        [1994, 'Toyota', 'Supra', 'Turbo', '2JZ-GTE I6', 'Coupe', 'AUTO', 'RWD', 3.0, 6, 'GAS', '2JZ-GTE'],
        [1997, 'Honda', 'Civic', 'Type-R', 'B18C I4', 'Coupe', 'MANUAL', 'FWD', 1.8, 4, 'GAS', 'B18C'],
    ]
    
    with open('sample_vehicles.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(data)
    
    print("Created sample_vehicles.csv")


def create_sample_fitments_csv():
    """Create sample fitments CSV"""
    data = [
        ['part_manufacturer', 'part_number', 'vehicle_year', 'vehicle_make', 'vehicle_model', 'vehicle_trim', 'vehicle_engine', 'position', 'quantity', 'notes', 'is_verified'],
        # LS1 Engine fitments
        ['GM', '12345678', 1997, 'Chevrolet', 'Camaro', 'Z28', 'LS1 5.7L V8', '', 1, 'Complete engine assembly', True],
        ['GM', '12345678', 1998, 'Chevrolet', 'Camaro', 'Z28', 'LS1 5.7L V8', '', 1, 'Complete engine assembly', True],
        ['GM', '12345678', 1999, 'Chevrolet', 'Camaro', 'Z28', 'LS1 5.7L V8', '', 1, 'Complete engine assembly', True],
        ['GM', '12345678', 1997, 'Chevrolet', 'Corvette', 'Base', 'LS1 5.7L V8', '', 1, 'Complete engine assembly', True],
        ['GM', '12345678', 1998, 'Chevrolet', 'Corvette', 'Base', 'LS1 5.7L V8', '', 1, 'Complete engine assembly', True],
        
        # LS1 Cylinder Heads
        ['GM', '12345680', 1997, 'Chevrolet', 'Camaro', 'Z28', 'LS1 5.7L V8', 'Left', 1, 'Driver side cylinder head', True],
        ['GM', '12345681', 1997, 'Chevrolet', 'Camaro', 'Z28', 'LS1 5.7L V8', 'Right', 1, 'Passenger side cylinder head', True],
        ['GM', '12345680', 1998, 'Chevrolet', 'Camaro', 'Z28', 'LS1 5.7L V8', 'Left', 1, 'Driver side cylinder head', True],
        ['GM', '12345681', 1998, 'Chevrolet', 'Camaro', 'Z28', 'LS1 5.7L V8', 'Right', 1, 'Passenger side cylinder head', True],
        
        # Transmissions
        ['GM', '24237113', 1997, 'Chevrolet', 'Camaro', 'Z28', 'LS1 5.7L V8', '', 1, 'Automatic transmission for LS1', True],
        ['GM', '12341234', 1998, 'Chevrolet', 'Camaro', 'Z28', 'LS1 5.7L V8', '', 1, 'Manual transmission for LS1', True],
        ['GM', '12341234', 1999, 'Chevrolet', 'Camaro', 'Z28', 'LS1 5.7L V8', '', 1, 'Manual transmission for LS1', True],
        
        # Ford parts
        ['FORD', 'F150-302', 1985, 'Ford', 'Mustang', 'GT', '5.0L Windsor V8', '', 1, '302 Windsor engine block', True],
        ['FORD', 'F150-302', 1986, 'Ford', 'Mustang', 'GT', '5.0L Windsor V8', '', 1, '302 Windsor engine block', True],
        ['FORD', 'C4-AUTO', 1985, 'Ford', 'Mustang', 'GT', '5.0L Windsor V8', '', 1, 'C4 automatic transmission', True],
        
        # Chrysler parts
        ['CHRYSLER', '318-BLOCK', 1970, 'Plymouth', 'Cuda', '340', '340 LA V8', '', 1, '318 LA engine block', True],
        ['CHRYSLER', '340-HEAD', 1970, 'Plymouth', 'Cuda', '340', '340 LA V8', 'Left', 1, '340 cylinder head', True],
        ['CHRYSLER', '340-HEAD', 1970, 'Plymouth', 'Cuda', '340', '340 LA V8', 'Right', 1, '340 cylinder head', True],
        
        # Import parts
        ['TOYOTA', '2JZ-ENGINE', 1993, 'Toyota', 'Supra', 'Turbo', '2JZ-GTE I6', '', 1, '2JZ-GTE twin turbo engine', True],
        ['TOYOTA', '2JZ-ENGINE', 1994, 'Toyota', 'Supra', 'Turbo', '2JZ-GTE I6', '', 1, '2JZ-GTE twin turbo engine', True],
        ['HONDA', 'B18C-TYPE-R', 1997, 'Honda', 'Civic', 'Type-R', 'B18C I4', '', 1, 'B18C Type-R VTEC engine', True],
    ]
    
    with open('sample_fitments.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(data)
    
    print("Created sample_fitments.csv")


def create_readme():
    """Create README with import instructions"""
    readme_content = """# Sample Data for Parts Interchange Database

This directory contains sample CSV files for testing the parts interchange database.

## Files Generated:
- `sample_parts.csv` - Sample automotive parts
- `sample_vehicles.csv` - Sample vehicles with specifications
- `sample_fitments.csv` - Sample part-to-vehicle fitment relationships

## Usage:

1. First, initialize the database with basic data:
```bash
python manage.py init_basic_data
```

2. Import parts:
```bash
python manage.py import_csv sample_parts.csv --type parts
```

3. Import vehicles:
```bash
python manage.py import_csv sample_vehicles.csv --type vehicles
```

4. Import fitments:
```bash
python manage.py import_csv sample_fitments.csv --type fitments
```

## Test with dry run first:
```bash
python manage.py import_csv sample_parts.csv --type parts --dry-run
```

## CSV Column Requirements:

### Parts CSV:
- manufacturer (required)
- part_number (required)
- name (required)
- category (required)
- description (optional)
- weight (optional)
- dimensions (optional)

### Vehicles CSV:
- year (required)
- make (required)
- model (required)
- trim (optional)
- engine (optional)
- body_style (optional)
- transmission_type (optional)
- drivetrain (optional)

### Fitments CSV:
- part_manufacturer (required)
- part_number (required)
- vehicle_year (required)
- vehicle_make (required)
- vehicle_model (required)
- vehicle_trim (optional)
- vehicle_engine (optional)
- position (optional)
- quantity (optional)
- notes (optional)
- is_verified (optional)
"""
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("Created README.md")


def main():
    print("Generating sample CSV files for Parts Interchange Database...")
    
    create_sample_manufacturers_csv()
    create_sample_vehicles_csv()
    create_sample_fitments_csv()
    create_readme()
    
    print("\nSample files created successfully!")
    print("Run the following commands to import the data:")
    print("1. python manage.py init_basic_data")
    print("2. python manage.py import_csv sample_parts.csv --type parts")
    print("3. python manage.py import_csv sample_vehicles.csv --type vehicles")
    print("4. python manage.py import_csv sample_fitments.csv --type fitments")


if __name__ == "__main__":
    main()
