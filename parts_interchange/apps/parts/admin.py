from django.contrib import admin
from django.db import models
from django.conf import settings
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    Manufacturer, PartCategory, Part, InterchangeGroup, PartInterchange,
    PartGroup, PartGroupMembership, RawListingData, ConsensusFitment, ConflictingFitment
)


# Get page size from settings
ADMIN_PAGE_SIZE = getattr(settings, 'PARTS_INTERCHANGE', {}).get('ADMIN_LIST_PER_PAGE', 15)


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbreviation', 'country', 'parts_count', 'created_at']
    list_filter = ['country', 'created_at']
    search_fields = ['name', 'abbreviation']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = ADMIN_PAGE_SIZE
    ordering = ['name']
    show_full_result_count = False  # Performance improvement
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            parts_count=models.Count('parts')
        )
    
    def parts_count(self, obj):
        return obj.parts_count
    parts_count.short_description = 'Parts Count'
    parts_count.admin_order_field = 'parts_count'


@admin.register(PartCategory)
class PartCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent_category', 'parts_count', 'part_groups_count', 'created_at']
    list_filter = ['parent_category', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = ADMIN_PAGE_SIZE
    ordering = ['name']
    show_full_result_count = False
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parent_category').annotate(
            parts_count=models.Count('parts'),
            part_groups_count=models.Count('part_groups')
        )
    
    def parts_count(self, obj):
        return obj.parts_count
    parts_count.short_description = 'Parts'
    parts_count.admin_order_field = 'parts_count'
    
    def part_groups_count(self, obj):
        return obj.part_groups_count
    part_groups_count.short_description = 'Part Groups'
    part_groups_count.admin_order_field = 'part_groups_count'


class PartInterchangeInline(admin.TabularInline):
    model = PartInterchange
    extra = 0  # Reduced from 1 for performance
    max_num = 5  # Limit inline objects for performance
    show_change_link = True


class PartGroupMembershipInline(admin.TabularInline):
    model = PartGroupMembership
    extra = 0
    max_num = 3
    show_change_link = True
    fields = ['part_group', 'compatibility_level', 'is_verified', 'installation_notes']
    readonly_fields = ['created_at']


@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = [
        'part_number', 'manufacturer_name', 'name', 'category_name', 
        'part_groups_count', 'fitments_count', 'is_active'
    ]
    list_filter = ['manufacturer', 'category', 'is_active', 'created_at']
    search_fields = ['part_number', 'name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [PartGroupMembershipInline, PartInterchangeInline]
    list_per_page = ADMIN_PAGE_SIZE
    list_select_related = ['manufacturer', 'category']
    ordering = ['manufacturer__name', 'part_number']
    show_full_result_count = False
    
    actions = ['add_to_part_group', 'mark_verified']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'manufacturer', 'category'
        ).annotate(
            part_groups_count=models.Count('part_group_memberships'),
            fitments_count=models.Count('fitments')
        )
    
    def manufacturer_name(self, obj):
        return obj.manufacturer.name
    manufacturer_name.short_description = 'Manufacturer'
    manufacturer_name.admin_order_field = 'manufacturer__name'
    
    def category_name(self, obj):
        return obj.category.name
    category_name.short_description = 'Category'
    category_name.admin_order_field = 'category__name'
    
    def part_groups_count(self, obj):
        count = obj.part_groups_count
        if count > 0:
            return format_html('<span style="color: green;">{}</span>', count)
        return format_html('<span style="color: red;">0</span>')
    part_groups_count.short_description = 'Part Groups'
    part_groups_count.admin_order_field = 'part_groups_count'
    
    def fitments_count(self, obj):
        count = obj.fitments_count
        if count > 0:
            return format_html('<span style="color: blue;">{}</span>', count)
        return format_html('<span style="color: orange;">0</span>')
    fitments_count.short_description = 'Vehicles'
    fitments_count.admin_order_field = 'fitments_count'
    
    def add_to_part_group(self, request, queryset):
        # This would open a form to add selected parts to a part group
        # Implementation would require custom view
        self.message_user(request, f"Selected {queryset.count()} parts for part group assignment")
    add_to_part_group.short_description = "Add selected parts to part group"
    
    def mark_verified(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"Marked {updated} parts as verified/active")
    mark_verified.short_description = "Mark selected parts as verified"
    
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


