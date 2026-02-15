from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import TourRoute, TourStop
import json

class TourRouteMapSerializer(serializers.Serializer):
    type = serializers.CharField(default="FeatureCollection")
    features = serializers.SerializerMethodField()

    def get_features(self, obj):
        features = []

        features.append({
            "type": "Feature",
            "geometry": json.loads(obj.route.geojson),
            "properties": {
                "type": "route",
                "name": obj.name,
                "distance_km": obj.distance_km
            }
        })

        # stops = [rs.stop for rs in obj.routestop_set.all()]
        for rs in obj.routestop_set.all():
            stop = rs.stop
            features.append({
                "type": "Feature",
                "geometry": json.loads(stop.location.geojson),
                "properties": {
                    "type": "stop",
                    "name": stop.name,
                    "order": rs.order
                }
            })

        return features
