from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'parts', views.PartViewSet, basename='part')
router.register(r'vehicles', views.VehicleViewSet, basename='vehicle')
router.register(r'fitments', views.FitmentViewSet, basename='fitment')
router.register(r'manufacturers', views.ManufacturerViewSet, basename='manufacturer')
router.register(r'makes', views.MakeViewSet, basename='make')
router.register(r'models', views.ModelViewSet, basename='model')
router.register(r'engines', views.EngineViewSet, basename='engine')
router.register(r'interchange-groups', views.InterchangeGroupViewSet, basename='interchangegroup')
router.register(r'part-groups', views.PartGroupViewSet, basename='partgroup')

app_name = 'api'

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
    
    # Custom, non-router endpoints
    path('stats/', views.DatabaseStatsView.as_view(), name='database-stats'),
    path('junkyard-search/', views.JunkyardSearchView.as_view(), name='junkyard-search'),
    path('bulk/fitments/', views.BulkFitmentCreateView.as_view(), name='bulk-fitment-create'),
]
