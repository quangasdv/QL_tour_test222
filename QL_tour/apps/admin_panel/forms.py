from django import forms

from apps.tours.models.tour_route import TourRoute
from apps.tours.models.tours import Tour
from apps.tours.models.tour_schedules import TourSchedule
from apps.tours.models.tour_stop import TourStop
from apps.tours.models.route_stop import RouteStop
from datetime import datetime, time


class TourRouteAdminForm(forms.ModelForm):
    """
    Custom admin form:
    - Exclude geometry field `route`
    - Exclude derived field `distance_km`
    """

    class Meta:
        model = TourRoute
        exclude = ("route", "distance_km")


class TourScheduleAdminForm(forms.ModelForm):
    """
    Use datetime-local widgets so UI shows native date/time picker.
    """

    class Meta:
        model = TourSchedule
        fields = "__all__"
        labels = {
            "start_day": "Từ ngày",
            "end_day": "Đến ngày",
        }
        widgets = {
            "start_day": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"}
            ),
            "end_day": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"}
            ),
        }


class TourDurationRangeAdminForm(forms.ModelForm):
    """
    Admin-panel custom form for `Tour`:
    - Hide `duration_days` (existing field)
    - Provide a UI to select start/end datetime with predefined time slots
    - Upsert `TourSchedule` (1..N schedules for the tour) to match the range.
    """

    TIME_SLOTS = [
        (f"{h:02d}:00", f"{h:02d}:00") for h in range(6, 22)
    ]  # 06:00 - 21:00

    start_date = forms.DateField(
        label="Từ ngày",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        required=True,
    )
    start_time = forms.ChoiceField(
        label="Giờ bắt đầu",
        choices=TIME_SLOTS,
        widget=forms.Select(attrs={"class": "form-select"}),
        required=True,
    )
    end_date = forms.DateField(
        label="Đến ngày",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        required=True,
    )
    end_time = forms.ChoiceField(
        label="Giờ kết thúc",
        choices=TIME_SLOTS,
        widget=forms.Select(attrs={"class": "form-select"}),
        required=True,
    )
    stop_ids = forms.ModelMultipleChoiceField(
        label="Tour stops",
        queryset=TourStop.objects.all().order_by("name"),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-select", "size": "8"}),
        help_text="Chọn các điểm dừng thuộc tour này.",
    )

    class Meta:
        model = Tour
        exclude = ("duration_days",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Prefill range fields from an existing schedule (if any).
        if getattr(self.instance, "pk", None):
            schedule = (
                TourSchedule.objects.filter(tour=self.instance)
                .order_by("-id")
                .first()
            )
            if schedule and schedule.start_day and schedule.end_day:
                self.fields["start_date"].initial = schedule.start_day.date()
                self.fields["end_date"].initial = schedule.end_day.date()

                start_t = schedule.start_day.strftime("%H:%M")
                end_t = schedule.end_day.strftime("%H:%M")

                # If stored time is not in predefined slots, fallback to nearest hour slot.
                slot_values = [v for v, _ in self.TIME_SLOTS]
                if start_t not in slot_values:
                    start_t = f"{schedule.start_day.hour:02d}:00"
                if end_t not in slot_values:
                    end_t = f"{schedule.end_day.hour:02d}:00"

                self.fields["start_time"].initial = start_t
                self.fields["end_time"].initial = end_t

            # Prefill selected stops from route (prefer active route, fallback first route).
            route = (
                TourRoute.objects.filter(tour=self.instance, is_active=True).order_by("-id").first()
                or TourRoute.objects.filter(tour=self.instance).order_by("-id").first()
            )
            if route:
                selected_stop_ids = list(
                    RouteStop.objects.filter(route=route).order_by("order").values_list("stop_id", flat=True)
                )
                if selected_stop_ids:
                    self.initial["stop_ids"] = selected_stop_ids

    def _combine_dt(self, d, t_str: str) -> datetime:
        # t_str: "HH:MM"
        hh, mm = t_str.split(":")
        return datetime.combine(d, time(int(hh), int(mm)))

    def clean(self):
        cleaned = super().clean()
        start_date = cleaned.get("start_date")
        end_date = cleaned.get("end_date")
        start_time = cleaned.get("start_time")
        end_time = cleaned.get("end_time")

        if start_date and start_time:
            cleaned["_start_dt"] = self._combine_dt(start_date, start_time)
        if end_date and end_time:
            cleaned["_end_dt"] = self._combine_dt(end_date, end_time)

        start_dt = cleaned.get("_start_dt")
        end_dt = cleaned.get("_end_dt")
        if start_dt and end_dt and end_dt < start_dt:
            raise forms.ValidationError("Thời gian kết thúc phải sau thời gian bắt đầu.")

        return cleaned

    def save(self, commit=True):
        tour = super().save(commit=False)
        start_dt = self.cleaned_data.get("_start_dt")
        end_dt = self.cleaned_data.get("_end_dt")
        selected_stops_qs = self.cleaned_data.get("stop_ids")

        # `Tour.duration_days` is a required DateTimeField in your model.
        # We keep it consistent by storing the selected start datetime.
        if start_dt:
            tour.duration_days = start_dt

        tour.save()

        if start_dt and end_dt:
            # Update all existing schedules for this tour to match the selected range.
            TourSchedule.objects.filter(tour=tour).update(start_day=start_dt, end_day=end_dt)
            if not TourSchedule.objects.filter(tour=tour).exists():
                # In case there were no schedules.
                TourSchedule.objects.create(tour=tour, start_day=start_dt, end_day=end_dt)

        # Sync RouteStop from selected stops (option A: only stops linked to tour are shown on map).
        route = (
            TourRoute.objects.filter(tour=tour, is_active=True).order_by("-id").first()
            or TourRoute.objects.filter(tour=tour).order_by("-id").first()
        )
        if not route:
            route = TourRoute.objects.create(tour=tour, name=f"{tour.title} Route", is_active=True)

        selected_stop_ids = []
        if selected_stops_qs is not None:
            # Keep user selection order based on submitted form list when possible.
            submitted_ids = [int(v) for v in self.data.getlist("stop_ids") if str(v).isdigit()]
            selected_set = set(selected_stops_qs.values_list("id", flat=True))
            selected_stop_ids = [sid for sid in submitted_ids if sid in selected_set]
            # Fallback if no POST order is available.
            if not selected_stop_ids:
                selected_stop_ids = list(selected_set)

        RouteStop.objects.filter(route=route).delete()
        for idx, stop_id in enumerate(selected_stop_ids, start=1):
            RouteStop.objects.create(route=route, stop_id=stop_id, order=idx)

        if commit:
            tour.save()
        return tour

