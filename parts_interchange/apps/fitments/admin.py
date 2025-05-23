from django.contrib import admin
from .models import Fitment, FitmentNote, FitmentBulkImport


class FitmentNoteInline(admin.TabularInline):
    model = FitmentNote
    extra = 1


@admin.register(Fitment)
class FitmentAdmin(admin.ModelAdmin):
    list_display = [
        'part', 'vehicle', 'position', 'quantity', 'is_verified', 'created_at'
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
    
    # Optimize queries
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'part__manufacturer', 'part__category',
            'vehicle__make', 'vehicle__model', 'vehicle__trim', 'vehicle__engine'
        )


@admin.register(FitmentNote)
class FitmentNoteAdmin(admin.ModelAdmin):
    list_display = ['fitment', 'note_type', 'title', 'is_critical', 'created_at']
    list_filter = ['note_type', 'is_critical', 'created_at']
    search_fields = ['title', 'description', 'fitment__part__part_number']
    readonly_fields = ['created_at']


@admin.register(FitmentBulkImport)
class FitmentBulkImportAdmin(admin.ModelAdmin):
    list_display = [
        'import_name', 'status', 'total_records', 
        'successful_imports', 'failed_imports', 'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['import_name', 'description', 'file_name']
    readonly_fields = ['created_at', 'completed_at']
    
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
