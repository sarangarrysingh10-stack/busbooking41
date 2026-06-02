import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import Route, BusTrip, City, Inquiry, BusLocation


def home(request):
    cities = City.objects.all()
    return render(request, 'index.html', {
        'cities': cities,
        'support_phone': settings.SUPPORT_PHONE,
        'support_email': settings.SUPPORT_EMAIL,
    })


def search(request):
    from_city = request.GET.get('from', '').strip()
    to_city = request.GET.get('to', '').strip()

    if not from_city or not to_city:
        messages.error(request, 'Please select both From and To cities.')
        return redirect('home')

    if from_city == to_city:
        messages.error(request, 'From and To cities cannot be the same.')
        return redirect('home')

    routes = Route.objects.filter(from_city__name=from_city, to_city__name=to_city)

    if routes.exists():
        trips = BusTrip.objects.filter(route__in=routes).select_related('route__from_city', 'route__to_city')
        return render(request, 'results.html', {
            'trips': trips,
            'from_city': from_city,
            'to_city': to_city,
            'support_phone': settings.SUPPORT_PHONE,
            'support_email': settings.SUPPORT_EMAIL,
        })
    else:
        suggestions = Route.objects.filter(from_city__name=from_city).select_related('to_city')
        return render(request, 'no_routes.html', {
            'suggestions': suggestions,
            'from_city': from_city,
            'to_city': to_city,
            'support_phone': settings.SUPPORT_PHONE,
            'support_email': settings.SUPPORT_EMAIL,
        })


def inquiry(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        message_text = request.POST.get('message', '').strip()
        phone = request.POST.get('phone', '').strip()
        from_city = request.POST.get('from_city', '').strip()
        to_city = request.POST.get('to_city', '').strip()

        if not name or not email or not message_text:
            messages.error(request, 'Please fill in all required fields.')
            return redirect('home')

        Inquiry.objects.create(
            name=name, email=email, phone=phone,
            from_city=from_city, to_city=to_city, message=message_text,
        )
        messages.success(request, 'Your inquiry has been submitted! We will contact you soon.')
        return redirect('home')

    return redirect('home')


# ── Map view ──────────────────────────────────────────────────────────────────
def map_view(request):
    cities = City.objects.exclude(latitude=None).exclude(longitude=None)
    routes = Route.objects.select_related('from_city', 'to_city').prefetch_related('trips')

    city_data = [
        {'name': c.name, 'lat': c.latitude, 'lng': c.longitude}
        for c in cities
    ]

    route_data = []
    for r in routes:
        if not (r.from_city.latitude and r.to_city.latitude):
            continue
        first_trip = r.trips.first()
        dep_time = first_trip.departure_time.strftime('%I:%M %p') if first_trip else None
        arr_time = first_trip.arrival_time.strftime('%I:%M %p') if first_trip else None

        route_data.append({
            'from': r.from_city.name,
            'to': r.to_city.name,
            'from_lat': r.from_city.latitude,
            'from_lng': r.from_city.longitude,
            'to_lat': r.to_city.latitude,
            'to_lng': r.to_city.longitude,
            'trips': r.trips.count(),
            'distance_km': r.distance_km,
            'dep_time': dep_time,
            'arr_time': arr_time,
            'bus_name': first_trip.bus_name if first_trip else None,
            'price': str(first_trip.price) if first_trip else None,
        })

    return render(request, 'map.html', {
        'cities_json': json.dumps(city_data),
        'routes_json': json.dumps(route_data),
        'total_cities': cities.count(),
        'total_routes': len(route_data),
    })


# ── API: get all live bus locations ──────────────────────────────────────────
def live_locations_api(request):
    """Returns JSON of all active bus locations — polled every 5s by passenger map."""
    locations = BusLocation.objects.filter(is_active=True).select_related(
        'trip__route__from_city', 'trip__route__to_city'
    )
    data = []
    for loc in locations:
        trip = loc.trip
        data.append({
            'trip_id': trip.id,
            'bus_name': trip.bus_name,
            'bus_type': trip.get_bus_type_display(),
            'from': trip.route.from_city.name,
            'to': trip.route.to_city.name,
            'lat': loc.latitude,
            'lng': loc.longitude,
            'speed_kmh': loc.speed_kmh,
            'last_updated': loc.last_updated.strftime('%H:%M:%S'),
        })
    return JsonResponse({'buses': data})


# ── API: driver pushes their GPS location ─────────────────────────────────────
@csrf_exempt
@require_http_methods(['POST'])
def update_location_api(request, token):
    """Driver app calls this every 5s with their current GPS coords."""
    trip = get_object_or_404(BusTrip, driver_token=token)
    try:
        body = json.loads(request.body)
        lat = float(body['lat'])
        lng = float(body['lng'])
        speed = float(body.get('speed', 0))
    except (KeyError, ValueError, json.JSONDecodeError):
        return JsonResponse({'error': 'Invalid data'}, status=400)

    BusLocation.objects.update_or_create(
        trip=trip,
        defaults={'latitude': lat, 'longitude': lng, 'speed_kmh': speed, 'is_active': True}
    )
    return JsonResponse({'status': 'ok', 'bus': trip.bus_name})


# ── Driver app page ───────────────────────────────────────────────────────────
def driver_app(request, token):
    """Mobile web page the driver opens on their phone."""
    trip = get_object_or_404(BusTrip, driver_token=token)
    return render(request, 'driver.html', {'trip': trip, 'token': token})


# ── Admin live dashboard ──────────────────────────────────────────────────────
def admin_tracking(request):
    """Admin page showing all buses live."""
    if not request.user.is_staff:
        return redirect('/admin/login/?next=/tracking/')
    trips = BusTrip.objects.select_related('route__from_city', 'route__to_city').all()
    return render(request, 'tracking_admin.html', {'trips': trips})
