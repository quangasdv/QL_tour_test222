from django.urls import path

from .api import TourMapAPI
from .views import tour_detail, tours, tour_search

urlpatterns = [
    path('detail/<int:id>', tour_detail, name='tour_detail'),
    path('route-map/<int:id>', TourMapAPI.as_view(), name='tour_list_api'),
    path('', tours),
    path('search/', tour_search, name='search'),
]