"""
Advanced caching middleware and utilities for Parts Interchange Database
Implements intelligent caching strategies for maximum performance
"""

from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.utils.cache import get_cache_key
from django.conf import settings
import hashlib
import json
from functools import wraps
from typing import Any, Optional, Dict, List


class PartsCacheManager:
    """Centralized cache management for parts database"""
    
    # Cache timeout constants (from settings)
    TIMEOUT_SHORT = getattr(settings, 'PARTS_INTERCHANGE', {}).get('CACHE_TIMEOUT_SHORT', 300)      # 5 minutes
    TIMEOUT_MEDIUM = getattr(settings, 'PARTS_INTERCHANGE', {}).get('CACHE_TIMEOUT_MEDIUM', 1800)   # 30 minutes  
    TIMEOUT_LONG = getattr(settings, 'PARTS_INTERCHANGE', {}).get('CACHE_TIMEOUT_LONG', 7200)       # 2 hours
    
    # Cache key prefixes
    PREFIX_PART = 'part'
    PREFIX_VEHICLE = 'vehicle'
    PREFIX_FITMENT = 'fitment'
    PREFIX_PARTGROUP = 'partgroup'
    PREFIX_SEARCH = 'search'
    PREFIX_API = 'api'
    PREFIX_STATS = 'stats'
    
    @classmethod
    def _make_key(cls, prefix: str, identifier: str, version: str = '1') -> str:
        """Create a standardized cache key"""
        return f"pi:{prefix}:{version}:{identifier}"
    
    @classmethod
    def cache_part_fitments(cls, part_id: int, fitments_data: List[Dict]) -> str:
        """Cache part fitments with smart timeout"""
        key = cls._make_key(cls.PREFIX_FITMENT, f"part_{part_id}")
        cache.set(key, fitments_data, cls.TIMEOUT_MEDIUM)
        return key
    
    @classmethod
    def get_part_fitments(cls, part_id: int) -> Optional[List[Dict]]:
        """Get cached part fitments"""
        key = cls._make_key(cls.PREFIX_FITMENT, f"part_{part_id}")
        return cache.get(key)
    
    @classmethod
    def cache_vehicle_parts(cls, vehicle_id: int, parts_data: List[Dict]) -> str:
        """Cache vehicle parts with smart timeout"""
        key = cls._make_key(cls.PREFIX_FITMENT, f"vehicle_{vehicle_id}")
        cache.set(key, parts_data, cls.TIMEOUT_MEDIUM)
        return key
    
    @classmethod
    def get_vehicle_parts(cls, vehicle_id: int) -> Optional[List[Dict]]:
        """Get cached vehicle parts"""
        key = cls._make_key(cls.PREFIX_FITMENT, f"vehicle_{vehicle_id}")
        return cache.get(key)
    
    @classmethod
    def cache_part_group_compatibility(cls, part_group_id: int, compatibility_data: Dict) -> str:
        """Cache part group compatibility data"""
        key = cls._make_key(cls.PREFIX_PARTGROUP, f"compatibility_{part_group_id}")
        cache.set(key, compatibility_data, cls.TIMEOUT_LONG)  # Longer timeout for part groups
        return key
    
    @classmethod
    def get_part_group_compatibility(cls, part_group_id: int) -> Optional[Dict]:
        """Get cached part group compatibility"""
        key = cls._make_key(cls.PREFIX_PARTGROUP, f"compatibility_{part_group_id}")
        return cache.get(key)
    
    @classmethod
    def cache_junkyard_search(cls, search_params: Dict, results: Dict) -> str:
        """Cache junkyard search results"""
        # Create hash of search parameters for key
        params_str = json.dumps(search_params, sort_keys=True)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:12]
        key = cls._make_key(cls.PREFIX_SEARCH, f"junkyard_{params_hash}")
        cache.set(key, results, cls.TIMEOUT_SHORT)  # Shorter timeout for search results
        return key
    
    @classmethod
    def get_junkyard_search(cls, search_params: Dict) -> Optional[Dict]:
        """Get cached junkyard search results"""
        params_str = json.dumps(search_params, sort_keys=True)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:12]
        key = cls._make_key(cls.PREFIX_SEARCH, f"junkyard_{params_hash}")
        return cache.get(key)
    
    @classmethod
    def cache_database_stats(cls, stats: Dict) -> str:
        """Cache database statistics"""
        key = cls._make_key(cls.PREFIX_STATS, 'database')
        cache.set(key, stats, cls.TIMEOUT_LONG)  # Long timeout for stats
        return key
    
    @classmethod
    def get_database_stats(cls) -> Optional[Dict]:
        """Get cached database statistics"""
        key = cls._make_key(cls.PREFIX_STATS, 'database')
        return cache.get(key)
    
    @classmethod
    def invalidate_part_cache(cls, part_id: int) -> None:
        """Invalidate all cache entries related to a part"""
        patterns = [
            cls._make_key(cls.PREFIX_PART, f"{part_id}"),
            cls._make_key(cls.PREFIX_FITMENT, f"part_{part_id}"),
            cls._make_key(cls.PREFIX_SEARCH, "*"),  # Invalidate all searches (broad but safe)
            cls._make_key(cls.PREFIX_STATS, "*"),   # Invalidate stats
        ]
        
        for pattern in patterns:
            if '*' in pattern:
                # For patterns, we'd need cache.delete_pattern (Redis) or manual tracking
                # For now, just delete the stats we know about
                if 'stats' in pattern:
                    cache.delete(cls._make_key(cls.PREFIX_STATS, 'database'))
            else:
                cache.delete(pattern)
    
    @classmethod
    def invalidate_vehicle_cache(cls, vehicle_id: int) -> None:
        """Invalidate all cache entries related to a vehicle"""
        patterns = [
            cls._make_key(cls.PREFIX_VEHICLE, f"{vehicle_id}"),
            cls._make_key(cls.PREFIX_FITMENT, f"vehicle_{vehicle_id}"),
            cls._make_key(cls.PREFIX_SEARCH, "*"),
            cls._make_key(cls.PREFIX_STATS, "*"),
        ]
        
        for pattern in patterns:
            if '*' in pattern:
                if 'stats' in pattern:
                    cache.delete(cls._make_key(cls.PREFIX_STATS, 'database'))
            else:
                cache.delete(pattern)
    
    @classmethod
    def warm_critical_caches(cls) -> Dict[str, Any]:
        """Warm up critical caches - called by management command"""
        from apps.parts.models import Part, Manufacturer
        from apps.vehicles.models import Make
        from django.db.models import Count
        
        results = {
            'warmed_caches': [],
            'errors': []
        }
        
        try:
            # Warm database stats
            stats = {
                'parts_count': Part.objects.filter(is_active=True).count(),
                'manufacturers_count': Manufacturer.objects.count(),
                'makes_count': Make.objects.filter(is_active=True).count(),
            }
            cls.cache_database_stats(stats)
            results['warmed_caches'].append('database_stats')
            
            # Warm top manufacturers
            top_manufacturers = Manufacturer.objects.annotate(
                parts_count=Count('parts')
            ).order_by('-parts_count')[:10]
            
            for mfr in top_manufacturers:
                key = cls._make_key(cls.PREFIX_PART, f"manufacturer_{mfr.id}")
                cache.set(key, {
                    'id': mfr.id,
                    'name': mfr.name,
                    'abbreviation': mfr.abbreviation,
                    'parts_count': mfr.parts_count
                }, cls.TIMEOUT_LONG)
            
            results['warmed_caches'].append(f'top_{len(top_manufacturers)}_manufacturers')
            
        except Exception as e:
            results['errors'].append(f"Error warming caches: {e}")
        
        return results


