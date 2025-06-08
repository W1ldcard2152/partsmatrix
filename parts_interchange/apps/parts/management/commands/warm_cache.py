from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.db.models import Count
from apps.parts.models import Part, Manufacturer, PartCategory
from apps.vehicles.models import Vehicle, Make, Model
from apps.fitments.models import Fitment
import time

class Command(BaseCommand):
    help = 'Warm up critical caches to improve performance'

    def add_arguments(self, parser):
        parser.add_argument(
            '--full',
            action='store_true',
            help='Perform full cache warming (slower but more comprehensive)'
        )

    def handle(self, *args, **options):
        full_warm = options['full']
        
        self.stdout.write(self.style.SUCCESS('🔥 Warming up caches...'))
        start_time = time.time()
        
        # 1. Warm database stats (most expensive query)
        self.stdout.write('📊 Warming database stats...')
        try:
            stats = {
                'parts': {
                    'total': Part.objects.count(),
                    'active': Part.objects.filter(is_active=True).count(),
                    'by_manufacturer': dict(
                        Part.objects.values_list('manufacturer__name').annotate(count=Count('id')).order_by('-count')[:10]
                    )
                },
                'vehicles': {
                    'total': Vehicle.objects.count(),
                    'active': Vehicle.objects.filter(is_active=True).count(),
                    'by_make': dict(
                        Vehicle.objects.values_list('make__name').annotate(count=Count('id')).order_by('-count')[:10]
                    )
                },
                'fitments': {
                    'total': Fitment.objects.count(),
                    'verified': Fitment.objects.filter(is_verified=True).count(),
                }
            }
            cache.set('database_stats', stats, 900)  # 15 minutes
            self.stdout.write(self.style.SUCCESS('✅ Database stats cached'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Failed to cache database stats: {e}'))

        # 2. Warm popular manufacturer data
        self.stdout.write('🏭 Warming manufacturer data...')
        try:
            popular_manufacturers = Manufacturer.objects.annotate(
                parts_count=Count('parts')
            ).order_by('-parts_count')[:10]
            
            for mfr in popular_manufacturers:
                cache_key = f"manufacturer_{mfr.id}_parts"
                parts = Part.objects.filter(
                    manufacturer=mfr, is_active=True
                ).select_related('category')[:20]
                cache.set(cache_key, list(parts.values()), 600)
            
            self.stdout.write(self.style.SUCCESS(f'✅ Cached data for {len(popular_manufacturers)} manufacturers'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Failed to cache manufacturer data: {e}'))

        # 3. Warm popular vehicle data
        self.stdout.write('🚗 Warming vehicle data...')
        try:
            popular_makes = Make.objects.annotate(
                vehicle_count=Count('vehicles')
            ).order_by('-vehicle_count')[:5]
            
            for make in popular_makes:
                cache_key = f"make_{make.id}_models"
                models = Model.objects.filter(make=make).order_by('name')[:10]
                cache.set(cache_key, list(models.values()), 600)
            
            self.stdout.write(self.style.SUCCESS(f'✅ Cached data for {len(popular_makes)} makes'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Failed to cache vehicle data: {e}'))

        # 4. Pre-warm common search queries
        self.stdout.write('🔍 Warming common searches...')
        try:
            common_searches = [
                'GM', 'FORD', 'TOYOTA', 'HONDA', 'BMW',
                'engine', 'transmission', 'brake', 'suspension'
            ]
            
            for term in common_searches:
                cache_key = f"search_parts_{term}"
                results = Part.objects.filter(
                    part_number__icontains=term
                ).select_related('manufacturer', 'category')[:20]
                cache.set(cache_key, list(results.values()), 300)
            
            self.stdout.write(self.style.SUCCESS(f'✅ Cached {len(common_searches)} common searches'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Failed to cache search data: {e}'))

        if full_warm:
            # 5. Warm fitment data for popular parts
            self.stdout.write('🔧 Warming fitment data (full mode)...')
            try:
                popular_parts = Part.objects.annotate(
                    fitment_count=Count('fitments')
                ).filter(is_active=True).order_by('-fitment_count')[:20]
                
                for part in popular_parts:
                    cache_key = f"part_fitments_{part.id}"
                    fitments = Fitment.objects.filter(part=part).select_related(
                        'vehicle__make', 'vehicle__model'
                    )[:50]
                    cache.set(cache_key, list(fitments.values()), 600)
                
                self.stdout.write(self.style.SUCCESS(f'✅ Cached fitments for {len(popular_parts)} popular parts'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Failed to cache fitment data: {e}'))

        # 6. Keep database connection alive
        self.stdout.write('💓 Keeping database connection alive...')
        cache.set('db_keepalive', int(time.time()), 300)

        elapsed = time.time() - start_time
        self.stdout.write(
            self.style.SUCCESS(
                f'🎉 Cache warming completed in {elapsed:.2f} seconds!'
            )
        )
        
        # Performance tips
        self.stdout.write('\n💡 PERFORMANCE TIPS:')
        self.stdout.write('• Run this command every 10-15 minutes to keep caches warm')
        self.stdout.write('• Use smaller page sizes in admin (25 items)')
        self.stdout.write('• Consider upgrading to Render paid tier for better performance')
        self.stdout.write('• Monitor slow queries with Django Debug Toolbar in development')
        
        # Cache status
        self.stdout.write('\n📊 CACHE STATUS:')
        try:
            # Test cache functionality
            test_key = 'cache_test'
            test_value = 'working'
            cache.set(test_key, test_value, 60)
            cached_value = cache.get(test_key)
            
            if cached_value == test_value:
                self.stdout.write('✅ Cache is working properly')
            else:
                self.stdout.write('⚠️ Cache may not be working correctly')
                
            cache.delete(test_key)
        except Exception as e:
            self.stdout.write(f'❌ Cache test failed: {e}')
