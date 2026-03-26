from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import models
from django.forms import modelform_factory
from django.forms.widgets import HiddenInput, CheckboxInput
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.functional import cached_property
from django.views import View
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from django.db.models import Q

from apps.bookings.models import Booking
from apps.payments.models import Payment
from apps.tours.forms import TourStopAdminForm
from apps.tours.models.categories import Category
from apps.tours.models.continent import Continent
from apps.tours.models.country import Country
from apps.tours.models.tour_route import TourRoute
from apps.tours.models.tours import Tour
from apps.tours.models.tour_schedules import TourSchedule
from apps.tours.models.tour_stop import TourStop
from apps.tours.models.route_stop import RouteStop

from .forms import TourRouteAdminForm, TourScheduleAdminForm, TourDurationRangeAdminForm


@dataclass(frozen=True)
class ModelConfig:
    key: str
    model: type[models.Model]
    label: str
    list_display: list[str]  # attribute paths. Special: 'latitude'/'longitude' for TourStop.
    search_fields: list[str]
    exclude_form_fields: tuple[str, ...] = ()
    # Optional custom ModelForm class for create/update.
    form_class: Any | None = None


def _perm_code(model: type[models.Model], action: str) -> str:
    # action: view/add/change/delete
    return f"{model._meta.app_label}.{action}_{model._meta.model_name}"


class StaffRequiredMixin(LoginRequiredMixin):
    login_url = "/login/"

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not request.user.is_staff:
            raise PermissionDenied("Bạn không có quyền truy cập admin.")
        return super().dispatch(request, *args, **kwargs)

    def require_perm(self, request: HttpRequest, model: type[models.Model], action: str) -> None:
        if not request.user.has_perm(_perm_code(model, action)):
            raise PermissionDenied("Bạn không có quyền thực hiện thao tác này.")


class AdminDashboardView(StaffRequiredMixin, TemplateView):
    template_name = "admin_panel/dashboard.html"

    @cached_property
    def menu(self) -> list[ModelConfig]:
        return get_model_configs()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        ctx["menu"] = self.menu
        return ctx


def get_model_configs() -> list[ModelConfig]:
    # Keep ordering stable and intuitive.
    return [
        ModelConfig(
            key="categories",
            model=Category,
            label="Categories",
            list_display=["id", "name"],
            search_fields=["name"],
        ),
        ModelConfig(
            key="continents",
            model=Continent,
            label="Continents",
            list_display=["id", "name", "code"],
            search_fields=["name", "code"],
        ),
        ModelConfig(
            key="countries",
            model=Country,
            label="Countries",
            list_display=["id", "name", "code", "continent.name"],
            search_fields=["name", "code", "continent__name"],
        ),
        ModelConfig(
            key="tours",
            model=Tour,
            label="Tours",
            list_display=[
                "id",
                "title",
                "category.name",
                "country.name",
                "price",
                "duration_days",
                "max_people",
                "status",
                "create_at",
            ],
            search_fields=["title", "description", "category__name", "country__name", "status"],
            # Tour diễn ra từ/ngày nào đến/ngày nào nằm ở `TourSchedule`.
            # Ẩn trường `duration_days` để admin-panel không gây nhầm lẫn.
            exclude_form_fields=("duration_days",),
            form_class=TourDurationRangeAdminForm,
        ),
        ModelConfig(
            key="tour_schedules",
            model=TourSchedule,
            label="Tour Schedules",
            list_display=["id", "tour.title", "start_day", "end_day", "total_slots"],
            search_fields=["tour__title"],
            form_class=TourScheduleAdminForm,
        ),
        ModelConfig(
            key="tour_routes",
            model=TourRoute,
            label="Tour Routes",
            list_display=["id", "tour.title", "name", "distance_km", "is_active"],
            search_fields=["name", "tour__title"],
            exclude_form_fields=("route", "distance_km"),
            form_class=TourRouteAdminForm,  # custom form
        ),
        ModelConfig(
            key="tour_stops",
            model=TourStop,
            label="Tour Stops",
            list_display=["id", "name", "description", "latitude", "longitude"],
            search_fields=["name", "description"],
            form_class=TourStopAdminForm,
        ),
        ModelConfig(
            key="route_stops",
            model=RouteStop,
            label="Route Stops",
            list_display=["id", "route.name", "stop.name", "order", "stay_minutes"],
            search_fields=["route__name", "stop__name"],
        ),
        ModelConfig(
            key="bookings",
            model=Booking,
            label="Bookings",
            list_display=[
                "id",
                "user.username",
                "tour_schedule.tour.title",
                "total_people",
                "total_price",
                "status",
                "payment_method",
                "create_at",
            ],
            search_fields=["user__username", "note", "status", "tour_schedule__tour__title"],
        ),
        ModelConfig(
            key="payments",
            model=Payment,
            label="Payments",
            list_display=[
                "id",
                "transaction_id",
                "booking.id",
                "booking.user.username",
                "payment_method",
                "status",
                "amount",
                "paid_at",
            ],
            search_fields=["transaction_id", "booking__user__username", "booking__tour_schedule__tour__title"],
        ),
    ]


