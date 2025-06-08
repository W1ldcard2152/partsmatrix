from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Min, Max
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
import hashlib

from apps.parts.models import Part, Manufacturer, PartCategory, InterchangeGroup, PartGroup, PartGroupMembership
from apps.vehicles.models import Vehicle, Make, Model, Engine, Trim
from apps.fitments.models import Fitment
from .serializers import (
    PartSerializer, PartLookupSerializer,
    VehicleSerializer, VehicleLookupSerializer,
    FitmentSerializer, FitmentLookupSerializer,
    ManufacturerSerializer, MakeSerializer, ModelSerializer,
    EngineSerializer, InterchangeGroupSerializer,
    PartGroupSerializer, PartGroupLookupSerializer
)


class PartViewSet(viewsets.ModelViewSet):
    """API endpoint for automotive parts - OPTIMIZED"""
    queryset = Part.objects.select_related(
        'manufacturer', 'category'
    ).filter(is_active=True).prefetch_related('fitments__vehicle')
    serializer_class = PartSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'category', 'is_active']
    search_fields = ['part_number', 'name', 'description']
    ordering_fields = ['part_number', 'name', 'created_at']
    ordering = ['manufacturer__name', 'part_number']

    @method_decorator(cache_page(300))  # Cache for 5 minutes
    @method_decorator(vary_on_headers('User-Agent'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=['get'])
    def fitments(self, request, pk=None):
        """Get all fitments for a specific part - CACHED"""
        cache_key = f"part_fitments_{pk}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return Response(cached_result)
        
        part = self.get_object()
        fitments = Fitment.objects.filter(part=part).select_related(
            'vehicle__make', 'vehicle__model', 'vehicle__trim', 'vehicle__engine'
        )[:100]  # Limit results
        
        serializer = FitmentLookupSerializer(fitments, many=True)
        result = serializer.data
        
        # Cache for 10 minutes
        cache.set(cache_key, result, 600)
        return Response(result)

    @action(detail=True, methods=['get'])
    def interchanges(self, request, pk=None):
        """Get interchange parts for a specific part - CACHED"""
        cache_key = f"part_interchanges_{pk}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return Response(cached_result)
        
        part = self.get_object()
        interchange_groups = InterchangeGroup.objects.filter(parts__part=part)
        serializer = InterchangeGroupSerializer(interchange_groups, many=True)
        result = serializer.data
        
        # Cache for 15 minutes
        cache.set(cache_key, result, 900)
        return Response(result)


class VehicleViewSet(viewsets.ModelViewSet):
    """API endpoint for vehicles - OPTIMIZED"""
    queryset = Vehicle.objects.select_related(
        'make', 'model', 'trim', 'engine'
    ).filter(is_active=True)
    serializer_class = VehicleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['year', 'make', 'model', 'trim', 'engine', 'transmission_type', 'drivetrain']
    search_fields = ['make__name', 'model__name', 'trim__name', 'engine__name']
    ordering_fields = ['year', 'make__name', 'model__name']
    ordering = ['year', 'make__name', 'model__name']

    @method_decorator(cache_page(300))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=['get'])
    def parts(self, request, pk=None):
        """Get all parts that fit this vehicle - CACHED"""
        cache_key = f"vehicle_parts_{pk}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return Response(cached_result)
        
        vehicle = self.get_object()
        fitments = Fitment.objects.filter(vehicle=vehicle).select_related(
            'part__manufacturer', 'part__category'
        )[:100]  # Limit results
        
        serializer = FitmentLookupSerializer(fitments, many=True)
        result = serializer.data
        
        # Cache for 10 minutes
        cache.set(cache_key, result, 600)
        return Response(result)


class FitmentViewSet(viewsets.ModelViewSet):
    """API endpoint for part-vehicle fitments - OPTIMIZED"""
    queryset = Fitment.objects.select_related(
        'part__manufacturer', 'part__category',
        'vehicle__make', 'vehicle__model', 'vehicle__trim', 'vehicle__engine'
    )
    serializer_class = FitmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['part', 'vehicle', 'position', 'is_verified']
    search_fields = ['part__part_number', 'part__name', 'vehicle__make__name', 'vehicle__model__name']
    ordering_fields = ['created_at', 'part__part_number']
    ordering = ['-created_at']


class ManufacturerViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for manufacturers - CACHED"""
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'abbreviation']
    ordering = ['name']

    @method_decorator(cache_page(900))  # Cache for 15 minutes
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class MakeViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for vehicle makes - CACHED"""
    queryset = Make.objects.filter(is_active=True)
    serializer_class = MakeSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering = ['name']

    @method_decorator(cache_page(900))  # Cache for 15 minutes
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ModelViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for vehicle models - CACHED"""
    queryset = Model.objects.select_related('make').filter(is_active=True)
    serializer_class = ModelSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['make']
    search_fields = ['name', 'make__name']
    ordering = ['make__name', 'name']

    @method_decorator(cache_page(900))  # Cache for 15 minutes
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class EngineViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for engines - CACHED"""
    queryset = Engine.objects.all()
    serializer_class = EngineSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['fuel_type', 'aspiration', 'cylinders']
    search_fields = ['name', 'engine_code']
    ordering = ['name']

    @method_decorator(cache_page(900))  # Cache for 15 minutes
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class InterchangeGroupViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for interchange groups - CACHED"""
    queryset = InterchangeGroup.objects.select_related('category')
    serializer_class = InterchangeGroupSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['name', 'description']
    ordering = ['name']

    @method_decorator(cache_page(900))  # Cache for 15 minutes
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


# Custom API Views for specific lookup operations
class PartFitmentsView(APIView):
    """Get all vehicles that a specific part fits - CACHED"""
    
    def get(self, request, part_id):
        cache_key = f"part_lookup_{part_id}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return Response(cached_result)
        
        part = get_object_or_404(Part, id=part_id, is_active=True)
        fitments = Fitment.objects.filter(part=part).select_related(
            'vehicle__make', 'vehicle__model', 'vehicle__trim', 'vehicle__engine'
        )[:100]  # Limit results
        
        data = {
            'part': PartLookupSerializer(part).data,
            'fitments': FitmentLookupSerializer(fitments, many=True).data,
            'total_vehicles': fitments.count()
        }
        
        # Cache for 10 minutes
        cache.set(cache_key, data, 600)
        return Response(data)


class VehiclePartsView(APIView):
    """Get all parts that fit a specific vehicle - CACHED"""
    
    def get(self, request, vehicle_id):
        cache_key = f"vehicle_lookup_{vehicle_id}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return Response(cached_result)
        
        vehicle = get_object_or_404(Vehicle, id=vehicle_id, is_active=True)
        fitments = Fitment.objects.filter(vehicle=vehicle).select_related(
            'part__manufacturer', 'part__category'
        )[:100]  # Limit results
        
        data = {
            'vehicle': VehicleLookupSerializer(vehicle).data,
            'fitments': FitmentLookupSerializer(fitments, many=True).data,
            'total_parts': fitments.count()
        }
        
        # Cache for 10 minutes
        cache.set(cache_key, data, 600)
        return Response(data)


class InterchangeLookupView(APIView):
    """Look up interchange parts by part number - CACHED"""
    
    def get(self, request, part_number):
        cache_key = f"interchange_lookup_{part_number}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return Response(cached_result)
        
        # Find the part
        try:
            part = Part.objects.select_related('manufacturer', 'category').get(
                part_number=part_number, is_active=True
            )
        except Part.DoesNotExist:
            return Response(
                {'error': f'Part number {part_number} not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get interchange groups for this part
        interchange_groups = InterchangeGroup.objects.filter(
            parts__part=part
        ).prefetch_related('parts__part__manufacturer')
        
        # Get all interchangeable parts
        interchangeable_parts = []
        for group in interchange_groups:
            group_parts = Part.objects.filter(
                partinterchange__interchange_group=group,
                is_active=True
            ).exclude(id=part.id).select_related('manufacturer', 'category')[:20]  # Limit
            interchangeable_parts.extend(group_parts)
        
        data = {
            'original_part': PartLookupSerializer(part).data,
            'interchange_groups': InterchangeGroupSerializer(interchange_groups, many=True).data,
            'interchangeable_parts': PartLookupSerializer(interchangeable_parts, many=True).data,
            'total_interchanges': len(interchangeable_parts)
        }
        
        # Cache for 15 minutes
        cache.set(cache_key, data, 900)
        return Response(data)


class PartSearchView(APIView):
    """Advanced part search with multiple criteria - CACHED"""
    
    def get(self, request):
        # Create cache key from query parameters
        query_hash = hashlib.md5(
            str(sorted(request.GET.items())).encode()
        ).hexdigest()
        cache_key = f"part_search_{query_hash}"
        
        cached_result = cache.get(cache_key)
        if cached_result:
            return Response(cached_result)
        
        queryset = Part.objects.select_related('manufacturer', 'category').filter(is_active=True)
        
        # Search parameters
        part_number = request.GET.get('part_number')
        name = request.GET.get('name')
        manufacturer = request.GET.get('manufacturer')
        category = request.GET.get('category')
        
        # Apply filters efficiently
        if part_number:
            queryset = queryset.filter(part_number__icontains=part_number)
        if name:
            queryset = queryset.filter(name__icontains=name)
        if manufacturer:
            queryset = queryset.filter(manufacturer__name__icontains=manufacturer)
        if category:
            queryset = queryset.filter(category__name__icontains=category)
        
        # Limit and serialize
        queryset = queryset[:50]  # Reduced limit
        serializer = PartLookupSerializer(queryset, many=True)
        
        result = {
            'results': serializer.data,
            'count': len(serializer.data)
        }
        
        # Cache for 5 minutes
        cache.set(cache_key, result, 300)
        return Response(result)


class VehicleSearchView(APIView):
    """Advanced vehicle search with multiple criteria - CACHED"""
    
    def get(self, request):
        # Create cache key from query parameters
        query_hash = hashlib.md5(
            str(sorted(request.GET.items())).encode()
        ).encode()
        cache_key = f"vehicle_search_{query_hash.hex()}"
        
        cached_result = cache.get(cache_key)
        if cached_result:
            return Response(cached_result)
        
        queryset = Vehicle.objects.select_related(
            'make', 'model', 'trim', 'engine'
        ).filter(is_active=True)
        
        # Search parameters
        year = request.GET.get('year')
        make = request.GET.get('make')
        model = request.GET.get('model')
        trim = request.GET.get('trim')
        engine = request.GET.get('engine')
        
        # Apply filters
        if year:
            queryset = queryset.filter(year=year)
        if make:
            queryset = queryset.filter(make__name__icontains=make)
        if model:
            queryset = queryset.filter(model__name__icontains=model)
        if trim:
            queryset = queryset.filter(trim__name__icontains=trim)
        if engine:
            queryset = queryset.filter(engine__name__icontains=engine)
        
        # Limit results
        queryset = queryset[:50]  # Reduced limit
        
        serializer = VehicleLookupSerializer(queryset, many=True)
        result = {
            'results': serializer.data,
            'count': len(serializer.data)
        }
        
        # Cache for 5 minutes
        cache.set(cache_key, result, 300)
        return Response(result)


class FitmentSearchView(APIView):
    """Search fitments by part or vehicle criteria - CACHED"""
    
    def get(self, request):
        # Create cache key from query parameters
        query_hash = hashlib.md5(
            str(sorted(request.GET.items())).encode()
        ).hexdigest()
        cache_key = f"fitment_search_{query_hash}"
        
        cached_result = cache.get(cache_key)
        if cached_result:
            return Response(cached_result)
        
        queryset = Fitment.objects.select_related(
            'part__manufacturer', 'part__category',
            'vehicle__make', 'vehicle__model', 'vehicle__trim', 'vehicle__engine'
        )
        
        # Search parameters
        part_number = request.GET.get('part_number')
        vehicle_year = request.GET.get('vehicle_year')
        vehicle_make = request.GET.get('vehicle_make')
        vehicle_model = request.GET.get('vehicle_model')
        
        # Apply filters
        if part_number:
            queryset = queryset.filter(part__part_number__icontains=part_number)
        if vehicle_year:
            queryset = queryset.filter(vehicle__year=vehicle_year)
        if vehicle_make:
            queryset = queryset.filter(vehicle__make__name__icontains=vehicle_make)
        if vehicle_model:
            queryset = queryset.filter(vehicle__model__name__icontains=vehicle_model)
        
        # Limit results
        queryset = queryset[:50]  # Reduced limit
        
        serializer = FitmentLookupSerializer(queryset, many=True)
        result = {
            'results': serializer.data,
            'count': len(serializer.data)
        }
        
        # Cache for 5 minutes
        cache.set(cache_key, result, 300)
        return Response(result)


class BulkFitmentCreateView(APIView):
    """Bulk create fitments from uploaded data"""
    
    def post(self, request):
        # This would handle bulk fitment creation
        # Implementation depends on your specific data format
        return Response({
            'message': 'Bulk fitment creation endpoint - implementation pending',
            'status': 'not_implemented'
        }, status=status.HTTP_501_NOT_IMPLEMENTED)


class DatabaseStatsView(APIView):
    """Get database statistics - HEAVILY CACHED"""
    
    @method_decorator(cache_page(900))  # Cache for 15 minutes
    def get(self, request):
        cache_key = "database_stats"
        stats = cache.get(cache_key)
        
        if not stats:
            # Generate stats - this is expensive so cache well
            stats = {
                'parts': {
                    'total': Part.objects.count(),
                    'active': Part.objects.filter(is_active=True).count(),
                    'by_manufacturer': dict(
                        Part.objects.values_list('manufacturer__name').annotate(
                            count=Count('id')
                        ).order_by('-count')[:5]  # Only top 5
                    )
                },
                'vehicles': {
                    'total': Vehicle.objects.count(),
                    'active': Vehicle.objects.filter(is_active=True).count(),
                    'by_make': dict(
                        Vehicle.objects.values_list('make__name').annotate(
                            count=Count('id')
                        ).order_by('-count')[:5]  # Only top 5
                    ),
                    'year_range': {
                        'earliest': Vehicle.objects.aggregate(min_year=Min('year'))['min_year'],
                        'latest': Vehicle.objects.aggregate(max_year=Max('year'))['max_year']
                    }
                },
                'fitments': {
                    'total': Fitment.objects.count(),
                    'verified': Fitment.objects.filter(is_verified=True).count(),
                    'by_category': dict(
                        Fitment.objects.values_list('part__category__name').annotate(
                            count=Count('id')
                        ).order_by('-count')[:5]  # Only top 5
                    )
                },
                'interchange_groups': InterchangeGroup.objects.count()
            }
            
            # Cache for 15 minutes
            cache.set(cache_key, stats, 900)
        
        return Response(stats)


# Part Groups API Endpoints
class PartGroupViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for part groups - CACHED"""
    queryset = PartGroup.objects.select_related('category').filter(is_active=True)
    serializer_class = PartGroupSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'voltage', 'amperage']
    search_fields = ['name', 'description', 'mounting_pattern', 'connector_type']
    ordering = ['category__name', 'name']

    @method_decorator(cache_page(900))  # Cache for 15 minutes
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=['get'])
    def compatible_parts(self, request, pk=None):
        """Get all parts in this part group with compatibility info"""
        cache_key = f"part_group_parts_{pk}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return Response(cached_result)
        
        part_group = self.get_object()
        memberships = PartGroupMembership.objects.filter(
            part_group=part_group
        ).select_related(
            'part__manufacturer', 'part__category'
        ).annotate(
            fitment_count=Count('part__fitments')
        ).order_by('compatibility_level', '-fitment_count')
        
        # Group by compatibility level
        result = {
            'part_group': {
                'name': part_group.name,
                'description': part_group.description,
                'category': part_group.category.name,
                'specifications': {
                    'voltage': part_group.voltage,
                    'amperage': part_group.amperage,
                    'wattage': part_group.wattage,
                    'mounting_pattern': part_group.mounting_pattern,
                    'connector_type': part_group.connector_type
                }
            },
            'compatible_parts': {
                'IDENTICAL': [],
                'COMPATIBLE': [],
                'CONDITIONAL': []
            },
            'total_parts': memberships.count()
        }
        
        for membership in memberships:
            part_data = {
                'part_number': membership.part.part_number,
                'manufacturer': membership.part.manufacturer.abbreviation,
                'name': membership.part.name,
                'fitment_count': membership.fitment_count,
                'installation_notes': membership.installation_notes,
                'year_restriction': membership.year_restriction,
                'is_verified': membership.is_verified
            }
            
            result['compatible_parts'][membership.compatibility_level].append(part_data)
        
        # Cache for 10 minutes
        cache.set(cache_key, result, 600)
        return Response(result)

    @action(detail=True, methods=['get'])
    def vehicle_coverage(self, request, pk=None):
        """Get vehicle coverage for parts in this group"""
        part_group = self.get_object()
        
        # Get all vehicles that parts in this group fit
        vehicles = Vehicle.objects.filter(
            fitments__part__part_group_memberships__part_group=part_group
        ).select_related('make', 'model').distinct()
        
        coverage = {
            'total_vehicles': vehicles.count(),
            'makes': list(vehicles.values_list('make__name', flat=True).distinct()),
            'year_range': {
                'earliest': vehicles.aggregate(min_year=Min('year'))['min_year'],
                'latest': vehicles.aggregate(max_year=Max('year'))['max_year']
            },
            'sample_vehicles': [
                f"{v.year} {v.make.name} {v.model.name}"
                for v in vehicles[:10]
            ]
        }
        
        return Response(coverage)


