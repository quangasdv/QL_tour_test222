from django.shortcuts import render
from ..tours.models.continent import Continent
from ..tours.models.country import Country
from ..tours.models.categories import Category

def search_tours_data(request):
    categories = Category.objects.all()
    countries = Country.objects.all()
    continents = Continent.objects.all()

    return render(
        request, 
        'index.html',
        {
            "categories": categories,
            'countries': countries,
            "continents": continents
        }
    )