from django.db import models


class Area(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True, verbose_name='Nombre del área')
    description = models.TextField(blank=True, null=True, verbose_name='Descripción')
    is_active = models.BooleanField(default=True, db_index=True, verbose_name='Activo')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creado el')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Actualizado el')

    class Meta:
        verbose_name = 'Área'
        verbose_name_plural = 'Áreas'
        ordering = ['name']

    def __str__(self):
        return self.name


class LocationType(models.Model):
    name = models.CharField(max_length=50, unique=True, db_index=True, verbose_name='Tipo de ubicación')
    is_active = models.BooleanField(default=True, db_index=True, verbose_name='Activo')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creado el')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Actualizado el')

    class Meta:
        verbose_name = 'Tipo de ubicación'
        verbose_name_plural = 'Tipos de ubicación'
        ordering = ['name']

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name='Nombre de la ubicación')

    code = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        verbose_name='Código de ubicación',
        help_text='Código único para la ubicación (ej: ALM-001)'
    )

    location_type = models.ForeignKey(
        LocationType,
        on_delete=models.PROTECT,
        related_name='locations',
        verbose_name='Tipo de ubicación'
    )

    area = models.ForeignKey(
        Area,
        on_delete=models.PROTECT,
        related_name='locations',
        verbose_name='Área'
    )

    description = models.TextField(blank=True, null=True, verbose_name='Descripción')

    is_active = models.BooleanField(default=True, db_index=True, verbose_name='Activo')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creado el')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Actualizado el')

    class Meta:
        verbose_name = 'Ubicación'
        verbose_name_plural = 'Ubicaciones'
        ordering = ['code']
        indexes = [
            models.Index(fields=['area', 'location_type', 'is_active']),
        ]

    def __str__(self):
        return f'{self.code} - {self.name}'