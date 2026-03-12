from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter, SearchFilter
from datetime import datetime
from api.pagination import StandardResultsSetPagination
from api.permissions import CanManageTransactions, IsManagerOrAdmin
from transactions.models import *
from transactions.services import *
from api.serializers.transactions import *
from api.exceptions import *

class TransactionsViewSet(viewsets.ModelViewSet):
    permission_classes = [CanManageTransactions]
    pagination_class = StandardResultsSetPagination
    queryset = InventoryTransaction.objects.select_related(
        "transaction_type",
        "status",
        "source_location",
        "target_location"
    ).prefetch_related("details").all().order_by("-created_at")

    filter_backends = [OrderingFilter, SearchFilter]
    search_fields = [
        'number',
        'reference',
        'notes',
        'transaction_type__name',
        'created_by__username',
    ]
    ordering_fields = [
        'number',
        'performed_at',
        'created_at',
        'transaction_type__name',
        'status__name',
        'is_applied',
    ]
    ordering = ['-performed_at']

    def get_serializer_class(self):
        if self.action == "create":
            return InventoryTransactionCreateSerializer
        return InventoryTransactionSerializer
    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtro por tipo de transacción
        transaction_type = self.request.query_params.get("transaction_type", None)
        if transaction_type is not None:
            queryset = queryset.filter(transaction_type_id=transaction_type)

        # Filtro por estado
        status = self.request.query_params.get("status", None)
        if status is not None:
            queryset = queryset.filter(status_id=status)

        # Filtrar por is_applied
        is_applied = self.request.query_params.get('is_applied', None)
        if is_applied is not None:
            queryset = queryset.filter(is_applied=is_applied.lower() == 'true')
        
        # Filtrar por usuario creador
        created_by = self.request.query_params.get('created_by', None)
        if created_by is not None:
            queryset = queryset.filter(created_by_id=created_by)
        
        # Filtrar por etiqueta
        tag = self.request.query_params.get('tag', None)
        if tag is not None:
            queryset = queryset.filter(tags__id=tag)
        
        # Filtrar por rango de fechas (performed_at)
        date_from = self.request.query_params.get('date_from', None)
        if date_from is not None:
            try:
                date_from_parsed = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(performed_at__date__gte=date_from_parsed)
            except ValueError:
                raise serializers.ValidationError("El formato de date_from debe ser YYYY-MM-DD.")
        
        date_to = self.request.query_params.get('date_to', None)
        if date_to is not None:
            try:
                date_to_parsed = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(performed_at__date__lte=date_to_parsed)
            except ValueError:
                raise serializers.ValidationError("El formato de date_to debe ser YYYY-MM-DD.")
        
        # Filtrar por mes específico
        month = self.request.query_params.get('month', None)
        if month is not None:
            try:
                queryset = queryset.filter(performed_at__month=int(month))
            except ValueError:
                raise serializers.ValidationError("El formato de month debe ser un número entero.")
        
        # Filtrar por año específico
        year = self.request.query_params.get('year', None)
        if year is not None:
            try:
                queryset = queryset.filter(performed_at__year=int(year))
            except ValueError:
                raise serializers.ValidationError("El formato de year debe ser un número entero.")

        return queryset
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        transaction = create_transaction(
            user=request.user,
            validated_data=serializer.validated_data,
        )

        output_serializer = InventoryTransactionSerializer(transaction)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        transaction = self.get_object()

        if transaction.is_applied:
            raise TransactionAlreadyAppliedException()
        
        if not request.user.is_staff:
            if transaction.created_by != request.user:
                raise OnlyOwnerCanEditException()
            
    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        transaction = self.get_object()
        try:
            apply_transaction(transaction)
            return Response({
                'message': 'Transacción aplicada exitosamente.'
            })
        except InsufficientPermissionsException as e:
            raise e
        
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        transaction = self.get_object()
        try:
            cancel_transaction(transaction)
            return Response({
                'message': 'Transacción cancelada exitosamente.'
            })
        except InsufficientPermissionsException as e:
            raise e
        
class TransactionTagViewSet(viewsets.ModelViewSet):
    permission_classes = [IsManagerOrAdmin]
    queryset = TransactionTag.objects.all()
    serializer_class = TransactionTagSerializer

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name','code','description']
    ordering_fields = ['name','code','created_at']
    ordering = ['name']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        is_auto = self.request.query_params.get('is_auto', None)
        if is_auto is not None:
            queryset = queryset.filter(is_auto=is_auto.lower() == 'true')
        
        return queryset
class TransactionTypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar tipos de transacción
    """
    # permission_classes = [IsManagerOrAdmin]
    pagination_class = StandardResultsSetPagination
    queryset = TransactionType.objects.all()
    serializer_class = TransactionTypeSerializer
    
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por efecto en stock
        stock_effect = self.request.query_params.get('stock_effect', None)
        if stock_effect is not None:
            queryset = queryset.filter(stock_effect=stock_effect)
        
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset


class TransactionStatusViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar estados de transacción
    """
    # permission_classes = [IsManagerOrAdmin]
    pagination_class = StandardResultsSetPagination
    queryset = TransactionStatus.objects.all()
    serializer_class = TransactionStatusSerializer
    
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset