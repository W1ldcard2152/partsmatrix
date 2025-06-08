# Generated manually for database performance optimization

from django.db import migrations, connection


def create_performance_indexes(apps, schema_editor):
    """Create performance indexes compatible with both PostgreSQL and SQLite"""
    db_vendor = connection.vendor
    
    if db_vendor == 'postgresql':
        # PostgreSQL-specific indexes with advanced features
        indexes = [
            # Parts table performance indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS parts_part_manufacturer_category_idx ON parts_part (manufacturer_id, category_id);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS parts_part_active_lookup_idx ON parts_part (is_active, manufacturer_id);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS parts_part_number_search_idx ON parts_part (part_number varchar_pattern_ops);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS parts_part_name_search_idx ON parts_part (name varchar_pattern_ops);",
            
            # Vehicle table performance indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS vehicles_vehicle_lookup_idx ON vehicles_vehicle (year, make_id, model_id);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS vehicles_vehicle_complete_idx ON vehicles_vehicle (make_id, model_id, trim_id, engine_id);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS vehicles_vehicle_active_idx ON vehicles_vehicle (is_active, year);",
            
            # Fitment table performance indexes (most critical)
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS fitments_fitment_part_lookup_idx ON fitments_fitment (part_id, is_verified);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS fitments_fitment_vehicle_lookup_idx ON fitments_fitment (vehicle_id, is_verified);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS fitments_fitment_search_idx ON fitments_fitment (part_id, vehicle_id, position);",
            
            # Manufacturer and category indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS parts_manufacturer_search_idx ON parts_manufacturer (name varchar_pattern_ops, abbreviation varchar_pattern_ops);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS parts_partcategory_hierarchy_idx ON parts_partcategory (parent_category_id, name);",
            
            # Vehicle hierarchy indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS vehicles_make_active_idx ON vehicles_make (is_active, name);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS vehicles_model_lookup_idx ON vehicles_model (make_id, is_active);",
            
            # Date-based indexes for admin filtering and pagination
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS parts_part_created_idx ON parts_part (created_at DESC);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS vehicles_vehicle_created_idx ON vehicles_vehicle (created_at DESC);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS fitments_fitment_created_idx ON fitments_fitment (created_at DESC);",
        ]
    else:
        # SQLite-compatible indexes (and other databases)
        indexes = [
            # Parts table performance indexes
            "CREATE INDEX IF NOT EXISTS parts_part_manufacturer_category_idx ON parts_part (manufacturer_id, category_id);",
            "CREATE INDEX IF NOT EXISTS parts_part_active_lookup_idx ON parts_part (is_active, manufacturer_id);",
            "CREATE INDEX IF NOT EXISTS parts_part_number_search_idx ON parts_part (part_number);",
            "CREATE INDEX IF NOT EXISTS parts_part_name_search_idx ON parts_part (name);",
            
            # Vehicle table performance indexes
            "CREATE INDEX IF NOT EXISTS vehicles_vehicle_lookup_idx ON vehicles_vehicle (year, make_id, model_id);",
            "CREATE INDEX IF NOT EXISTS vehicles_vehicle_complete_idx ON vehicles_vehicle (make_id, model_id, trim_id, engine_id);",
            "CREATE INDEX IF NOT EXISTS vehicles_vehicle_active_idx ON vehicles_vehicle (is_active, year);",
            
            # Fitment table performance indexes (most critical)
            "CREATE INDEX IF NOT EXISTS fitments_fitment_part_lookup_idx ON fitments_fitment (part_id, is_verified);",
            "CREATE INDEX IF NOT EXISTS fitments_fitment_vehicle_lookup_idx ON fitments_fitment (vehicle_id, is_verified);",
            "CREATE INDEX IF NOT EXISTS fitments_fitment_search_idx ON fitments_fitment (part_id, vehicle_id, position);",
            
            # Manufacturer and category indexes
            "CREATE INDEX IF NOT EXISTS parts_manufacturer_search_idx ON parts_manufacturer (name, abbreviation);",
            "CREATE INDEX IF NOT EXISTS parts_partcategory_hierarchy_idx ON parts_partcategory (parent_category_id, name);",
            
            # Vehicle hierarchy indexes
            "CREATE INDEX IF NOT EXISTS vehicles_make_active_idx ON vehicles_make (is_active, name);",
            "CREATE INDEX IF NOT EXISTS vehicles_model_lookup_idx ON vehicles_model (make_id, is_active);",
            
            # Date-based indexes for admin filtering and pagination
            "CREATE INDEX IF NOT EXISTS parts_part_created_idx ON parts_part (created_at);",
            "CREATE INDEX IF NOT EXISTS vehicles_vehicle_created_idx ON vehicles_vehicle (created_at);",
            "CREATE INDEX IF NOT EXISTS fitments_fitment_created_idx ON fitments_fitment (created_at);",
        ]
    
    # Execute the appropriate indexes
    with connection.cursor() as cursor:
        for sql in indexes:
            try:
                cursor.execute(sql)
            except Exception as e:
                # Log the error but don't fail the migration
                print(f"Warning: Could not create index: {sql} - {e}")


def drop_performance_indexes(apps, schema_editor):
    """Drop performance indexes"""
    db_vendor = connection.vendor
    
    index_names = [
        'parts_part_manufacturer_category_idx',
        'parts_part_active_lookup_idx', 
        'parts_part_number_search_idx',
        'parts_part_name_search_idx',
        'vehicles_vehicle_lookup_idx',
        'vehicles_vehicle_complete_idx',
        'vehicles_vehicle_active_idx',
        'fitments_fitment_part_lookup_idx',
        'fitments_fitment_vehicle_lookup_idx',
        'fitments_fitment_search_idx',
        'parts_manufacturer_search_idx',
        'parts_partcategory_hierarchy_idx',
        'vehicles_make_active_idx',
        'vehicles_model_lookup_idx',
        'parts_part_created_idx',
        'vehicles_vehicle_created_idx',
        'fitments_fitment_created_idx',
    ]
    
    with connection.cursor() as cursor:
        for index_name in index_names:
            try:
                if db_vendor == 'postgresql':
                    cursor.execute(f"DROP INDEX CONCURRENTLY IF EXISTS {index_name};")
                else:
                    cursor.execute(f"DROP INDEX IF EXISTS {index_name};")
            except Exception as e:
                # Log the error but don't fail the migration
                print(f"Warning: Could not drop index {index_name}: {e}")


class Migration(migrations.Migration):

    dependencies = [
        ('parts', '0001_initial'),
        ('vehicles', '0002_alter_vehicle_options_alter_vehicle_unique_together_and_more'),
        ('fitments', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            create_performance_indexes,
            drop_performance_indexes,
            hints={'supports_timezones': False}  # Optimization hint
        ),
    ]
