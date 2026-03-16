from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework.response import Response
from apps.tours.models.tours import Tour
from apps.tours.models.tour_schedules import TourSchedule
from .servers import create_booking
import leafmap.leafmap as lm

def booking_confirm(request, id):
    tour_schedule = get_object_or_404(TourSchedule, id=id)
    context = {
        'tour_schedule': tour_schedule,
        'tour': tour_schedule.tour
    }
    return render(request, 'booking.html', context)

@login_required(login_url='login')
def booking(request):
    if request.method == 'POST':
        user = request.user
        tour_schedule_id = request.POST.get('tour_schedule_id')
        quantity = request.POST.get('quantity')
        payment_method = request.POST.get('payment')
        notes = request.POST.get('notes')
        
        # Validation
        try:
            tour_schedule = TourSchedule.objects.get(id=tour_schedule_id)
            quantity = int(quantity)
            
            if quantity <= 0:
                messages.error(request, 'Số lượng phải lớn hơn 0')
                return redirect('booking_confirm', id=tour_schedule_id)
            
            if quantity > tour_schedule.total_slots:
                messages.error(request, 'Vượt quá số ghế trống')
                return redirect('booking_confirm', id=tour_schedule_id)
            
            # Calculate total price
            total_price = tour_schedule.tour.price * quantity
            
            # Create booking
            booking = create_booking(
                user_id=user.id,
                tour_schedule_id=tour_schedule_id,
                total_people=quantity,
                total_price=total_price,
                note=notes,
                payment_method=payment_method
            )
            
            messages.success(request, 'Đặt tour thành công!')
            return redirect('tour_detail', id=tour_schedule.tour.id)
            
        except TourSchedule.DoesNotExist:
            messages.error(request, 'Tour không tồn tại')
            return redirect('tour_list')
        except ValueError:
            messages.error(request, 'Dữ liệu không hợp lệ')
            return redirect('booking_confirm', id=tour_schedule_id)
    
    return redirect('tour_list')

def map_view(request):
    # 1. Tạo đối tượng bản đồ
    m = lm.Map(center=[21.0285, 105.8542], zoom=12) # Ví dụ: Hà Nội
    
    # 2. Thêm các thành phần nếu muốn (ví dụ: lớp nền)
    m.add_basemap("HYBRID")
    
    # 3. Xuất bản đồ ra chuỗi HTML
    # Chúng ta sử dụng .to_html() để lấy mã nhúng
    map_html = m.to_html()

    return render(request, 'map_template.html', {'map_html': map_html})

