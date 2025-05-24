from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime


class Make(models.Model):
    """Vehicle manufacturers (Chevrolet, Ford, Toyota, etc.)"""
    name = models.CharField(max_length=100, unique=True)
    country = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Model(models.Model):
    """Vehicle models (Camaro, F-150, Camry, etc.)"""
    make = models.ForeignKey(
        Make, 
        on_delete=models.CASCADE,
        related_name='models'
    )
    name = models.CharField(max_length=100)
    body_style = models.CharField(
        max_length=50, 
        blank=True,
        help_text="Sedan, Coupe, SUV, Truck, etc."
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['make', 'name']
        unique_together = ['make', 'name']

    def __str__(self):
        return f"{self.make.name} {self.name}"


class Engine(models.Model):
    """Engine specifications"""
    FUEL_TYPE_CHOICES = [
        ('GAS', 'Gasoline'),
        ('DSL', 'Diesel'),
        ('HYB', 'Hybrid'),
        ('ELC', 'Electric'),
        ('E85', 'E85 Ethanol'),
    ]
    
    ASPIRATION_CHOICES = [
        ('NA', 'Naturally Aspirated'),
        ('TC', 'Turbocharged'),
        ('SC', 'Supercharged'),
        ('TSC', 'Twin Supercharged'),
    ]

    name = models.CharField(max_length=100, unique=True)
    displacement = models.DecimalField(
        max_digits=4, 
        decimal_places=1, 
        help_text="Engine displacement in liters",
        null=True,
        blank=True
    )
    cylinders = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(16)],
        null=True,
        blank=True
    )
    fuel_type = models.CharField(max_length=3, choices=FUEL_TYPE_CHOICES, default='GAS')
    aspiration = models.CharField(max_length=3, choices=ASPIRATION_CHOICES, default='NA')
    horsepower = models.PositiveIntegerField(null=True, blank=True)
    torque = models.PositiveIntegerField(null=True, blank=True, help_text="Torque in lb-ft")
    engine_code = models.CharField(max_length=20, blank=True, help_text="Manufacturer engine code")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        displacement_str = f"{self.displacement}L " if self.displacement else ""
        cylinder_str = f"V{self.cylinders} " if self.cylinders else ""
        return f"{displacement_str}{cylinder_str}{self.name}"


class Trim(models.Model):
    """Vehicle trim levels (Base, LT, LTZ, etc.)"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Vehicle(models.Model):
    """Complete vehicle specifications following eBay's Year/Make/Model/Trim/Engine format"""
    year = models.PositiveIntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(datetime.now().year + 2)]
    )
    make = models.ForeignKey(
        Make,
        on_delete=models.CASCADE,
        related_name='vehicles'
    )
    model = models.ForeignKey(
        Model,
        on_delete=models.CASCADE,
        related_name='vehicles'
    )
    generation = models.CharField(
        max_length=20,
        blank=True,
        help_text="Model generation (e.g., 'Gen 3', '2nd Gen', 'Mk IV') - use when generation affects parts compatibility"
    )
    trim = models.ForeignKey(
        Trim,
        on_delete=models.CASCADE,
        related_name='vehicles',
        null=True,
        blank=True
    )
    engine = models.ForeignKey(
        Engine,
        on_delete=models.CASCADE,
        related_name='vehicles',
        null=True,
        blank=True
    )
    
    # Additional specifications
    transmission_type = models.CharField(
        max_length=20,
        choices=[
            ('AUTO', 'Automatic'),
            ('MANUAL', 'Manual'),
            ('CVT', 'CVT'),
        ],
        blank=True
    )
    drivetrain = models.CharField(
        max_length=10,
        choices=[
            ('FWD', 'Front Wheel Drive'),
            ('RWD', 'Rear Wheel Drive'),
            ('AWD', 'All Wheel Drive'),
            ('4WD', '4 Wheel Drive'),
        ],
        blank=True
    )
    
    # Build date range for precise fitment
    build_start_date = models.DateField(null=True, blank=True)
    build_end_date = models.DateField(null=True, blank=True)
    
    # Additional notes for specific applications
    notes = models.TextField(
        blank=True,
        help_text="Additional specifications like gear ratios, build dates, etc."
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['year', 'make', 'model', 'generation', 'trim']
        unique_together = ['year', 'make', 'model', 'generation', 'trim', 'engine']

    def __str__(self):
        base_str = f"{self.year} {self.make.name} {self.model.name}"
        if self.generation:
            base_str += f" {self.generation}"
        if self.trim:
            base_str += f" {self.trim.name}"
        if self.engine:
            base_str += f" ({self.engine})"
        return base_str
