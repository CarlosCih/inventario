from attr import attrs
from rest_framework import serializers 
from transactions.models import *


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
    
class InventoryTransactionCreateSerializer(serializers.Serializer):
    transaction_type = serializers.IntegerField()
    source_location = serializers.IntegerField(required=False, allow_null=True)
    target_location = serializers.IntegerField(required=False, allow_null=True)
    reference = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    details = TransactionDetailCreateSerializer(many=True)
    
    
    def validate(self, data):
        # Aquí se podrían agregar validaciones adicionales, como verificar que los IDs de artículos existan, que las cantidades sean positivas, etc.
        details = attrs.get("details", [])
        if not details:
            raise serializers.ValidationError("La transacción debe incluir al menos un detalle.")
        return attrs