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
|---|---|
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

```
/
├── manage.py
├── requirements.txt
├── build.sh                         # Render deployment script
├── SCPD/                            # Django project config
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── Backend/                         # Main Django app
    ├── models.py                    # Criminal, Police, Incidents, Warrants
    ├── serializers.py               # Role-aware field filtering
    ├── views.py                     # ViewSets + custom API views
    ├── urls.py                      # App routing
    ├── apps.py                      # AppConfig + scheduler startup
    ├── scheduler.py                 # APScheduler incident rotation
    ├── admin.py
    └── migrations/
```

---

## Data Models

### Criminal
Dual-perspective suspect/target profile. Police see the `police_*` fields; Mafia see all fields.

| Field | Type | Notes |
|---|---|---|
| `police_name` | CharField | Official LVPD designation |
| `mafia_name` | CharField | Syndicate alias |
| `police_status` | CharField | `ACTIVE` / `WANTED` / `CUSTODY` |
| `mafia_status` | CharField | `ONLINE` / `BURNED` / `COMPROMISED` / `KOMPROMAT` |
| `police_threat` | CharField | `LOW` / `MEDIUM` / `HIGH` / `CRITICAL` |
| `mafia_threat` | CharField | `LOW` / `MEDIUM` / `HIGH` / `CRITICAL` |
| `police_notes` | TextField | Intel from police perspective |
| `mafia_notes` | TextField | Intel from Syndicate perspective |

### Incidents
Live crime events across Las Vegas. Clandestine incidents are hidden from police users.

| Field | Type | Notes |
|---|---|---|
| `title` | CharField | Incident description |
| `Location` | TextField | Named area (e.g. "Fremont Street") |
| `Time` | DateTimeField | Incident timestamp |
| `latitude` / `longitude` | DecimalField | GPS coordinates for map pins |
| `severity` | IntegerField | 1–10 scale |
| `incident_type` | CharField | `robbery` / `assault` / `fraud` / `murder` / `smuggling` |
| `clandestine` | BooleanField | `True` → hidden from police users |
| `ai_generated` | BooleanField | Marks scheduler-created incidents |
| `description` | TextField | Extended details |

### Warrants
Arrest warrants (police) and burn orders (mafia).

| Field | Type | Notes |
|---|---|---|
| `target_id` | CharField | References a Criminal record ID |
| `urgency` | IntegerField | 0–100 priority scale |
| `justification` | TextField | Reasoning for the warrant |
| `type_warrant` | CharField | `WARRANT` or `BURN` |
| `timestamp` | DateTimeField | Auto-set on creation |

### Police
Officer roster (read-only for standard users).

| Field | Type |
|---|---|
| `police_id` | CharField (unique) |
| `name` | CharField |
| `area` | CharField |
| `dob` | DateField |
| `salary` | DecimalField |

---

## Role-Based Access Control

```
                    ┌─────────────────────┐
                    │   JWT Login         │
                    └──────────┬──────────┘
                               │
              ┌────────────────┴────────────────┐
              │                                 │
     ┌────────▼────────┐             ┌──────────▼──────────┐
     │  Standard User  │             │    Mafia Group       │
     │  (Police theme) │             │  (Syndicate theme)   │
     └────────┬────────┘             └──────────┬──────────┘
              │                                 │
  Criminals:  police_* fields only   Criminals: all fields
  Incidents:  clandestine=False      Incidents: all records
  Warrants:   type=WARRANT only      Warrants:  all types
```

Access is enforced at two layers:
- **QuerySet level** — `get_queryset()` on each ViewSet returns a filtered queryset based on group membership.
- **Serializer level** — `to_representation()` on `CriminalSerializer` removes Mafia-only fields for non-Mafia users.

### Privilege Escalation

```bash
POST /api/v1/breach/
Authorization: Bearer <token>
{"code": "CORLEONE_2026"}
```

On success, the user is permanently added to the `Mafia` Django group. All subsequent requests serve the elevated data view.

---

## API Endpoints

Base URL: `http://localhost:8000/api/v1/`

### Authentication

| Method | Endpoint | Body | Description |
|---|---|---|---|
| POST | `/token/` | `{username, password}` | Login → returns `access` + `refresh` JWT |
| POST | `/token/refresh/` | `{refresh}` | Returns a new `access` token |

### Criminals

| Method | Endpoint | Auth | Notes |
|---|---|---|---|
| GET | `/criminals/` | ✅ | Police: police fields; Mafia: all fields |
| GET | `/criminals/{id}/` | ✅ | Single record |
| POST | `/criminals/` | ✅ | Create new record |
| PATCH | `/criminals/{id}/` | Admin | Partial update |
| DELETE | `/criminals/{id}/` | ✅ | Any authenticated user |

### Incidents

| Method | Endpoint | Auth | Notes |
|---|---|---|---|
| GET | `/incidents/` | ✅ | Police skip `clandestine=True` records |
| GET | `/incidents/{id}/` | ✅ | Single incident |
| GET | `/incidents/map/` | ✅ | Flat array with lat/lng for map pins |
| GET | `/incidents/graph/` | ✅ | Aggregated: by type, severity, last 7 days |
| POST | `/incidents/generate/` | Admin | Body: `{"count": N}` — generates random incidents |

### Warrants

| Method | Endpoint | Auth | Notes |
|---|---|---|---|
| GET | `/warrants/` | ✅ | Sorted newest first |
| GET | `/warrants/{id}/` | ✅ | Single warrant |
| POST | `/warrants/` | ✅ | Create warrant or burn order |
| PATCH | `/warrants/{id}/` | ✅ | Update |
| DELETE | `/warrants/{id}/` | ✅ | Delete |

### System

| Method | Endpoint | Auth | Body |
|---|---|---|---|
| POST | `/breach/` | ✅ | `{"code": "CORLEONE_2026"}` |

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

### 5. Run migrations

```bash
python manage.py migrate
```

Migration `0005` automatically creates three users:

| Username | Password | Role |
|---|---|---|
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
```
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

## Deployment (Render)

The `build.sh` script handles everything Render needs:

```bash
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py createsuperuser --noinput --username admin --email admin@scpd.com || true
```

**Required environment variables on Render:**

| Variable | Value |
|---|---|
| `SECRET_KEY` | A long random string |
| `DATABASE_URL` | Your Aiven / Render PostgreSQL connection string |
| `RENDER` | `true` (Render sets this automatically) |
| `RENDER_EXTERNAL_HOSTNAME` | Your Render app hostname (set automatically) |

**CORS is pre-configured for:**
- `http://localhost:3000`
- `https://scpd.vercel.app`
- Any `scpd*.vercel.app` preview URL (regex match)

---

## Default Credentials (Quick Start)

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

---

## Troubleshooting

**PostgreSQL connection error:**
Ensure PostgreSQL is running (`sudo systemctl start postgresql`) and `DATABASE_URL` is set correctly.

**401 on all requests after a while:**
Access token expired (7-day lifetime). Use `/token/refresh/` or log in again. The frontend handles this automatically.

**APScheduler not rotating incidents on Render free tier:**
Render free services sleep after inactivity. The scheduler restarts on wake-up. Use a cron-based ping service or upgrade to a paid instance to keep it alive continuously.

**Migrations conflict:**
```bash
python manage.py migrate --fake-initial
```

---

## Admin Panel

URL: `http://127.0.0.1:8000/admin/`

Login with superuser credentials to manage all models, assign users to the `Mafia` group manually, and inspect the full dataset.

---

*Built with ⚡ for HackNite 2026 · SinCity Theme · by The Shadows (Amogh Gurudatta and Aatraya Mukherjee)*
