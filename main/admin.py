from django.contrib import admin
from django.utils.html import format_html
from .models import City, Route, BusTrip, BusLocation, Inquiry


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'latitude', 'longitude')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('from_city', 'to_city', 'distance_km')
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
    list_display = ('trip', 'latitude', 'longitude', 'speed_kmh', 'is_active', 'last_updated')
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
