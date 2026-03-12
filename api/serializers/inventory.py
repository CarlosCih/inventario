from rest_framework import serializers
from inventory.models import Item, Asset, Stock

class ItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    unit_name = serializers.CharField(source='unitofmeasure.name', read_only=True)
    
    class Meta:
        model = Item
        fields = [
            'id', 'sku', 'name', 'description', 'category', 'category_name',
            'brand', 'brand_name', 'unitofmeasure', 'unit_name',
            'is_serialized', 'is_lot_controlled', 'has_expiration',
            'is_active', 'created_at', 'updated_at'
        ]        
class AssetSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    status_name = serializers.CharField(source='status.name', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True)
    
    class Meta:
        model = Asset
        fields = [
            'id', 'item', 'item_name', 'serial_number', 'lot_number',
            'expiration_date', 'status', 'status_name', 'location', 'location_name',
            'is_active', 'created_at', 'updated_at'
        ]
class StockSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True)
    
    class Meta:
        model = Stock
        fields = [
            'id', 'item', 'item_name', 'location', 'location_name',
            'quantity', 'unit_cost', 'total_cost',
            'last_updated'
        ]
    