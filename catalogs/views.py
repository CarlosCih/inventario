from django.shortcuts import render
from django.views import View

# Create your views here.
def home(request):
    return render(request, 'catalogs/home.html')


class CatalogViews(View):

    def catalog_categories(request):
        return render(request, 'catalogs/catalog_categories.html')
    
    def catalog_status(request):
        return render(request, 'catalogs/catalog_status.html')
    
    def catalog_models(request):
        return render(request, 'catalogs/catalog_models.html')
    
    def catalog_units(request):
        return render(request, 'catalogs/catalog_units.html')
    
    def catalog_brands(request):
        return render(request, 'catalogs/catalog_brands.html')