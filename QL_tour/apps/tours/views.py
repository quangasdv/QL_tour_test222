from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view
from .models import Tour
from .serializers import TourSerializer
from rest_framework.response import Response
import json
from django.http import JsonResponse

def tour_detail(request, id):
    tour = get_object_or_404(Tour, pk=id)
    return render(request, 'detail.html', {'tour': tour})

@api_view(['GET'])
def tours(request):
    tours = Tour.objects.all()
    serializer = TourSerializer(tours, many=True)
    return Response(serializer.data) 

def tour_search(request):
    request_data = json.loads(request.body)
    search = request_data['search']
    return JsonResponse(search)
