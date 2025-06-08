from django.contrib import admin
from django.db import models
from django.conf import settings
from .models import Fitment, FitmentNote, FitmentBulkImport


# Get page size from settings
ADMIN_PAGE_SIZE = getattr(settings, 'PARTS_INTERCHANGE', {}).get('ADMIN_LIST_PER_PAGE', 15)


class FitmentNoteInline(admin.TabularInline):
    model = FitmentNote
    extra = 0  # Reduced from 1 for performance
    max_num = 3  # Limit inline objects for performance
    show_change_link = True


@admin.register(Fitment)
class FitmentAdmin(admin.ModelAdmin):
    list_display = [
        'part_number', 'part_manufacturer', 'vehicle_year', 'vehicle_make', 
        'vehicle_model', 'position', 'quantity', 'is_verified', 'created_at'
    ]
    list_filter = [
        'is_verified', 'position', 'quantity', 'created_at',
        'part__category', 'vehicle__make', 'vehicle__year'
    ]
    search_fields = [
        'part__part_number', 'part__name',
        'vehicle__make__name', 'vehicle__model__name'
    ]
    readonly_fields = ['created_at', 'updated_at']
    inlines = [FitmentNoteInline]
    list_per_page = ADMIN_PAGE_SIZE  # Smaller page size for complex objects
    list_select_related = [
        'part__manufacturer', 'part__category',
        'vehicle__make', 'vehicle__model', 'vehicle__trim', 'vehicle__engine'
    ]
    ordering = ['-created_at']
    show_full_result_count = False
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'part__manufacturer', 'part__category',
            'vehicle__make', 'vehicle__model', 'vehicle__trim', 'vehicle__engine'
        )
    
    def part_number(self, obj):
        return obj.part.part_number
    part_number.short_description = 'Part #'
    part_number.admin_order_field = 'part__part_number'
    
    def part_manufacturer(self, obj):
        return obj.part.manufacturer.abbreviation
    part_manufacturer.short_description = 'Mfr'
    part_manufacturer.admin_order_field = 'part__manufacturer__name'
    
    def vehicle_year(self, obj):
        return obj.vehicle.year
    vehicle_year.short_description = 'Year' 
    vehicle_year.admin_order_field = 'vehicle__year'
    
    def vehicle_make(self, obj):
        return obj.vehicle.make.name
    vehicle_make.short_description = 'Make'
    vehicle_make.admin_order_field = 'vehicle__make__name'
    
    def vehicle_model(self, obj):
        return obj.vehicle.model.name
    vehicle_model.short_description = 'Model'
    vehicle_model.admin_order_field = 'vehicle__model__name'
    
    fieldsets = (
        ('Fitment Relationship', {
            'fields': ('part', 'vehicle')
        }),
        ('Fitment Details', {
            'fields': ('position', 'quantity', 'notes')
        }),
        ('Verification', {
            'fields': ('is_verified', 'verified_by', 'verification_date'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(FitmentNote)
class FitmentNoteAdmin(admin.ModelAdmin):
    list_display = ['fitment_summary', 'note_type', 'title', 'is_critical', 'created_at']
    list_filter = ['note_type', 'is_critical', 'created_at']
    search_fields = ['title', 'description', 'fitment__part__part_number']
    readonly_fields = ['created_at']
    list_per_page = ADMIN_PAGE_SIZE
    list_select_related = ['fitment__part', 'fitment__vehicle']
    show_full_result_count = False
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'fitment__part', 'fitment__vehicle'
        )
    
    def fitment_summary(self, obj):
        return f"{obj.fitment.part.part_number} → {obj.fitment.vehicle}"
    fitment_summary.short_description = 'Fitment'


@admin.register(FitmentBulkImport)
class FitmentBulkImportAdmin(admin.ModelAdmin):
    list_display = [
        'import_name', 'status', 'total_records', 
        'successful_imports', 'failed_imports', 'success_rate', 'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['import_name', 'description', 'file_name']
    readonly_fields = ['created_at', 'completed_at']
    list_per_page = ADMIN_PAGE_SIZE
    ordering = ['-created_at']
    show_full_result_count = False
    
    def success_rate(self, obj):
        if obj.total_records > 0:
            rate = (obj.successful_imports / obj.total_records) * 100
            return f"{rate:.1f}%"
        return "0%"
    success_rate.short_description = 'Success Rate'
    
    fieldsets = (
        ('Import Information', {
            'fields': ('import_name', 'description', 'file_name', 'created_by')
        }),
        ('Status', {
            'fields': ('status', 'created_at', 'completed_at')
        }),
        ('Results', {
            'fields': ('total_records', 'successful_imports', 'failed_imports')
        }),
        ('Log', {
            'fields': ('import_log',),
            'classes': ('collapse',)
        }),
    )
