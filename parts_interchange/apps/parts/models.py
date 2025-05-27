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
