from django.db import models
from django.utils import timezone


class EbayAccountDeletionLog(models.Model):
    """Log of eBay marketplace account deletion notifications received"""
    
    notification_id = models.CharField(max_length=255, unique=True, db_index=True)
    username = models.CharField(max_length=255, db_index=True)
    user_id = models.CharField(max_length=255, db_index=True)
    eias_token = models.TextField()
    
    event_date = models.DateTimeField()
    publish_date = models.DateTimeField()
    received_date = models.DateTimeField(default=timezone.now)
    publish_attempt_count = models.IntegerField()
    
    processed = models.BooleanField(default=False)
    processed_date = models.DateTimeField(null=True, blank=True)
    
    # Store any user data that was found and deleted
    deleted_data_summary = models.TextField(blank=True, help_text="Summary of what data was deleted for this user")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ebay_account_deletion_log'
        ordering = ['-received_date']
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['user_id']),
            models.Index(fields=['notification_id']),
            models.Index(fields=['processed']),
            models.Index(fields=['received_date']),
        ]
    
    def __str__(self):
        return f"eBay Account Deletion: {self.username} ({self.notification_id})"


class EbayNotificationConfig(models.Model):
    """Configuration for eBay notifications"""
    
    verification_token = models.CharField(max_length=80, help_text="32-80 character verification token for eBay notifications")
    endpoint_url = models.URLField(help_text="The notification endpoint URL")
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ebay_notification_config'
    
    def __str__(self):
        return f"eBay Notification Config - {self.endpoint_url}"
