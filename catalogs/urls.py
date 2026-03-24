from django.urls import path
from . import views

app_name = 'catalogs'

urlpatterns = [
    path('', views.home, name='home'),
    path('list/', views.home, name='list'),
]