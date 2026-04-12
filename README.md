# SCPD — Sin City Police Department API

A Django REST Framework backend for the Sin City Police Department (SCPD) surveillance system with dual role-based access control. Manage criminals, police officers, incidents, and warrants with restricted views for Police users and full access for Mafia members. Features JWT authentication, AI-generated incidents, map visualization, analytics dashboards, and a privilege escalation endpoint.

---

## 🎯 Key Features

- **Role-Based Access Control**: Two user tiers (Police & Mafia) with different data visibility
- **JWT Authentication**: Secure token-based authentication with refresh token support
- **AI-Generated Incidents**: Automatically generate realistic incidents across Las Vegas locations
- **Map Data Endpoint**: Get incident data with GPS coordinates for map visualization
- **Analytics Dashboard**: Query incidents by type, severity, and timeline (last 7 days)
- **Privilege Escalation**: Secret breach endpoint to grant Mafia access (`CORLEONE_2026` code)
- **Warrant Management**: Track arrest warrants and burn orders with urgency levels
- **Dynamic Filtering**: Automatically filter sensitive data based on user role
- **CORS Support**: Pre-configured for local frontend development (React, Vite, Next.js)

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
SCPD-Backend/
├── README.md                  # Project documentation
├── manage.py                  # Django management script
├── SCPD/                      # Django project configuration
│   ├── __init__.py
│   ├── settings.py            # Project settings, database, apps config
│   ├── urls.py                # Main URL routing
│   ├── asgi.py                # ASGI configuration
│   └── wsgi.py                # WSGI configuration
└── Backend/                   # Main Django app
    ├── __init__.py
    ├── models.py              # Criminal, Police, Incidents, Warrants models
    ├── views.py               # ViewSets and API endpoints
    ├── serializers.py         # DRF serializers
    ├── urls.py                # App URL routing
    ├── admin.py               # Django admin configuration
    ├── apps.py                # App configuration
    ├── scheduler.py           # Scheduled tasks
    ├── tests.py               # Test cases
    └── migrations/            # Database migrations
        ├── __init__.py
        ├── 0001_initial.py
        ├── 0002_remove_incidents_inc_id_incidents_ai_generated_and_more.py
        └── 0003_warrants.py
```

## Models Overview

### 1. **Criminal**

Tracks organized crime members with intelligence data.

- `criminal_id`: Unique identifier
- `incidents`: Associated criminal incidents
- `last_seen`: Last known location/time
- `loyalty_name`: Criminal organization name
- `loyalty_level`: Rank within organization (Mafia-only field)
- `unmonitored_lanes`: Escape routes (Mafia-only field)
- `casinos`: Casino operations

### 2. **Police**

Records police officer information and assignments.

- `police_id`: Unique officer identifier
- `name`: Officer name
- `area`: Assigned patrol area
- `dob`: Date of birth
- `salary`: Officer salary

### 3. **Incidents**

Tracks crime incidents across Las Vegas. Supports AI generation and filtering based on access level.

- `title`: Incident description
- `Location`: Physical location
- `Time`: Incident timestamp
- `latitude`, `longitude`: Precise coordinates for map visualization
- `severity`: Severity level (1-10 scale)
- `incident_type`: Category (robbery, assault, fraud, murder, smuggling)
- `clandestine`: Classified operational incident (Mafia-only view)
- `ai_generated`: Indicates if auto-generated
- `description`: Detailed incident notes

### 4. **Warrants**

Manages arrest warrants and burn orders.

- `target_id`: Target criminal/suspect ID
- `urgency`: Priority level (0-100 scale)
- `justification`: Legal justification for warrant
- `type_warrant`: Type - WARRANT or BURN ORDER
- `timestamp`: Creation timestamp

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

## 🚀 Quick Start

### 1. Create test users

```bash
# Access Django shell
python3 manage.py shell

