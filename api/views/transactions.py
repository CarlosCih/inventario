from rest_framework import viewsets, status
from rest_framework.response import Response

from transactions.models import *
from transactions.services import *
from api.serializers.transactions import *

class TransactionsViewSet(viewsets.ModelViewSet):
    queryset = InventoryTransaction.objects.select_related(
        "transaction_type",
        "status",
        "source_location",
        "target_location"
    ).prefetch_related("details").all().order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "create":
            return InventoryTransactionCreateSerializer
        return InventoryTransactionSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        transaction = create_transaction(
            user=request.user,
            validated_data=serializer.validated_data,
        )

        output_serializer = InventoryTransactionSerializer(transaction)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)