def get_model_config(model_key: str) -> ModelConfig:
    for cfg in get_model_configs():
        if cfg.key == model_key:
            return cfg
    raise PermissionDenied("Không tồn tại module admin này.")


def _get_attr_path(obj: Any, attr_path: str) -> Any:
    # Special computed columns for GIS.
    if attr_path == "latitude":
        loc = getattr(obj, "location", None)
        return getattr(loc, "y", None)
    if attr_path == "longitude":
        loc = getattr(obj, "location", None)
        return getattr(loc, "x", None)

    current = obj
    for part in attr_path.split("."):
        current = getattr(current, part, None)
        if current is None:
            return None
    return current


def _get_list_display_rows(config: ModelConfig, object_list: list[models.Model]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for obj in object_list:
        row: dict[str, Any] = {}
        for col in config.list_display:
            value = _get_attr_path(obj, col)
            row[col] = value
        rows.append(row)
    return rows


def _column_label(col: str) -> str:
    if col == "latitude":
        return "Latitude"
    if col == "longitude":
        return "Longitude"
    # Show last part of dotted attribute, e.g. `category.name` => `name`.
    last = col.split(".")[-1]
    return last.replace("_", " ").strip().title()


def _build_form_class(config: ModelConfig):
    if config.form_class is not None:
        return config.form_class
    return modelform_factory(config.model, exclude=config.exclude_form_fields)


def _apply_bootstrap_form_widgets(form) -> list[str]:
    """
    Add consistent Bootstrap classes for widgets so templates stay simple.
    Returns list of checkbox field names for special rendering.
    """
    checkbox_fields: list[str] = []
    from django.forms.widgets import Select

    for name, field in form.fields.items():
        widget = field.widget
        if isinstance(widget, HiddenInput):
            continue

        existing = widget.attrs.get("class", "")
        if isinstance(widget, CheckboxInput):
            checkbox_fields.append(name)
            widget.attrs["class"] = " ".join([existing, "form-check-input"]).strip()
        elif isinstance(widget, Select):
            widget.attrs["class"] = " ".join([existing, "form-select"]).strip()
        else:
            widget.attrs["class"] = " ".join([existing, "form-control"]).strip()

    return checkbox_fields


class AdminModelListView(StaffRequiredMixin, View):
    template_name = "admin_panel/model_list.html"
    paginate_by = 10

    def get(self, request: HttpRequest, model_key: str) -> HttpResponse:
        config = get_model_config(model_key)
        self.require_perm(request, config.model, "view")

        qs = config.model.objects.all()

        q = request.GET.get("q", "").strip()
        if q:
            query = Q()
            for field in config.search_fields:
                # Best-effort search on text fields.
                query |= Q(**{f"{field}__icontains": q})
            qs = qs.filter(query)

        # Simple ordering by GET `order` (e.g. `id` or `-id`)
        order = request.GET.get("order") or "-id"
        if order.lstrip("-").isidentifier():
            qs = qs.order_by(order)

        paginator = Paginator(qs, self.paginate_by)
        page_number = request.GET.get("page") or 1
        page_obj = paginator.get_page(page_number)

        rows = _get_list_display_rows(config, list(page_obj.object_list))
        columns = [{"key": col, "label": _column_label(col)} for col in config.list_display]

        return render(
            request,
            self.template_name,
            {
                "menu": get_model_configs(),
                "current_key": config.key,
                "config": config,
                "page_obj": page_obj,
                "rows": rows,
                "columns": columns,
                "q": q,
            },
        )


class AdminModelCreateView(StaffRequiredMixin, View):
    template_name = "admin_panel/model_form.html"

    def get(self, request: HttpRequest, model_key: str) -> HttpResponse:
        config = get_model_config(model_key)
        self.require_perm(request, config.model, "add")
        form_class = _build_form_class(config)
        form = form_class()
        checkbox_fields = _apply_bootstrap_form_widgets(form)
        return render(
            request,
            self.template_name,
            {
                "menu": get_model_configs(),
                "current_key": config.key,
                "config": config,
                "form": form,
                "mode": "create",
                "checkbox_fields": checkbox_fields,
            },
        )

    def post(self, request: HttpRequest, model_key: str) -> HttpResponse:
        config = get_model_config(model_key)
        self.require_perm(request, config.model, "add")
        form_class = _build_form_class(config)
        form = form_class(request.POST, request.FILES)
        checkbox_fields = _apply_bootstrap_form_widgets(form)
        if form.is_valid():
            form.save()
            messages.success(request, f"Đã tạo mới {config.label} thành công.")
            return redirect(reverse("admin_panel:model_list", kwargs={"model_key": config.key}))
        return render(
            request,
            self.template_name,
            {
                "menu": get_model_configs(),
                "current_key": config.key,
                "config": config,
                "form": form,
                "mode": "create",
                "checkbox_fields": checkbox_fields,
            },
        )


class AdminModelUpdateView(StaffRequiredMixin, View):
    template_name = "admin_panel/model_form.html"

    def get(self, request: HttpRequest, model_key: str, pk: int) -> HttpResponse:
        config = get_model_config(model_key)
        self.require_perm(request, config.model, "change")
        obj = get_object_or_404(config.model, pk=pk)
        form_class = _build_form_class(config)
        form = form_class(instance=obj)
        checkbox_fields = _apply_bootstrap_form_widgets(form)
        return render(
            request,
            self.template_name,
            {
                "menu": get_model_configs(),
                "current_key": config.key,
                "config": config,
                "form": form,
                "mode": "edit",
                "obj": obj,
                "checkbox_fields": checkbox_fields,
            },
        )

    def post(self, request: HttpRequest, model_key: str, pk: int) -> HttpResponse:
        config = get_model_config(model_key)
        self.require_perm(request, config.model, "change")
        obj = get_object_or_404(config.model, pk=pk)
        form_class = _build_form_class(config)
        form = form_class(request.POST, request.FILES, instance=obj)
        checkbox_fields = _apply_bootstrap_form_widgets(form)
        if form.is_valid():
            form.save()
            messages.success(request, f"Đã cập nhật {config.label} thành công.")
            return redirect(reverse("admin_panel:model_list", kwargs={"model_key": config.key}))
        return render(
            request,
            self.template_name,
            {
                "menu": get_model_configs(),
                "current_key": config.key,
                "config": config,
                "form": form,
                "mode": "edit",
                "obj": obj,
                "checkbox_fields": checkbox_fields,
            },
        )


class AdminModelDeleteView(StaffRequiredMixin, View):
    template_name = "admin_panel/model_confirm_delete.html"

    def get(self, request: HttpRequest, model_key: str, pk: int) -> HttpResponse:
        config = get_model_config(model_key)
        self.require_perm(request, config.model, "delete")
        obj = get_object_or_404(config.model, pk=pk)
        return render(
            request,
            self.template_name,
            {
                "menu": get_model_configs(),
                "current_key": config.key,
                "config": config,
                "obj": obj,
            },
        )

    def post(self, request: HttpRequest, model_key: str, pk: int) -> HttpResponse:
        config = get_model_config(model_key)
        self.require_perm(request, config.model, "delete")
        obj = get_object_or_404(config.model, pk=pk)
        obj.delete()
        messages.success(request, f"Đã xóa {config.label} thành công.")
        return redirect(reverse("admin_panel:model_list", kwargs={"model_key": config.key}))

