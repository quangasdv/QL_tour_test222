from django.urls import path

from .api import TourMapAPI
from .views import tour_detail

urlpatterns = [
    path('detail/<int:id>', tour_detail, name='tour_detail'),
    path('route-map/<int:id>', TourMapAPI.as_view(), name='tour_list_api'),
]