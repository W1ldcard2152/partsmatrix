from django.contrib import admin
from .models import EbayAccountDeletionLog, EbayNotificationConfig


@admin.register(EbayAccountDeletionLog)
class EbayAccountDeletionLogAdmin(admin.ModelAdmin):
    list_display = ['notification_id', 'username', 'user_id', 'event_date', 'received_date', 'processed', 'processed_date']
    list_filter = ['processed', 'event_date', 'received_date', 'publish_attempt_count']
    search_fields = ['notification_id', 'username', 'user_id', 'eias_token']
    readonly_fields = ['notification_id', 'username', 'user_id', 'eias_token', 'event_date', 'publish_date', 'received_date', 'publish_attempt_count', 'created_at', 'updated_at']
    date_hierarchy = 'received_date'
    
    fieldsets = (
        ('eBay User Information', {
            'fields': ('notification_id', 'username', 'user_id', 'eias_token')
        }),
        ('Notification Details', {
            'fields': ('event_date', 'publish_date', 'received_date', 'publish_attempt_count')
        }),
        ('Processing Status', {
            'fields': ('processed', 'processed_date', 'deleted_data_summary')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(EbayNotificationConfig)
class EbayNotificationConfigAdmin(admin.ModelAdmin):
    list_display = ['endpoint_url', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Configuration', {
            'fields': ('verification_token', 'endpoint_url', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
