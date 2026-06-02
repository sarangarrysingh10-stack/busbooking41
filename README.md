# BusGo — US Bus Route Booking

A Django web app for searching and booking bus routes across major US cities, deployable to Railway with one click.

---

## Live deployment (Railway)

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
# Create a repo on github.com, then:
git remote add origin https://github.com/YOUR_USERNAME/busgo.git
git push -u origin main
```

### 2. Deploy on Railway

1. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**
2. Select your repository
3. Inside the project dashboard, click **+ New** → **Database** → **Add PostgreSQL**
   - Railway automatically injects `DATABASE_URL` into your app
4. Go to your service → **Variables** tab → add:

| Variable | Value |
|---|---|
| `SECRET_KEY` | Run `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `*.up.railway.app` |

5. Click **Deploy** — Railway will automatically run migrations, collect static files, load sample data, and start Gunicorn.

### 3. Access your site

Railway provides a URL like `https://busgo-production.up.railway.app`.

**Custom domain:** Settings → Domains → Custom Domain → point DNS CNAME to Railway hostname, then set `CUSTOM_DOMAIN` env var.

---

## Local development

```bash
git clone https://github.com/YOUR_USERNAME/busgo.git
cd busgo
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # Edit .env and set SECRET_KEY
python manage.py migrate
python manage.py load_sample_data
python manage.py runserver
```

Visit http://localhost:8000

---

## Project structure

```
busgo_railway_rebuilt/
├── bus_booking/          # Django project config
│   ├── settings.py       # All settings (reads from env vars)
│   ├── urls.py
│   └── wsgi.py
├── main/                 # Main app
│   ├── models.py         # City, Route, BusTrip models
│   ├── views.py
│   ├── templates/
│   └── management/commands/load_sample_data.py
├── us_bus_routes.csv     # 98 accurate US bus routes
├── requirements.txt
├── runtime.txt           # Python 3.13.3
├── railway.json          # Railway deployment config
├── Procfile              # Gunicorn start command
├── .env.example          # Environment variable template
└── .gitignore
```

---

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | Yes | Django secret key — generate a fresh one |
| `DEBUG` | No | `False` in production, `True` for local dev |
| `ALLOWED_HOSTS` | No | Comma-separated hostnames, defaults to `*` |
| `DATABASE_URL` | Auto | PostgreSQL URL — Railway injects this automatically |
| `CUSTOM_DOMAIN` | No | Your custom domain, e.g. `https://busgo.com` |
| `DJANGO_LOG_LEVEL` | No | Log verbosity: DEBUG/INFO/WARNING (default: INFO) |

---

## Tech stack

- **Backend:** Django 5.1, Python 3.13
- **Database:** PostgreSQL (Railway) / SQLite (local)
- **Server:** Gunicorn + WhiteNoise
- **Deployment:** Railway (Nixpacks)
