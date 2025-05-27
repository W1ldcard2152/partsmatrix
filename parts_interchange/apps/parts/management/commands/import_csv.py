import csv
import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from apps.parts.models import Part, Manufacturer, PartCategory
from apps.vehicles.models import Vehicle, Make, Model, Engine, Trim
from apps.fitments.models import Fitment, FitmentBulkImport
from datetime import datetime


class Command(BaseCommand):
    help = 'Import parts and fitment data from CSV files'

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help='Path to the CSV file to import'
        )
        parser.add_argument(
            '--type',
            type=str,
            choices=['parts', 'vehicles', 'fitments'],
            required=True,
            help='Type of data to import'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Perform a dry run without making changes'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Batch size for bulk operations'
        )

    def handle(self, *args, **options):
        file_path = options['file_path']
        import_type = options['type']
        dry_run = options['dry_run']
        batch_size = options['batch_size']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))

        try:
            df = pd.read_csv(file_path)
            self.stdout.write(f'Loaded {len(df)} records from {file_path}')
        except Exception as e:
            raise CommandError(f'Error reading CSV file: {e}')

        # Create bulk import record
        bulk_import = FitmentBulkImport.objects.create(
            import_name=f'{import_type.title()} Import - {datetime.now().strftime("%Y-%m-%d %H:%M")}',
            description=f'Import {import_type} from {file_path}',
            file_name=file_path,
            total_records=len(df),
            status='PROCESSING'
        )

        try:
            if import_type == 'parts':
                self.import_parts(df, dry_run, batch_size, bulk_import)
            elif import_type == 'vehicles':
                self.import_vehicles(df, dry_run, batch_size, bulk_import)
            elif import_type == 'fitments':
                self.import_fitments(df, dry_run, batch_size, bulk_import)

            bulk_import.status = 'COMPLETED'
            bulk_import.completed_at = datetime.now()
            bulk_import.save()

        except Exception as e:
            bulk_import.status = 'FAILED'
            bulk_import.import_log += f'\nError: {str(e)}'
            bulk_import.save()
            raise CommandError(f'Import failed: {e}')

    def import_parts(self, df, dry_run, batch_size, bulk_import):
        """Import parts from CSV"""
        required_columns = ['manufacturer', 'part_number', 'name', 'category']
        self.validate_columns(df, required_columns)

        successful = 0
        failed = 0
        parts_to_create = []

        for index, row in df.iterrows():
            try:
                # Get or create manufacturer
                manufacturer, _ = Manufacturer.objects.get_or_create(
                    abbreviation=row['manufacturer'].upper(),
                    defaults={'name': row.get('manufacturer_name', row['manufacturer'])}
                )

                # Get or create category
                category, _ = PartCategory.objects.get_or_create(
                    name=row['category']
                )

                # Check if part already exists
                if Part.objects.filter(
                    manufacturer=manufacturer, 
                    part_number=row['part_number']
                ).exists():
                    continue

                part_data = {
                    'manufacturer': manufacturer,
                    'part_number': row['part_number'],
                    'name': row['name'],
                    'category': category,
                    'description': row.get('description', ''),
                    'weight': row.get('weight') if pd.notna(row.get('weight')) else None,
                    'dimensions': row.get('dimensions', ''),
                    'is_active': row.get('is_active', True)
                }

                if not dry_run:
                    parts_to_create.append(Part(**part_data))

                successful += 1

                if len(parts_to_create) >= batch_size:
                    if not dry_run:
                        Part.objects.bulk_create(parts_to_create)
                    parts_to_create = []

            except Exception as e:
                failed += 1
                bulk_import.import_log += f'\nRow {index}: {str(e)}'

        # Create remaining parts
        if parts_to_create and not dry_run:
            Part.objects.bulk_create(parts_to_create)

        bulk_import.successful_imports = successful
        bulk_import.failed_imports = failed
        bulk_import.save()

        self.stdout.write(
            self.style.SUCCESS(
                f'Parts import completed: {successful} successful, {failed} failed'
            )
        )

    def import_vehicles(self, df, dry_run, batch_size, bulk_import):
        """Import vehicles from CSV"""
        required_columns = ['year', 'make', 'model']
        self.validate_columns(df, required_columns)

        successful = 0
        failed = 0

        for index, row in df.iterrows():
            try:
                with transaction.atomic():
                    # Get or create make
                    make, _ = Make.objects.get_or_create(
                        name=row['make']
                    )

                    # Get or create model
                    model, _ = Model.objects.get_or_create(
                        make=make,
                        name=row['model'],
                        defaults={'body_style': row.get('body_style', '')}
                    )

                    # Get or create trim (if specified)
                    trim = None
                    if pd.notna(row.get('trim')):
                        trim, _ = Trim.objects.get_or_create(
                            name=row['trim']
                        )

                    # Get or create engine (if specified)
                    engine = None
                    if pd.notna(row.get('engine')):
                        engine, _ = Engine.objects.get_or_create(
                            name=row['engine'],
                            defaults={
                                'displacement': row.get('displacement'),
                                'cylinders': row.get('cylinders'),
                                'fuel_type': row.get('fuel_type', 'GAS'),
                                'engine_code': row.get('engine_code', '')
                            }
                        )

                    # Check if vehicle already exists
                    if Vehicle.objects.filter(
                        year=row['year'],
                        make=make,
                        model=model,
                        trim=trim,
                        engine=engine
                    ).exists():
                        continue

                    if not dry_run:
                        Vehicle.objects.create(
                            year=row['year'],
                            make=make,
                            model=model,
                            trim=trim,
                            engine=engine,
                            transmission_type=row.get('transmission_type', ''),
                            drivetrain=row.get('drivetrain', ''),
                            notes=row.get('notes', '')
                        )

                    successful += 1

            except Exception as e:
                failed += 1
                bulk_import.import_log += f'\nRow {index}: {str(e)}'

        bulk_import.successful_imports = successful
        bulk_import.failed_imports = failed
        bulk_import.save()

        self.stdout.write(
            self.style.SUCCESS(
                f'Vehicles import completed: {successful} successful, {failed} failed'
            )
        )

    def import_fitments(self, df, dry_run, batch_size, bulk_import):
        """Import fitments from CSV"""
        required_columns = ['part_manufacturer', 'part_number', 'vehicle_year', 'vehicle_make', 'vehicle_model']
        self.validate_columns(df, required_columns)

        successful = 0
        failed = 0
        fitments_to_create = []

        for index, row in df.iterrows():
            try:
                # Find the part
                try:
                    manufacturer = Manufacturer.objects.get(
                        abbreviation=row['part_manufacturer'].upper()
                    )
                    part = Part.objects.get(
                        manufacturer=manufacturer,
                        part_number=row['part_number']
                    )
                except (Manufacturer.DoesNotExist, Part.DoesNotExist):
                    failed += 1
                    bulk_import.import_log += f'\nRow {index}: Part not found'
                    continue

                # Find the vehicle
                try:
                    make = Make.objects.get(name=row['vehicle_make'])
                    model = Model.objects.get(make=make, name=row['vehicle_model'])
                    
                    vehicle_filter = {
                        'year': row['vehicle_year'],
                        'make': make,
                        'model': model
                    }
                    
                    if pd.notna(row.get('vehicle_trim')):
                        trim = Trim.objects.get(name=row['vehicle_trim'])
                        vehicle_filter['trim'] = trim
                    
                    if pd.notna(row.get('vehicle_engine')):
                        engine = Engine.objects.get(name=row['vehicle_engine'])
                        vehicle_filter['engine'] = engine
                    
                    vehicle = Vehicle.objects.get(**vehicle_filter)
                    
                except (Make.DoesNotExist, Model.DoesNotExist, Vehicle.DoesNotExist, Trim.DoesNotExist, Engine.DoesNotExist):
                    failed += 1
                    bulk_import.import_log += f'\nRow {index}: Vehicle not found'
                    continue

                # Check if fitment already exists
                if Fitment.objects.filter(part=part, vehicle=vehicle).exists():
                    continue

                fitment_data = {
                    'part': part,
                    'vehicle': vehicle,
                    'position': row.get('position', ''),
                    'quantity': row.get('quantity', 1),
                    'notes': row.get('notes', ''),
                    'is_verified': row.get('is_verified', False)
                }

                if not dry_run:
                    fitments_to_create.append(Fitment(**fitment_data))

                successful += 1

                if len(fitments_to_create) >= batch_size:
                    if not dry_run:
                        Fitment.objects.bulk_create(fitments_to_create)
                    fitments_to_create = []

            except Exception as e:
                failed += 1
                bulk_import.import_log += f'\nRow {index}: {str(e)}'

        # Create remaining fitments
        if fitments_to_create and not dry_run:
            Fitment.objects.bulk_create(fitments_to_create)

        bulk_import.successful_imports = successful
        bulk_import.failed_imports = failed
        bulk_import.save()

        self.stdout.write(
            self.style.SUCCESS(
                f'Fitments import completed: {successful} successful, {failed} failed'
            )
        )

    def validate_columns(self, df, required_columns):
        """Validate that required columns exist in the DataFrame"""
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise CommandError(f'Missing required columns: {missing_columns}')
        
        self.stdout.write(f'All required columns present: {required_columns}')
