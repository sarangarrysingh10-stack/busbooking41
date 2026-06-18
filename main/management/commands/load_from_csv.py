import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from main.models import City, Route, BusTrip


# Coordinates lookup for supported mainland dataset cities
CITY_COORDS = {
    'Birmingham':       (33.5186,  -86.8104),
    'Montgomery':       (32.3668,  -86.3000),
    'Anchorage':        (61.2181, -149.9003),
    'Fairbanks':        (64.8378, -147.7164),
    'Phoenix':          (33.4484, -112.0740),
    'Tucson':           (32.2226, -110.9747),
    'Flagstaff':        (35.1983, -111.6513),
    'Little Rock':      (34.7465,  -92.2896),
    'Fort Smith':       (35.3859,  -94.3985),
    'Los Angeles':      (34.0522, -118.2437),
    'San Francisco':    (37.7749, -122.4194),
    'San Diego':        (32.7157, -117.1611),
    'Sacramento':       (38.5816, -121.4944),
    'Fresno':           (36.7378, -119.7871),
    'Denver':           (39.7392, -104.9903),
    'Colorado Springs': (38.8339, -104.8214),
    'Hartford':         (41.7658,  -72.6851),
    'New Haven':        (41.3083,  -72.9279),
    'Wilmington':       (39.7447,  -75.5484),
    'Miami':            (25.7617,  -80.1918),
    'Orlando':          (28.5383,  -81.3792),
    'Tampa':            (27.9506,  -82.4572),
    'Jacksonville':     (30.3322,  -81.6557),
    'Atlanta':          (33.7490,  -84.3880),
    'Savannah':         (32.0809,  -81.0912),
    'Honolulu':         (21.3069, -157.8583),
    'Hilo':             (19.7297, -155.0900),
    'Boise':            (43.6150, -116.2023),
    'Pocatello':        (42.8713, -112.4455),
    'Chicago':          (41.8781,  -87.6298),
    'Springfield':      (39.7817,  -89.6501),
    'Indianapolis':     (39.7684,  -86.1581),
    'Fort Wayne':       (41.1306,  -85.1289),
    'Des Moines':       (41.5868,  -93.6250),
    'Cedar Rapids':     (41.9779,  -91.6656),
    'Wichita':          (37.6872,  -97.3301),
    'Louisville':       (38.2527,  -85.7585),
    'Lexington':        (38.0406,  -84.5037),
    'New Orleans':      (29.9511,  -90.0715),
    'Baton Rouge':      (30.4515,  -91.1871),
    'Shreveport':       (32.5252,  -93.7502),
    'Baltimore':        (39.2904,  -76.6122),
    'Annapolis':        (38.9784,  -76.4922),
    'Boston':           (42.3601,  -71.0589),
    'Worcester':        (42.2626,  -71.8023),
    'Detroit':          (42.3314,  -83.0458),
    'Grand Rapids':     (42.9634,  -85.6681),
    'Lansing':          (42.7325,  -84.5555),
    'Minneapolis':      (44.9778,  -93.2650),
    'Saint Paul':       (44.9537,  -93.0900),
    'Duluth':           (46.7867,  -92.1005),
    'Jackson':          (32.2988,  -90.1848),
    'Biloxi':           (30.3960,  -88.8853),
    'Saint Louis':      (38.6270,  -90.1994),
    'Billings':         (45.7833, -108.5007),
    'Missoula':         (46.8721, -113.9940),
    'Omaha':            (41.2565,  -95.9345),
    'Lincoln':          (40.8136,  -96.7026),
    'Las Vegas':        (36.1699, -115.1398),
    'Reno':             (39.5296, -119.8138),
    'Manchester':       (42.9956,  -71.4548),
    'Concord':          (43.2081,  -71.5376),
    'Newark':           (40.7357,  -74.1724),
    'Atlantic City':    (39.3643,  -74.4229),
    'Albuquerque':      (35.0844, -106.6504),
    'Santa Fe':         (35.6870, -105.9378),
    'New York':         (40.7128,  -74.0060),
    'Buffalo':          (42.8864,  -78.8784),
    'Albany':           (42.6526,  -73.7562),
    'Rochester':        (43.1566,  -77.6088),
    'Charlotte':        (35.2271,  -80.8431),
    'Raleigh':          (35.7796,  -78.6382),
    'Greensboro':       (36.0726,  -79.7920),
    'Fargo':            (46.8772,  -96.7898),
    'Bismarck':         (46.8083, -100.7837),
    'Columbus':         (39.9612,  -82.9988),
    'Cleveland':        (41.4993,  -81.6944),
    'Cincinnati':       (39.1031,  -84.5120),
    'Oklahoma City':    (35.4676,  -97.5164),
    'Tulsa':            (36.1540,  -95.9928),
    'Eugene':           (44.0521, -123.0868),
    'Salem':            (44.9429, -123.0351),
    'Philadelphia':     (39.9526,  -75.1652),
    'Pittsburgh':       (40.4406,  -79.9959),
    'Allentown':        (40.6023,  -75.4714),
    'Providence':       (41.8240,  -71.4128),
    'Newport':          (41.4901,  -71.3128),
    'Columbia':         (34.0007,  -81.0348),
    'Sioux Falls':      (43.5446,  -96.7311),
    'Rapid City':       (44.0805, -103.2310),
    'Nashville':        (36.1627,  -86.7816),
    'Memphis':          (35.1495,  -90.0490),
    'Knoxville':        (35.9606,  -83.9207),
    'Houston':          (29.7604,  -95.3698),
    'Dallas':           (32.7767,  -96.7970),
    'San Antonio':      (29.4241,  -98.4936),
    'Austin':           (30.2672,  -97.7431),
    'El Paso':          (31.7619, -106.4850),
    'Salt Lake City':   (40.7608, -111.8910),
    'Provo':            (40.2338, -111.6585),
    'Burlington':       (44.4759,  -73.2121),
    'Montpelier':       (44.2601,  -72.5754),
    'Virginia Beach':   (36.8529,  -75.9780),
    'Richmond':         (37.5407,  -77.4360),
    'Norfolk':          (36.8508,  -76.2859),
    'Seattle':          (47.6062, -122.3321),
    'Spokane':          (47.6588, -117.4260),
    'Tacoma':           (47.2529, -122.4443),
    'Huntington':       (38.4192,  -82.4452),
    'Milwaukee':        (43.0389,  -87.9065),
    'Madison':          (43.0731,  -89.4012),
    'Cheyenne':         (41.1400, -104.8202),
    'Casper':           (42.8501, -106.3252),
    'Washington DC':    (38.9072,  -77.0369),
    'Bangor':           (44.8012,  -68.7778),
    # Cities with duplicate names — resolved by state context in CSV
    # Portland ME vs OR, Kansas City KS vs MO, Charleston SC vs WV
    'Portland':         (45.5051, -122.6750),   # OR (default)
    'Kansas City':      (39.0997,  -94.5786),   # MO (default)
    'Charleston':       (32.7765,  -79.9311),   # SC (default)
}

