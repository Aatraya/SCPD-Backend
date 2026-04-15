# SCPD — Sin City Police Department · Backend

[![Django](https://img.shields.io/badge/Django-6.0.4-green?style=for-the-badge&logo=django)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.17-red?style=for-the-badge)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-blue?style=for-the-badge&logo=postgresql)](https://www.postgresql.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

Django REST Framework backend for the SCPD v2 dual-theme surveillance dashboard. Manages criminals, incidents, warrants, and police officers — with two-tier role-based access control that serves fundamentally different data views to **Police** users and **Mafia** users.

---

## Key Features

- **Two-Tier RBAC**: Police and Mafia groups receive different querysets and serialized fields from the same endpoints.
- **JWT Authentication**: Short-lived access tokens with refresh support via `djangorestframework-simplejwt`.
- **Privilege Escalation Endpoint**: Secret bypass code promotes a user to the Mafia group at runtime.
- **AI-Generated Incidents**: Randomly generates realistic incidents across real Las Vegas landmarks.
- **Live Incident Rotation**: APScheduler swaps one incident every 1–2 minutes, keeping the map dynamic.
- **Map & Graph Data Endpoints**: Pre-shaped responses for frontend map pins and analytics charts.
- **Render-Ready Deployment**: `build.sh`, WhiteNoise static files, `dj-database-url`, CORS configured.

---

## Tech Stack

| Component | Technology |
| - | - |
| Framework | Django 6.0.4 |
| API Layer | Django REST Framework 3.17 |
| Auth | SimpleJWT 5.5.1 |
| Database | PostgreSQL 17 |
| ORM Driver | psycopg 3 (binary + pool) |
| Scheduler | APScheduler 3.11 |
| Static Files | WhiteNoise 6.12 |
| CORS | django-cors-headers 4.9 |
| Deployment | Render |

---

## Project Structure

```plaintext
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

### Prerequisites

- Python 3.13
- PostgreSQL 17 running locally

### 1. Clone and create virtual environment

```bash
git clone https://github.com/your-org/scpd-backend.git
cd scpd-backend
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file (never commit this):

```env
SECRET_KEY=your-random-50-char-secret-key
DATABASE_URL=postgres://youruser:yourpassword@127.0.0.1:5432/sincity_db
```

### 4. Set up PostgreSQL

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE sincity_db;
CREATE USER youruser WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE sincity_db TO youruser;
ALTER DATABASE sincity_db OWNER TO youruser;
\q
```

### 6. Configure environment variables

Create a `.env` file in the root directory (never commit this):

```plaintext
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
python manage.py migrate
```

Migration `0005` automatically creates three users:

| Username | Password | Role |
| - | - | - |
| `officer_vance` | `securepassword123` | Police (standard user) |
| `tony_pro` | `mafiapassword456` | Mafia (elevated group) |
| `admin_aatraya` | `adminpassword789` | Superuser |

> ⚠️ Change all default passwords before any public deployment.

### 6. Start the server

```bash
python manage.py runserver   # http://127.0.0.1:8000
```

---

## AI Incident Generator

Incidents are generated using Python's `random` module — no external API required. Pins are placed around 15 real Las Vegas landmarks with a small random offset to spread them naturally.

**Coverage area:**

```plaintext
Latitude:  35.95 – 36.40
Longitude: -115.40 – -114.96
```

**Incident types:** `robbery`, `assault`, `fraud`, `murder`, `smuggling`

```bash
# Generate 10 incidents (requires admin token)
curl -X POST http://127.0.0.1:8000/api/v1/incidents/generate/ \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"count": 10}'
```

### Live Rotation (APScheduler)

`BackgroundScheduler` runs automatically when the server starts (controlled by the `RUN_MAIN` or `RENDER` env var in `apps.py`). Every 1–2 minutes it:

1. Deletes one random incident.
2. Creates one new random incident at a different Las Vegas location.

This keeps the frontend map alive without any manual intervention.

---

## API Endpoints

Base URL: `http://127.0.0.1:8000/api/v1/`

### Authentication

| Method | Endpoint | Description | Auth Required |
| - | - | - | - |
| POST | `/token/` | Login — returns access + refresh JWT tokens | No |
| POST | `/token/refresh/` | Refresh expired access token | No |

### Criminals

| Method | Endpoint | Description | Auth Required | Admin Only |
| - | - | - | - | - |
| GET | `/criminals/` | List all criminals (Police see limited fields, Mafia see all) | Yes | No |
| GET | `/criminals/{id}/` | Retrieve single criminal | Yes | No |

**Access Control**: Mafia users see `loyalty_name`, `loyalty_level`, `unmonitored_lanes`. Police users see only basic info.

### Police Officers

| Method | Endpoint | Description | Auth Required | Admin Only |
| - | - | - | - | - |
| GET | `/police/` | List all police officers | Yes | No |
| GET | `/police/{id}/` | Retrieve single officer | Yes | No |
| POST | `/police/` | Create new police officer | Yes | Yes |

### Incidents

| Method | Endpoint | Description | Auth Required | Admin Only |
| - | - | - | - | - |
| GET | `/incidents/` | List incidents (Mafia see all, Police see only non-clandestine) | Yes | No |
| GET | `/incidents/{id}/` | Retrieve single incident | Yes | No |
| GET | `/incidents/map/` | Get map-ready incident data with coordinates | Yes | No |
| GET | `/incidents/graph/` | Get analytics: incidents by type, severity, day (last 7 days) | Yes | No |
| POST | `/incidents/generate/` | Generate random Las Vegas incidents (5 default) | Yes | Yes |

**Request body for generate**: `{"count": 10}` (optional)

**Access Control**: Clandestine incidents only visible to Mafia users.

### Warrants API

| Method | Endpoint | Description | Auth Required | Admin Only |
| - | - | - | - | - |
| GET | `/warrants/` | List all warrants (sorted by latest first) | Yes | No |
| GET | `/warrants/{id}/` | Retrieve single warrant | Yes | No |
| POST | `/warrants/` | Create new warrant | Yes | Yes |
| PATCH | `/warrants/{id}/` | Update warrant | Yes | Yes |
| DELETE | `/warrants/{id}/` | Delete warrant | Yes | Yes |

### Privilege Escalation

| Method | Endpoint | Description | Auth Required |
| - | - | - | - |
| POST | `/breach/` | Escalate privileges to Mafia access | Yes |

**Request body**: `{"code": "CORLEONE_2026"}`

**Response (on success)**: User is added to Mafia group with elevated access to classified data.

---

## JWT Authentication

This API uses JWT (JSON Web Tokens). Access token expires in **5 minutes**. Refresh token expires in **1 day**.

### Login

```bash
# Get a police token
curl -X POST http://127.0.0.1:8000/api/v1/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "officer_vance", "password": "securepassword123"}'

# Get a mafia token
curl -X POST http://127.0.0.1:8000/api/v1/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "tony_pro", "password": "mafiapassword456"}'

# Escalate any user to Mafia
curl -X POST http://127.0.0.1:8000/api/v1/breach/ \
  -H "Authorization: Bearer <token>" \
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
| - | - | - |
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
| - | - | - |
| police_id | CharField | Unique officer ID |
| name | CharField | Officer name |
| area | CharField | Patrol area |
| dob | DateField | Date of birth |
| salary | DecimalField | Officer salary |

### Incidents Model

| Field | Type | Description |
| - | - | - |
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
| - | - | - |
| target_id | CharField | Target criminal/suspect identifier |
| urgency | IntegerField | Priority level 0-100 |
| justification | TextField | Legal justification for warrant |
| type_warrant | CharField | WARRANT or BURN ORDER |
| timestamp | DateTimeField | Auto-generated creation time |

---

## Incident Generation

Incidents are auto-generated using Python's `random` module — no external API needed. Pins are placed across real Las Vegas landmarks with a slight random offset to spread them naturally across the city.

### Las Vegas Bounding Box

```plaintext
Latitude:  35.95 to 36.40
Longitude: -115.40 to -114.96
```

### Generate incidents

```bash
python manage.py migrate --fake-initial
```

---

## Admin Panel

URL: `http://127.0.0.1:8000/admin/`

Login with superuser credentials to manage all models, assign users to the `Mafia` group manually, and inspect the full dataset.

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

```plaintext
psycopg.OperationalError: connection failed
```

**Solution:** Ensure PostgreSQL is running (`sudo systemctl start postgresql`) and database credentials in `.env` are correct.

### Migration Conflicts

```plaintext
django.db.migrations.exceptions.InconsistentMigrationHistory
```

**Solution:** Run `python3 manage.py migrate --fake` to mark migrations as applied, or reset migrations folder.

### CORS Error in Frontend

```plaintext
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

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework Docs](https://www.django-rest-framework.org/)
- [SimpleJWT Documentation](https://django-rest-framework-simplejwt.readthedocs.io/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Las Vegas Coordinates Reference](https://en.wikipedia.org/wiki/Las_Vegas)
