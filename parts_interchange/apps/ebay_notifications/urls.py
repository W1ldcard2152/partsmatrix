from django.urls import path
from . import views

app_name = 'ebay_notifications'

urlpatterns = [
    path('marketplace-account-deletion/', views.MarketplaceAccountDeletionView.as_view(), name='marketplace-account-deletion'),
]
