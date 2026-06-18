from django.db import models
import uuid


class City(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=50, default='USA')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Cities'
        ordering = ['name']

    def __str__(self):
        return self.name


class Route(models.Model):
    from_city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='departures')
    to_city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='arrivals')
    distance_miles = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('from_city', 'to_city')

    def __str__(self):
        return f"{self.from_city} → {self.to_city}"


class BusTrip(models.Model):
    BUS_TYPES = [
        ('AC', 'AC Sleeper'),
        ('NAC', 'Non-AC Sleeper'),
        ('SEATER', 'AC Seater'),
        ('LUXURY', 'Luxury'),
    ]

    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='trips')
    bus_name = models.CharField(max_length=100)
    bus_type = models.CharField(max_length=10, choices=BUS_TYPES, default='AC')
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    total_seats = models.PositiveIntegerField(default=40)
    available_seats = models.PositiveIntegerField(default=40)
    amenities = models.CharField(max_length=255, blank=True)

    # Driver tracking token — unique secret link for each driver
    driver_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    class Meta:
        ordering = ['departure_time']

    def __str__(self):
        return f"{self.bus_name} ({self.route})"

    @property
    def is_available(self):
        return self.available_seats > 0

    @property
    def duration_display(self):
        from datetime import datetime, timedelta
        dep = datetime.combine(datetime.today(), self.departure_time)
        arr = datetime.combine(datetime.today(), self.arrival_time)
        if arr < dep:
            arr += timedelta(days=1)
        diff = arr - dep
        hours, rem = divmod(diff.seconds, 3600)
        mins = rem // 60
        return f"{hours}h {mins}m"


class BusLocation(models.Model):
    """Stores the latest GPS location for each active bus trip."""
    trip = models.OneToOneField(BusTrip, on_delete=models.CASCADE, related_name='location')
    latitude = models.FloatField()
    longitude = models.FloatField()
    speed_mph = models.FloatField(default=0)
    is_active = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.trip.bus_name} @ {self.latitude:.4f},{self.longitude:.4f}"


class Inquiry(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True)
    from_city = models.CharField(max_length=100, blank=True)
    to_city = models.CharField(max_length=100, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Inquiries'

    def __str__(self):
        return f"{self.name} ({self.email})"


class Booking(models.Model):
    """Stores passenger booking requests made from the trip results page."""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('PAY_LATER', 'Pay Later / Counter'),
        ('PAYPAL', 'PayPal'),
        ('CARD', 'Debit / Credit Card'),
        ('NET_BANKING', 'Net Banking'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('NOT_PAID', 'Not Paid'),
        ('PENDING', 'Payment Pending'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
    ]

    trip = models.ForeignKey(BusTrip, on_delete=models.CASCADE, related_name='bookings')
    passenger_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    seats = models.PositiveIntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='PENDING')

    # Payment details for demo/verification. Do not store full card number or sensitive bank details.
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='PAY_LATER')
    payment_status = models.CharField(max_length=12, choices=PAYMENT_STATUS_CHOICES, default='NOT_PAID')
    payer_name = models.CharField(max_length=100, blank=True)
    payer_upi_id = models.CharField(max_length=100, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True, help_text='PayPal/Card/Net Banking transaction reference ID')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Booking #{self.id} - {self.passenger_name} - {self.trip.bus_name}"
