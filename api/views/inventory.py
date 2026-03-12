from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from api.pagination import StandardResultsSetPagination
from api.permissions import IsManagerOrAdmin
from inventory.models import *
from api.serializers.inventory import *

class ItemViewSet(viewsets.ModelViewSet):
    permission_classes = [IsManagerOrAdmin]
    pagination_class = StandardResultsSetPagination
    queryset = Item.objects.select_related('category','brand','unitofmeasure').all().order_by('name')
    serializer_class = ItemSerializer

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['sku','name','description', 'category__name', 'brand__name']
    ordering_fields = ['sku','name','description', 'category__name', 'brand__name','created_at','updated_at']
    ordering = ['name']

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtro por categoria
        category = self.request.query_params.get('category', None)
        if category is not None:
            queryset = queryset.filter(category_id=category)
        
        # Filtro por marca
        brand = self.request.query_params.get('brand',None)
        if brand is not None:
            queryset = queryset.filter(brand_id=brand)
        
        # Filtro por is_serialized
        is_serialized = self.request.query_params.get('is_serialized', None)
        if is_serialized is not None:
            queryset = queryset.filter(is_serialized=is_serialized.lower() == 'true')

        # Filtro por is_lot_crontrolled
        is_lot_controlled = self.request.query_params.get('is_lot_controlled',None)
        if is_lot_controlled is not None:
            queryset = queryset.filter(is_lot_controlled=is_lot_controlled.lower() == 'true')
        
        # Filtro por has_expiration
        has_expiration = self.request.query_params.get('has_expiration',None)
        if has_expiration is not None:
            queryset = queryset.filter(has_expiration=has_expiration.lower() == 'true')

        # Filtro por is_active
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset
    @action(detail=True, methods=['post'])
    def low_stock(self, request, pk=None):
        item = self.get_object()
        low_stock = item.is_low_stock()
        return Response({'low_stock': low_stock})


class AssetViewSet(viewsets.ModelViewSet):
    permission_classes = [IsManagerOrAdmin]
    pagination_class = StandardResultsSetPagination
    queryset = Asset.objects.select_related('item','status','location','location__area').all().order_by('internal_code')
    serializer_class = AssetSerializer

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['num_serial','internal_code','item__name','item__sku','location__code','location__name','notes']
    ordering_fields = ['num_serial','internal_code','item__name','status__name','location__code', 'created_at','updated_at']
    ordering = ['internal_code']

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtro por item
        item = self.request.query_params.get('item', None)
        if item is not None:
            queryset = queryset.filter(item_id=item)

        # Filtro por estado
        status = self.request.query_params.get('status', None)
        if status is not None:
            queryset = queryset.filter(status_id=status)
        # Filtro por ubicación
        location = self.request.query_params.get('location', None)
        if location is not None:
            queryset = queryset.filter(location_id=location)
        # Filtro por area
        area = self.request.query_params.get('area', None)
        if area is not None:
            queryset = queryset.filter(location__area_id=area)
        # Filtro por activo
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset
        

class StockViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsManagerOrAdmin]
    pagination_class = StandardResultsSetPagination
    queryset = Stock.objects.select_related('item','location','location__area').all().order_by('item__name')
    serializer_class = StockSerializer

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['item__sku', 'item__name', 'location__code', 'location__name']
    ordering_fields = [
        'item__name',
        'location__code',
        'quantity_on_hand',
        'quantity_reserved',
        'updated_at'
    ]
    ordering = ['item__name']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtro por item
        item = self.request.query_params.get('item', None)
        if item is not None:
            queryset = queryset.filter(item_id=item)

        # Filtro por ubicacion
        location = self.request.query_params.get('location', None)
        if location is not None:
            queryset = queryset.filter(location_id=location)
        # Filtro por área

        area = self.request.query_params.get('area', None)
        if area is not None:
            queryset = queryset.filter(location__area_id=area)
        
        # Filtro por stock minimo
        min_quantity = self.request.query_params.get('min_quantity', None)
        if min_quantity is not None:
            queryset = queryset.filter(quantity_on_hand__gte=min_quantity)

        # Filtro por stock máximo
        max_quantity = self.request.query_params.get('max_quantity', None)
        if max_quantity is not None:
            queryset = queryset.filter(quantity_on_hand__lte=max_quantity)
        return queryset