def cache_api_response(timeout: int = None):
    """Decorator to cache API responses based on request parameters"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Only cache GET requests
            if request.method != 'GET':
                return view_func(request, *args, **kwargs)
            
            # Create cache key from request path and query parameters
            cache_key_data = {
                'path': request.path,
                'query': dict(request.GET.items()),
                'args': args,
                'kwargs': kwargs
            }
            
            cache_key_str = json.dumps(cache_key_data, sort_keys=True)
            cache_key_hash = hashlib.md5(cache_key_str.encode()).hexdigest()[:16]
            cache_key = PartsCacheManager._make_key(PartsCacheManager.PREFIX_API, cache_key_hash)
            
            # Try to get from cache
            cached_response = cache.get(cache_key)
            if cached_response is not None:
                return cached_response
            
            # Execute view and cache result
            response = view_func(request, *args, **kwargs)
            
            # Only cache successful responses
            if hasattr(response, 'status_code') and response.status_code == 200:
                cache_timeout = timeout or PartsCacheManager.TIMEOUT_SHORT
                cache.set(cache_key, response, cache_timeout)
            
            return response
        return wrapper
    return decorator


def cache_expensive_query(key_prefix: str, timeout: int = None):
    """Decorator to cache expensive database queries"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key_data = {
                'function': func.__name__,
                'args': str(args),
                'kwargs': str(sorted(kwargs.items()))
            }
            key_str = json.dumps(key_data, sort_keys=True)
            key_hash = hashlib.md5(key_str.encode()).hexdigest()[:12]
            cache_key = PartsCacheManager._make_key(key_prefix, f"{func.__name__}_{key_hash}")
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_timeout = timeout or PartsCacheManager.TIMEOUT_MEDIUM
            cache.set(cache_key, result, cache_timeout)
            
            return result
        return wrapper
    return decorator


