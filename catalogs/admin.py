from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active',)
    readonly_fields = ('created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_active', 'created_at', 'updated_at')

@admin.register(UnitOfMeasure)
class UnitOfMeasureAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbr', 'is_active',)
    readonly_fields = ('created_at', 'updated_at')
    search_fields = ('name', 'abbr',)
    list_filter = ('is_active', 'created_at', 'updated_at')
    
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active',)
    readonly_fields = ('created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_active', 'created_at', 'updated_at')
    
@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active',)
    readonly_fields = ('created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_active', 'created_at', 'updated_at')

@admin.register(Modelo)
class ModeloAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'marca', 'is_active',)
    readonly_fields = ('created_at', 'updated_at')
    search_fields = ('name', 'code', 'marca__name',)
    list_filter = ('is_active', 'created_at', 'updated_at', 'marca')