from django.db import transaction
from django.utils import timezone
from .models import Stock
from django.db.models import F
from transactions.models import InventoryTransaction, TransactionType
from decimal import Decimal
from django.core.exceptions import ValidationError
from transactions.services import *
from api.exceptions import *

#Archivos que deben estar en inventory/services.py:
# get_or_create_stock
# get_stock_quantity
# increase_stock
# decrease_stock
# transfer_stock

def get_or_create_stock(item, location):
    stock, _ = Stock.objects.get_or_create(
        item=item,
        location=location,
        defaults={
            "quantity_on_hand": 0,
            "quantity_reserved": 0,
        },
    )
    return stock
def get_stock_quantity(item, location):
    """Devuelve la existencia actual del item en la ubicacion. """
    stock = Stock.objects.filter(item=item, location=location).first()
    if not stock:
        return Decimal("0.00")
    return stock.quantity_on_hand


def validate_stock_availability(item, location, qty):
    """
    Valida que exista suficiente stock disponible.
    """
    available_qty = get_stock_quantity(item=item, location=location)

    if available_qty < qty:
        raise InsufficientStockException(
            item_name=item.name,
            available=available_qty,
            requested=qty,
            location_name=location.name if location else "N/A"
        )

def increase_stock(item, location, qty):
    """Incrementa el stock disponible del item en la ubicación indicada."""
    stock = get_or_create_stock(item=item, location=location)
    
    Stock.objects.filter(pk=stock.pk).update(quantity_on_hand=F("quantity_on_hand") + qty)
    
def decrease_stock(item, location, qty):
    """Disminuye el stock disponible del item en la ubicación indicada."""
    validate_stock_availability(item=item, location=location, qty=qty)
    
    stock = get_or_create_stock(item=item, location=location)
    
    updated = Stock.objects.filter(pk=stock.pk, quantity_on_hand__gte=qty).update(quantity_on_hand=F("quantity_on_hand") - qty)
    
    if updated == 0:
        raise ValidationError(
            f"Stock insuficiente para '{item}' en '{location}'. "
            f"Disponible: {get_stock_quantity(item=item, location=location)}, requerido: {qty}."
        )
        
def transfer_stock(item, source_location, target_location, qty):
    """Transfiere stock entre ubicaciones."""
    if source_location == target_location:
        raise SameSourceAndTargetException()
    decrease_stock(item=item, location=source_location, qty=qty)
    increase_stock(item=item, location=target_location, qty=qty)