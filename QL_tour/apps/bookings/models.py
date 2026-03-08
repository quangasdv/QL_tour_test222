from django.db import models
from django.contrib.auth.models import User
from django.conf import settings 
from apps.tours.models.tour_schedules import TourSchedule

class Status(models.TextChoices):
    PENDING = 'PENDING', 'Chưa đặt'
    CONFIRMED = 'CONFIRMED', 'Đã xác nhận'
    CANCELLED = 'CANCELLED', 'Đã hủy'

class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tour_schedule = models.ForeignKey(TourSchedule, on_delete=models.CASCADE)
    total_people = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(choices=Status.choices, default=Status.PENDING)
    note = models.TextField(blank=True, null=True)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking by {self.user.username} for {self.tour_schedule.tour.title}"