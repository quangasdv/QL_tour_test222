from django.db import models
from django.contrib.gis.db import models
from .tours import Tour
from .tour_stop import TourStop

class TourRoute(models.Model):
    tour = models.ForeignKey(
        Tour,
        on_delete=models.CASCADE
    )

    route = models.LineStringField(null=True, blank=True)
    name = models.CharField(max_length=255)
    distance_km = models.FloatField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}"
