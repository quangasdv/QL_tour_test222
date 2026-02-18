from django.urls import path
from .views import search_tours_data

urlpatterns = [
    path('tours', search_tours_data, name='search_tours')
]