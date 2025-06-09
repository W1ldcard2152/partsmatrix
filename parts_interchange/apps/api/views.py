import logging
from django.core.cache import cache
from django.db.models import Count, Min, Max
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.parts.models import Part, Manufacturer, PartCategory, InterchangeGroup, PartGroup, PartGroupMembership
from apps.vehicles.models import Vehicle, Make, Model, Engine
from apps.fitments.models import Fitment
from .serializers import (
    PartSerializer, PartLookupSerializer,
    VehicleSerializer, VehicleLookupSerializer,
    FitmentSerializer, FitmentLookupSerializer,
    ManufacturerSerializer, MakeSerializer, ModelSerializer,
    EngineSerializer, InterchangeGroupSerializer,
    PartGroupSerializer, PartGroupMembershipSerializer
)

logger = logging.getLogger(__name__)

# --- Constants ---
CACHE_TIMEOUT_SHORT = 300  # 5 minutes
CACHE_TIMEOUT_MEDIUM = 600  # 10 minutes
CACHE_TIMEOUT_LONG = 900  # 15 minutes

# --- Base Classes ---

class CachedReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    """Base ViewSet for read-only models with caching."""
    permission_classes = [IsAuthenticated]

    @method_decorator(cache_page(CACHE_TIMEOUT_LONG))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(CACHE_TIMEOUT_LONG))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

# --- Model ViewSets ---

class PartViewSet(viewsets.ModelViewSet):
    """API endpoint for automotive parts."""
    queryset = Part.objects.select_related('manufacturer', 'category').filter(is_active=True)
    serializer_class = PartSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'category']
    search_fields = ['part_number', 'name', 'description']
    ordering_fields = ['part_number', 'name', 'created_at']
    ordering = ['manufacturer__name', 'part_number']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()

    @method_decorator(cache_page(CACHE_TIMEOUT_SHORT))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=['get'])
    def fitments(self, request, pk=None):
        """Get all vehicles that a specific part fits."""
        cache_key = f"part_fitments_{pk}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        part = self.get_object()
        fitments = Fitment.objects.filter(part=part).select_related(
            'vehicle__make', 'vehicle__model', 'vehicle__trim', 'vehicle__engine'
        )[:100]
        
        serializer = FitmentLookupSerializer(fitments, many=True)
        cache.set(cache_key, serializer.data, CACHE_TIMEOUT_MEDIUM)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def interchanges(self, request, pk=None):
        """Get interchange parts for a specific part."""
        cache_key = f"part_interchanges_{pk}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        part = self.get_object()
        interchange_groups = InterchangeGroup.objects.filter(parts__part=part)
        serializer = InterchangeGroupSerializer(interchange_groups, many=True)
        cache.set(cache_key, serializer.data, CACHE_TIMEOUT_MEDIUM)
        return Response(serializer.data)


class VehicleViewSet(viewsets.ModelViewSet):
    """API endpoint for vehicles."""
    queryset = Vehicle.objects.select_related('make', 'model', 'trim', 'engine').filter(is_active=True)
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['year', 'make', 'model', 'trim', 'engine']
    search_fields = ['make__name', 'model__name', 'trim__name']
    ordering_fields = ['year', 'make__name', 'model__name']
    ordering = ['year', 'make__name', 'model__name']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()

    @method_decorator(cache_page(CACHE_TIMEOUT_SHORT))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=['get'])
    def parts(self, request, pk=None):
        """Get all parts that fit this vehicle."""
        cache_key = f"vehicle_parts_{pk}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        vehicle = self.get_object()
        fitments = Fitment.objects.filter(vehicle=vehicle).select_related(
            'part__manufacturer', 'part__category'
        )[:100]
        
        serializer = FitmentLookupSerializer(fitments, many=True)
        cache.set(cache_key, serializer.data, CACHE_TIMEOUT_MEDIUM)
        return Response(serializer.data)


class FitmentViewSet(viewsets.ModelViewSet):
    """API endpoint for part-vehicle fitments."""
    queryset = Fitment.objects.select_related(
        'part__manufacturer', 'part__category',
        'vehicle__make', 'vehicle__model'
    )
    serializer_class = FitmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['part', 'vehicle', 'is_verified']
    search_fields = ['part__part_number', 'vehicle__make__name', 'vehicle__model__name']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()


class ManufacturerViewSet(CachedReadOnlyViewSet):
    """API endpoint for manufacturers."""
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer
    search_fields = ['name', 'abbreviation']
    ordering = ['name']


class MakeViewSet(CachedReadOnlyViewSet):
    """API endpoint for vehicle makes."""
    queryset = Make.objects.filter(is_active=True)
    serializer_class = MakeSerializer
    search_fields = ['name']
    ordering = ['name']


class ModelViewSet(CachedReadOnlyViewSet):
    """API endpoint for vehicle models."""
    queryset = Model.objects.select_related('make').filter(is_active=True)
    serializer_class = ModelSerializer
    filterset_fields = ['make']
    search_fields = ['name', 'make__name']
    ordering = ['make__name', 'name']


class EngineViewSet(CachedReadOnlyViewSet):
    """API endpoint for engines."""
    queryset = Engine.objects.all()
    serializer_class = EngineSerializer
    filterset_fields = ['fuel_type', 'aspiration', 'cylinders']
    search_fields = ['name', 'engine_code']
    ordering = ['name']


