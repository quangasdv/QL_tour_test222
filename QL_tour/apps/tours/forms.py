from django import forms
from django.contrib.gis.geos import Point
from .models.tours import Tour
from .models.tour_stop import TourStop

class TourAdminForm(forms.ModelForm):
    # Định nghĩa 2 ô nhập số thủ công
    lat_input = forms.FloatField(label="Latitude", required=False)
    lon_input = forms.FloatField(label="Longitude", required=False)

    class Meta:
        model = Tour
        fields = '__all__'


class TourStopAdminForm(forms.ModelForm):
    lat_input = forms.FloatField(label="Latitude", required=False)
    lon_input = forms.FloatField(label="Longitude", required=False)

    class Meta:
        model = TourStop
        # We will set `location` from lat/lon inputs in `ModelAdmin.save_model()`.
        exclude = ('location',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Prefill lat/lon when editing an existing object.
        if getattr(self.instance, "pk", None) and getattr(self.instance, "location", None):
            try:
                self.fields["lat_input"].initial = self.instance.location.y
                self.fields["lon_input"].initial = self.instance.location.x
            except Exception:
                # If geometry is missing/invalid, just leave inputs empty.
                pass

    def clean(self):
        cleaned_data = super().clean()
        lat = cleaned_data.get('lat_input')
        lon = cleaned_data.get('lon_input')

        # On create: `TourStop.location` is required by the model.
        # Since we exclude `location` from the form, we must require lat/lon.
        if self.instance.pk is None and (lat is None or lon is None):
            raise forms.ValidationError('Vui lòng nhập đủ Latitude và Longitude.')

        return cleaned_data

    def save(self, commit=True):
        obj = super().save(commit=False)
        lat = self.cleaned_data.get("lat_input")
        lon = self.cleaned_data.get("lon_input")
        if lat is not None and lon is not None:
            obj.location = Point(lon, lat)
        if commit:
            obj.save()
            self.save_m2m()
        return obj