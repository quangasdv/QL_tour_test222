from django.contrib import admin
from ..tours.forms import TourAdminForm
from .models.categories import Category
from .models.tours import Tour
from .models.tour_schedules import TourSchedule
from .models.tour_stop import TourStop
from .models.tour_route import TourRoute
from .models.route_stop import RouteStop
from .models.country import Country
from django.contrib.gis.geos import Point

@admin.register(Category)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

    search_fields = ('name',)

@admin.register(Tour)
class ToursAdmin(admin.ModelAdmin):
    form = TourAdminForm
    list_display = [field.name for field in Tour._meta.fields]

    search_fields = ('title', 'price', 'category__name')

    exclude = ('location',)

    def save_model(self, request, obj, form, change):
        lat = form.cleaned_data.get('lat_input')
        lon = form.cleaned_data.get('lon_input')
        
        if lat is not None and lon is not None:
            obj.location = Point(lon, lat)
            
        super().save_model(request, obj, form, change)

@admin.register(TourSchedule)
class TourSchedulesAdmin(admin.ModelAdmin):
    list_display = [field.name for field in TourSchedule._meta.fields]

    search_fields = ('name', 'latitude', 'longitude')

@admin.register(Country)
class CountriesAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Country._meta.fields]

@admin.register(TourRoute)
class TourRoutesAdmin(admin.ModelAdmin):
    list_display = [field.name for field in TourRoute._meta.fields]

    exclude = ('route',)

@admin.register(TourStop)
class TourStopsAdmin(admin.ModelAdmin):
    form = TourAdminForm
    list_display = [field.name for field in TourStop._meta.fields]

    search_fields = ('name', 'latitude', 'longitude')

    exclude = ('location',)

    def save_model(self, request, obj, form, change):
        lat = form.cleaned_data.get('lat_input')
        lon = form.cleaned_data.get('lon_input')

        if lat is not None and lon is not None:
            obj.location = Point(lon, lat)

        super().save_model(request, obj, form, change)

@admin.register(RouteStop)
class RoutesStopAdmin(admin.ModelAdmin):
    list_display = [field.name for field in RouteStop._meta.fields]