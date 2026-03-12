from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from api.pagination import StandardResultsSetPagination
from api.permissions import IsManagerOrAdmin
from catalogs.models import *
from api.serializers.catalogs import *

class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsManagerOrAdmin]
    pagination_class = StandardResultsSetPagination
    queryset = Categoria.objects.all().order_by("name")
    serializer_class = CategorySerializer

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name','created_at','updated_at']
    ordering = ['name']

    def get_queryset(self):
        """Filtros personalizado por query params"""
        queryset = super().get_queryset()
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset
    
class BrandViewSet(viewsets.ModelViewSet):
    permission_classes = [IsManagerOrAdmin]
    pagination_class = StandardResultsSetPagination
    queryset = Marca.objects.all().order_by("name")
    serializer_class = BrandSerializer

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name','created_at','updated_at']
    ordering = ['name']

    def get_queryset(self):
        """Filtros personalizado por query params"""
        queryset = super().get_queryset()
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset
    
class ModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsManagerOrAdmin]
    pagination_class = StandardResultsSetPagination
    queryset = Modelo.objects.select_related('marca').all().order_by('name')
    serializer_class = ModelSerializer

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name','code','marca__name']
    ordering_fields = ['name','code','marca__name','created_at','updated_at']
    ordering = ['marca__name','name']

    def get_queryset(self):
        queryset=super().get_queryset()
        marca = self.request.query_params.get('marca',None)
        if marca is not None:
            queryset = queryset.filter(marca_id=marca)

        is_active = self.request.query_params.get('is_active',None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset

class UnitOfMeasureViewSet(viewsets.ModelViewSet):
    permission_classes = [IsManagerOrAdmin]
    pagination_class = StandardResultsSetPagination
    queryset = UnitOfMeasure.objects.all().order_by("name")
    serializer_class = UnitOfMeasureSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name','abbr']
    ordering_fields = ['name','abbr','created_at']
    ordering = ['name']

    def get_queryset(self):
        queryset = super().get_queryset()
        is_active = self.request.query_params.get('is_active',None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset

class StateViewSet(viewsets.ModelViewSet):
    permission_classes = [IsManagerOrAdmin]
    pagination_class = StandardResultsSetPagination
    queryset = Estado.objects.all().order_by("name")
    serializer_class = StateSerializer

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name','created_at']
    ordering = ['name']

    def get_queryset(self):
        queryset = super().get_queryset()
        is_active = self.request.query_params.get('is_active',None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset