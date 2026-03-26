from django.contrib import admin
from django.contrib.gis.geos import Point

from .forms import TourStopAdminForm

from .models.categories import Category
from .models.continent import Continent
from .models.country import Country
from .models.route_stop import RouteStop
from .models.tour_route import TourRoute
from .models.tour_schedules import TourSchedule
from .models.tour_stop import TourStop
from .models.tours import Tour


@admin.register(Category)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Tour)
class ToursAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'category',
        'country',
        'price',
        'duration_days',
        'max_people',
        'status',
        'create_at',
    )
    search_fields = ('title', 'description', 'category__name', 'country__name')
    list_filter = ('status', 'category', 'country')
    ordering = ('-create_at',)


@admin.register(TourSchedule)
class TourSchedulesAdmin(admin.ModelAdmin):
    list_display = ('id', 'tour', 'start_day', 'end_day', 'total_slots')
    search_fields = ('tour__title',)
    list_filter = ('tour__category', 'start_day', 'end_day')
    ordering = ('-start_day',)


@admin.register(Country)
class CountriesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'continent')
    search_fields = ('name', 'code')
    list_filter = ('continent',)
    ordering = ('name',)


@admin.register(Continent)
class ContinentsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code')
    search_fields = ('name', 'code')
    ordering = ('name',)


@admin.register(TourRoute)
class TourRoutesAdmin(admin.ModelAdmin):
    list_display = ('id', 'tour', 'name', 'distance_km', 'is_active')
    search_fields = ('name', 'tour__title')
    list_filter = ('is_active', 'tour__category')
    ordering = ('tour', 'name')
    exclude = ('route',)  # Avoid editing geometry directly in admin forms.


@admin.register(TourStop)
class TourStopsAdmin(admin.ModelAdmin):
    form = TourStopAdminForm
    list_display = ('id', 'name', 'latitude', 'longitude', 'description')
    search_fields = ('name', 'description')
    ordering = ('name',)
    exclude = ('location',)  # Use lat_input/lon_input instead.

    def latitude(self, obj):
        return obj.location.y if obj.location else None

    latitude.short_description = 'Latitude'

    def longitude(self, obj):
        return obj.location.x if obj.location else None

    longitude.short_description = 'Longitude'

    def save_model(self, request, obj, form, change):
        lat = form.cleaned_data.get('lat_input')
        lon = form.cleaned_data.get('lon_input')

        # On create: location is required by the model; require lat/lon in the form.
        if lat is not None and lon is not None:
            obj.location = Point(lon, lat)

        super().save_model(request, obj, form, change)


@admin.register(RouteStop)
class RoutesStopAdmin(admin.ModelAdmin):
    list_display = ('id', 'route', 'stop', 'order', 'stay_minutes')
    search_fields = ('route__name', 'stop__name')
    ordering = ('route', 'order')