# Map bus type strings from CSV → Django model choices
BUS_TYPE_MAP = {
    'seater':  'SEATER',
    'ac':      'AC',
    'sleeper': 'NAC',
    'luxury':  'LUXURY',
}


class Command(BaseCommand):
    help = 'Load cities, routes, and bus trips from us_bus_routes_all_states.csv (mainland dataset)'

    def handle(self, *args, **kwargs):
        # Find CSV — try project root first, then BASE_DIR
        csv_path = os.path.join(settings.BASE_DIR, 'us_bus_routes_all_states.csv')
        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f'CSV not found at: {csv_path}'))
            return

        self.stdout.write(self.style.MIGRATE_HEADING('\n🚌 BusGo — Loading from CSV...\n'))

        city_cache  = {}   # name → City obj
        route_cache = {}   # "From→To" → Route obj
        cities_new  = 0
        routes_new  = 0
        trips_new   = 0
        skipped     = 0

        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        self.stdout.write(f'  📄 {len(rows)} rows found in CSV\n')

        for row in rows:
            from_name  = row['From_City'].strip()
            from_state = row['From_State'].strip()
            to_name    = row['To_City'].strip()
            to_state   = row['To_State'].strip()

            # Skip non-mainland rows kept out of the presentation dataset
            if from_state in {'Alaska', 'Hawaii'} or to_state in {'Alaska', 'Hawaii'}:
                skipped += 1
                continue

            # ── GET OR CREATE: From City ──────────────────
            fc_key = from_name
            if fc_key not in city_cache:
                coords = CITY_COORDS.get(from_name, (None, None))
                obj, created = City.objects.get_or_create(
                    name=from_name,
                    defaults={
                        'country':   'USA',
                        'latitude':  coords[0],
                        'longitude': coords[1],
                    }
                )
                city_cache[fc_key] = obj
                if created:
                    cities_new += 1
                    self.stdout.write(f'  ✅ City: {from_name}, {from_state}')

            # ── GET OR CREATE: To City ────────────────────
            tc_key = to_name
            if tc_key not in city_cache:
                coords = CITY_COORDS.get(to_name, (None, None))
                obj, created = City.objects.get_or_create(
                    name=to_name,
                    defaults={
                        'country':   'USA',
                        'latitude':  coords[0],
                        'longitude': coords[1],
                    }
                )
                city_cache[tc_key] = obj
                if created:
                    cities_new += 1
                    self.stdout.write(f'  ✅ City: {to_name}, {to_state}')

            from_city_obj = city_cache[fc_key]
            to_city_obj   = city_cache[tc_key]

            # ── GET OR CREATE: Route ──────────────────────
            route_key = f'{from_name}→{to_name}'
            if route_key not in route_cache:
                try:
                    dist_miles = int(row['Distance_Miles'])
                except (ValueError, KeyError):
                    dist_miles = None

                obj, created = Route.objects.get_or_create(
                    from_city=from_city_obj,
                    to_city=to_city_obj,
                    defaults={'distance_miles': dist_miles}
                )
                route_cache[route_key] = obj
                if created:
                    routes_new += 1

            route_obj = route_cache[route_key]

            # ── GET OR CREATE: Bus Trip ───────────────────
            bus_name = row['Bus_Operator'].strip()
            raw_type = row['Bus_Type'].strip().lower()
            bus_type = BUS_TYPE_MAP.get(raw_type, 'SEATER')

            try:
                price      = float(row['Ticket_Price_USD'])
                total      = int(row['Total_Seats'])
                available  = int(row['Seats_Available'])
                dep_time   = row['Departure_Time'].strip()
                arr_time   = row['Arrival_Time'].strip()
                amenities  = row['Amenities'].strip()
            except (ValueError, KeyError) as e:
                self.stdout.write(self.style.WARNING(f'  ⚠️  Skipping row (bad data): {e}'))
                skipped += 1
                continue

            _, created = BusTrip.objects.get_or_create(
                route=route_obj,
                bus_name=bus_name,
                departure_time=dep_time,
                defaults={
                    'bus_type':        bus_type,
                    'arrival_time':    arr_time,
                    'price':           price,
                    'total_seats':     total,
                    'available_seats': available,
                    'amenities':       amenities,
                }
            )
            if created:
                trips_new += 1

        # ── Summary ───────────────────────────────────────
        self.stdout.write('\n' + '─' * 45)
        self.stdout.write(self.style.SUCCESS('✅ Import complete!\n'))
        self.stdout.write(f'  New cities added  : {cities_new}')
        self.stdout.write(f'  New routes added  : {routes_new}')
        self.stdout.write(f'  New trips added   : {trips_new}')
        self.stdout.write(f'  Rows skipped      : {skipped}')
        self.stdout.write('─' * 45)
        self.stdout.write(f'  Total cities in DB : {City.objects.count()}')
        self.stdout.write(f'  Total routes in DB : {Route.objects.count()}')
        self.stdout.write(f'  Total trips in DB  : {BusTrip.objects.count()}')
        self.stdout.write('─' * 45 + '\n')
