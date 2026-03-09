#Endpoit para serializar los modelos de Catalogos
from rest_framework import serializers
from catalogs.models import *


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = "__all__"
        
class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = "__all__"
        
class ModelSerializer(serializers.ModelSerializer):
    marca = BrandSerializer(read_only=True)
    
    class Meta:
        model = Modelo
        fields = "__all__"
        
class UnitOfMeasureSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitOfMeasure
        fields = "__all__"

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estado
        fields = "__all__"
