from django.db import models
from django.core.exceptions import ValidationError

# Modelos de catálogo para inventario adaptable a diferentes áreas de la empresa
class CatalogAbstract(models.Model):
    """Modelo abstracto base para todos los catálogos del sistema"""
    name = models.CharField(max_length=100, db_index=True, verbose_name="Nombre")
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado")
    
    class Meta:
        abstract = True
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Estado(CatalogAbstract):
    class Meta:
        verbose_name = "Estado"
        verbose_name_plural = "Estados"
        constraints = [
            models.UniqueConstraint(fields=["name"], name="uq_estado_name"),
        ]
        
    def clean(self):
        # Validación para evitar estados con nombres similares (ej. "Activo" vs "activo")
        if Estado.objects.filter(name__iexact=self.name).exclude(pk=self.pk).exists():
            raise ValidationError(f"Ya existe un estado con el nombre '{self.name}' (case-insensitive).")
        


class UnitOfMeasure(CatalogAbstract):
    abbr = models.CharField(max_length=5, unique=True, verbose_name="Abreviatura")
    
    class Meta:
        verbose_name = "Unidad de medida"
        verbose_name_plural = "Unidades de medida"


class Categoria(CatalogAbstract):
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        constraints = [
            models.UniqueConstraint(fields=["name"], name="uq_categoria_name"),
        ]


class Marca(CatalogAbstract):
    class Meta:
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"
        constraints = [
            models.UniqueConstraint(fields=["name"], name="uq_marca_name"),
        ]


class Modelo(CatalogAbstract):
    # Sobrescribimos name para quitar unique (se valida con constraint)
    name = models.CharField(max_length=100, db_index=True, verbose_name="Nombre")
    code = models.CharField(max_length=50, unique=True, verbose_name="Código")
    marca = models.ForeignKey(Marca, on_delete=models.PROTECT, related_name="modelos", verbose_name="Marca")
    
    class Meta:
        verbose_name = "Modelo"
        verbose_name_plural = "Modelos"
        ordering = ['marca', 'name']
        constraints = [
            models.UniqueConstraint(fields=["marca", "name"], name="uq_modelo_marca_name"),
        ]
    
    def __str__(self):
        return f"{self.marca.name} - {self.name}"