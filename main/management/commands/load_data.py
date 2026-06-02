from django.core.management.base import BaseCommand
from main.models import City, Route, BusTrip


class Command(BaseCommand):
    help = 'Loads 15 US cities, routes, and sample bus trips into the database'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.MIGRATE_HEADING('\n🚌 BusGo — Loading sample data...\n'))

        # ── CITIES ────────────────────────────────────────────
        cities_data = [
            {'name': 'New York',      'country': 'USA', 'latitude': 40.7128,  'longitude': -74.0060},
            {'name': 'Los Angeles',   'country': 'USA', 'latitude': 34.0522,  'longitude': -118.2437},
            {'name': 'Chicago',       'country': 'USA', 'latitude': 41.8781,  'longitude': -87.6298},
            {'name': 'Houston',       'country': 'USA', 'latitude': 29.7604,  'longitude': -95.3698},
            {'name': 'Philadelphia',  'country': 'USA', 'latitude': 39.9526,  'longitude': -75.1652},
            {'name': 'Dallas',        'country': 'USA', 'latitude': 32.7767,  'longitude': -96.7970},
            {'name': 'Seattle',       'country': 'USA', 'latitude': 47.6062,  'longitude': -122.3321},
            {'name': 'Denver',        'country': 'USA', 'latitude': 39.7392,  'longitude': -104.9903},
            {'name': 'Miami',         'country': 'USA', 'latitude': 25.7617,  'longitude': -80.1918},
            {'name': 'Atlanta',       'country': 'USA', 'latitude': 33.7490,  'longitude': -84.3880},
            {'name': 'Boston',        'country': 'USA', 'latitude': 42.3601,  'longitude': -71.0589},
            {'name': 'Las Vegas',     'country': 'USA', 'latitude': 36.1699,  'longitude': -115.1398},
            {'name': 'San Francisco', 'country': 'USA', 'latitude': 37.7749,  'longitude': -122.4194},
            {'name': 'Washington DC', 'country': 'USA', 'latitude': 38.9072,  'longitude': -77.0369},
            {'name': 'Orlando',       'country': 'USA', 'latitude': 28.5383,  'longitude': -81.3792},
        ]

        city_objs = {}
        created_count = 0
        for data in cities_data:
            obj, created = City.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            city_objs[data['name']] = obj
            if created:
                created_count += 1
                self.stdout.write(f"  ✅ City: {obj.name}")
            else:
                self.stdout.write(f"  ⏭  City already exists: {obj.name}")

        self.stdout.write(self.style.SUCCESS(f'\n  {created_count} new cities added.\n'))

        # ── ROUTES ────────────────────────────────────────────
        routes_data = [
            ('New York',      'Philadelphia',  152),
            ('New York',      'Boston',        346),
            ('New York',      'Washington DC', 365),
            ('Washington DC', 'Philadelphia',  225),
            ('Los Angeles',   'San Francisco', 559),
            ('Los Angeles',   'Las Vegas',     435),
            ('Miami',         'Orlando',       380),
            ('Miami',         'Atlanta',       1061),
            ('Seattle',       'Denver',        2120),
            ('Houston',       'Dallas',        386),
            ('Atlanta',       'Washington DC', 1100),
            ('Boston',        'Washington DC', 710),
            ('Chicago',       'Houston',       1700),
            ('Dallas',        'Denver',        1480),
            ('San Francisco', 'Las Vegas',     919),
        ]

        route_objs = {}
        r_created = 0
        for frm, to, km in routes_data:
            if frm not in city_objs or to not in city_objs:
                self.stdout.write(self.style.WARNING(f"  ⚠️  Skipping route {frm}→{to}: city not found"))
                continue
            obj, created = Route.objects.get_or_create(
                from_city=city_objs[frm],
                to_city=city_objs[to],
                defaults={'distance_km': km}
            )
            route_objs[f"{frm}→{to}"] = obj
            if created:
                r_created += 1
                self.stdout.write(f"  ✅ Route: {frm} → {to} ({km} km)")
            else:
                self.stdout.write(f"  ⏭  Route already exists: {frm} → {to}")

        self.stdout.write(self.style.SUCCESS(f'\n  {r_created} new routes added.\n'))

        # ── BUS TRIPS ─────────────────────────────────────────
        trips_data = [
            # (route_key, bus_name, bus_type, dep, arr, price, total, avail, amenities)
            ('New York→Philadelphia',  'Greyhound Express',    'SEATER', '07:00', '09:30',  25.00, 45, 45, 'WiFi, Charging, AC'),
            ('New York→Philadelphia',  'FlixBus Morning',      'SEATER', '09:00', '11:15',  19.00, 50, 50, 'WiFi, AC'),
            ('New York→Philadelphia',  'Greyhound Night',      'AC',     '22:00', '00:30',  35.00, 40, 40, 'WiFi, Blanket, AC'),
            ('New York→Boston',        'Greyhound Express',    'SEATER', '08:00', '13:30',  45.00, 45, 45, 'WiFi, Charging, AC'),
            ('New York→Boston',        'FlixBus Comfort',      'LUXURY', '10:00', '15:30',  65.00, 30, 30, 'WiFi, Meals, USB, AC, Recliner'),
            ('New York→Boston',        'Peter Pan Night',      'AC',     '22:00', '03:30',  55.00, 40, 40, 'WiFi, Blanket, Pillow, AC'),
            ('New York→Washington DC', 'Bolt Bus',             'SEATER', '06:30', '12:30',  39.00, 50, 50, 'WiFi, Charging, AC'),
            ('New York→Washington DC', 'Luxury Liner',         'LUXURY', '16:00', '22:00',  75.00, 25, 25, 'WiFi, Meals, Lounge, AC'),
            ('Washington DC→Philadelphia', 'Coastal Connector','SEATER', '07:30', '11:00',  29.00, 50, 50, 'WiFi, Charging, AC'),
            ('Los Angeles→San Francisco',  'Pacific Cruiser',  'AC',     '08:00', '16:30',  59.00, 40, 40, 'WiFi, Charging, Blanket, AC'),
            ('Los Angeles→San Francisco',  'CA Express',       'SEATER', '12:00', '20:00',  45.00, 50, 50, 'WiFi, AC'),
            ('Los Angeles→Las Vegas',      'Desert Runner',    'SEATER', '07:00', '13:30',  35.00, 50, 50, 'WiFi, Charging, AC'),
            ('Los Angeles→Las Vegas',      'Vegas Night',      'LUXURY', '22:00', '04:30',  75.00, 30, 30, 'WiFi, Meals, Recliner, AC'),
            ('Miami→Orlando',              'Sunshine Express', 'SEATER', '08:30', '14:30',  39.00, 45, 45, 'WiFi, Charging, AC'),
            ('Miami→Orlando',              'Florida Cruiser',  'AC',     '21:00', '03:00',  55.00, 40, 40, 'WiFi, Blanket, AC'),
            ('Miami→Atlanta',              'Southeast Express','AC',     '20:00', '06:00',  79.00, 40, 40, 'WiFi, Blanket, Pillow, Meals, AC'),
            ('Seattle→Denver',             'Mountain Express', 'AC',     '19:00', '13:00',  89.00, 40, 40, 'WiFi, Blanket, Pillow, AC'),
            ('Houston→Dallas',             'Texas Star',       'SEATER', '08:00', '13:30',  39.00, 50, 50, 'WiFi, Charging, AC'),
            ('Houston→Dallas',             'Lone Star Night',  'AC',     '22:00', '03:30',  55.00, 40, 40, 'WiFi, Blanket, AC'),
            ('Boston→Washington DC',       'Northeast Express','AC',     '07:00', '19:00',  85.00, 40, 40, 'WiFi, Blanket, Charging, AC'),
            ('Chicago→Houston',            'Midwest Express',  'AC',     '18:00', '10:00',  95.00, 40, 40, 'WiFi, Blanket, Pillow, Meals, AC'),
            ('Dallas→Denver',              'Rocky Mountain',   'AC',     '19:00', '09:00',  89.00, 40, 40, 'WiFi, Blanket, Pillow, Meals, AC'),
            ('San Francisco→Las Vegas',    'Desert Wind',      'SEATER', '08:00', '19:00',  55.00, 45, 45, 'WiFi, Charging, AC'),
            ('Atlanta→Washington DC',      'Capital Express',  'AC',     '20:00', '08:00',  79.00, 40, 40, 'WiFi, Blanket, AC'),
        ]

        t_created = 0
        for (rkey, bname, btype, dep, arr, price, total, avail, amen) in trips_data:
            if rkey not in route_objs:
                self.stdout.write(self.style.WARNING(f"  ⚠️  Skipping trip {bname}: route {rkey} not found"))
                continue
            exists = BusTrip.objects.filter(route=route_objs[rkey], bus_name=bname).exists()
            if not exists:
                BusTrip.objects.create(
                    route=route_objs[rkey],
                    bus_name=bname,
                    bus_type=btype,
                    departure_time=dep,
                    arrival_time=arr,
                    price=price,
                    total_seats=total,
                    available_seats=avail,
                    amenities=amen,
                )
                t_created += 1
                self.stdout.write(f"  ✅ Trip: {bname} ({rkey})")
            else:
                self.stdout.write(f"  ⏭  Trip already exists: {bname}")

        self.stdout.write(self.style.SUCCESS(f'\n  {t_created} new bus trips added.\n'))
        self.stdout.write(self.style.SUCCESS(
            f'🎉 Done! {created_count} cities, {r_created} routes, {t_created} trips loaded.\n'
            f'   Visit /admin/ to view all data.\n'
            f'   Visit /map/ to see routes on the map.\n'
        ))
