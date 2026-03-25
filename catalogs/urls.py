from django.urls import path
from . import views

app_name = 'catalogs'

urlpatterns = [
    path('', views.home, name='home'),
    path('categorias/', views.CatalogViews.catalog_categories, name='catalog_categories'),
    path('estados/', views.CatalogViews.catalog_status, name='catalog_status'),
    path('unidades/', views.CatalogViews.catalog_units, name='catalog_units'),
    path('marcas/', views.CatalogViews.catalog_brands, name='catalog_brands'),
    path('modelos/', views.CatalogViews.catalog_models, name='catalog_models'),
]