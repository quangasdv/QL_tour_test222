# api.py
from django.db.models import Prefetch
from rest_framework.views import APIView
from rest_framework.response import Response
from .models.tour_route import TourRoute
from .models.route_stop import RouteStop
from .models.tour_stop import TourStop
from .serializer import TourRouteMapSerializer

class TourMapAPI(APIView):
    def get(self, request, id):
        route = (
            TourRoute.objects
            .prefetch_related(
                Prefetch(
                    "routestop_set",
                    queryset=RouteStop.objects
                    .select_related("stop")
                    .order_by("order")
                )
            )
            .get(tour=id)
        )

        serializer = TourRouteMapSerializer(route)

        return Response(serializer.data)
