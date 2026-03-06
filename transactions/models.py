from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import models
from django.conf import settings

# Create your models here.

class TransactionType(models.Model):

    STOCK_EFFECT_NONE = "none"
    STOCK_EFFECT_INCREASE = "increase"
    STOCK_EFFECT_DECREASE = "decrease"
    STOCK_EFFECT_TRANSFER = "transfer"
    STOCK_EFFECT_ADJUST = "adjust"

    STOCK_EFFECT_CHOICES = (
        (STOCK_EFFECT_NONE, "Sin efecto"),
        (STOCK_EFFECT_INCREASE, "Incrementa stock"),
        (STOCK_EFFECT_DECREASE, "Disminuye stock"),
        (STOCK_EFFECT_TRANSFER, "Transferencia"),
        (STOCK_EFFECT_ADJUST, "Ajuste"),
    )

    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name="Código"
    )

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre"
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descripción"
    )

    stock_effect = models.CharField(
        max_length=20,
        choices=STOCK_EFFECT_CHOICES,
        default=STOCK_EFFECT_NONE,
        verbose_name="Efecto en el stock"
    )

    requires_source_location = models.BooleanField(
        default=False,
        verbose_name="Requiere ubicación origen"
    )

    requires_target_location = models.BooleanField(
        default=False,
        verbose_name="Requiere ubicación destino"
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Activo"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Creado el"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Actualizado el"
    )

    class Meta:
        verbose_name = "Tipo de Transacción"
        verbose_name_plural = "Tipos de Transacción"
        ordering = ["name"]

    def __str__(self):
        return self.name
    
class TransactionStatus(models.Model):
    """Modelo para definir los estados de las transacciones (ej. Pendiente, Completada, Cancelada).
    """
    name = models.CharField(max_length=50, unique=True, db_index=True, verbose_name="Nombre")
    code = models.CharField(max_length=50, unique=True, db_index=True, verbose_name="Código")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado el")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado el")
    
    class Meta:
        verbose_name = "Estado de Transacción"
        verbose_name_plural = "Estados de Transacción"
        ordering = ['name']
        
    def __str__(self):
        return self.name

class InventoryTransaction(models.Model):
    """
    Modelo para registrar las transacciones de inventario, como entradas, salidas, ajustes, etc.
    """
    transaction_type = models.ForeignKey(TransactionType, on_delete=models.PROTECT, related_name="transactions", verbose_name="Tipo de Transacción")
    status = models.ForeignKey(TransactionStatus, on_delete=models.PROTECT, related_name="transactions", verbose_name="Estado de Transacción")
    reference = models.CharField(max_length=100, blank=True, null=True, db_index=True, verbose_name="Referencia")
    number= models.CharField(max_length=30, unique=True, db_index=True, verbose_name="Folio")
    notes=models.TextField(blank=True, null=True, verbose_name="Notas")
    performed_at = models.DateTimeField(verbose_name="Fecha y Hora de la Transacción")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="transactions_created",
        verbose_name="Creado por"
    )
    is_applied = models.BooleanField(default=False, db_index=True, verbose_name="¿Aplicada?")
    applied_at = models.DateTimeField(blank=True, null=True, verbose_name="Fecha y Hora de Aplicación")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado el")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado el")
    
    class Meta:
        verbose_name = "Transacción de Inventario"
        verbose_name_plural = "Transacciones de Inventario"
        ordering = ['-performed_at']
        
    def __str__(self):
        return f"{self.transaction_type.name} - {self.performed_at}"

class TransactionDetail(models.Model):
    """Modelo para representar los detalles de cada transacción, como el artículo involucrado, cantidad, ubicación, etc.
    """
    transaction = models.ForeignKey(
        InventoryTransaction,
        on_delete=models.CASCADE,
        related_name="details",
        verbose_name="Transacción"
    )
    item = models.ForeignKey(
        'inventory.Item',
        on_delete=models.PROTECT,
        verbose_name="Articulo"
    )
    quantity = models.DecimalField(max_digits=12,decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))], verbose_name="Cantidad")
    source_location = models.ForeignKey(
        'locations.Location',
        on_delete=models.PROTECT,
        related_name="transaction_source",
        blank=True,
        null=True,
        verbose_name="Ubicación de origen"
    )
    target_location = models.ForeignKey(
        'locations.Location',
        on_delete=models.PROTECT,
        related_name="transaction_target",
        blank=True,
        null=True,
        verbose_name="Ubicación de destino"
    )
    unit_cost = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        blank=True,
        null=True,
        verbose_name="Costo unitario"
    )
    notes = models.TextField(blank=True, null=True, verbose_name="Notas")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado el")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado el")
    
    class Meta:
        verbose_name = "Detalle de Transacción"
        verbose_name_plural = "Detalles de Transacción"
        
    def __str__(self):
        return f"{self.item.name} - {self.quantity}"
