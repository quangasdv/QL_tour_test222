from .models import Booking
from django.contrib.auth import get_user_model
from ..tours.models.tour_schedules import TourSchedule

User = get_user_model()

def create_booking(user_id, tour_schedule_id, total_people, total_price, note=None, payment_method=None): 
    user = User.objects.get(id=user_id)
    tour_schedule = TourSchedule.objects.get(id=tour_schedule_id)

    booking = Booking.objects.create(
        user=user,
        tour_schedule=tour_schedule,
        total_people=total_people,
        total_price=total_price,
        note=note,
        payment_method=payment_method
    )
    return booking