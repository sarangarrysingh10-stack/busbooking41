import logging
from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from django.urls import reverse
from .models import City, Route, BusTrip, BusLocation, Inquiry, Booking
from .email_utils import send_booking_confirmed_email, send_booking_cancelled_email, send_payment_paid_email

logger = logging.getLogger(__name__)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'latitude', 'longitude')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('from_city', 'to_city', 'distance_miles')
    list_filter = ('from_city', 'to_city')
    search_fields = ('from_city__name', 'to_city__name')


@admin.register(BusTrip)
class BusTripAdmin(admin.ModelAdmin):
    list_display = ('bus_name', 'bus_type', 'route', 'departure_time', 'arrival_time', 'price', 'available_seats', 'driver_link')
    list_filter = ('bus_type',)
    search_fields = ('bus_name',)
    readonly_fields = ('driver_token', 'driver_link')

    def driver_link(self, obj):
        url = f"/driver/{obj.driver_token}/"
        return format_html('<a href="{}" target="_blank">📱 Driver Link</a>', url)
    driver_link.short_description = 'Driver App Link'


@admin.register(BusLocation)
class BusLocationAdmin(admin.ModelAdmin):
    list_display = ('trip', 'latitude', 'longitude', 'speed_mph', 'is_active', 'last_updated')
    list_filter = ('is_active',)
    readonly_fields = ('last_updated',)
    list_editable = ('is_active',)


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'from_city', 'to_city', 'created_at', 'is_resolved')
    list_filter = ('is_resolved', 'created_at')
    search_fields = ('name', 'email')
    readonly_fields = ('created_at',)
    list_editable = ('is_resolved',)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'passenger_name', 'phone', 'email', 'trip', 'seats', 'total_amount',
        'status', 'payment_method', 'payment_status', 'payment_reference', 'created_at'
    )
    list_filter = (
        'status', 'payment_method', 'payment_status', 'created_at',
        'trip__route__from_city', 'trip__route__to_city'
    )
    search_fields = (
        'passenger_name', 'phone', 'email', 'trip__bus_name',
        'payer_name', 'payer_upi_id', 'payment_reference'
    )
    readonly_fields = ('created_at', 'total_amount')
    list_editable = ('status', 'payment_status')

    def _booking_links(self, request, obj):
        booking_url = request.build_absolute_uri(reverse('booking_lookup') + f'?q={obj.phone}')
        map_url = request.build_absolute_uri(reverse('map') + f'?route={obj.trip.route.id}')
        return booking_url, map_url

    def save_model(self, request, obj, form, change):
        old_status = None
        old_payment_status = None
        if change and obj.pk:
            try:
                old_obj = Booking.objects.get(pk=obj.pk)
                old_status = old_obj.status
                old_payment_status = old_obj.payment_status
            except Booking.DoesNotExist:
                pass

        super().save_model(request, obj, form, change)

        if not change:
            return

        # Email notification must never break Django Admin save.
        try:
            booking_url, map_url = self._booking_links(request, obj)

            # Email passenger only when admin changes booking status.
            if old_status != obj.status:
                if obj.status == 'CONFIRMED':
                    send_booking_confirmed_email(obj, booking_url=booking_url, map_url=map_url)
                elif obj.status == 'CANCELLED':
                    send_booking_cancelled_email(obj, booking_url=booking_url, map_url=map_url)

            # Optional: email passenger when admin verifies payment.
            if old_payment_status != obj.payment_status and obj.payment_status == 'PAID':
                send_payment_paid_email(obj, booking_url=booking_url, map_url=map_url)

        except Exception as exc:
            logger.warning("Booking was saved, but email notification failed: %s", exc)
            self.message_user(
                request,
                "Booking saved, but email notification could not be sent. Check Railway email variables.",
                level=messages.WARNING,
            )
