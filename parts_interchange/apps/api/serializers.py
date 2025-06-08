from rest_framework import serializers
from apps.parts.models import Part, Manufacturer, PartCategory, InterchangeGroup, PartGroup, PartGroupMembership
from apps.vehicles.models import Vehicle, Make, Model, Engine, Trim
from apps.fitments.models import Fitment


class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = ['id', 'name', 'abbreviation', 'country']


class PartCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PartCategory
        fields = ['id', 'name', 'description']


class PartSerializer(serializers.ModelSerializer):
    manufacturer = ManufacturerSerializer(read_only=True)
    category = PartCategorySerializer(read_only=True)
    
    class Meta:
        model = Part
        fields = [
            'id', 'part_number', 'name', 'description',
            'manufacturer', 'category', 'weight', 'dimensions',
            'is_active', 'created_at'
        ]


class MakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Make
        fields = ['id', 'name', 'country']


class ModelSerializer(serializers.ModelSerializer):
    make = MakeSerializer(read_only=True)
    
    class Meta:
        model = Model
        fields = ['id', 'name', 'body_style', 'make']


class EngineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Engine
        fields = [
            'id', 'name', 'displacement', 'cylinders', 
            'fuel_type', 'aspiration', 'horsepower', 'torque', 'engine_code'
        ]


class TrimSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trim
        fields = ['id', 'name', 'description']


class VehicleSerializer(serializers.ModelSerializer):
    make = MakeSerializer(read_only=True)
    model = ModelSerializer(read_only=True)
    trim = TrimSerializer(read_only=True)
    engine = EngineSerializer(read_only=True)
    
    class Meta:
        model = Vehicle
        fields = [
            'id', 'year', 'make', 'model', 'trim', 'engine',
            'transmission_type', 'drivetrain', 'notes'
        ]


class FitmentSerializer(serializers.ModelSerializer):
    part = PartSerializer(read_only=True)
    vehicle = VehicleSerializer(read_only=True)
    
    class Meta:
        model = Fitment
        fields = [
            'id', 'part', 'vehicle', 'position', 'quantity',
            'notes', 'is_verified', 'verified_by'
        ]


class InterchangeGroupSerializer(serializers.ModelSerializer):
    parts_count = serializers.SerializerMethodField()
    category = PartCategorySerializer(read_only=True)
    
    class Meta:
        model = InterchangeGroup
        fields = ['id', 'name', 'description', 'category', 'parts_count']
    
    def get_parts_count(self, obj):
        return obj.parts.count()


# Simplified serializers for lookup responses
class PartLookupSerializer(serializers.ModelSerializer):
    manufacturer_name = serializers.CharField(source='manufacturer.name', read_only=True)
    manufacturer_abbrev = serializers.CharField(source='manufacturer.abbreviation', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Part
        fields = [
            'id', 'part_number', 'name', 'manufacturer_name', 
            'manufacturer_abbrev', 'category_name'
        ]


class VehicleLookupSerializer(serializers.ModelSerializer):
    make_name = serializers.CharField(source='make.name', read_only=True)
    model_name = serializers.CharField(source='model.name', read_only=True)
    trim_name = serializers.CharField(source='trim.name', read_only=True)
    engine_name = serializers.CharField(source='engine.name', read_only=True)
    
    class Meta:
        model = Vehicle
        fields = [
            'id', 'year', 'make_name', 'model_name', 
            'trim_name', 'engine_name'
        ]


class FitmentLookupSerializer(serializers.ModelSerializer):
    part = PartLookupSerializer(read_only=True)
    vehicle = VehicleLookupSerializer(read_only=True)
    
    class Meta:
        model = Fitment
        fields = ['part', 'vehicle', 'position', 'quantity', 'notes']


# Part Groups Serializers
class PartGroupSerializer(serializers.ModelSerializer):
    category = PartCategorySerializer(read_only=True)
    parts_count = serializers.SerializerMethodField()
    vehicle_coverage = serializers.SerializerMethodField()
    
    class Meta:
        model = PartGroup
        fields = [
            'id', 'name', 'description', 'category',
            'voltage', 'amperage', 'wattage',
            'mounting_pattern', 'connector_type', 'thread_size',
            'max_length', 'max_width', 'max_height',
            'specifications', 'parts_count', 'vehicle_coverage',
            'is_active', 'created_at'
        ]
    
    def get_parts_count(self, obj):
        return obj.memberships.count()
    
    def get_vehicle_coverage(self, obj):
        return obj.get_vehicle_coverage()


class PartGroupMembershipSerializer(serializers.ModelSerializer):
    part = PartLookupSerializer(read_only=True)
    part_group_name = serializers.CharField(source='part_group.name', read_only=True)
    
    class Meta:
        model = PartGroupMembership
        fields = [
            'id', 'part', 'part_group_name', 'compatibility_level',
            'part_voltage', 'part_amperage', 'part_wattage',
            'installation_notes', 'year_restriction', 'application_restriction',
            'is_verified', 'verified_by', 'verification_date'
        ]


class PartGroupLookupSerializer(serializers.ModelSerializer):
    """Simplified serializer for part group lookups"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    parts_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PartGroup
        fields = [
            'id', 'name', 'description', 'category_name',
            'voltage', 'amperage', 'mounting_pattern', 'connector_type',
            'parts_count'
        ]
    
    def get_parts_count(self, obj):
        return obj.memberships.count()
