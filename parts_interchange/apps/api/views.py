from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Min, Max
from django.shortcuts import get_object_or_404

from apps.parts.models import Part, Manufacturer, PartCategory, InterchangeGroup
from apps.vehicles.models import Vehicle, Make, Model, Engine, Trim
from apps.fitments.models import Fitment
from .serializers import (
    PartSerializer, PartLookupSerializer,
    VehicleSerializer, VehicleLookupSerializer,
    FitmentSerializer, FitmentLookupSerializer,
    ManufacturerSerializer, MakeSerializer, ModelSerializer,
    EngineSerializer, InterchangeGroupSerializer
)


class PartViewSet(viewsets.ModelViewSet):
    """API endpoint for automotive parts"""
    queryset = Part.objects.select_related('manufacturer', 'category').filter(is_active=True)
    serializer_class = PartSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'category', 'is_active']
    search_fields = ['part_number', 'name', 'description']
    ordering_fields = ['part_number', 'name', 'created_at']
    ordering = ['manufacturer__name', 'part_number']

    @action(detail=True, methods=['get'])
    def fitments(self, request, pk=None):
        """Get all fitments for a specific part"""
        part = self.get_object()
        fitments = Fitment.objects.filter(part=part).select_related(
            'vehicle__make', 'vehicle__model', 'vehicle__trim', 'vehicle__engine'
        )
        serializer = FitmentLookupSerializer(fitments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def interchanges(self, request, pk=None):
        """Get interchange parts for a specific part"""
        part = self.get_object()
        interchange_groups = InterchangeGroup.objects.filter(parts__part=part)
        serializer = InterchangeGroupSerializer(interchange_groups, many=True)
        return Response(serializer.data)


class VehicleViewSet(viewsets.ModelViewSet):
    """API endpoint for vehicles"""
    queryset = Vehicle.objects.select_related(
        'make', 'model', 'trim', 'engine'
    ).filter(is_active=True)
    serializer_class = VehicleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['year', 'make', 'model', 'trim', 'engine', 'transmission_type', 'drivetrain']
    search_fields = ['make__name', 'model__name', 'trim__name', 'engine__name']
    ordering_fields = ['year', 'make__name', 'model__name']
    ordering = ['year', 'make__name', 'model__name']

    @action(detail=True, methods=['get'])
    def parts(self, request, pk=None):
        """Get all parts that fit this vehicle"""
        vehicle = self.get_object()
        fitments = Fitment.objects.filter(vehicle=vehicle).select_related(
            'part__manufacturer', 'part__category'
        )
        serializer = FitmentLookupSerializer(fitments, many=True)
        return Response(serializer.data)


class FitmentViewSet(viewsets.ModelViewSet):
    """API endpoint for part-vehicle fitments"""
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
    """API endpoint for manufacturers"""
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'abbreviation']
    ordering = ['name']


class MakeViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for vehicle makes"""
    queryset = Make.objects.filter(is_active=True)
    serializer_class = MakeSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering = ['name']


class ModelViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for vehicle models"""
    queryset = Model.objects.select_related('make').filter(is_active=True)
    serializer_class = ModelSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['make']
    search_fields = ['name', 'make__name']
    ordering = ['make__name', 'name']


class EngineViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for engines"""
    queryset = Engine.objects.all()
    serializer_class = EngineSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['fuel_type', 'aspiration', 'cylinders']
    search_fields = ['name', 'engine_code']
    ordering = ['name']


class InterchangeGroupViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for interchange groups"""
    queryset = InterchangeGroup.objects.select_related('category')
    serializer_class = InterchangeGroupSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['name', 'description']
    ordering = ['name']


# Custom API Views for specific lookup operations
class PartFitmentsView(APIView):
    """Get all vehicles that a specific part fits"""
    
    def get(self, request, part_id):
        part = get_object_or_404(Part, id=part_id, is_active=True)
        fitments = Fitment.objects.filter(part=part).select_related(
            'vehicle__make', 'vehicle__model', 'vehicle__trim', 'vehicle__engine'
        )
        
        data = {
            'part': PartLookupSerializer(part).data,
            'fitments': FitmentLookupSerializer(fitments, many=True).data,
            'total_vehicles': fitments.count()
        }
        return Response(data)


class VehiclePartsView(APIView):
    """Get all parts that fit a specific vehicle"""
    
    def get(self, request, vehicle_id):
        vehicle = get_object_or_404(Vehicle, id=vehicle_id, is_active=True)
        fitments = Fitment.objects.filter(vehicle=vehicle).select_related(
            'part__manufacturer', 'part__category'
        )
        
        data = {
            'vehicle': VehicleLookupSerializer(vehicle).data,
            'fitments': FitmentLookupSerializer(fitments, many=True).data,
            'total_parts': fitments.count()
        }
        return Response(data)


class InterchangeLookupView(APIView):
    """Look up interchange parts by part number"""
    
    def get(self, request, part_number):
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
            ).exclude(id=part.id).select_related('manufacturer', 'category')
            interchangeable_parts.extend(group_parts)
        
        data = {
            'original_part': PartLookupSerializer(part).data,
            'interchange_groups': InterchangeGroupSerializer(interchange_groups, many=True).data,
            'interchangeable_parts': PartLookupSerializer(interchangeable_parts, many=True).data,
            'total_interchanges': len(interchangeable_parts)
        }
        return Response(data)


class PartSearchView(APIView):
    """Advanced part search with multiple criteria"""
    
    def get(self, request):
        queryset = Part.objects.select_related('manufacturer', 'category').filter(is_active=True)
        
        # Search parameters
        part_number = request.GET.get('part_number')
        name = request.GET.get('name')
        manufacturer = request.GET.get('manufacturer')
        category = request.GET.get('category')
        
        # Apply filters
        if part_number:
            queryset = queryset.filter(part_number__icontains=part_number)
        if name:
            queryset = queryset.filter(name__icontains=name)
        if manufacturer:
            queryset = queryset.filter(manufacturer__name__icontains=manufacturer)
        if category:
            queryset = queryset.filter(category__name__icontains=category)
        
        # Limit results
        queryset = queryset[:100]
        
        serializer = PartLookupSerializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'count': len(serializer.data)
        })


class VehicleSearchView(APIView):
    """Advanced vehicle search with multiple criteria"""
    
    def get(self, request):
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
        queryset = queryset[:100]
        
        serializer = VehicleLookupSerializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'count': len(serializer.data)
        })


class FitmentSearchView(APIView):
    """Search fitments by part or vehicle criteria"""
    
    def get(self, request):
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
        queryset = queryset[:100]
        
        serializer = FitmentLookupSerializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'count': len(serializer.data)
        })


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
    """Get database statistics"""
    
    def get(self, request):
        stats = {
            'parts': {
                'total': Part.objects.count(),
                'active': Part.objects.filter(is_active=True).count(),
                'by_manufacturer': dict(
                    Part.objects.values_list('manufacturer__name').annotate(
                        count=Count('id')
                    ).order_by('-count')[:10]
                )
            },
            'vehicles': {
                'total': Vehicle.objects.count(),
                'active': Vehicle.objects.filter(is_active=True).count(),
                'by_make': dict(
                    Vehicle.objects.values_list('make__name').annotate(
                        count=Count('id')
                    ).order_by('-count')[:10]
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
                    ).order_by('-count')[:10]
                )
            },
            'interchange_groups': InterchangeGroup.objects.count()
        }
        return Response(stats)
