from django.urls import path

from .views import *

urlpatterns = [
    path('schedule/<int:id>/', booking_confirm, name='booking_confirm'),
    path('create/', booking, name='booking_create'),
    path('map/', map_view, name='map-view'),
]