class InterchangeGroupViewSet(CachedReadOnlyViewSet):
    """API endpoint for interchange groups."""
    queryset = InterchangeGroup.objects.select_related('category')
    serializer_class = InterchangeGroupSerializer
    filterset_fields = ['category']
    search_fields = ['name', 'description']
    ordering = ['name']


class PartGroupViewSet(CachedReadOnlyViewSet):
    """API endpoint for part groups."""
    queryset = PartGroup.objects.select_related('category').filter(is_active=True)
    serializer_class = PartGroupSerializer
    filterset_fields = ['category', 'voltage', 'amperage']
    search_fields = ['name', 'description', 'mounting_pattern', 'connector_type']
    ordering = ['category__name', 'name']

    @action(detail=True, methods=['get'])
    def compatible_parts(self, request, pk=None):
        """Get all parts in this part group."""
        cache_key = f"part_group_compatible_parts_{pk}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        part_group = self.get_object()
        memberships = PartGroupMembership.objects.filter(part_group=part_group).select_related(
            'part__manufacturer'
        ).order_by('compatibility_level')
        
        # This logic can be complex, so for now we serialize the memberships directly
        # A more advanced implementation could group them by compatibility level
        serializer = PartGroupMembershipSerializer(memberships, many=True)
        cache.set(cache_key, serializer.data, CACHE_TIMEOUT_MEDIUM)
        return Response(serializer.data)


# --- Custom API Views ---

class DatabaseStatsView(APIView):
    """Get database statistics."""
    permission_classes = [IsAdminUser]

    @method_decorator(cache_page(CACHE_TIMEOUT_LONG))
    def get(self, request):
        stats = {
            'parts': {'total': Part.objects.count(), 'active': Part.objects.filter(is_active=True).count()},
            'vehicles': {'total': Vehicle.objects.count(), 'active': Vehicle.objects.filter(is_active=True).count()},
            'fitments': {'total': Fitment.objects.count(), 'verified': Fitment.objects.filter(is_verified=True).count()},
            'interchange_groups': InterchangeGroup.objects.count(),
            'part_groups': PartGroup.objects.count(),
            'year_range': Vehicle.objects.aggregate(min_year=Min('year'), max_year=Max('year')),
        }
        return Response(stats)


class JunkyardSearchView(APIView):
    """
    Junkyard search: Find compatible parts for a given vehicle.
    Query params: `vehicle_id` or (`year`, `make`, `model`), and optional `part_type`.
    """
    permission_classes = [IsAuthenticated]

    def get_vehicle(self, request):
        vehicle_id = request.query_params.get('vehicle_id')
        if vehicle_id:
            return Vehicle.objects.filter(id=vehicle_id).first()

        year = request.query_params.get('year')
        make = request.query_params.get('make')
        model = request.query_params.get('model')

        if not (year and make and model):
            return None
        
        return Vehicle.objects.filter(
            year=year, make__name__iexact=make, model__name__iexact=model
        ).first()

    def get(self, request, *args, **kwargs):
        vehicle = self.get_vehicle(request)
        if not vehicle:
            return Response(
                {'error': 'A valid vehicle_id or year, make, and model are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        part_type = request.query_params.get('part_type')
        
        # Find parts that directly fit the vehicle
        fitments = Fitment.objects.filter(vehicle=vehicle).select_related('part__manufacturer', 'part__category')
        if part_type:
            fitments = fitments.filter(part__category__name__icontains=part_type)
        
        direct_parts_serializer = FitmentLookupSerializer(fitments[:50], many=True) # Limit results

        # Find part groups associated with these direct-fit parts
        part_ids = [f.part.id for f in fitments]
        part_groups = PartGroup.objects.filter(
            memberships__part__id__in=part_ids
        ).distinct().prefetch_related('memberships__part__manufacturer')

        part_groups_data = []
        for group in part_groups:
            memberships = group.memberships.all()
            part_groups_data.append({
                'group_name': group.name,
                'compatible_parts': PartGroupMembershipSerializer(memberships[:20], many=True).data # Limit results
            })

        return Response({
            'vehicle': VehicleLookupSerializer(vehicle).data,
            'direct_fit_parts': direct_parts_serializer.data,
            'compatible_part_groups': part_groups_data,
        })

class BulkFitmentCreateView(APIView):
    """Bulk create fitments. Expects a list of {'part_id': 1, 'vehicle_id': 2} objects."""
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        fitment_data = request.data
        if not isinstance(fitment_data, list):
            return Response(
                {'error': 'Expected a list of fitment objects.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        fitments_to_create = []
        for item in fitment_data:
            part_id = item.get('part_id')
            vehicle_id = item.get('vehicle_id')
            if part_id and vehicle_id:
                fitments_to_create.append(
                    Fitment(part_id=part_id, vehicle_id=vehicle_id)
                )
        
        try:
            Fitment.objects.bulk_create(fitments_to_create, ignore_conflicts=True)
            return Response(
                {'message': f'{len(fitments_to_create)} fitments processed.'},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.error(f"Bulk fitment creation failed: {e}")
            return Response(
                {'error': 'An error occurred during bulk creation.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
