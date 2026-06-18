#!/bin/bash
set -e

echo "============================================"
echo " BusGo — Container Starting"
echo "============================================"

echo "Waiting for PostgreSQL at ${PGHOST}:${PGPORT:-5432}..."

MAX_RETRIES=30
COUNT=0

until python -c "
import os, psycopg2, sys, re
try:
    raw_port = os.environ.get('PGPORT', '5432')
    port = int(re.sub(r'[^0-9]', '', raw_port) or '5432')
    psycopg2.connect(
        host=os.environ.get('PGHOST', 'localhost'),
        port=port,
        dbname=os.environ.get('PGDATABASE', 'railway'),
        user=os.environ.get('PGUSER', 'postgres'),
        password=os.environ.get('PGPASSWORD', ''),
        connect_timeout=3,
    )
    print('PostgreSQL is ready!')
    sys.exit(0)
except psycopg2.OperationalError as e:
    print(f'Not ready: {e}')
    sys.exit(1)
" 2>&1; do
    COUNT=$((COUNT + 1))
    if [ "$COUNT" -ge "$MAX_RETRIES" ]; then
        echo "ERROR: PostgreSQL did not become ready after ${MAX_RETRIES} attempts. Exiting."
        exit 1
    fi
    echo "Attempt $COUNT/$MAX_RETRIES — retrying in 3s..."
    sleep 3
done

echo "--------------------------------------------"
echo "Running database migrations..."
python manage.py migrate --noinput

echo "--------------------------------------------"
echo "Removing old outside-mainland route cities if already present..."
python manage.py shell -c "from main.models import City; City.objects.filter(name__in=['Anchorage','Fairbanks','Honolulu','Hilo']).delete()"

echo "--------------------------------------------"
echo "Loading route data from CSV..."
python manage.py load_from_csv

echo "--------------------------------------------"
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "--------------------------------------------"
echo "Starting Gunicorn server on port ${PORT:-8000}..."
exec gunicorn bus_booking.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers 2 \
    --timeout 120 \
    --log-file - \
    --access-logfile -