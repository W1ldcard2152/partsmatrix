from django.contrib import admin
from .models import Make, Model, Engine, Trim, Vehicle


@admin.register(Make)
class MakeAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'is_active', 'created_at']
    list_filter = ['country', 'is_active', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Model)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'make', 'body_style', 'is_active', 'created_at']
    list_filter = ['make', 'body_style', 'is_active', 'created_at']
    search_fields = ['name', 'make__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Engine)
class EngineAdmin(admin.ModelAdmin):
    list_display = ['name', 'displacement', 'cylinders', 'fuel_type', 'horsepower', 'created_at']
    list_filter = ['fuel_type', 'aspiration', 'cylinders', 'created_at']
    search_fields = ['name', 'engine_code']
    readonly_fields = ['created_at', 'updated_at']
    
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
    list_display = ['name', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['year', 'make', 'model', 'trim', 'engine', 'transmission_type', 'is_active']
    list_filter = ['year', 'make', 'transmission_type', 'drivetrain', 'is_active', 'created_at']
    search_fields = ['make__name', 'model__name', 'trim__name', 'engine__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Vehicle Identification', {
            'fields': ('year', 'make', 'model', 'trim', 'engine')
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
    
    # Custom filters for better navigation
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'make', 'model', 'trim', 'engine'
        )