class JunkyardSearchView(APIView):
    """Junkyard search API - Find compatible parts for vehicles"""
    
    def get(self, request):
        # Search parameters
        vehicle_id = request.GET.get('vehicle_id')
        part_type = request.GET.get('part_type')
        year = request.GET.get('year')
        make = request.GET.get('make')
        model = request.GET.get('model')
        
        if vehicle_id:
            # Search by specific vehicle ID
            try:
                vehicle = Vehicle.objects.get(id=vehicle_id)
            except Vehicle.DoesNotExist:
                return Response({'error': 'Vehicle not found'}, status=404)
        elif year and make and model:
            # Search by year/make/model
            vehicles = Vehicle.objects.filter(
                year=year,
                make__name__icontains=make,
                model__name__icontains=model
            )
            if not vehicles.exists():
                return Response({'error': 'No vehicles found'}, status=404)
            vehicle = vehicles.first()
        else:
            return Response({
                'error': 'Provide vehicle_id OR year/make/model parameters'
            }, status=400)
        
        # Find parts that fit this vehicle
        fitments = Fitment.objects.filter(
            vehicle=vehicle
        ).select_related('part__manufacturer', 'part__category')
        
        if part_type:
            fitments = fitments.filter(
                Q(part__name__icontains=part_type) |
                Q(part__category__name__icontains=part_type)
            )
        
        # Find part groups for these parts
        part_groups_data = {}
        direct_parts = []
        
        for fitment in fitments[:50]:  # Limit results
            part = fitment.part
            direct_parts.append({
                'part_number': part.part_number,
                'manufacturer': part.manufacturer.abbreviation,
                'name': part.name,
                'category': part.category.name,
                'position': fitment.position,
                'notes': fitment.notes
            })
            
            # Find part groups this part belongs to
            memberships = PartGroupMembership.objects.filter(
                part=part
            ).select_related('part_group')
            
            for membership in memberships:
                group = membership.part_group
                if group.id not in part_groups_data:
                    # Get all compatible parts in this group
                    all_memberships = PartGroupMembership.objects.filter(
                        part_group=group
                    ).select_related('part__manufacturer')[:20]  # Limit
                    
                    compatible_parts = []
                    for m in all_memberships:
                        compatible_parts.append({
                            'part_number': m.part.part_number,
                            'manufacturer': m.part.manufacturer.abbreviation,
                            'name': m.part.name,
                            'compatibility_level': m.compatibility_level,
                            'installation_notes': m.installation_notes,
                            'is_verified': m.is_verified
                        })
                    
                    part_groups_data[group.id] = {
                        'name': group.name,
                        'description': group.description,
                        'category': group.category.name,
                        'specifications': {
                            'voltage': group.voltage,
                            'amperage': group.amperage,
                            'mounting_pattern': group.mounting_pattern,
                            'connector_type': group.connector_type
                        },
                        'compatible_parts': compatible_parts,
                        'total_compatible': len(compatible_parts)
                    }
        
        result = {
            'vehicle': {
                'id': vehicle.id,
                'description': str(vehicle)
            },
            'search_criteria': {
                'part_type': part_type
            },
            'direct_fit_parts': direct_parts,
            'part_groups': list(part_groups_data.values()),
            'summary': {
                'direct_parts_count': len(direct_parts),
                'part_groups_count': len(part_groups_data),
                'total_compatible_parts': sum(
                    group['total_compatible'] for group in part_groups_data.values()
                )
            }
        }
        
        return Response(result)
