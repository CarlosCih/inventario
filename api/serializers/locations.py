from rest_framework import serializers
from locations.models import Area, LocationType, Location

class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = [
            'id',
            'name',
            'description',
            'is_active',
            'created_at',
            'updated_at'
        ]

class LocationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationType
        fields =[
            'id','name',
            'is_active',
            'created_at',
            'updated_at'
        ]

class LocationSerializer(serializers.ModelSerializer):
    area_name = serializers.CharField(
        source='area.name',
        read_only=True
    )
    location_type_name = serializers.CharField(
        source='location_type.name',
        read_only=True
    )

    class Meta:
        model = Location
        fields = [
            'id',
            'name',
            'code',
            'description',
            'location_type',
            'location_type_name',
            'area',
            'area_name',
            'is_active',
            'created_at',
            'updated_at'
        ]
class LocationCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = [
            'id',
            'name',
            'code',
            'description',
            'location_type',
            'area',
            'is_active',
        ]