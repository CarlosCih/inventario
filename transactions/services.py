from django.db import transaction
from django.utils import timezone
from transactions.models import *
from django.core.exceptions import ValidationError
from inventory.services import *
from decimal import Decimal

def validate_transaction_for_application(transaction_obj):
    """Valida si una transaccion puede aplicarse al inventario"""
    if not isinstance(transaction_obj, InventoryTransaction):
        raise ValidationError("El objeto proporcionado no es una transacción válida.")
    if transaction_obj.applied_at is not None:
        raise ValidationError("La transacción ya ha sido aplicada.")
    if transaction_obj.status.code != "COMPLETED":
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
        
    transaction_obj.applied_at = timezone.now()
    transaction_obj.save(update_fields=["applied_at", "updated_at"])
    
    # Auto-etiquetar la transacción después de aplicarla
    auto_tag_transaction(transaction_obj)
    
    return transaction_obj
def cancel_transaction(transaction_obj):
    """Cancela una transaccion, solo si no ha sido aplicada."""
    if transaction_obj.status.code == "COMPLETED":
        raise ValidationError("No se puede cancelar una transacción ya aplicada.")
    transaction_obj.status = TransactionStatus.objects.get(code="CANCELED")
    transaction_obj.save(update_fields=["status", "updated_at"])
    
    return transaction_obj

def reverse_transaction(transaction_obj):
    """Revierte una transaccion aplicada, creando una nueva transaccion con efectos opuestos."""
    if transaction_obj.status.code != "COMPLETED" or not transaction_obj.applied_at:
        raise ValidationError("Solo se pueden revertir transacciones aplicadas.")
    
    with transaction.atomic():
        # Crear nueva transacción de reversa
        reverse_tx = InventoryTransaction.objects.create(
            transaction_type=transaction_obj.transaction_type,
            status=TransactionStatus.objects.get(code="COMPLETED"),
            reference=f"Reversa de {transaction_obj.number}",
            number=f"{transaction_obj.number}-REV",
            notes=f"Transacción de reversa para {transaction_obj}",
            performed_at=timezone.now(),
            created_by=transaction_obj.created_by,
            is_applied=True,
            applied_at=timezone.now(),
        )
        
        # Crear detalles con cantidades opuestas
        for detail in transaction_obj.details.all():
            TransactionDetail.objects.create(
                transaction=reverse_tx,
                item=detail.item,
                quantity=detail.quantity,  # La lógica de aplicación se encargará de invertir el efecto
                source_location=detail.target_location,  # Invertir origen y destino
                target_location=detail.source_location,
            )
        
        # Aplicar la transacción de reversa
        apply_transaction(reverse_tx.id)
        
    return reverse_tx

def auto_tag_transaction(transaction_obj):
    """ Funcion para asignar etiquetas automáticas a una transacción según reglas predefinidas."""
    tags_to_add = []    
    
    #Regla 1: Transacciones de alto valor
    total_value = sum(
        (detail.quantity * (detail.unit_cost or Decimal("0.00"))) for detail in transaction_obj.details.all()
    )
    if total_value >= Decimal("10000.00"):
        tag = TransactionTag.objects.filter(code="HIGH_VALUE").first()
        if tag:
            tags_to_add.append(tag)
            
    #Regla 2: Transacciones con muchos articulos (mas de 10)
    if transaction_obj.details.count() > 10:
        tag = TransactionTag.objects.filter(code="BULK", is_active=True).first()
        if tag:
            tags_to_add.append(tag)
            
    #Regla 3: Transacciones urgentes (realizadas el mismo dia de creacion)
    if transaction_obj.performed_at.date() == transaction_obj.created_at.date():
        tag = TransactionTag.objects.filter(code="URGENT", is_active=True).first()
        if tag:
            tags_to_add.append(tag)
    #Regla 4: Ajustes de inventario
    if transaction_obj.transaction_type.stock_effect == TransactionType.STOCK_EFFECT_ADJUST:
        tag = TransactionTag.objects.filter(code="ADJUSTMENT", is_active=True).first()
        if tag:
            tags_to_add.append(tag)
    #Regla 5: Transferencias entre ubicaciones
    if transaction_obj.transaction_type.stock_effect == TransactionType.STOCK_EFFECT_TRANSFER:
        tag = TransactionTag.objects.filter(code="TRANSFER", is_active=True).first()
        if tag:
            tags_to_add.append(tag)
    #Regla 6: Transacciones con articulos de multiples categorias
    #categories = set(
        #detail.item.category_id for detail in transaction_obj.details.select_related#("item__category").all()
        #if hasattr(detail.item, 'category') and detail.item.category is not None
        
    #)
    #if len(categories) > 3:
        #tag = TransactionTag.objects.filter(code="MULTICATEGORY", is_active=True).first()
        #if tag:
            #tags_to_add.append(tag)
    
    # Aplicar las etiquetas a la transacción
    if tags_to_add:
        transaction_obj.tags.add(*tags_to_add)
        
    return tags_to_add

def auto_folio_transaction(transaction_obj):
    """Genera un número de folio automático para la transacción según el formato: [TIPO]-[AÑO][MES][DÍA]-[ID]"""
    date_str = transaction_obj.created_at.strftime("%Y%m%d")
    folio = f"{transaction_obj.transaction_type.code}-{date_str}-{transaction_obj.id:04d}"
    transaction_obj.number = folio
    transaction_obj.save(update_fields=["number"])
    return folio
    