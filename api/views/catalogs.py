from rest_framework import viewsets
from catalogs.models import *
from api.serializers.catalogs import *

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all().order_by("name")
    serializer_class = CategorySerializer
    
    
class BrandViewSet(viewsets.ModelViewSet):
    queryset = Marca.objects.all().order_by("name")
    serializer_class = BrandSerializer
    
class ModelViewSet(viewsets.ModelViewSet):
    queryset = Modelo.objects.all().order_by("name")
    serializer_class = ModelSerializer
    
class UnitOfMeasureViewSet(viewsets.ModelViewSet):
    queryset = UnitOfMeasure.objects.all().order_by("name")
    serializer_class = UnitOfMeasureSerializer
    
class StateViewSet(viewsets.ModelViewSet):
    queryset = Estado.objects.all().order_by("name")
    serializer_class = StateSerializer
    