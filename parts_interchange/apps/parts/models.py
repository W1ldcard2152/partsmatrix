from django.db import models
from django.core.validators import RegexValidator


class Manufacturer(models.Model):
    """Automotive manufacturers (GM, Ford, Toyota, etc.)"""
    name = models.CharField(max_length=100, unique=True)
    abbreviation = models.CharField(max_length=10, unique=True)
    country = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.abbreviation})"


class PartCategory(models.Model):
    """Categories for parts (Engine, Transmission, Suspension, etc.)"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    parent_category = models.ForeignKey(
        'self', 
        null=True, 
        blank=True, 
        on_delete=models.CASCADE,
        related_name='subcategories'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Part Categories'

    def __str__(self):
        if self.parent_category:
            return f"{self.parent_category.name} - {self.name}"
        return self.name


class Part(models.Model):
    """Individual automotive parts with manufacturer part numbers"""
    manufacturer = models.ForeignKey(
        Manufacturer, 
        on_delete=models.CASCADE,
        related_name='parts'
    )
    part_number = models.CharField(max_length=50)
    category = models.ForeignKey(
        PartCategory,
        on_delete=models.CASCADE,
        related_name='parts'
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Physical specifications
    weight = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Weight in pounds")
    dimensions = models.CharField(max_length=100, blank=True, help_text="L x W x H in inches")
    
    # Status and metadata
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['manufacturer', 'part_number']
        unique_together = ['manufacturer', 'part_number']

    def __str__(self):
        return f"{self.manufacturer.abbreviation}-{self.part_number}: {self.name}"


class InterchangeGroup(models.Model):
    """Groups of parts that are functionally equivalent across different part numbers"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        PartCategory,
        on_delete=models.CASCADE,
        related_name='interchange_groups'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class PartInterchange(models.Model):
    """Links parts that are interchangeable with each other"""
    part = models.ForeignKey(
        Part,
        on_delete=models.CASCADE,
        related_name='interchanges'
    )
    interchange_group = models.ForeignKey(
        InterchangeGroup,
        on_delete=models.CASCADE,
        related_name='parts'
    )
    is_primary = models.BooleanField(default=False, help_text="Primary part number for this group")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['part', 'interchange_group']

    def __str__(self):
        return f"{self.part} ↔ {self.interchange_group}"


class PartGroup(models.Model):
    """Functional compatibility groups for junkyard/interchange searches"""
    COMPATIBILITY_CHOICES = [
        ('IDENTICAL', 'Identical - Direct replacement'),
        ('COMPATIBLE', 'Compatible - Same function, minor differences'),
        ('CONDITIONAL', 'Conditional - Requires modification/adaptation'),
    ]
    
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    category = models.ForeignKey(
        PartCategory,
        on_delete=models.CASCADE,
        related_name='part_groups'
    )
    
    # Technical specifications for compatibility
    voltage = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True, help_text="Voltage (e.g., 12.0)")
    amperage = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True, help_text="Amperage/Current rating")
    wattage = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=True, help_text="Power rating in watts")
    
    # Physical specifications
    mounting_pattern = models.CharField(max_length=100, blank=True, help_text="Bolt pattern, mounting configuration")
    connector_type = models.CharField(max_length=100, blank=True, help_text="Electrical connector type")
    thread_size = models.CharField(max_length=50, blank=True, help_text="Thread size for bolts/fittings")
    
    # Dimensional constraints
    max_length = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Maximum length in inches")
    max_width = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Maximum width in inches")
    max_height = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Maximum height in inches")
    
    # Additional specifications (JSON field for flexibility)
    specifications = models.JSONField(default=dict, blank=True, help_text="Additional technical specifications")
    
    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['category__name', 'name']

    def __str__(self):
        return f"{self.name} ({self.category.name})"
    
    def get_part_count(self):
        return self.memberships.count()
    
    def get_vehicle_coverage(self):
        """Get years range of vehicles this part group covers"""
        from apps.fitments.models import Fitment
        fitments = Fitment.objects.filter(part__part_group_memberships__part_group=self)
        if fitments.exists():
            years = fitments.values_list('vehicle__year', flat=True)
            return f"{min(years)}-{max(years)}"
        return "No vehicles"


class PartGroupMembership(models.Model):
    """Links parts to functional compatibility groups"""
    COMPATIBILITY_LEVELS = [
        ('IDENTICAL', 'Identical - Direct replacement'),
        ('COMPATIBLE', 'Compatible - Same function, minor differences'),
        ('CONDITIONAL', 'Conditional - Requires modification/adaptation'),
    ]
    
    part = models.ForeignKey(
        Part,
        on_delete=models.CASCADE,
        related_name='part_group_memberships'
    )
    part_group = models.ForeignKey(
        PartGroup,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    
    compatibility_level = models.CharField(
        max_length=20,
        choices=COMPATIBILITY_LEVELS,
        default='COMPATIBLE'
    )
    
    # Part-specific specifications that may differ within group
    part_voltage = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    part_amperage = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    part_wattage = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=True)
    
    # Installation/compatibility notes
    installation_notes = models.TextField(
        blank=True,
        help_text="Specific installation requirements or compatibility notes"
    )
    
    # Restrictions
    year_restriction = models.CharField(
        max_length=20,
        blank=True,
        help_text="Year range restriction (e.g., '2005-2010')"
    )
    application_restriction = models.CharField(
        max_length=200,
        blank=True,
        help_text="Specific application restrictions"
    )
    
    # Verification
    is_verified = models.BooleanField(
        default=False,
        help_text="Has this compatibility been verified?"
    )
    verified_by = models.CharField(max_length=100, blank=True)
    verification_date = models.DateField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, blank=True)

    class Meta:
        unique_together = ['part', 'part_group']
        ordering = ['compatibility_level', 'part__part_number']

    def __str__(self):
        return f"{self.part.part_number} → {self.part_group.name} ({self.compatibility_level})"
    
    def get_fitment_count(self):
        """Get number of vehicle fitments for this part"""
        return self.part.fitments.count()
    
    def get_vehicle_years(self):
        """Get year range for vehicles this part fits"""
        fitments = self.part.fitments.all()
        if fitments.exists():
            years = [f.vehicle.year for f in fitments]
            if years:
                return f"{min(years)}-{max(years)}"
        return "No fitments"
