from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models.tours import Tour
import json

class TourRouteMapSerializer(serializers.Serializer):
    type = serializers.CharField(default="FeatureCollection")
    features = serializers.SerializerMethodField()

    def get_features(self, obj):
        features = []

        # Only include route geometry if it exists; returning "" breaks Leaflet GeoJSON parsing.
        if obj.route:
            features.append({
                "type": "Feature",
                "geometry": json.loads(obj.route.geojson),
                "properties": {
                    "type": "route",
                    "name": obj.name,
                    "distance_km": obj.distance_km or 0,
                }
            })

        for rs in obj.routestop_set.all():
            stop = rs.stop
            features.append({
                "type": "Feature",
                "geometry": json.loads(stop.location.geojson),
                "properties": {
                    "type": "stop",
                    "name": stop.name,
                    "order": rs.order,
                    "description": stop.description
                }
            })

        return features

class TourSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Tour
        geo_field = 'location'
        fields = ('id', 'title', 'thumbnail')