from django.shortcuts import get_object_or_404, redirect, render
from rest_framework.decorators import api_view
from .models import Tour
from .models.tour_schedules import TourSchedule
from .serializers import TourSerializer
from rest_framework.response import Response

def tour_detail(request, id):
    tour = get_object_or_404(Tour, pk=id)
    schedules = TourSchedule.objects.filter(tour=tour)

    return render(request, 'detail.html', {'tour': tour, 'schedules': schedules})

@api_view(['GET'])
def tours(request):
    tours = Tour.objects.all()
    serializer = TourSerializer(tours, many=True)
    return Response(serializer.data) 

def tour_search(request):
    data = {k: v for k, v in request.POST.items() if v and k != 'csrfmiddlewaretoken'}
    
    # Xử lý title riêng để tìm kiếm mờ (LIKE %...%)
    title = data.pop('title', '')
    
    # Tạo query từ các field khác (category, country)
    tours = Tour.objects.filter(**data)
    
    # Thêm điều kiện tìm kiếm title nếu có
    if title:
        tours = tours.filter(title__icontains=title)
    
    request.session['tour_ids'] = list(tours.values_list('id', flat=True))
    return redirect('tour_results') 

def tour_results(request):
    tour_ids = request.session.pop('tour_ids', [])
    tours = Tour.objects.filter(id__in=tour_ids) if tour_ids else Tour.objects.none()
    return render(request, 'index.html', {'tours': tours})
