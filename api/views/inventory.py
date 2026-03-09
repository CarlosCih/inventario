from rest_framework import viewsets
from inventory.models import *
from api.serializers.inventory import *

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.select_related('category','brand','unit').all().order_by('name')
    serializer_class = ItemSerializer

class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.select_related('item','status','current_location').all().order_by('internal_code')
    serializer_class = AssetSerializer

class StockViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Stock.objects.select_related('item','location').all().order_by('item__name')
    serializer_class = StockSerializer