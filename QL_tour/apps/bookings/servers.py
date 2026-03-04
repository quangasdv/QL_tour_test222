from .models import Booking
from django.contrib.auth.models import User
from ..tours.models.tour_schedules import TourSchedule

def create_booking(user_id, tour_schedule_id, total_people, total_price): 
    user = User.objects.get(id=user_id)
    tour_schedule = TourSchedule.objects.get(id=tour_schedule_id)

    booking = Booking.objects.create(
        user=user,
        tour_schedule=tour_schedule,
        total_people=total_people,
        total_price=total_price
    )
    return booking