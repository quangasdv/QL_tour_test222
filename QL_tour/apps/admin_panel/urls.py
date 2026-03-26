from django.urls import path

from .views import (
    AdminDashboardView,
    AdminModelCreateView,
    AdminModelDeleteView,
    AdminModelListView,
    AdminModelUpdateView,
)

app_name = "admin_panel"

urlpatterns = [
    path("", AdminDashboardView.as_view(), name="dashboard"),
    path("<str:model_key>/", AdminModelListView.as_view(), name="model_list"),
    path("<str:model_key>/create/", AdminModelCreateView.as_view(), name="model_create"),
    path("<str:model_key>/<int:pk>/edit/", AdminModelUpdateView.as_view(), name="model_edit"),
    path("<str:model_key>/<int:pk>/delete/", AdminModelDeleteView.as_view(), name="model_delete"),
]

