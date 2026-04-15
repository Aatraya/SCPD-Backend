# SCPD — Sin City Police Department · Backend

[![Django](https://img.shields.io/badge/Django-6.0.4-green?style=for-the-badge&logo=django)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.17-red?style=for-the-badge)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-blue?style=for-the-badge&logo=postgresql)](https://www.postgresql.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Live](https://img.shields.io/badge/Live-scpd.live-brightgreen?style=for-the-badge)](https://scpd.live)

Django REST Framework backend for the SCPD v2 dual-theme surveillance dashboard. Manages criminals, incidents, warrants, and police officers — with two-tier role-based access control that serves fundamentally different data views to **Police** users and **Mafia** users.

🌐 **Frontend live at [https://scpd.live](https://scpd.live)**

---

## Key Features

- **Two-Tier RBAC**: Police and Mafia groups receive different querysets and serialized fields from the same endpoints.
- **JWT Authentication**: Access tokens with automatic refresh support via `djangorestframework-simplejwt`.
- **Privilege Escalation Endpoint**: Secret bypass code promotes a user to the Mafia group at runtime.
- **BURN Order Enforcement**: Only Mafia-authenticated users can create BURN orders. On creation, the target Criminal is automatically deleted server-side.
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
    ├── serializers.py         # DRF serializers with role-based field stripping
    ├── urls.py                # App URL routing
    ├── admin.py               # Django admin configuration
    ├── apps.py                # App configuration + scheduler startup
    ├── scheduler.py           # APScheduler background job (incident rotation)
    ├── tests.py               # Test cases
    └── migrations/            # Database migrations
```

---

## Models Overview

### 1. **Criminal**

Tracks suspects with dual-view intelligence data — Police and Mafia see different fields.

| Field | Type | Visible To |
| - | - | - |
| `id` | BigAutoField (PK) | Both |
| `police_name` | CharField | Both |
| `mafia_name` | CharField | Mafia only |
| `police_status` | CharField (`ACTIVE`, `WANTED`, `CUSTODY`) | Both |
| `mafia_status` | CharField (`ONLINE`, `BURNED`, `COMPROMISED`, `KOMPROMAT`) | Mafia only |
| `police_threat` | CharField (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) | Both |
| `mafia_threat` | CharField (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) | Mafia only |
| `police_notes` | TextField | Both |
| `mafia_notes` | TextField | Mafia only |

### 2. **Police**

Records police officer information and assignments.

| Field | Type | Description |
| - | - | - |
| `police_id` | CharField | Unique officer identifier |
| `name` | CharField | Officer name |
| `area` | CharField | Assigned patrol area |
| `dob` | DateField | Date of birth |
| `salary` | DecimalField | Officer salary |

### 3. **Incidents**

Tracks crime incidents across Las Vegas with AI generation and clandestine filtering.

| Field | Type | Description |
| - | - | - |
| `id` | BigAutoField (PK) | Auto-generated |
| `title` | CharField | Incident title |
| `Location` | TextField | Location name |
| `Time` | DateTimeField | Incident timestamp |
| `latitude` | DecimalField | GPS latitude (9 digits, 6 decimal places) |
| `longitude` | DecimalField | GPS longitude |
| `clandestine` | BooleanField | Hidden from Police if `true` |
| `severity` | IntegerField | Severity scale 1–10 |
| `incident_type` | CharField | `robbery`, `assault`, `fraud`, `murder`, `smuggling` |
| `ai_generated` | BooleanField | `true` if auto-generated |
| `description` | TextField | Incident notes |

### 4. **Warrants**

Manages arrest warrants and burn orders with role-enforced creation.

| Field | Type | Description |
| - | - | - |
| `id` | BigAutoField (PK) | Auto-generated |
| `target_id` | CharField | Target Criminal identifier |
| `urgency` | IntegerField | Priority level 0–100 |
| `justification` | TextField | Justification text |
| `type_warrant` | CharField | `WARRANT` or `BURN` |
| `timestamp` | DateTimeField | Auto-set on creation (`auto_now_add`) |

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

Demo users created by seed migrations:

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

## API Endpoints

Base URL: `http://127.0.0.1:8000/api/v1/`  
Production: `https://scpd-backend.onrender.com/api/v1/`

### Authentication

| Method | Endpoint | Description | Auth Required |
| - | - | - | - |
| POST | `/token/` | Login — returns access + refresh JWT tokens | No |
| POST | `/token/refresh/` | Refresh expired access token | No |

### Criminals

| Method | Endpoint | Description | Auth Required | Role Restriction |
| - | - | - | - | - |
| GET | `/criminals/` | List all criminals (Police see limited fields, Mafia see all) | Yes | — |
| GET | `/criminals/{id}/` | Retrieve single criminal | Yes | — |
| POST | `/criminals/` | Create new criminal record | Yes | — |
| PATCH | `/criminals/{id}/` | Update criminal fields | Yes | Admin |
| DELETE | `/criminals/{id}/` | Delete criminal record | Yes | Mafia or Admin |

**Access Control**: `CriminalSerializer.to_representation` strips all `mafia_*` fields for non-Mafia users at serialization time.

### Police Officers

| Method | Endpoint | Description | Auth Required | Role Restriction |
| - | - | - | - | - |
| GET | `/police/` | List all police officers | Yes | — |
| GET | `/police/{id}/` | Retrieve single officer | Yes | — |
| POST | `/police/` | Create new police officer | Yes | Admin |

### Incidents

| Method | Endpoint | Description | Auth Required | Role Restriction |
| - | - | - | - | - |
| GET | `/incidents/` | List incidents (Mafia see all; Police see non-clandestine only) | Yes | — |
| GET | `/incidents/{id}/` | Retrieve single incident | Yes | — |
| GET | `/incidents/map/` | Map-ready data with `float`-cast coordinates | Yes | — |
| GET | `/incidents/graph/` | Analytics: by type, severity, day (last 7 days) | Yes | — |
| POST | `/incidents/generate/` | Generate random Las Vegas incidents | Yes | Admin |

**Access Control**: Clandestine incidents are filtered at the queryset level for Police users — they never leave the database.

### Warrants

| Method | Endpoint | Description | Auth Required | Role Restriction |
| - | - | - | - | - |
| GET | `/warrants/` | List warrants (Police: `WARRANT` only; Mafia: all) | Yes | — |
| GET | `/warrants/{id}/` | Retrieve single warrant | Yes | — |
| POST | `/warrants/` | Create warrant or BURN order | Yes | BURN requires Mafia/Admin |
| PATCH | `/warrants/{id}/` | Update warrant | Yes | Admin |
| DELETE | `/warrants/{id}/` | Delete warrant | Yes | Admin |

**BURN Order Enforcement** (`perform_create`):

1. If `type_warrant == "BURN"` and the user is not Mafia/staff/superuser → `HTTP 403 Forbidden`.
2. On successful BURN order save, the target `Criminal` is automatically deleted from the database.

### Privilege Escalation

| Method | Endpoint | Description | Auth Required |
| - | - | - | - |
| POST | `/breach/` | Escalate privileges to Mafia access | Yes |

**Request body**: `{"code": "<breach_code>"}`

**Response (on success)**:

```json
{
    "status": "infiltrated",
    "message": "LVPD Firewall Bypassed. Welcome, Capo.",
    "access_level": "Elevated"
}
```

---

## JWT Authentication

Access token: **7 days**. Refresh token: **30 days**.

```bash
# Get a police token
curl -X POST http://127.0.0.1:8000/api/v1/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "officer_vance", "password": "securepassword123"}'

# Get a mafia token
curl -X POST http://127.0.0.1:8000/api/v1/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "tony_pro", "password": "mafiapassword456"}'

# Escalate to Mafia
curl -X POST http://127.0.0.1:8000/api/v1/breach/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"code": "<breach_code>"}'
```

---

## AI Incident Generator

Incidents are generated using Python's `random` module — no external API required. Pins are placed around 15 real Las Vegas landmarks with a small random offset.

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

`BackgroundScheduler` runs automatically on server start. Every 1–2 minutes it:

1. Deletes one random incident.
2. Creates one new random incident at a different Las Vegas location.

---

## CORS Configuration

Allowed origins:

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "https://scpd.live",
    "https://www.scpd.live",
    "https://scpd.vercel.app",
]

CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://scpd.*\.vercel\.app$",
]
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

- Set a strong random `SECRET_KEY` via environment variable
- Add your domain to `ALLOWED_HOSTS`
- Move the breach code out of source into an environment variable and read it in `views.py`
- Reduce `ACCESS_TOKEN_LIFETIME` to 5–15 minutes and enable `ROTATE_REFRESH_TOKENS`

---

## Common Commands

```bash
# Start PostgreSQL
sudo systemctl start postgresql

# Activate venv
source .venv/bin/activate

# Run server
python3 manage.py runserver

# Migrations
python3 manage.py makemigrations
python3 manage.py migrate

# Reset a user password
python3 manage.py changepassword <username>

# Create superuser
python3 manage.py createsuperuser

# Run tests
python3 manage.py test
```

---

## Troubleshooting

### PostgreSQL Connection Error

```plaintext
psycopg.OperationalError: connection failed
```

Ensure PostgreSQL is running (`sudo systemctl start postgresql`) and credentials in `.env` match.

### CORS Error in Frontend

```plaintext
Access to XMLHttpRequest blocked by CORS policy
```

Add your frontend URL to `CORS_ALLOWED_ORIGINS` in `settings.py`.

### Token Expired (401 Unauthorized)

```bash
curl -X POST http://127.0.0.1:8000/api/v1/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<refresh_token>"}'
```

### BURN Order Returns 403

The requesting user does not belong to the `Mafia` group. Call the `/breach/` endpoint first with a valid code to elevate privileges.

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

Built with ⚡ for **HackNite 2026** · SinCity Theme · by **The Shadows** (Amogh Gurudatta and Aatraya Mukherjee)
