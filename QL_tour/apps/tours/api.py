# api.py
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import RouteStop, tours

class TourMapAPI(APIView):
    def get(self, request, id):
        tour = tours.objects.get(id=id)

        routes = RouteStop.objects.all(id = tour)

        return Response([
            {
                "id": t.id,
                "title": t.title,
                "lat": t.location.y,  # latitude
                "lng": t.location.x,  # longitude
                "thumbnail_url": t.thumbnail.url if t.thumbnail else None
            }
            for t in tourRoute
        ])
