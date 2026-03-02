from django.urls import path

from .servers import TourMapAPI
from .views import *

urlpatterns = [
    path('detail/<int:id>', tour_detail, name='tour_detail'),
    path('route-map/<int:id>', TourMapAPI.as_view(), name='tour_list_api'),
    path('search/', tour_search, name='search'),
    path('', tours, name='tours_api'),
    path('results/', tour_results, name='tour_results'),
]