@admin.register(PartGroup)
class PartGroupAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category_name', 'parts_count', 'vehicle_coverage', 
        'voltage', 'amperage', 'is_active'
    ]
    list_filter = ['category', 'is_active', 'created_at', 'voltage']
    search_fields = ['name', 'description', 'mounting_pattern', 'connector_type']
    readonly_fields = ['created_at', 'updated_at', 'get_part_count', 'get_vehicle_coverage']
    list_per_page = ADMIN_PAGE_SIZE
    list_select_related = ['category']
    ordering = ['category__name', 'name']
    show_full_result_count = False
    
    actions = ['duplicate_part_group', 'export_compatibility_matrix']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category').annotate(
            parts_count=models.Count('memberships')
        )
    
    def category_name(self, obj):
        return obj.category.name
    category_name.short_description = 'Category'
    category_name.admin_order_field = 'category__name'
    
    def parts_count(self, obj):
        count = obj.parts_count
        if count > 0:
            url = reverse('admin:parts_partgroupmembership_changelist')
            return format_html('<a href="{}?part_group__id={}">{} parts</a>', url, obj.id, count)
        return format_html('<span style="color: red;">0 parts</span>')
    parts_count.short_description = 'Parts Count'
    parts_count.admin_order_field = 'parts_count'
    
    def vehicle_coverage(self, obj):
        return obj.get_vehicle_coverage()
    vehicle_coverage.short_description = 'Vehicle Years'
    
    def duplicate_part_group(self, request, queryset):
        for part_group in queryset:
            # Create duplicate with "(Copy)" suffix
            new_name = f"{part_group.name} (Copy)"
            PartGroup.objects.create(
                name=new_name,
                description=part_group.description,
                category=part_group.category,
                voltage=part_group.voltage,
                amperage=part_group.amperage,
                wattage=part_group.wattage,
                mounting_pattern=part_group.mounting_pattern,
                connector_type=part_group.connector_type,
                thread_size=part_group.thread_size,
                specifications=part_group.specifications.copy(),
                is_active=False,  # Start as inactive
                created_by=request.user.username if request.user.is_authenticated else ''
            )
        self.message_user(request, f"Created {queryset.count()} duplicate part groups")
    duplicate_part_group.short_description = "Duplicate selected part groups"
    
    def export_compatibility_matrix(self, request, queryset):
        # Would export compatibility data - placeholder for now
        self.message_user(request, f"Export compatibility matrix for {queryset.count()} part groups")
    export_compatibility_matrix.short_description = "Export compatibility matrix"
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category', 'is_active')
        }),
        ('Technical Specifications', {
            'fields': ('voltage', 'amperage', 'wattage'),
            'classes': ('wide',)
        }),
        ('Physical Properties', {
            'fields': ('mounting_pattern', 'connector_type', 'thread_size'),
            'classes': ('wide',)
        }),
        ('Dimensional Constraints', {
            'fields': ('max_length', 'max_width', 'max_height'),
            'classes': ('collapse',)
        }),
        ('Additional Specifications', {
            'fields': ('specifications',),
            'classes': ('collapse',),
            'description': 'JSON field for additional technical specifications'
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('get_part_count', 'get_vehicle_coverage'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PartGroupMembership)
class PartGroupMembershipAdmin(admin.ModelAdmin):
    list_display = [
        'part_number', 'part_manufacturer', 'part_group_name', 
        'compatibility_level', 'fitments_count', 'vehicle_years', 
        'is_verified'
    ]
    list_filter = [
        'compatibility_level', 'is_verified', 'created_at',
        'part_group__category', 'part__manufacturer'
    ]
    search_fields = [
        'part__part_number', 'part__name', 'part_group__name',
        'installation_notes'
    ]
    readonly_fields = ['created_at', 'updated_at', 'get_fitment_count', 'get_vehicle_years']
    list_per_page = ADMIN_PAGE_SIZE
    list_select_related = ['part__manufacturer', 'part_group__category']
    ordering = ['part_group__name', 'compatibility_level', 'part__part_number']
    show_full_result_count = False
    
    actions = ['mark_verified', 'mark_identical', 'bulk_verify']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'part__manufacturer', 'part_group__category'
        ).annotate(
            fitments_count=models.Count('part__fitments')
        )
    
    def part_number(self, obj):
        return obj.part.part_number
    part_number.short_description = 'Part Number'
    part_number.admin_order_field = 'part__part_number'
    
    def part_manufacturer(self, obj):
        return obj.part.manufacturer.abbreviation
    part_manufacturer.short_description = 'Mfg'
    part_manufacturer.admin_order_field = 'part__manufacturer__name'
    
    def part_group_name(self, obj):
        return obj.part_group.name
    part_group_name.short_description = 'Part Group'
    part_group_name.admin_order_field = 'part_group__name'
    
    def fitments_count(self, obj):
        count = obj.fitments_count
        if count > 0:
            return format_html('<span style="color: blue;">{}</span>', count)
        return format_html('<span style="color: orange;">0</span>')
    fitments_count.short_description = 'Fitments'
    fitments_count.admin_order_field = 'fitments_count'
    
    def vehicle_years(self, obj):
        return obj.get_vehicle_years()
    vehicle_years.short_description = 'Vehicle Years'
    
    def mark_verified(self, request, queryset):
        updated = queryset.update(is_verified=True, verified_by=request.user.username)
        self.message_user(request, f"Marked {updated} memberships as verified")
    mark_verified.short_description = "Mark as verified"
    
    def mark_identical(self, request, queryset):
        updated = queryset.update(compatibility_level='IDENTICAL')
        self.message_user(request, f"Marked {updated} memberships as identical compatibility")
    mark_identical.short_description = "Mark as identical compatibility"
    
    def bulk_verify(self, request, queryset):
        from datetime import date
        updated = queryset.update(
            is_verified=True,
            verified_by=request.user.username,
            verification_date=date.today()
        )
        self.message_user(request, f"Bulk verified {updated} memberships")
    bulk_verify.short_description = "Bulk verify with timestamp"
    
    fieldsets = (
        ('Relationship', {
            'fields': ('part', 'part_group', 'compatibility_level')
        }),
        ('Part-Specific Specifications', {
            'fields': ('part_voltage', 'part_amperage', 'part_wattage'),
            'classes': ('wide',)
        }),
        ('Installation & Compatibility', {
            'fields': ('installation_notes', 'year_restriction', 'application_restriction'),
            'classes': ('wide',)
        }),
        ('Verification', {
            'fields': ('is_verified', 'verified_by', 'verification_date'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('get_fitment_count', 'get_vehicle_years'),
            'classes': ('collapse',)
        }),
    )


@admin.register(InterchangeGroup)
class InterchangeGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_name', 'parts_count', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [PartInterchangeInline]
    list_per_page = ADMIN_PAGE_SIZE
    list_select_related = ['category']
    show_full_result_count = False
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category').annotate(
            parts_count=models.Count('parts')
        )
    
    def category_name(self, obj):
        return obj.category.name
    category_name.short_description = 'Category'
    category_name.admin_order_field = 'category__name'
    
    def parts_count(self, obj):
        return obj.parts_count
    parts_count.short_description = 'Parts Count'
    parts_count.admin_order_field = 'parts_count'


@admin.register(PartInterchange)
class PartInterchangeAdmin(admin.ModelAdmin):
    list_display = ['part_number', 'part_manufacturer', 'interchange_group', 'is_primary', 'created_at']
    list_filter = ['is_primary', 'created_at', 'interchange_group__category']
    search_fields = ['part__part_number', 'part__name', 'interchange_group__name']
    readonly_fields = ['created_at']
    list_per_page = ADMIN_PAGE_SIZE
    list_select_related = ['part__manufacturer', 'interchange_group']
    show_full_result_count = False
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'part__manufacturer', 'interchange_group'
        )
    
    def part_number(self, obj):
        return obj.part.part_number
    part_number.short_description = 'Part Number'
    part_number.admin_order_field = 'part__part_number'
    
    def part_manufacturer(self, obj):
        return obj.part.manufacturer.abbreviation
    part_manufacturer.short_description = 'Manufacturer'
    part_manufacturer.admin_order_field = 'part__manufacturer__name'


