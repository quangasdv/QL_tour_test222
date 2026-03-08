from django.db import models

class TourSchedule(models.Model):
    tour = models.ForeignKey('Tour', on_delete=models.CASCADE)
    start_day = models.DateTimeField()
    end_day = models.DateTimeField()
    total_slots  = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.tour.title} from {self.start_day} to {self.end_day}"