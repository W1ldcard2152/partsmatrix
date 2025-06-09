from django.urls import path
from . import views
from . import views_fast
from . import views_smart_parser

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
    
    # Smart Parser URLs
    path('smart-parser/', views_smart_parser.smart_parser_interface, name='smart_parser'),
    path('smart-parser/confirm/', views_smart_parser.confirm_parsed_part, name='confirm_parsed_part'),
    path('smart-parser/api/parse/', views_smart_parser.parse_text_api, name='parse_text_api'),
    path('smart-parser/bulk/', views_smart_parser.bulk_smart_parser, name='bulk_smart_parser'),
    path('smart-parser/bulk/confirm/', views_smart_parser.confirm_bulk_parts, name='confirm_bulk_parts'),
]
