from django.db import transaction
from django.utils import timezone
from .models import Stock
from django.db.models import F
from transactions.models import InventoryTransaction, TransactionType
from decimal import Decimal
from django.core.exceptions import ValidationError

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

def validate_transaction_for_application(transaction_obj):
    """Valida si una transaccion puede aplicarse al inventario"""
    if not isinstance(transaction_obj, InventoryTransaction):
        raise ValidationError("El objeto proporcionado no es una transacción válida.")
    if transaction_obj.is_applied:
        raise ValidationError("La transacción ya ha sido aplicada.")
    if transaction_obj.status.code != "completed":
        raise ValidationError("Solo se pueden aplicar transacciones completadas.")
    if not transaction_obj.transaction_type.is_active:
        raise ValidationError("El tipo de transacción no está activo.")
    if not transaction_obj.status.is_active:
        raise ValidationError("El estado de la transacción no está activo.")
    if not transaction_obj.details.exists():
        raise ValidationError("La transacción no tiene detalles asociados.")
    tx_type = transaction_obj.transaction_type
    for detail in transaction_obj.details.select_related(
        "item",
        "source_location",
        "target_location",
        
    ):
        validate_transaction_detail(tx_type, detail)

def validate_transaction_detail(transaction_type, detail):
    """Valida un renglon de transaccion degun las reglas del tipo de transaccion"""
    if detail.quantity <= 0:
        raise ValidationError(f"La cantidad debe ser mayor a cero para el artículo {detail.item.name}.")
    if transaction_type.requires_source_location and not detail.source_location:
        raise ValidationError(
            f"El tipo de transacción '{transaction_type.name}' requiere ubicación origen."
        )

    if transaction_type.requires_target_location and not detail.target_location:
        raise ValidationError(
            f"El tipo de transacción '{transaction_type.name}' requiere ubicación destino."
        )

    effect = transaction_type.stock_effect

    if effect == TransactionType.STOCK_EFFECT_TRANSFER:
        if not detail.source_location or not detail.target_location:
            raise ValidationError(
                f"La transferencia del artículo '{detail.item}' requiere origen y destino."
            )

        if detail.source_location_id == detail.target_location_id:
            raise ValidationError(
                f"La ubicación origen y destino no pueden ser iguales para '{detail.item}'."
            )

        validate_stock_availability(
            item=detail.item,
            location=detail.source_location,
            qty=detail.quantity,
        )

    elif effect == TransactionType.STOCK_EFFECT_DECREASE:
        validate_stock_availability(
            item=detail.item,
            location=detail.source_location,
            qty=detail.quantity,
        )

    elif effect == TransactionType.STOCK_EFFECT_ADJUST:
        # En este diseño, ADJUST requiere que definas si el ajuste sube o baja
        # usando origen o destino:
        #
        # - Ajuste positivo: target_location con cantidad positiva
        # - Ajuste negativo: source_location con cantidad positiva
        #
        # Si ambos vienen llenos, se considera inválido.
        if detail.source_location and detail.target_location:
            raise ValidationError(
                f"El ajuste para '{detail.item}' debe tener origen o destino, no ambos."
            )

        if not detail.source_location and not detail.target_location:
            raise ValidationError(
                f"El ajuste para '{detail.item}' requiere una ubicación."
            )

        if detail.source_location:
            validate_stock_availability(
                item=detail.item,
                location=detail.source_location,
                qty=detail.quantity,
            )
def validate_stock_availability(item, location, qty):
    """
    Valida que exista suficiente stock disponible.
    """
    available_qty = get_stock_quantity(item=item, location=location)

    if available_qty < qty:
        location_name = str(location) if location else "Sin ubicación"
        raise ValidationError(
            f"Stock insuficiente para '{item}' en '{location_name}'. "
            f"Disponible: {available_qty}, requerido: {qty}."
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
        raise ValidationError("La ubicación origen y destino no pueden ser la misma.")
    decrease_stock(item=item, location=source_location, qty=qty)
    increase_stock(item=item, location=target_location, qty=qty)
    
def apply_transaction_detail(transaction_type, detail):
    """Aplica un detalle de transaccion al stock."""
    effect = transaction_type.stock_effect
    
    if effect == TransactionType.STOCK_EFFECT_NONE:
        return # No hace nada
    if effect == TransactionType.STOCK_EFFECT_INCREASE:
        increase_stock(
            item=detail.item,
            location=detail.target_location,
            qty=detail.quantity,
        )
        return
    
    if effect == TransactionType.STOCK_EFFECT_DECREASE:
        decrease_stock(
            item=detail.item,
            location=detail.source_location,
            qty=detail.quantity,
        )
        return
    if effect == TransactionType.STOCK_EFFECT_TRANSFER:
        transfer_stock(
            item=detail.item,
            source_location=detail.source_location,
            target_location=detail.target_location,
            qty=detail.quantity,
        )
        return
    if effect == TransactionType.STOCK_EFFECT_ADJUST:
        # Convención:
        # - si trae target_location => ajuste positivo
        # - si trae source_location => ajuste negativo
        if detail.target_location and not detail.source_location:
            increase_stock(
                item=detail.item,
                location=detail.target_location,
                qty=detail.quantity,
            )
            return

        if detail.source_location and not detail.target_location:
            decrease_stock(
                item=detail.item,
                location=detail.source_location,
                qty=detail.quantity,
            )
            return

        raise ValidationError(
            f"No se pudo determinar el sentido del ajuste para '{detail.item}'."
        )

    raise ValidationError(
        f"Efecto de stock no soportado: '{effect}'."
    )
    
@transaction.atomic
def apply_transaction(transaction_id):
    """Aplica una transaccion completa al inventario.
    Bloquea la transaccion y sus stocks relacionados dentro de una operacion atómica"""
    
    transaction_obj = (
        InventoryTransaction.objects.select_for_update()
        .select_related("transaction_type", "status")
        .prefetch_related("details__item", "details__source_location", "details__target_location")
        .get(pk=transaction_id)
    )
    validate_transaction_for_application(transaction_obj)
    
    for detail in transaction_obj.details.all():
        apply_transaction_detail(
            transaction_type=transaction_obj.transaction_type,
            detail=detail,
        )
        
    transaction_obj.is_applied = True
    transaction_obj.applied_at = timezone.now()
    transaction_obj.save(update_fields=["is_applied", "applied_at", "updated_at"])
    return transaction_obj