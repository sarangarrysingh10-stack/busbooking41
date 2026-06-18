import logging
from django.conf import settings
from django.core.mail import EmailMessage, get_connection

logger = logging.getLogger(__name__)


def _money(value):
    try:
        return f"${value:.2f}"
    except Exception:
        return f"${value}"


def booking_public_message(booking, heading, note, booking_url=None, map_url=None):
    """Builds a safe plain-text email message for passenger booking updates."""
    trip = booking.trip
    route = trip.route

    dep_time = trip.departure_time.strftime('%H:%M') if trip.departure_time else 'N/A'
    arr_time = trip.arrival_time.strftime('%H:%M') if trip.arrival_time else 'N/A'

    lines = [
        heading,
        "",
        note,
        "",
        f"Booking ID: #{booking.id}",
        f"Status: {booking.get_status_display() if hasattr(booking, 'get_status_display') else booking.status}",
        f"Passenger: {booking.passenger_name}",
        f"Route: {route.from_city.name} → {route.to_city.name}",
        f"Bus: {trip.bus_name}",
        f"Time: {dep_time} → {arr_time}",
        f"Seats: {booking.seats}",
        f"Total Amount: {_money(booking.total_amount)}",
        f"Payment Method: {booking.get_payment_method_display() if hasattr(booking, 'get_payment_method_display') else getattr(booking, 'payment_method', '')}",
        f"Payment Status: {booking.get_payment_status_display() if hasattr(booking, 'get_payment_status_display') else getattr(booking, 'payment_status', '')}",
    ]

    selected_seats = getattr(booking, 'selected_seats', '')
    if selected_seats:
        lines.append(f"Selected Seat(s): {selected_seats}")

    payment_reference = getattr(booking, 'payment_reference', '')
    if payment_reference:
        lines.append(f"Payment Reference: {payment_reference}")

    if booking_url:
        lines += ["", f"Check your booking: {booking_url}"]
    if map_url:
        lines.append(f"View route on map: {map_url}")

    lines += [
        "",
        "For any help, contact BusGo support.",
        f"Phone: {getattr(settings, 'SUPPORT_PHONE', '')}",
        f"Email: {getattr(settings, 'SUPPORT_EMAIL', '')}",
        "",
        "Note: This is an automated email from BusGo.",
    ]
    return "\n".join(lines)


def send_passenger_email(booking, subject, heading, note, booking_url=None, map_url=None):
    """
    Sends an email to the passenger.
    Very important: email failure must never break booking or Django Admin save.
    """
    try:
        if not getattr(booking, 'email', ''):
            return False

        message = booking_public_message(
            booking=booking,
            heading=heading,
            note=note,
            booking_url=booking_url,
            map_url=map_url,
        )

        connection = get_connection(
            fail_silently=True,
            timeout=getattr(settings, 'EMAIL_TIMEOUT', 8),
        )

        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
            to=[booking.email],
            connection=connection,
        )
        sent_count = email.send(fail_silently=True)
        return sent_count > 0

    except Exception as exc:
        # Never raise this exception because it can break booking/admin pages.
        logger.warning("BusGo email could not be sent to %s: %s", getattr(booking, 'email', ''), exc)
        return False


def send_booking_created_email(booking, booking_url=None, map_url=None):
    return send_passenger_email(
        booking=booking,
        subject=f"BusGo Booking Request Created - #{booking.id}",
        heading="BusGo Booking Request Created",
        note="Your booking request has been created successfully. It is pending until admin verifies and confirms it.",
        booking_url=booking_url,
        map_url=map_url,
    )


def send_booking_confirmed_email(booking, booking_url=None, map_url=None):
    return send_passenger_email(
        booking=booking,
        subject=f"BusGo Booking Confirmed - #{booking.id}",
        heading="BusGo Booking Confirmed",
        note="Good news! Your booking has been confirmed by admin.",
        booking_url=booking_url,
        map_url=map_url,
    )


def send_booking_cancelled_email(booking, booking_url=None, map_url=None):
    return send_passenger_email(
        booking=booking,
        subject=f"BusGo Booking Cancelled - #{booking.id}",
        heading="BusGo Booking Cancelled",
        note="Your booking has been cancelled by admin. Please contact support if you need help.",
        booking_url=booking_url,
        map_url=map_url,
    )


def send_payment_paid_email(booking, booking_url=None, map_url=None):
    return send_passenger_email(
        booking=booking,
        subject=f"BusGo Payment Verified - #{booking.id}",
        heading="BusGo Payment Verified",
        note="Your payment has been marked as paid by admin.",
        booking_url=booking_url,
        map_url=map_url,
    )
