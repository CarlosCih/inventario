from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from api.pagination import StandardResultsSetPagination
from api.permissions import IsManagerOrAdmin
from locations.models import Area, LocationType, Location
from api.serializers.locations import AreaSerializer, LocationTypeSerializer, LocationSerializer, LocationCreateUpdateSerializer


class AreaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsManagerOrAdmin]
    pagination_class = StandardResultsSetPagination
    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['name']

    def get_queryset(self):
        queryset = super().get_queryset()
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset
class LocationTypeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsManagerOrAdmin]
    pagination_class = StandardResultsSetPagination
    queryset = LocationType.objects.all()
    serializer_class = LocationTypeSerializer
    
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['name']

    def get_queryset(self):
        queryset = super().get_queryset()
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset
    
class LocationViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar ubicaciones
    """
    permission_classes = [IsManagerOrAdmin]
    pagination_class = StandardResultsSetPagination
    queryset = Location.objects.select_related('area', 'location_type').all()
    
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'code', 'description', 'area__name', 'location_type__name']
    ordering_fields = ['name', 'code', 'area__name', 'location_type__name', 'created_at']
    ordering = ['code']
    
    def get_serializer_class(self):
        """Usar diferentes serializers para lectura y escritura"""
        if self.action in ['create', 'update', 'partial_update']:
            return LocationCreateUpdateSerializer
        return LocationSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por área
        area = self.request.query_params.get('area', None)
        if area is not None:
            queryset = queryset.filter(area_id=area)
        
        # Filtrar por tipo de ubicación
        location_type = self.request.query_params.get('location_type', None)
        if location_type is not None:
            queryset = queryset.filter(location_type_id=location_type)
        
        # Filtrar por is_active
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset