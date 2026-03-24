from django.shortcuts import render
from django.views import View

# Create your views here.
class Location(View):
    
    def home(request):
        return render(request, 'locations/home.html')
    
    
