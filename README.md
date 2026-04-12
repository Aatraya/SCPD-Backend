# SCPD — Sin City Police Department API

A Django REST Framework backend with role-based access control for the LVPD surveillance system. Features two access tiers: **Police** (restricted view) and **Mafia** (full access including classified data). Includes dynamic AI-generated incidents with map and graph data endpoints.

---

## Tech Stack

- Python 3.13
- Django 6.0.3
- Django REST Framework
- PostgreSQL 17
- SimpleJWT (Authentication)
- Whitenoise (Static files)
- psycopg[binary,pool] (PostgreSQL driver)

---

## Project Structure

```
SCPD/
├── SCPD/               # Project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── Backend/            # Main app
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── urls.py
│   ├── admin.py
│   └── apps.py
└── manage.py
```

---

## Installation & Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd SCPD
```

### 2. Create and activate virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install django djangorestframework django-cors-headers
pip install "psycopg[binary,pool]"
pip install whitenoise
pip install djangorestframework-simplejwt
pip install gunicorn  # for production
```

### 4. Install and setup PostgreSQL

```bash
# Install PostgreSQL (run in regular terminal, not venv)
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 5. Create database and user

```bash
sudo -u postgres psql
```

Inside psql:

```sql
CREATE DATABASE sincity_db;
CREATE USER aatraya WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE sincity_db TO aatraya;
GRANT ALL ON SCHEMA public TO aatraya;
ALTER DATABASE sincity_db OWNER TO aatraya;
\q
```

### 6. Configure environment variables

Create a `.env` file in the root directory (never commit this):

```
SECRET_KEY=your-random-secret-key
DB_NAME=sincity_db
DB_USER=aatraya
DB_PASSWORD=your_secure_password
DB_HOST=127.0.0.1
DB_PORT=5432
BREACH_CODE=CORLEONE_2026
```

### 7. Run migrations

```bash
source .venv/bin/activate
python3 manage.py makemigrations
python3 manage.py migrate
```

### 8. Create superuser

```bash
python3 manage.py createsuperuser
```

### 9. Start the server

```bash
python3 manage.py runserver
```

Server runs at: `http://127.0.0.1:8000`

---

## Settings Configuration

### settings.py key configurations

```python
INSTALLED_APPS = [
    ...
    'rest_framework',
    'corsheaders',
    'Backend',
]

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    ...
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'sincity_db',
        'USER': 'aatraya',
        'PASSWORD': 'your_secure_password',
        'HOST': '127.0.0.1',
        'PORT': '5432',
        'OPTIONS': {
            'pool': True,
        },
    }
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",   # React default
    "http://localhost:5173",   # Vite default
    # Add your frontend production URL here when deploying
]

STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

---

## API Endpoints

Base URL: `http://127.0.0.1:8000/api/v1/`

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/token/` | Login — returns access + refresh tokens | No |
| POST | `/api/v1/token/refresh/` | Refresh expired access token | No |
| GET | `/api/v1/criminals/` | List all criminals | Yes |
| GET | `/api/v1/criminals/{id}/` | Get single criminal | Yes |
| GET | `/api/v1/police/` | List all police officers | Yes |
| GET | `/api/v1/police/{id}/` | Get single officer | Yes |
| POST | `/api/v1/police/` | Add police officer | Admin only |
| GET | `/api/v1/incidents/` | List all incidents | Yes |
| GET | `/api/v1/incidents/{id}/` | Get single incident | Yes |
| GET | `/api/v1/incidents/map/` | Map-ready data with lat/lng | Yes |
| GET | `/api/v1/incidents/graph/` | Graph stats by type, severity, day | Yes |
| POST | `/api/v1/incidents/generate/` | Generate random LV incidents | Admin only |
| POST | `/api/v1/breach/` | Escalate to Mafia access | Yes |

---

## Authentication

This API uses JWT (JSON Web Tokens). Access token expires in **5 minutes**. Refresh token expires in **1 day**.

### Login

```bash
curl -X POST http://127.0.0.1:8000/api/v1/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "aatraya", "password": "yourpassword"}'
```

Response:

```json
{
    "access": "eyJ0eXAiOiJKV1...",
    "refresh": "eyJ0eXAiOiJKV1..."
}
```

### Using the token

```bash
curl http://127.0.0.1:8000/api/v1/criminals/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1..."
```

### Refresh token

```bash
curl -X POST http://127.0.0.1:8000/api/v1/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "eyJ0eXAiOiJKV1..."}'
```

---

## Role-Based Access Control

### Police / Normal Users
- Can view criminals but **cannot see**: `loyalty_name`, `loyalty_level`, `unmonitored_lanes`
- Cannot see incidents marked as `clandestine: true`

### Mafia Users
- Can see **all** criminal fields including classified data
- Can see **all** incidents including clandestine ones

### System Breach — Escalate to Mafia

```bash
curl -X POST http://127.0.0.1:8000/api/v1/breach/ \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"code": "CORLEONE_2026"}'
```

Success response:

```json
{
    "status": "infiltrated",
    "message": "LVPD Firewall Bypassed. Welcome, Capo.",
    "access_level": "Elevated"
}
```

---

## Data Models

### Criminal

| Field | Type | Description |
|-------|------|-------------|
| criminal_id | CharField | Unique criminal identifier |
| incidents | TextField | Related incident descriptions |
| last_seen | DateTimeField | Last known sighting |
| loyalty_name | CharField | Mafia syndicate name (Mafia only) |
| loyalty_level | IntegerField | Loyalty score (Mafia only) |
| unmonitored_lanes | JSONField | Secret escape routes (Mafia only) |
| casinos | TextField | Associated casino locations |

Example `unmonitored_lanes` JSON:
```json
["Route 66 - Downtown Bypass", "Fremont Street Back Alley", "Industrial Zone Lane 4"]
```

### Police

| Field | Type | Description |
|-------|------|-------------|
| police_id | CharField | Unique officer ID |
| name | CharField | Officer name |
| area | CharField | Patrol area |
| dob | DateField | Date of birth |
| salary | DecimalField | Officer salary |

### Incidents

| Field | Type | Description |
|-------|------|-------------|
| title | CharField | Incident title |
| Location | TextField | Location description |
| Time | DateTimeField | Time of incident |
| latitude | DecimalField | GPS latitude |
| longitude | DecimalField | GPS longitude |
| clandestine | BooleanField | Hidden from police if true |
| severity | IntegerField | Severity score 1-10 |
| incident_type | CharField | robbery, assault, fraud, murder, smuggling |
| ai_generated | BooleanField | True if auto-generated |
| description | TextField | Incident description |

---

## Incident Generation

Incidents are auto-generated using Python's `random` module — no external API needed. Pins are placed across real Las Vegas landmarks with a slight random offset to spread them naturally across the city.

### Las Vegas Bounding Box
```
Latitude:  35.95 to 36.40
Longitude: -115.40 to -114.96
```

### Generate incidents

```bash
curl -X POST http://127.0.0.1:8000/api/v1/incidents/generate/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"count": 10}'
```

### Map data response format

```json
[
  {
    "id": 2,
    "title": "Smuggling at Bellagio Area",
    "location": "Bellagio Area",
    "latitude": 36.119726,
    "longitude": -115.18204,
    "severity": 4,
    "incident_type": "smuggling",
    "time": "2026-04-11T15:01:18Z",
    "clandestine": false,
    "ai_generated": true
  }
]
```

### Graph data response format

```json
{
  "by_type": [{"incident_type": "smuggling", "count": 7}],
  "by_severity": [{"severity": 1, "count": 3}],
  "by_day": [{"day": "2026-04-11", "count": 30}],
  "total": 31,
  "ai_generated": 30
}
```

---

## Admin Panel

URL: `http://127.0.0.1:8000/admin/`

