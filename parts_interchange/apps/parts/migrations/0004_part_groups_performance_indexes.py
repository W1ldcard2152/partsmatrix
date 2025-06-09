# Generated for Part Groups performance optimization

from django.db import migrations, connection


def create_part_groups_indexes(apps, schema_editor):
    """Create performance indexes for Part Groups functionality"""
    db_vendor = connection.vendor
    
    if db_vendor == 'postgresql':
        # PostgreSQL-specific indexes with advanced features
        indexes = [
            # Part Groups table indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS parts_partgroup_category_active_idx ON parts_partgroup (category_id, is_active);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS parts_partgroup_specs_idx ON parts_partgroup (voltage, amperage, wattage) WHERE voltage IS NOT NULL;",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS parts_partgroup_search_idx ON parts_partgroup USING gin (to_tsvector('english', name || ' ' || description));",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS parts_partgroup_mounting_idx ON parts_partgroup (mounting_pattern) WHERE mounting_pattern != '';",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS parts_partgroup_connector_idx ON parts_partgroup (connector_type) WHERE connector_type != '';",
            
            # Part Group Memberships indexes (critical for junkyard search)
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS parts_partgroupmembership_group_compatibility_idx ON parts_partgroupmembership (part_group_id, compatibility_level, is_verified);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS parts_partgroupmembership_part_lookup_idx ON parts_partgroupmembership (part_id, is_verified);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS parts_partgroupmembership_verified_idx ON parts_partgroupmembership (is_verified, verification_date) WHERE is_verified = true;",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS parts_partgroupmembership_year_restriction_idx ON parts_partgroupmembership (year_restriction) WHERE year_restriction IS NOT NULL;",
            
            # Composite indexes for complex junkyard queries
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS parts_partgroup_junkyard_search_idx ON parts_partgroup (category_id, is_active, voltage, amperage);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS parts_partgroupmembership_junkyard_lookup_idx ON parts_partgroupmembership (part_group_id, compatibility_level, is_verified, part_id);",
            
            # JSON field indexes for specifications search
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS parts_partgroup_specs_gin_idx ON parts_partgroup USING gin (specifications);",
        ]
    else:
        # SQLite-compatible indexes (and other databases)
        indexes = [
            # Part Groups table indexes
            "CREATE INDEX IF NOT EXISTS parts_partgroup_category_active_idx ON parts_partgroup (category_id, is_active);",
            "CREATE INDEX IF NOT EXISTS parts_partgroup_specs_idx ON parts_partgroup (voltage, amperage, wattage);",
            "CREATE INDEX IF NOT EXISTS parts_partgroup_mounting_idx ON parts_partgroup (mounting_pattern);",
            "CREATE INDEX IF NOT EXISTS parts_partgroup_connector_idx ON parts_partgroup (connector_type);",
            
            # Part Group Memberships indexes
            "CREATE INDEX IF NOT EXISTS parts_partgroupmembership_group_compatibility_idx ON parts_partgroupmembership (part_group_id, compatibility_level, is_verified);",
            "CREATE INDEX IF NOT EXISTS parts_partgroupmembership_part_lookup_idx ON parts_partgroupmembership (part_id, is_verified);",
            "CREATE INDEX IF NOT EXISTS parts_partgroupmembership_verified_idx ON parts_partgroupmembership (is_verified, verification_date);",
            "CREATE INDEX IF NOT EXISTS parts_partgroupmembership_year_restriction_idx ON parts_partgroupmembership (year_restriction);",
            
            # Composite indexes for complex queries
            "CREATE INDEX IF NOT EXISTS parts_partgroup_junkyard_search_idx ON parts_partgroup (category_id, is_active, voltage, amperage);",
            "CREATE INDEX IF NOT EXISTS parts_partgroupmembership_junkyard_lookup_idx ON parts_partgroupmembership (part_group_id, compatibility_level, is_verified, part_id);",
        ]
    
    # Execute the appropriate indexes
    with connection.cursor() as cursor:
        for sql in indexes:
            try:
                cursor.execute(sql)
                print(f"✓ Created index: {sql.split()[-1] if 'ON' in sql else 'unknown'}")
            except Exception as e:
                # Log the error but don't fail the migration
                print(f"Warning: Could not create index: {sql} - {e}")


def drop_part_groups_indexes(apps, schema_editor):
    """Drop Part Groups performance indexes"""
    db_vendor = connection.vendor
    
    index_names = [
        'parts_partgroup_category_active_idx',
        'parts_partgroup_specs_idx', 
        'parts_partgroup_search_idx',
        'parts_partgroup_mounting_idx',
        'parts_partgroup_connector_idx',
        'parts_partgroupmembership_group_compatibility_idx',
        'parts_partgroupmembership_part_lookup_idx',
        'parts_partgroupmembership_verified_idx',
        'parts_partgroupmembership_year_restriction_idx',
        'parts_partgroup_junkyard_search_idx',
        'parts_partgroupmembership_junkyard_lookup_idx',
        'parts_partgroup_specs_gin_idx',
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
    atomic = False

    dependencies = [
        ('parts', '0003_add_part_groups'),
    ]

    operations = [
        migrations.RunPython(
            create_part_groups_indexes,
            drop_part_groups_indexes,
            hints={'supports_timezones': False}
        ),
    ]
