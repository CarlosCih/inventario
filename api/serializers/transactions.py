from attr import attrs
from rest_framework import serializers 
from inventory.models import Item
from transactions.models import *
from api.exceptions import *

# Lectura
class TransactionDetailSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source="item.name", read_only=True)
    
    class Meta:
        model = TransactionDetail
        fields = [
            "id",
            "item",
            "item_name",
            "quantity",
        ]
class InventoryTransactionSerializer(serializers.ModelSerializer):
    transation_type_name = serializers.CharField(source="transaction_type.name", read_only=True)
    status_name = serializers.CharField(source="status.name", read_only=True)
    details = TransactionDetailSerializer(many=True, read_only=True)
    
    class Meta:
        model = InventoryTransaction
        fields = [
            "id",
            "transaction_type",
            "transation_type_name",
            "status",
            "status_name",
            "reference",
            "number",
            "tags",
            "notes",
            "performed_at",
            "created_by",
            "is_applied",
            "applied_at",
            "created_at",
            "updated_at",
        ]
        
# Creacion
class TransactionDetailCreateSerializer(serializers.Serializer):
    item = serializers.IntegerField()
    quantity = serializers.DecimalField(max_digits=14, decimal_places=2)

    def validate_quantity(self, value):
        if value <= 0:
            raise InvalidQuantityException()
        return value
    
    def validate_item(self, value):
        try:
            item = Item.objects.get(pk=value)
        except Item.DoesNotExist:
            raise ItemNotFoundException(item_id=value)
        
        if not item.is_active:
            raise ItemInactiveException()
        return value
    
class InventoryTransactionCreateSerializer(serializers.Serializer):
    transaction_type = serializers.IntegerField()
    source_location = serializers.IntegerField(required=False, allow_null=True)
    target_location = serializers.IntegerField(required=False, allow_null=True)
    reference = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    details = TransactionDetailCreateSerializer(many=True)
    
    
    def validate(self, data):
        # Aquí se podrían agregar validaciones adicionales, como verificar que los IDs de artículos existan, que las cantidades sean positivas, etc.
        details = data.get("details", [])
        if not details:
            raise EmptyTransactionException()
        return data
    
class TransactionTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionTag
        fields = [
            'id',
            'name',
            'code',
            'decription',
            'color',
            'is_active',
            'is_auto',
            'created_at',
            'update_at'
        ]

class TransactionTypeSerializer(serializers.ModelSerializer):
    stock_effect_display = serializers.CharField(source="get_stock_effect_display", read_only=True)
    
    class Meta:
        model = TransactionType
        fields = [
            'id', 'code', 'name', 'description',
            'stock_effect', 'stock_effect_display',
            'requires_source_location', 'requires_target_location',
            'is_active', 'created_at', 'updated_at'
        ]

class TransactionStatusSerializer(serializers.ModelSerializer):
    class Meta:
        models = TransactionStatus
        fields = [
            'id','name','code','description','is_active','created_at','updated_at'
        ]