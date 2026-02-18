from typing import Any
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from ..tours.models.categories import Category
from ..tours.models.continent import Continent
from ..tours.models.country import Country
from apps.tours.models.tours import Tour


class Home(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'
    login_url = '/login/'
    redirect_field_name = 'next'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['tours'] = Tour.objects.all()
        context['categories'] = Category.objects.all()
        context['countries'] = Country.objects.all()
        context['continents'] = Continent.objects.all()
        return context

class About(TemplateView):
    template_name = 'about.html'