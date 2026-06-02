from django.core.management.base import BaseCommand
from main.models import City, Route, BusTrip


class Command(BaseCommand):
    help = 'Loads sample cities, routes and bus trips into the database'

    def handle(self, *args, **kwargs):
        self.stdout.write('Loading sample data...')

        # ── Cities ────────────────────────────────────────
        cities_data = [
            ("New York",      "New York",      "USA", 40.7128,  -74.0060),
            ("Los Angeles",   "California",    "USA", 34.0522,  -118.2437),
            ("Chicago",       "Illinois",      "USA", 41.8781,  -87.6298),
            ("Houston",       "Texas",         "USA", 29.7604,  -95.3698),
            ("Phoenix",       "Arizona",       "USA", 33.4484,  -112.0740),
            ("Philadelphia",  "Pennsylvania",  "USA", 39.9526,  -75.1652),
            ("Dallas",        "Texas",         "USA", 32.7767,  -96.7970),
            ("Seattle",       "Washington",    "USA", 47.6062,  -122.3321),
            ("Denver",        "Colorado",      "USA", 39.7392,  -104.9903),
            ("Miami",         "Florida",       "USA", 25.7617,  -80.1918),
            ("Atlanta",       "Georgia",       "USA", 33.7490,  -84.3880),
            ("Boston",        "Massachusetts", "USA", 42.3601,  -71.0589),
            ("Las Vegas",     "Nevada",        "USA", 36.1699,  -115.1398),
            ("San Francisco", "California",    "USA", 37.7749,  -122.4194),
            ("Washington DC", "DC",            "USA", 38.9072,  -77.0369),
            ("Nashville",     "Tennessee",     "USA", 36.1627,  -86.7816),
            ("Portland",      "Oregon",        "USA", 45.5051,  -122.6750),
            ("Orlando",       "Florida",       "USA", 28.5383,  -81.3792),
            ("San Diego",     "California",    "USA", 32.7157,  -117.1611),
            ("San Antonio",   "Texas",         "USA", 29.4241,  -98.4936),
        ]

        city_objs = {}
        for name, state, country, lat, lng in cities_data:
            obj, created = City.objects.get_or_create(
                name=name,
                defaults={'country': country, 'latitude': lat, 'longitude': lng}
            )
            city_objs[name] = obj
            if created:
                self.stdout.write(f'  ✅ City: {name}')

        # ── Routes ────────────────────────────────────────
        routes_data = [
            ("New York",      "Philadelphia",  152),
            ("New York",      "Boston",        346),
            ("New York",      "Washington DC", 365),
            ("Washington DC", "Philadelphia",  225),
            ("Los Angeles",   "San Francisco", 559),
            ("Los Angeles",   "Las Vegas",     435),
            ("Los Angeles",   "San Diego",     193),
            ("Miami",         "Orlando",       380),
            ("Miami",         "Atlanta",       1061),
            ("Seattle",       "Portland",      280),
            ("Houston",       "Dallas",        386),
            ("Atlanta",       "Nashville",     413),
            ("Boston",        "Washington DC", 710),
            ("Dallas",        "San Antonio",   320),
            ("San Francisco", "San Diego",     800),
        ]

        route_objs = {}
        for frm, to, km in routes_data:
            if frm in city_objs and to in city_objs:
                obj, created = Route.objects.get_or_create(
                    from_city=city_objs[frm],
                    to_city=city_objs[to],
                    defaults={'distance_km': km}
                )
                route_objs[f"{frm}-{to}"] = obj
                if created:
                    self.stdout.write(f'  ✅ Route: {frm} → {to}')

        # ── Bus Trips ─────────────────────────────────────
        trips_data = [
            # (from, to, bus_name, bus_type, dep, arr, price, seats, amenities)
            ("New York", "Philadelphia", "Greyhound Express",   "SEATER", "07:00", "09:30", 25,  45, "WiFi, Charging, AC"),
            ("New York", "Philadelphia", "FlixBus Morning",     "SEATER", "09:00", "11:15", 19,  50, "WiFi, AC"),
            ("New York", "Philadelphia", "Megabus Express",     "SEATER", "14:00", "16:20", 15,  55, "WiFi, Charging"),
            ("New York", "Philadelphia", "Greyhound Night",     "AC",     "22:00", "00:30", 35,  40, "WiFi, Blanket, AC"),
            ("New York", "Boston",       "Greyhound Express",   "SEATER", "08:00", "13:30", 45,  45, "WiFi, Charging, AC"),
            ("New York", "Boston",       "FlixBus Comfort",     "LUXURY", "10:00", "15:30", 65,  30, "WiFi, Meals, USB, Recliner"),
            ("New York", "Boston",       "Peter Pan Night",     "AC",     "22:00", "03:30", 55,  40, "WiFi, Blanket, Pillow"),
            ("New York", "Washington DC","Bolt Bus",            "SEATER", "06:30", "12:30", 39,  50, "WiFi, Charging, AC"),
            ("New York", "Washington DC","Luxury Liner",        "LUXURY", "16:00", "22:00", 75,  25, "WiFi, Meals, Lounge, AC"),
            ("Washington DC","Philadelphia","Coastal Connector","SEATER", "07:30", "11:00", 29,  50, "WiFi, Charging, AC"),
            ("Los Angeles","San Francisco","Pacific Cruiser",   "AC",     "08:00", "16:30", 59,  40, "WiFi, Charging, Blanket"),
            ("Los Angeles","San Francisco","CA Express",        "SEATER", "12:00", "20:00", 45,  50, "WiFi, AC"),
            ("Los Angeles","Las Vegas",   "Desert Runner",      "SEATER", "07:00", "13:30", 35,  50, "WiFi, Charging, AC"),
            ("Los Angeles","Las Vegas",   "Vegas Night Express","LUXURY", "22:00", "04:30", 75,  30, "WiFi, Meals, Recliner"),
            ("Los Angeles","San Diego",   "SoCal Shuttle",      "SEATER", "08:00", "11:00", 22,  55, "WiFi, AC"),
            ("Miami",      "Orlando",    "Sunshine Express",   "SEATER", "08:30", "14:30", 39,  45, "WiFi, Charging, AC"),
            ("Miami",      "Atlanta",    "Southeast Express",  "AC",     "20:00", "06:00", 79,  40, "WiFi, Blanket, Meals"),
            ("Seattle",    "Portland",   "PNW Connector",      "SEATER", "09:00", "13:30", 35,  50, "WiFi, Charging, AC"),
            ("Houston",    "Dallas",     "Texas Star",         "SEATER", "08:00", "13:30", 39,  50, "WiFi, Charging, AC"),
            ("Atlanta",    "Nashville",  "Music City Express", "SEATER", "09:00", "15:30", 42,  45, "WiFi, Charging, AC"),
        ]

        for frm, to, name, btype, dep, arr, price, seats, amen in trips_data:
            key = f"{frm}-{to}"
            if key in route_objs:
                _, created = BusTrip.objects.get_or_create(
                    route=route_objs[key],
                    bus_name=name,
                    defaults={
                        'bus_type': btype,
                        'departure_time': dep,
                        'arrival_time': arr,
                        'price': price,
                        'total_seats': seats,
                        'available_seats': seats,
                        'amenities': amen,
                    }
                )
                if created:
                    self.stdout.write(f'  ✅ Trip: {name} ({frm} → {to})')

        self.stdout.write(self.style.SUCCESS('\n✅ Sample data loaded successfully!'))
        self.stdout.write('   Cities:    ' + str(City.objects.count()))
        self.stdout.write('   Routes:    ' + str(Route.objects.count()))
        self.stdout.write('   Bus Trips: ' + str(BusTrip.objects.count()))
