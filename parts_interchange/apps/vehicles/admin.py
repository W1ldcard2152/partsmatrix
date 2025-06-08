from django.contrib import admin
from django.db import models
from django.conf import settings
from .models import Make, Model, Engine, Trim, Vehicle


# Get page size from settings
ADMIN_PAGE_SIZE = getattr(settings, 'PARTS_INTERCHANGE', {}).get('ADMIN_LIST_PER_PAGE', 15)


@admin.register(Make)
class MakeAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'is_active', 'models_count', 'vehicles_count', 'created_at']
    list_filter = ['country', 'is_active', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = ADMIN_PAGE_SIZE
    ordering = ['name']
    show_full_result_count = False
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            models_count=models.Count('models', distinct=True),
            vehicles_count=models.Count('vehicles', distinct=True)
        )
    
    def models_count(self, obj):
        return obj.models_count
    models_count.short_description = 'Models'
    models_count.admin_order_field = 'models_count'
    
    def vehicles_count(self, obj):
        return obj.vehicles_count
    vehicles_count.short_description = 'Vehicles'
    vehicles_count.admin_order_field = 'vehicles_count'


@admin.register(Model)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'make_name', 'body_style', 'is_active', 'vehicles_count', 'created_at']
    list_filter = ['make', 'body_style', 'is_active', 'created_at']
    search_fields = ['name', 'make__name']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = ADMIN_PAGE_SIZE
    list_select_related = ['make']
    ordering = ['make__name', 'name']
    show_full_result_count = False
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('make').annotate(
            vehicles_count=models.Count('vehicles')
        )
    
    def make_name(self, obj):
        return obj.make.name
    make_name.short_description = 'Make'
    make_name.admin_order_field = 'make__name'
    
    def vehicles_count(self, obj):  
        return obj.vehicles_count
    vehicles_count.short_description = 'Vehicles'
    vehicles_count.admin_order_field = 'vehicles_count'


@admin.register(Engine)
class EngineAdmin(admin.ModelAdmin):
    list_display = ['name', 'displacement', 'cylinders', 'fuel_type', 'horsepower', 'vehicles_count', 'created_at']
    list_filter = ['fuel_type', 'aspiration', 'cylinders', 'created_at']
    search_fields = ['name', 'engine_code']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = ADMIN_PAGE_SIZE
    ordering = ['name']
    show_full_result_count = False
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            vehicles_count=models.Count('vehicles')
        )
    
    def vehicles_count(self, obj):
        return obj.vehicles_count
    vehicles_count.short_description = 'Vehicles'
    vehicles_count.admin_order_field = 'vehicles_count'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'engine_code')
        }),
        ('Engine Specifications', {
            'fields': ('displacement', 'cylinders', 'fuel_type', 'aspiration')
        }),
        ('Performance', {
            'fields': ('horsepower', 'torque'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Trim)
class TrimAdmin(admin.ModelAdmin):
    list_display = ['name', 'vehicles_count', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = ADMIN_PAGE_SIZE
    ordering = ['name']
    show_full_result_count = False
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            vehicles_count=models.Count('vehicles')
        )
    
    def vehicles_count(self, obj):
        return obj.vehicles_count
    vehicles_count.short_description = 'Vehicles'
    vehicles_count.admin_order_field = 'vehicles_count'


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['year', 'make_name', 'model_name', 'generation', 'trim_name', 'engine_name', 'transmission_type', 'is_active']
    list_filter = ['year', 'make', 'generation', 'transmission_type', 'drivetrain', 'is_active', 'created_at']
    search_fields = ['make__name', 'model__name', 'generation', 'trim__name', 'engine__name']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = ADMIN_PAGE_SIZE  # Smaller page size for complex objects
    list_select_related = ['make', 'model', 'trim', 'engine']
    ordering = ['year', 'make__name', 'model__name']
    show_full_result_count = False
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'make', 'model', 'trim', 'engine'
        )
    
    def make_name(self, obj):
        return obj.make.name
    make_name.short_description = 'Make'
    make_name.admin_order_field = 'make__name'
    
    def model_name(self, obj):
        return obj.model.name
    model_name.short_description = 'Model'
    model_name.admin_order_field = 'model__name'
    
    def trim_name(self, obj):
        return obj.trim.name if obj.trim else '-'
    trim_name.short_description = 'Trim'
    trim_name.admin_order_field = 'trim__name'
    
    def engine_name(self, obj):
        return obj.engine.name if obj.engine else '-'
    engine_name.short_description = 'Engine'
    engine_name.admin_order_field = 'engine__name'
    
    fieldsets = (
        ('Vehicle Identification', {
            'fields': ('year', 'make', 'model', 'generation', 'trim', 'engine')
        }),
        ('Drivetrain', {
            'fields': ('transmission_type', 'drivetrain')
        }),
        ('Build Information', {
            'fields': ('build_start_date', 'build_end_date'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('notes', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
