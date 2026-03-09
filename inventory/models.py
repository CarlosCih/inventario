from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

# Create your models here.
class Item(models.Model):
    """Representa un artículo o producto que se puede gestionar en el inventario."""
    
    sku = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name='Clave'
    )
    name = models.CharField(
        max_length=255,
        db_index=True,
        verbose_name='Nombre'
    )
    description = models.TextField(
        blank=True,
        null = True,
        verbose_name='Descripción'
    )
    unitofmeasure = models.ForeignKey(
        'catalogs.UnitOfMeasure',
        on_delete=models.PROTECT,
        related_name='items',
        verbose_name='Unidad de medida'
    )
    category = models.ForeignKey(
        'catalogs.Categoria',
        on_delete=models.PROTECT,
        related_name='items',
        verbose_name='Categoría'
    )
    brand = models.ForeignKey(
        'catalogs.Marca',
        on_delete=models.PROTECT,
        related_name='items',
        verbose_name='Marca'
    )
    is_serialized = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name='¿Requiere número de serie?'
    )
    is_lot_controlled = models.BooleanField(
        default = False,
        db_index = True,
        verbose_name = '¿Requiere control de lote?'
    )
    has_expiration = models.BooleanField(
        default = False,
        db_index = True,
        verbose_name = '¿Tiene fecha de caducidad?'
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name='¿Activo?'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de actualización'
    )
    class Meta:
        verbose_name = 'Artículo'
        verbose_name_plural = 'Artículos'
        ordering = ['name']
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]
    def __str__(self):
        return f'{self.sku} - {self.name}'

class Asset(models.Model):
    """Representa una unidad fisica de un artículo, con número de serie e información de ubicación."""
    
    item = models.ForeignKey(
        Item,
        on_delete=models.PROTECT,
        related_name='assets',
        verbose_name='Artículo'
    )
    num_serial = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        verbose_name='Número de serie'
    )
    internal_code = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        verbose_name='Código interno'
    )
    status = models.ForeignKey(
        'catalogs.Estado',
        on_delete=models.PROTECT,
        related_name='assets',
        verbose_name='Estatus'
    )
    
    location = models.ForeignKey(
        'locations.Location',
        on_delete=models.PROTECT,
        related_name='assets',
        verbose_name='Ubicación'
    )
    
    notes = models.TextField(blank=True, null=True, verbose_name='Notas')
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name='¿Activo?'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de actualización'
    )
    
    class Meta:
        verbose_name = 'Activo'
        verbose_name_plural = 'Activos'
        ordering = ['item__name', 'num_serial']
        indexes = [
            models.Index(fields=['num_serial']),
            models.Index(fields=['internal_code']),
            models.Index(fields=['status']),
        ]
        
    def __str__(self):
        return f"{self.num_serial} - {self.item.sku}"
    

class Stock(models.Model):
    """Representa la cantidad por item y ubicación, sin importar el número de serie o lote."""
    
    item = models.ForeignKey(
        Item,
        on_delete=models.PROTECT,
        related_name='stocks',
        verbose_name='Artículo'
    )
    location = models.ForeignKey(
        'locations.Location',
        on_delete=models.PROTECT,
        related_name='stocks',
        verbose_name='Ubicación'
    )
    # La cantidad disponible, sin incluir lo reservado para órdenes o proyectos. Es decir, lo que realmente se tiene en existencia para usar o vender.
    quantity_on_hand = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name='Cantidad disponible'
    )
    # La cantidad que está reservada para órdenes de venta, proyectos u otros compromisos. Esta cantidad no está disponible para otras operaciones hasta que se libere o se complete la orden.
    quantity_reserved = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name='Cantidad reservada'
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')
    
    class Meta:
        verbose_name = "Stock"
        verbose_name_plural = "Stocks"
        ordering = [
            "item",
            "location"
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "item",
                    "location"
                ],
                name="uq_stock_item_location"
            )
        ]
        indexes = [
            models.Index(
                fields=[
                    "item",
                    "location"
                ]
            )
        ]
    
    def __str__(self):
        loc = self.location if self.location is not None else "Global"
        return f"{self.item.sku} @ {loc}: {self.quantity_on_hand}"

