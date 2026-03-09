from django.contrib import admin
from .models import *
# Register your models here.
@admin.register(TransactionType)
class TransactionTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name', 'description', 'stock_effect', 'requires_source_location', 'requires_target_location', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('code', 'name')
    ordering = ('name',)

@admin.register(TransactionStatus)
class TransactionStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name', 'description', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'transaction_type', 'status', 'reference', 'number', 'performed_at', 'created_by', 'is_applied')
    readonly_fields = ('created_at', 'updated_at', 'applied_at')
    list_filter = ('transaction_type', 'status', 'created_at')
    search_fields = ('reference', 'created_by__username')
    ordering = ('-performed_at',)

@admin.register(TransactionDetail)
class TransactionDetailAdmin(admin.ModelAdmin):
    list_display = ('id', 'transaction', 'item', 'quantity', 'unit_cost', 'source_location', 'target_location')
    readonly_fields = ('created_at', 'updated_at')
    list_filter = ('transaction', 'created_at')
    search_fields = ('item__name',)
    ordering = ('-created_at',)
    
@admin.register(TransactionTag)
class TransactionTagAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name', 'description', 'color', 'is_auto')
    readonly_fields = ('created_at', 'updated_at')
    list_filter = ('is_auto', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)