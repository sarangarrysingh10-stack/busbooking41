from decimal import Decimal
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Route, BusTrip, City, Inquiry, BusLocation, Booking


def support_context():
    return {
        'support_phone': settings.SUPPORT_PHONE,
        'support_phone_digits': settings.SUPPORT_WHATSAPP,
        'support_email': settings.SUPPORT_EMAIL,
    }


def home(request):
    cities = City.objects.all()
    context = {'cities': cities}
    context.update(support_context())
    return render(request, 'index.html', context)


def search(request):
    from_city = request.GET.get('from', '').strip()
    to_city = request.GET.get('to', '').strip()
    trip_type = request.GET.get('trip_type', 'oneway').strip().lower()
    is_round_trip = trip_type == 'round'

    if not from_city or not to_city:
        messages.error(request, 'Please select both From and To cities.')
        return redirect('home')

    if from_city == to_city:
        messages.error(request, 'From and To cities cannot be the same.')
        return redirect('home')

    outbound_routes = Route.objects.filter(from_city__name=from_city, to_city__name=to_city)
    return_routes = Route.objects.none()

    if is_round_trip:
        return_routes = Route.objects.filter(from_city__name=to_city, to_city__name=from_city)

    if outbound_routes.exists() or return_routes.exists():
        trips = BusTrip.objects.filter(route__in=outbound_routes).select_related('route__from_city', 'route__to_city')
        return_trips = BusTrip.objects.filter(route__in=return_routes).select_related('route__from_city', 'route__to_city') if is_round_trip else []
        context = {
            'trips': trips,
            'return_trips': return_trips,
            'from_city': from_city,
            'to_city': to_city,
            'is_round_trip': is_round_trip,
        }
        context.update(support_context())
        return render(request, 'results.html', context)

    suggestions = Route.objects.filter(from_city__name=from_city).select_related('to_city')
    context = {'suggestions': suggestions, 'from_city': from_city, 'to_city': to_city, 'is_round_trip': is_round_trip}
    context.update(support_context())
    return render(request, 'no_routes.html', context)


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


def book_trip(request, trip_id):
    trip = get_object_or_404(BusTrip.objects.select_related('route__from_city', 'route__to_city'), id=trip_id)

    if request.method == 'POST':
        passenger_name = request.POST.get('passenger_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        payment_method = request.POST.get('payment_method', 'PAY_LATER').strip()
        payer_name = request.POST.get('payer_name', '').strip()
        payer_upi_id = request.POST.get('payer_upi_id', '').strip()
        payment_reference = request.POST.get('payment_reference', '').strip()

        valid_methods = {'PAY_LATER', 'PAYPAL', 'CARD', 'NET_BANKING'}
        if payment_method not in valid_methods:
            payment_method = 'PAY_LATER'

        try:
            seats = int(request.POST.get('seats', '1'))
        except ValueError:
            seats = 1

        if not passenger_name or not email or not phone:
            messages.error(request, 'Please fill name, email and phone number.')
            return redirect('book_trip', trip_id=trip.id)

        if seats < 1:
            messages.error(request, 'Please select at least 1 seat.')
            return redirect('book_trip', trip_id=trip.id)

        if seats > trip.available_seats:
            messages.error(request, f'Only {trip.available_seats} seat(s) are available for this trip.')
            return redirect('book_trip', trip_id=trip.id)

        # For online demo payments, collect details for admin verification.
        if payment_method in {'PAYPAL', 'CARD', 'NET_BANKING'}:
            if not payer_name or not payment_reference:
                messages.error(request, 'For online payment, enter payer name and transaction/reference ID.')
                return redirect('book_trip', trip_id=trip.id)
            if payment_method == 'PAYPAL' and not payer_upi_id:
                messages.error(request, 'For PayPal payment, enter PayPal email/account ID.')
                return redirect('book_trip', trip_id=trip.id)

        total_amount = Decimal(seats) * trip.price
        payment_status = 'NOT_PAID' if payment_method == 'PAY_LATER' else 'PENDING'

        booking = Booking.objects.create(
            trip=trip,
            passenger_name=passenger_name,
            email=email,
            phone=phone,
            seats=seats,
            total_amount=total_amount,
            status='PENDING',
            payment_method=payment_method,
            payment_status=payment_status,
            payer_name=payer_name,
            payer_upi_id=payer_upi_id,
            payment_reference=payment_reference,
        )
        trip.available_seats -= seats
        trip.save(update_fields=['available_seats'])

        messages.success(request, 'Booking request created successfully. Admin can confirm it from Django Admin.')
        return redirect('booking_success', booking_id=booking.id)

    context = {'trip': trip}
    context.update(support_context())
    return render(request, 'booking_form.html', context)


def booking_success(request, booking_id):
    booking = get_object_or_404(Booking.objects.select_related('trip__route__from_city', 'trip__route__to_city'), id=booking_id)
    context = {'booking': booking}
    context.update(support_context())
    return render(request, 'booking_success.html', context)


def booking_lookup(request):
    query = request.GET.get('q', '').strip()
    bookings = []
    if query:
        bookings = Booking.objects.select_related('trip__route__from_city', 'trip__route__to_city').filter(
            phone__icontains=query
        ) | Booking.objects.select_related('trip__route__from_city', 'trip__route__to_city').filter(
            email__icontains=query
        )
    context = {'query': query, 'bookings': bookings}
    context.update(support_context())
    return render(request, 'booking_lookup.html', context)


# ── Map view ──────────────────────────────────────────────────────────────────
def map_view(request):
    # Used after booking success, for example: /map/?route=12
    highlight_route_id = request.GET.get('route') or request.GET.get('route_id') or ''

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
            'id': r.id,
            'from': r.from_city.name,
            'to': r.to_city.name,
            'from_lat': r.from_city.latitude,
            'from_lng': r.from_city.longitude,
            'to_lat': r.to_city.latitude,
            'to_lng': r.to_city.longitude,
            'trips': r.trips.count(),
            'distance_miles': r.distance_miles,
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
        'highlight_route_id': highlight_route_id,
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
            'speed_mph': loc.speed_mph,
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
        defaults={'latitude': lat, 'longitude': lng, 'speed_mph': speed, 'is_active': True}
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