# Create a police officer user
from django.contrib.auth.models import User, Group
police_user = User.objects.create_user('officer1', 'officer@pd.com', 'pass123')

# Create a mafia user
mafia_user = User.objects.create_user('capo1', 'capo@mob.com', 'pass123')

# Assign mafia_user to Mafia group
mafia_group, _ = Group.objects.get_or_create(name='Mafia')
mafia_user.groups.add(mafia_group)
mafia_user.save()

exit()
```

### 2. Generate test data

```bash
# Generate 10 incidents
curl -X POST http://127.0.0.1:8000/api/v1/incidents/generate/ \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"count": 10}'
```

### 3. Test the API

**Login as police officer:**

```bash
curl -X POST http://127.0.0.1:8000/api/v1/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "officer1", "password": "pass123"}'
```

**Get incidents (limited view):**

```bash
curl http://127.0.0.1:8000/api/v1/incidents/ \
  -H "Authorization: Bearer <POLICE_TOKEN>"
# Only non-clandestine incidents visible
```

**Login as mafia member and escalate:**

```bash
curl -X POST http://127.0.0.1:8000/api/v1/breachSecurity/ \
  -H "Authorization: Bearer <MAFIA_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"code": "CORLEONE_2026"}'
```

**After breach, get all incidents (including clandestine):**

```bash
curl http://127.0.0.1:8000/api/v1/incidents/ \
  -H "Authorization: Bearer <MAFIA_TOKEN>"
```

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

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/token/` | Login — returns access + refresh JWT tokens | No |
| POST | `/token/refresh/` | Refresh expired access token | No |

### Criminals

| Method | Endpoint | Description | Auth Required | Admin Only |
|--------|----------|-------------|---------------|-----------|
| GET | `/criminals/` | List all criminals (Police see limited fields, Mafia see all) | Yes | No |
| GET | `/criminals/{id}/` | Retrieve single criminal | Yes | No |

**Access Control**: Mafia users see `loyalty_name`, `loyalty_level`, `unmonitored_lanes`. Police users see only basic info.

### Police Officers

| Method | Endpoint | Description | Auth Required | Admin Only |
|--------|----------|-------------|---------------|-----------|
| GET | `/police/` | List all police officers | Yes | No |
| GET | `/police/{id}/` | Retrieve single officer | Yes | No |
| POST | `/police/` | Create new police officer | Yes | Yes |

### Incidents

| Method | Endpoint | Description | Auth Required | Admin Only |
|--------|----------|-------------|---------------|-----------|
| GET | `/incidents/` | List incidents (Mafia see all, Police see only non-clandestine) | Yes | No |
| GET | `/incidents/{id}/` | Retrieve single incident | Yes | No |
| GET | `/incidents/map/` | Get map-ready incident data with coordinates | Yes | No |
| GET | `/incidents/graph/` | Get analytics: incidents by type, severity, day (last 7 days) | Yes | No |
| POST | `/incidents/generate/` | Generate random Las Vegas incidents (5 default) | Yes | Yes |

**Request body for generate**: `{"count": 10}` (optional)

**Access Control**: Clandestine incidents only visible to Mafia users.

### Warrants

| Method | Endpoint | Description | Auth Required | Admin Only |
|--------|----------|-------------|---------------|-----------|
| GET | `/warrants/` | List all warrants (sorted by latest first) | Yes | No |
| GET | `/warrants/{id}/` | Retrieve single warrant | Yes | No |
| POST | `/warrants/` | Create new warrant | Yes | Yes |
| PATCH | `/warrants/{id}/` | Update warrant | Yes | Yes |
| DELETE | `/warrants/{id}/` | Delete warrant | Yes | Yes |

