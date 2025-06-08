from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'parts', views.PartViewSet)
router.register(r'vehicles', views.VehicleViewSet)
router.register(r'fitments', views.FitmentViewSet)
router.register(r'manufacturers', views.ManufacturerViewSet)
router.register(r'makes', views.MakeViewSet)
router.register(r'models', views.ModelViewSet)
router.register(r'engines', views.EngineViewSet)
router.register(r'interchange-groups', views.InterchangeGroupViewSet)
router.register(r'part-groups', views.PartGroupViewSet)

app_name = 'api'

urlpatterns = [
    # API Root and router endpoints
    path('', include(router.urls)),
    
    # Custom interchange lookup endpoints
    path('lookup/part-fitments/<int:part_id>/', views.PartFitmentsView.as_view(), name='part-fitments'),
    path('lookup/vehicle-parts/<int:vehicle_id>/', views.VehiclePartsView.as_view(), name='vehicle-parts'),
    path('lookup/interchange/<str:part_number>/', views.InterchangeLookupView.as_view(), name='interchange-lookup'),
    
    # Search endpoints
    path('search/parts/', views.PartSearchView.as_view(), name='part-search'),
    path('search/vehicles/', views.VehicleSearchView.as_view(), name='vehicle-search'),
    path('search/fitments/', views.FitmentSearchView.as_view(), name='fitment-search'),
    
    # Bulk operations
    path('bulk/fitments/', views.BulkFitmentCreateView.as_view(), name='bulk-fitments'),
    
    # Statistics endpoint
    path('stats/', views.DatabaseStatsView.as_view(), name='stats'),
    
    # Part Groups endpoints
    path('junkyard-search/', views.JunkyardSearchView.as_view(), name='junkyard-search'),
]
