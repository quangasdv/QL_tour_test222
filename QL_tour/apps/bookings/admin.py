from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingsAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'tour_schedule',
        'total_people',
        'total_price',
        'status',
        'payment_method',
        'create_at',
    )
    search_fields = ('user__username', 'tour_schedule__tour__title', 'note', 'status')
    list_filter = ('status', 'payment_method', 'create_at')
    ordering = ('-create_at',)

    def get_queryset(self, request):
        # Speed up FK rendering in changelist.
        return super().get_queryset(request).select_related('user', 'tour_schedule', 'tour_schedule__tour')
