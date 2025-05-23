from django.db import models
from apps.parts.models import Part
from apps.vehicles.models import Vehicle


class Fitment(models.Model):
    """Junction table linking parts to compatible vehicles"""
    part = models.ForeignKey(
        Part,
        on_delete=models.CASCADE,
        related_name='fitments'
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='fitments'
    )
    
    # Fitment precision fields
    position = models.CharField(
        max_length=50,
        blank=True,
        help_text="Front, Rear, Left, Right, Upper, Lower, etc."
    )
    quantity = models.PositiveSmallIntegerField(
        default=1,
        help_text="Number of this part required per vehicle"
    )
    
    # Additional fitment specifications
    notes = models.TextField(
        blank=True,
        help_text="Special fitment requirements, exceptions, or additional specifications"
    )
    
    # Verification status
    is_verified = models.BooleanField(
        default=False,
        help_text="Has this fitment been verified for accuracy?"
    )
    verified_by = models.CharField(
        max_length=100,
        blank=True,
        help_text="Source of verification (catalog, manual, etc.)"
    )
    verification_date = models.DateField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, blank=True)

    class Meta:
        unique_together = ['part', 'vehicle', 'position']
        ordering = ['part', 'vehicle']

    def __str__(self):
        position_str = f" ({self.position})" if self.position else ""
        return f"{self.part} → {self.vehicle}{position_str}"


class FitmentNote(models.Model):
    """Additional notes and exceptions for specific fitments"""
    fitment = models.ForeignKey(
        Fitment,
        on_delete=models.CASCADE,
        related_name='additional_notes'
    )
    note_type = models.CharField(
        max_length=20,
        choices=[
            ('EXCEPTION', 'Exception'),
            ('REQUIREMENT', 'Requirement'),
            ('WARNING', 'Warning'),
            ('INFO', 'Information'),
        ],
        default='INFO'
    )
    title = models.CharField(max_length=100)
    description = models.TextField()
    is_critical = models.BooleanField(
        default=False,
        help_text="Is this note critical for proper fitment?"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_critical', 'note_type', 'title']

    def __str__(self):
        return f"{self.fitment} - {self.title}"


class FitmentBulkImport(models.Model):
    """Track bulk import operations for fitment data"""
    import_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file_name = models.CharField(max_length=200, blank=True)
    total_records = models.PositiveIntegerField(default=0)
    successful_imports = models.PositiveIntegerField(default=0)
    failed_imports = models.PositiveIntegerField(default=0)
    import_log = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('PROCESSING', 'Processing'),
            ('COMPLETED', 'Completed'),
            ('FAILED', 'Failed'),
        ],
        default='PENDING'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.import_name} - {self.status}"