class PerformanceCacheMiddleware:
    """Middleware to add performance caching headers and optimizations"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Add cache headers for static content
        response = self.get_response(request)
        
        # Add cache control headers for API responses
        if request.path.startswith('/api/'):
            if request.method == 'GET':
                # Cache GET API responses for 5 minutes
                response['Cache-Control'] = 'public, max-age=300'
                response['Vary'] = 'Accept, Accept-Encoding, Accept-Language'
            else:
                # Don't cache non-GET responses
                response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        
        # Add performance hints
        if hasattr(response, 'status_code') and response.status_code == 200:
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-Frame-Options'] = 'DENY'
        
        return response


# Cache warming utilities
def warm_manufacturer_cache():
    """Warm up manufacturer-related caches"""
    from apps.parts.models import Manufacturer, Part
    from django.db.models import Count
    
    manufacturers = Manufacturer.objects.annotate(
        parts_count=Count('parts')
    ).order_by('-parts_count')[:20]
    
    for mfr in manufacturers:
        # Cache manufacturer data
        key = PartsCacheManager._make_key(PartsCacheManager.PREFIX_PART, f"manufacturer_{mfr.id}")
        cache.set(key, {
            'id': mfr.id,
            'name': mfr.name,
            'abbreviation': mfr.abbreviation,
            'parts_count': mfr.parts_count
        }, PartsCacheManager.TIMEOUT_LONG)
        
        # Cache top parts for this manufacturer
        top_parts = Part.objects.filter(manufacturer=mfr, is_active=True)[:10]
        parts_key = PartsCacheManager._make_key(PartsCacheManager.PREFIX_PART, f"manufacturer_{mfr.id}_parts")
        cache.set(parts_key, list(top_parts.values()), PartsCacheManager.TIMEOUT_MEDIUM)


def warm_search_cache():
    """Warm up common search results"""
    common_searches = [
        {'query': 'alternator'},
        {'query': 'starter'},
        {'query': 'brake'},
        {'query': 'engine'},
        {'query': 'transmission'},
    ]
    
    for search in common_searches:
        # This would call your search logic and cache the results
        # Implementation depends on your search views
        pass
