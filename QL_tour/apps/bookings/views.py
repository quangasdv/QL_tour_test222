from django.shortcuts import render, get_object_or_404
from apps.tours.models.tours import Tour

def booking(request, id):
    tour = get_object_or_404(Tour, pk=id)

    if request.method == 'POST':
        # Handle booking form submission here
        pass
    return render(request, 'booking.html', {'tour': tour})