# Custom admin site configuration
admin.site.site_header = "Parts Matrix - Interchange Database"
admin.site.site_title = "Parts Matrix Admin"
admin.site.index_title = "Automotive Parts Interchange Management"

# Performance hint for admin
admin.site.enable_nav_sidebar = False  # Disable sidebar for better performance


# ===== CONSENSUS-BASED FITMENT ADMIN (Phase 1) =====

@admin.register(RawListingData)
class RawListingDataAdmin(admin.ModelAdmin):
    list_display = [
        'part_number', 'vehicle_year', 'vehicle_make', 'vehicle_model', 
        'seller_feedback_count', 'seller_is_business', 'quality_weight',
        'extraction_date'
    ]
    list_filter = [
        'vehicle_year', 'vehicle_make', 'seller_is_business', 
        'is_verified_seller', 'has_oem_reference', 'extraction_date'
    ]
    search_fields = ['part_number', 'vehicle_make', 'vehicle_model', 'listing_title']
    readonly_fields = ['extraction_date', 'quality_weight', 'get_fitment_signature']
    list_per_page = ADMIN_PAGE_SIZE
    ordering = ['-extraction_date']
    show_full_result_count = False
    
    actions = ['mark_verified_seller', 'mark_has_oem_reference', 'process_consensus']
    
    def quality_weight(self, obj):
        weight = obj.calculate_quality_weight()
        if weight >= 2.0:
            return format_html('<span style="color: green; font-weight: bold;">{:.2f}</span>', weight)
        elif weight >= 1.5:
            return format_html('<span style="color: orange;">{:.2f}</span>', weight)
        else:
            return format_html('<span style="color: red;">{:.2f}</span>', weight)
    quality_weight.short_description = 'Quality Weight'
    
    def get_fitment_signature(self, obj):
        return obj.get_fitment_signature()
    get_fitment_signature.short_description = 'Fitment Signature'
    
    def mark_verified_seller(self, request, queryset):
        updated = queryset.update(is_verified_seller=True)
        self.message_user(request, f"Marked {updated} listings as verified seller")
    mark_verified_seller.short_description = "Mark as verified seller"
    
    def mark_has_oem_reference(self, request, queryset):
        updated = queryset.update(has_oem_reference=True)
        self.message_user(request, f"Marked {updated} listings as having OEM reference")
    mark_has_oem_reference.short_description = "Mark as having OEM reference"
    
    def process_consensus(self, request, queryset):
        from .consensus.processor import FitmentConsensusProcessor
        processor = FitmentConsensusProcessor()
        
        part_numbers = queryset.values_list('part_number', flat=True).distinct()
        processed_count = 0
        
        for part_number in part_numbers:
            result = processor.process_part_number(part_number)
            processed_count += result.get('processed', 0)
        
        self.message_user(request, f"Processed consensus for {len(part_numbers)} part numbers, created/updated {processed_count} consensus fitments")
    process_consensus.short_description = "Process consensus fitments for selected listings"
    
    fieldsets = (
        ('Part Information', {
            'fields': ('part_number',)
        }),
        ('Vehicle Fitment', {
            'fields': ('vehicle_year', 'vehicle_make', 'vehicle_model', 'vehicle_trim', 'vehicle_engine')
        }),
        ('Source Data', {
            'fields': ('source_ebay_item_id', 'listing_title', 'listing_price')
        }),
        ('Seller Information', {
            'fields': ('seller_feedback_count', 'seller_is_business', 'is_verified_seller')
        }),
        ('Quality Indicators', {
            'fields': ('has_oem_reference', 'has_detailed_description')
        }),
        ('Metadata', {
            'fields': ('extraction_date', 'quality_weight', 'get_fitment_signature'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ConsensusFitment)
class ConsensusFitmentAdmin(admin.ModelAdmin):
    list_display = [
        'part_number', 'vehicle_year', 'vehicle_make', 'vehicle_model',
        'confidence_score', 'status', 'supporting_listings_count', 
        'production_ready', 'last_updated'
    ]
    list_filter = [
        'status', 'vehicle_year', 'vehicle_make', 'last_updated'
    ]
    search_fields = ['part_number', 'vehicle_make', 'vehicle_model']
    readonly_fields = ['last_updated', 'production_ready', 'get_fitment_signature']
    list_per_page = ADMIN_PAGE_SIZE
    ordering = ['-confidence_score', 'part_number']
    show_full_result_count = False
    
    actions = ['mark_verified', 'mark_rejected', 'export_production_ready']
    
    def production_ready(self, obj):
        if obj.is_production_ready():
            return format_html('<span style="color: green; font-weight: bold;">✓ Ready</span>')
        else:
            return format_html('<span style="color: red;">✗ Not Ready</span>')
    production_ready.short_description = 'Production Ready'
    production_ready.boolean = True
    
    def get_fitment_signature(self, obj):
        return obj.get_fitment_signature()
    get_fitment_signature.short_description = 'Fitment Signature'
    
    def mark_verified(self, request, queryset):
        updated = queryset.update(status='VERIFIED')
        self.message_user(request, f"Marked {updated} consensus fitments as verified")
    mark_verified.short_description = "Mark as manually verified"
    
    def mark_rejected(self, request, queryset):
        updated = queryset.update(status='REJECTED')
        self.message_user(request, f"Marked {updated} consensus fitments as rejected")
    mark_rejected.short_description = "Mark as rejected/incorrect"
    
    def export_production_ready(self, request, queryset):
        production_ready = queryset.filter(status__in=['HIGH_CONFIDENCE', 'VERIFIED'], confidence_score__gte=80)
        self.message_user(request, f"Found {production_ready.count()} production-ready fitments out of {queryset.count()} selected")
    export_production_ready.short_description = "Export production-ready fitments"
    
    fieldsets = (
        ('Part Information', {
            'fields': ('part_number',)
        }),
        ('Vehicle Fitment', {
            'fields': ('vehicle_year', 'vehicle_make', 'vehicle_model', 'vehicle_trim', 'vehicle_engine')
        }),
        ('Consensus Metrics', {
            'fields': ('confidence_score', 'supporting_listings_count', 'total_weight_score', 'status')
        }),
        ('Source Data', {
            'fields': ('supporting_raw_listings',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('last_updated', 'production_ready', 'get_fitment_signature'),
            'classes': ('collapse',)
        }),
    )
    
    filter_horizontal = ['supporting_raw_listings']


@admin.register(ConflictingFitment)
class ConflictingFitmentAdmin(admin.ModelAdmin):
    list_display = [
        'part_number', 'conflict_description_short', 'resolution_status',
        'conflicting_listings_count', 'created_date', 'resolved_by'
    ]
    list_filter = [
        'resolution_status', 'created_date', 'resolved_date'
    ]
    search_fields = ['part_number', 'conflict_description', 'resolution_notes']
    readonly_fields = ['created_date', 'conflicting_listings_count']
    list_per_page = ADMIN_PAGE_SIZE
    ordering = ['-created_date']
    show_full_result_count = False
    
    actions = ['mark_resolved', 'mark_dismissed', 'bulk_review']
    
    def conflict_description_short(self, obj):
        return obj.conflict_description[:50] + '...' if len(obj.conflict_description) > 50 else obj.conflict_description
    conflict_description_short.short_description = 'Conflict Description'
    
    def conflicting_listings_count(self, obj):
        return obj.conflicting_listings.count()
    conflicting_listings_count.short_description = 'Listings Count'
    
    def mark_resolved(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            resolution_status='RESOLVED',
            resolved_date=timezone.now(),
            resolved_by=request.user.username
        )
        self.message_user(request, f"Marked {updated} conflicts as resolved")
    mark_resolved.short_description = "Mark as resolved"
    
    def mark_dismissed(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            resolution_status='DISMISSED',
            resolved_date=timezone.now(),
            resolved_by=request.user.username
        )
        self.message_user(request, f"Dismissed {updated} conflicts as false positives")
    mark_dismissed.short_description = "Dismiss as false positive"
    
    def bulk_review(self, request, queryset):
        pending_count = queryset.filter(resolution_status='PENDING').count()
        self.message_user(request, f"Found {pending_count} conflicts pending review out of {queryset.count()} selected")
    bulk_review.short_description = "Review conflict status"
    
    fieldsets = (
        ('Conflict Information', {
            'fields': ('part_number', 'conflict_description')
        }),
        ('Resolution', {
            'fields': ('resolution_status', 'resolved_by', 'resolved_date', 'resolution_notes')
        }),
        ('Source Data', {
            'fields': ('conflicting_listings',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_date', 'conflicting_listings_count'),
            'classes': ('collapse',)
        }),
    )
    
    filter_horizontal = ['conflicting_listings']
