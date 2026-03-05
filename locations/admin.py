from django.contrib import admin
from .models import *


# Register your models here.
@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active',)
    readonly_fields = ('created_at', 'updated_at',)
    search_fields = ('name',)
    list_filter = ('is_active', 'created_at', 'updated_at')

@admin.register(LocationType)
class LocationTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active',)
    readonly_fields = ('created_at', 'updated_at',)
    search_fields = ('name',)
    list_filter = ('is_active', 'created_at', 'updated_at')

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'location_type', 'area', 'is_active',)
    readonly_fields = ('created_at', 'updated_at',)
    search_fields = ('name', 'code', 'location_type__name', 'area__name',)
    list_filter = ('is_active', 'created_at', 'updated_at', 'location_type', 'area')

