"""
Django management command to optimize database performance
Run this after adding data to create indexes and analyze performance
"""

from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings


class Command(BaseCommand):
    help = 'Optimize database performance with indexes and analysis'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-indexes',
            action='store_true',
            help='Create performance indexes'
        )
        parser.add_argument(
            '--analyze-queries',
            action='store_true',
            help='Analyze slow queries'
        )
        parser.add_argument(
            '--vacuum',
            action='store_true',
            help='Run VACUUM ANALYZE (PostgreSQL only)'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Run all optimizations'
        )

    def handle(self, *args, **options):
        if options['all']:
            options['create_indexes'] = True
            options['analyze_queries'] = True
            options['vacuum'] = True

        if options['create_indexes']:
            self.create_performance_indexes()
        
        if options['analyze_queries']:
            self.analyze_queries()
            
        if options['vacuum'] and 'postgresql' in settings.DATABASES['default']['ENGINE']:
            self.vacuum_database()

    def create_performance_indexes(self):
        """Create indexes for better query performance"""
        self.stdout.write('Creating performance indexes...')
        
        with connection.cursor() as cursor:
            # Critical indexes for admin performance
            indexes = [
                # Parts table indexes
                ('parts_part_manufacturer_category_idx', 
                 'CREATE INDEX CONCURRENTLY IF NOT EXISTS parts_part_manufacturer_category_idx ON parts_part (manufacturer_id, category_id)'),
                
                ('parts_part_active_lookup_idx',
                 'CREATE INDEX CONCURRENTLY IF NOT EXISTS parts_part_active_lookup_idx ON parts_part (is_active, manufacturer_id, part_number)'),
                
                ('parts_part_search_idx',
                 'CREATE INDEX CONCURRENTLY IF NOT EXISTS parts_part_search_idx ON parts_part USING gin (to_tsvector(\'english\', name || \' \' || part_number))'),
                
                # Vehicle table indexes  
                ('vehicles_vehicle_lookup_idx',
                 'CREATE INDEX CONCURRENTLY IF NOT EXISTS vehicles_vehicle_lookup_idx ON vehicles_vehicle (year, make_id, model_id, is_active)'),
                
                ('vehicles_vehicle_complete_idx',
                 'CREATE INDEX CONCURRENTLY IF NOT EXISTS vehicles_vehicle_complete_idx ON vehicles_vehicle (make_id, model_id, trim_id, engine_id)'),
                
                # Fitment table indexes (most critical for performance)
                ('fitments_fitment_part_lookup_idx',
                 'CREATE INDEX CONCURRENTLY IF NOT EXISTS fitments_fitment_part_lookup_idx ON fitments_fitment (part_id, is_verified)'),
                
                ('fitments_fitment_vehicle_lookup_idx', 
                 'CREATE INDEX CONCURRENTLY IF NOT EXISTS fitments_fitment_vehicle_lookup_idx ON fitments_fitment (vehicle_id, is_verified)'),
                
                ('fitments_fitment_position_idx',
                 'CREATE INDEX CONCURRENTLY IF NOT EXISTS fitments_fitment_position_idx ON fitments_fitment (position, quantity)'),
                
                # Manufacturer/Category lookup indexes
                ('parts_manufacturer_lookup_idx',
                 'CREATE INDEX CONCURRENTLY IF NOT EXISTS parts_manufacturer_lookup_idx ON parts_manufacturer (name, abbreviation)'),
                
                ('parts_partcategory_hierarchy_idx',
                 'CREATE INDEX CONCURRENTLY IF NOT EXISTS parts_partcategory_hierarchy_idx ON parts_partcategory (parent_category_id, name)'),
                
                # Vehicle hierarchy indexes
                ('vehicles_make_active_idx',
                 'CREATE INDEX CONCURRENTLY IF NOT EXISTS vehicles_make_active_idx ON vehicles_make (is_active, name)'),
                
                ('vehicles_model_lookup_idx',
                 'CREATE INDEX CONCURRENTLY IF NOT EXISTS vehicles_model_lookup_idx ON vehicles_model (make_id, is_active, name)'),
                
                # Engine search indexes
                ('vehicles_engine_specs_idx',
                 'CREATE INDEX CONCURRENTLY IF NOT EXISTS vehicles_engine_specs_idx ON vehicles_engine (fuel_type, cylinders, displacement)'),
                
                # Date-based indexes for admin filtering
                ('parts_part_created_idx',
                 'CREATE INDEX CONCURRENTLY IF NOT EXISTS parts_part_created_idx ON parts_part (created_at DESC)'),
                
                ('vehicles_vehicle_created_idx', 
                 'CREATE INDEX CONCURRENTLY IF NOT EXISTS vehicles_vehicle_created_idx ON vehicles_vehicle (created_at DESC)'),
                
                ('fitments_fitment_created_idx',
                 'CREATE INDEX CONCURRENTLY IF NOT EXISTS fitments_fitment_created_idx ON fitments_fitment (created_at DESC)'),
            ]
            
            created_count = 0
            for index_name, sql in indexes:
                try:
                    cursor.execute(sql)
                    created_count += 1
                    self.stdout.write(f'✓ Created index: {index_name}')
                except Exception as e:
                    if 'already exists' in str(e).lower():
                        self.stdout.write(f'- Index exists: {index_name}')
                    else:
                        self.stdout.write(f'✗ Failed to create {index_name}: {e}')
            
            self.stdout.write(self.style.SUCCESS(f'Created {created_count} new indexes'))

    def analyze_queries(self):
        """Analyze query performance"""
        self.stdout.write('Analyzing query performance...')
        
        with connection.cursor() as cursor:
            # Check for missing indexes on foreign keys
            cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    attname,
                    n_distinct,
                    correlation
                FROM pg_stats 
                WHERE schemaname = 'public' 
                AND tablename LIKE '%part%' OR tablename LIKE '%vehicle%' OR tablename LIKE '%fitment%'
                ORDER BY tablename, attname;
            """)
            
            stats = cursor.fetchall()
            if stats:
                self.stdout.write('Database statistics:')
                for stat in stats[:20]:  # Limit output
                    self.stdout.write(f'  {stat[1]}.{stat[2]}: distinct={stat[3]}, correlation={stat[4]}')
            
            # Check table sizes
            cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                    pg_stat_get_tuples_inserted(c.oid) as inserts,
                    pg_stat_get_tuples_updated(c.oid) as updates
                FROM pg_tables pt
                JOIN pg_class c ON c.relname = pt.tablename
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
            """)
            
            sizes = cursor.fetchall()
            if sizes:
                self.stdout.write('\nTable sizes:')
                for size in sizes:
                    self.stdout.write(f'  {size[1]}: {size[2]} ({size[3]} inserts, {size[4]} updates)')

    def vacuum_database(self):
        """Run VACUUM ANALYZE on PostgreSQL"""
        self.stdout.write('Running VACUUM ANALYZE...')
        
        with connection.cursor() as cursor:
            try:
                # VACUUM ANALYZE updates statistics and reclaims space
                cursor.execute('VACUUM ANALYZE;')
                self.stdout.write(self.style.SUCCESS('✓ VACUUM ANALYZE completed'))
                
                # Update table statistics
                cursor.execute('ANALYZE;')
                self.stdout.write(self.style.SUCCESS('✓ ANALYZE completed'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ VACUUM failed: {e}'))

    def get_slow_queries(self):
        """Get slow query information (PostgreSQL only)"""
        with connection.cursor() as cursor:
            # Check if pg_stat_statements is available
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements'
                );
            """)
            
            if cursor.fetchone()[0]:
                cursor.execute("""
                    SELECT 
                        query,
                        calls,
                        total_time,
                        mean_time,
                        rows
                    FROM pg_stat_statements 
                    WHERE query LIKE '%part%' OR query LIKE '%vehicle%' OR query LIKE '%fitment%'
                    ORDER BY mean_time DESC 
                    LIMIT 10;
                """)
                
                slow_queries = cursor.fetchall()
                if slow_queries:
                    self.stdout.write('\nSlow queries:')
                    for query in slow_queries:
                        self.stdout.write(f'  {query[2]:.2f}ms avg: {query[0][:100]}...')
