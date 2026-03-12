from rest_framework.routers import DefaultRouter
from api.views.catalogs import *
from api.views.inventory import *
from api.views.locations import *
from api.views.transactions import *

router = DefaultRouter()
# Catalogs
router.register(r"catalogs/categories", CategoryViewSet, basename="category")
router.register(r"catalogs/brands", BrandViewSet, basename="brand")
router.register(r"catalogs/models", ModelViewSet, basename="model")
router.register(r"catalogs/units", UnitOfMeasureViewSet, basename="unit")
router.register(r"catalogs/asset-states", StateViewSet, basename="state")
# Inventory
router.register(r"inventory/items", ItemViewSet, basename="item")
router.register(r"inventory/assets", AssetViewSet, basename="asset")
router.register(r"inventory/stock", StockViewSet, basename="stock")
# Transactions
router.register(r"transactions", TransactionsViewSet, basename="transaction")
router.register(r"transactions/tags", TransactionTagViewSet, basename="transaction-tag")
router.register(r"transactions/types", TransactionTypeViewSet, basename="transaction-type")
router.register(r"transactions/statuses", TransactionStatusViewSet, basename="transaction-status")
# Locations
router.register(r"locations/areas", AreaViewSet, basename="area")
router.register(r"locations/types", LocationTypeViewSet, basename="location-type")
router.register(r"locations", LocationViewSet, basename="location")