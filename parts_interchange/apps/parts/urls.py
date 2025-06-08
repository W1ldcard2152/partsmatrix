from django.urls import path
from . import views
from . import views_fast

app_name = 'parts'

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.part_search, name='search'),
    
    # Fast admin URLs
    path('fast/', views_fast.fast_dashboard, name='fast_dashboard'),
    path('fast/parts/', views_fast.fast_parts_list, name='fast_parts_list'),
    path('fast/parts/add/', views_fast.fast_part_add, name='fast_part_add'),
    path('fast/parts/<int:part_id>/edit/', views_fast.fast_part_edit, name='fast_part_edit'),
    path('fast/autocomplete/manufacturers/', views_fast.autocomplete_manufacturers, name='autocomplete_manufacturers'),
    path('fast/autocomplete/categories/', views_fast.autocomplete_categories, name='autocomplete_categories'),
]
