from django.contrib import admin
from .models import Manufacturer, PartCategory, Part, InterchangeGroup, PartInterchange


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbreviation', 'country', 'created_at']
    list_filter = ['country', 'created_at']
    search_fields = ['name', 'abbreviation']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PartCategory)
class PartCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent_category', 'created_at']
    list_filter = ['parent_category', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


class PartInterchangeInline(admin.TabularInline):
    model = PartInterchange
    extra = 1


@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ['part_number', 'manufacturer', 'name', 'category', 'is_active', 'created_at']
    list_filter = ['manufacturer', 'category', 'is_active', 'created_at']
    search_fields = ['part_number', 'name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [PartInterchangeInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('manufacturer', 'part_number', 'name', 'category', 'description')
        }),
        ('Physical Specifications', {
            'fields': ('weight', 'dimensions'),
            'classes': ('collapse',)
        }),
        ('Status & Notes', {
            'fields': ('is_active', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(InterchangeGroup)
class InterchangeGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [PartInterchangeInline]


@admin.register(PartInterchange)
class PartInterchangeAdmin(admin.ModelAdmin):
    list_display = ['part', 'interchange_group', 'is_primary', 'created_at']
    list_filter = ['is_primary', 'created_at', 'interchange_group__category']
    search_fields = ['part__part_number', 'part__name', 'interchange_group__name']
    readonly_fields = ['created_at']
