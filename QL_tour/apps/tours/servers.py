# api.py
from django.db.models import Prefetch
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from .models.tour_route import TourRoute
from .models.route_stop import RouteStop
from .serializers import TourRouteMapSerializer
import json

class TourMapAPI(APIView):
    def get(self, request, id):
        qs = (
            TourRoute.objects
            .filter(tour=id)
            .annotate(stop_count=Count("routestop"))
            .prefetch_related(
                Prefetch(
                    "routestop_set",
                    queryset=RouteStop.objects.select_related("stop").order_by("order"),
                )
            )
        )

        routes = list(qs.order_by("-is_active", "-stop_count", "-id"))
        if not routes:
            # No route created yet -> return empty feature collection (map won't crash).
            return Response({"type": "FeatureCollection", "features": []})

        # Build a single FeatureCollection that includes:
        # - The active (or best) route geometry (if any)
        # - ALL stops across ALL routes of this tour (dedup by stop id)
        best_route = routes[0]
        features = []

        # Route LineString (optional)
        if best_route.route:
            features.append(
                {
                    "type": "Feature",
                    "geometry": json.loads(best_route.route.geojson),
                    "properties": {
                        "type": "route",
                        "name": best_route.name,
                        "distance_km": best_route.distance_km or 0,
                    },
                }
            )

        # Stops (union of all routestops for this tour)
        seen_stop_ids = set()
        for route in routes:
            for rs in route.routestop_set.all():
                stop = rs.stop
                if not stop or stop.id in seen_stop_ids:
                    continue
                seen_stop_ids.add(stop.id)
                features.append(
                    {
                        "type": "Feature",
                        "geometry": json.loads(stop.location.geojson),
                        "properties": {
                            "type": "stop",
                            "name": stop.name,
                            # Keep "order" for display; if stop appears in multiple routes,
                            # we keep the first encountered order.
                            "order": rs.order,
                            "description": stop.description,
                        },
                    }
                )

        return Response({"type": "FeatureCollection", "features": features})