### Privilege Escalation

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/breach/` | Escalate privileges to Mafia access | Yes |

**Request body**: `{"code": "CORLEONE_2026"}`

**Response (on success)**: User is added to Mafia group with elevated access to classified data.

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

### Warrants

| Field | Type | Description |
|-------|------|-------------|
| target_id | CharField | Target criminal/suspect identifier |
| urgency | IntegerField | Priority level 0-100 |
| justification | TextField | Legal justification for warrant |
| type_warrant | CharField | WARRANT or BURN ORDER |
| timestamp | DateTimeField | Auto-generated creation time |

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

# Create superuser
python3 manage.py createsuperuser

# Run tests
python3 manage.py test
```

---

## 🔧 Troubleshooting

### PostgreSQL Connection Error

```
psycopg.OperationalError: connection failed
```

**Solution:** Ensure PostgreSQL is running (`sudo systemctl start postgresql`) and database credentials in `.env` are correct.

### Migration Conflicts

```
django.db.migrations.exceptions.InconsistentMigrationHistory
```

**Solution:** Run `python3 manage.py migrate --fake` to mark migrations as applied, or reset migrations folder.

### CORS Error in Frontend

```
Access to XMLHttpRequest blocked by CORS policy
```

**Solution:** Add your frontend URL to `CORS_ALLOWED_ORIGINS` in `settings.py`, e.g., `http://localhost:3000`.

### Token Expired (401 Unauthorized)

**Solution:** Use the refresh endpoint to get a new access token:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<refresh_token>"}'
```

### Superuser Cannot Create Resources

**Solution:** Ensure the user has admin privileges. Grant via Django shell:

```python
from django.contrib.auth.models import User
user = User.objects.get(username='your_username')
user.is_staff = True
user.is_superuser = True
user.save()
```

---

## 📝 API Usage Examples

### List Criminals (with role-based filtering)

**Police user sees:**

```json
[
  {
    "criminal_id": "crim_001",
    "incidents": "5 robbery cases",
    "last_seen": "2026-04-10T14:30:00Z",
    "casinos": "Bellagio, MGM Grand"
  }
]
```

**Mafia user sees:**

```json
[
  {
    "criminal_id": "crim_001",
    "incidents": "5 robbery cases",
    "last_seen": "2026-04-10T14:30:00Z",
    "loyalty_name": "Corleone Family",
    "loyalty_level": 8,
    "unmonitored_lanes": ["Route 66", "Fremont Back Alley"],
    "casinos": "Bellagio, MGM Grand"
  }
]
```

### Create a Warrant

```bash
curl -X POST http://127.0.0.1:8000/api/v1/warrants/ \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "target_id": "crim_001",
    "urgency": 85,
    "justification": "Suspected in 5 armed robberies",
    "type_warrant": "WARRANT"
  }'
```

### Get Incident Analytics

```bash
curl http://127.0.0.1:8000/api/v1/incidents/graph/ \
  -H "Authorization: Bearer <TOKEN>"
```

Response:

```json
{
  "by_type": [
    {"incident_type": "robbery", "count": 15},
    {"incident_type": "assault", "count": 12},
    {"incident_type": "fraud", "count": 8}
  ],
  "by_severity": [
    {"severity": 1, "count": 5},
    {"severity": 5, "count": 10},
    {"severity": 9, "count": 3}
  ],
  "by_day": [
    {"day": "2026-04-04", "count": 3},
    {"day": "2026-04-11", "count": 28}
  ],
  "total": 35,
  "ai_generated": 32
}
```

---

## 🔐 Security Notes

- **Never commit `.env` file** — add it to `.gitignore`
- **Breach code should be changed** in production — use environment variable
- **Use strong passwords** for database and superuser
- **HTTPS required** for production — use Let's Encrypt with Gunicorn + Nginx
- **Rate limiting recommended** — add `djangorestframework-ratelimit` package
- **Audit logging** — consider adding activity logs for sensitive operations

---

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework Docs](https://www.django-rest-framework.org/)
- [SimpleJWT Documentation](https://django-rest-framework-simplejwt.readthedocs.io/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Las Vegas Coordinates Reference](https://en.wikipedia.org/wiki/Las_Vegas)
