from django.contrib import admin
from .models import *

# Register your models here.

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = (
        'sku',
        'name',
        'description',
        'unitofmeasure',
        'is_serialized',
        'is_lot_controlled',
        'has_expiration',
        'is_active',
    )
    readonly_fields = ('created_at', 'updated_at')
    search_fields = ('sku', 'name')
    list_filter = ('is_active', 'is_serialized', 'is_lot_controlled', 'has_expiration')
    ordering = ('name',)
    
@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = (
        'item',
        'quantity_on_hand',
        'quantity_reserved',
        'location',
    )
    readonly_fields = ('updated_at',)
    search_fields = ('item__sku', 'item__name')
    list_filter = ('location',)
    ordering = ('item__name',)
    
@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = (
        'item',
        'num_serial',
        'internal_code',
        'status',
        'location',
        'notes',
        'is_active',
    )
    readonly_fields = ('created_at', 'updated_at')
    search_fields = ('item__sku', 'item__name', 'num_serial', 'internal_code')
    list_filter = ('location',)
    ordering = ('item__name',)
    