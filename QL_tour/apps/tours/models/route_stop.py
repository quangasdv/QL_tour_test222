from django.db import models
from .tour_stop import TourStop
from .tour_route import TourRoute

class RouteStop(models.Model):
    route = models.ForeignKey(TourRoute, on_delete=models.CASCADE)
    stop = models.ForeignKey(TourStop, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()
    stay_minutes = models.PositiveIntegerField(null=True)
