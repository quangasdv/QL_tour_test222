from django.db import models
from django.contrib.gis.db import models

class TourStop(models.Model):
    name = models.CharField(max_length=255)
    location = models.PointField(geography=True, srid=4326)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.name}"