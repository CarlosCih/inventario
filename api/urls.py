from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.routers import router

urlpatterns = [
    path('', include(router.urls)),
]