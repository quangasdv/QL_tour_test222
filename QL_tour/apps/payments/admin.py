from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentsAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'transaction_id',
        'booking',
        'payment_method',
        'status',
        'amount',
        'paid_at',
    )
    search_fields = ('transaction_id', 'booking__user__username', 'booking__tour_schedule__tour__title')
    list_filter = ('status', 'payment_method', 'paid_at')
    ordering = ('-paid_at',)

    def get_queryset(self, request):
        return (
            super().get_queryset(request)
            .select_related('booking', 'booking__user', 'booking__tour_schedule', 'booking__tour_schedule__tour')
        )