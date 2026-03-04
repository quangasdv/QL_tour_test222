from django.urls import path
from .views import *

urlpatterns = [
    path('create/<int:id>/', booking, name='booking_create'),
]