Login with superuser credentials. From here you can:
- Add/edit/delete Criminals, Police, Incidents
- Manage Users and Groups
- Assign users to the **Mafia** group for elevated access

---

## Frontend Integration (Next.js)

### Install packages

```bash
npm install react-leaflet leaflet recharts axios
```

### 1. Login

```javascript
const res = await axios.post('http://127.0.0.1:8000/api/v1/token/', {
  username, password
})
localStorage.setItem('access', res.data.access)
localStorage.setItem('refresh', res.data.refresh)
```

### 2. Authenticated requests header

```javascript
const headers = { Authorization: `Bearer ${localStorage.getItem('access')}` }
```

### 3. Map — fetch and render pins

```javascript
const res = await axios.get('http://127.0.0.1:8000/api/v1/incidents/map/', { headers })

// Each incident → drop a pin at latitude, longitude
// Use severity for pin color:
const pinColor = (severity) => {
  if (severity >= 7) return 'red'
  if (severity >= 4) return 'orange'
  return 'green'
}

// Default Las Vegas map center
center={[36.1699, -115.1398]}
zoom={12}

// Each incident has:
// latitude, longitude  → pin position
// severity (1-10)      → pin color
// incident_type        → pin label/icon
// title                → popup text
// clandestine          → only visible to Mafia users
```

### 4. Graph — fetch and render charts

```javascript
const res = await axios.get('http://127.0.0.1:8000/api/v1/incidents/graph/', { headers })

// res.data.by_type      → Pie chart or Bar chart
// res.data.by_severity  → Bar chart
// res.data.by_day       → Line chart / Timeline
// res.data.total        → Stat card
// res.data.ai_generated → Stat card
```

### 5. Generate incidents button (admin only)

```javascript
await axios.post('http://127.0.0.1:8000/api/v1/incidents/generate/',
  { count: 10 },
  { headers }
)
// Then refetch map and graph data
```

### 6. Mafia breach button

```javascript
await axios.post('http://127.0.0.1:8000/api/v1/breach/',
  { code: 'CORLEONE_2026' },
  { headers }
)
// After this criminals endpoint shows loyalty_name, loyalty_level, unmonitored_lanes
// Incidents endpoint shows clandestine incidents too
```

### 7. Token refresh (access token expires in 5 mins)

```javascript
const res = await axios.post('http://127.0.0.1:8000/api/v1/token/refresh/', {
  refresh: localStorage.getItem('refresh')
})
localStorage.setItem('access', res.data.access)
// Call this automatically when any request returns 401 Unauthorized
```

### CORS
Already configured for `localhost:3000` and `localhost:5173` — no browser errors during development.

---

## Production Deployment

```bash
# Collect static files
python3 manage.py collectstatic

# Run with gunicorn
gunicorn SCPD.wsgi:application --bind 0.0.0.0:8000
```

**Before going live checklist:**
- Set `DEBUG = False` in settings.py
- Set a strong random `SECRET_KEY`
- Add your domain to `ALLOWED_HOSTS`
- Add frontend production URL to `CORS_ALLOWED_ORIGINS`
- Move all secrets to environment variables
- Move `BREACH_CODE` to environment variable

---

## Common Commands

```bash
# Start PostgreSQL (regular terminal)
sudo systemctl start postgresql

# Activate venv
source .venv/bin/activate

# Run server
python3 manage.py runserver

# Make migrations after model changes
python3 manage.py makemigrations
python3 manage.py migrate

# Reset a user password
python3 manage.py changepassword <username>

# Generate incidents via curl
curl -X POST http://127.0.0.1:8000/api/v1/incidents/generate/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"count": 10}'
```
