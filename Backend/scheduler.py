import random
from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone


def rotate_incidents():
    # Import inside function to avoid AppRegistryNotReady errors
    from .models import Incidents
    from .views import (
        LV_LOCATIONS,
        INCIDENT_TYPES,
        LV_LAT_MIN,
        LV_LAT_MAX,
        LV_LNG_MIN,
        LV_LNG_MAX,
    )

    # 1. DELETE one random AI-generated incident
    # We only target ai_generated=True so we don't accidentally delete your fixed test data!
    incident_to_delete = (
        Incidents.objects.filter(ai_generated=True).order_by("?").first()
    )
    if incident_to_delete:
        incident_to_delete.delete()
        print(f"Deleted incident: {incident_to_delete.title}")

    # 2. INSERT one new random incident
    loc = random.choice(LV_LOCATIONS)
    lat = max(LV_LAT_MIN, min(LV_LAT_MAX, loc[1] + random.uniform(-0.008, 0.008)))
    lng = max(LV_LNG_MIN, min(LV_LNG_MAX, loc[2] + random.uniform(-0.008, 0.008)))
    incident_type = random.choice(INCIDENT_TYPES)

    new_incident = Incidents.objects.create(
        title=f"{incident_type.title()} at {loc[0]}",
        Location=loc[0],
        Time=timezone.now(),
        latitude=lat,
        longitude=lng,
        severity=random.randint(1, 10),
        incident_type=incident_type,
        clandestine=random.choice([True, False]),
        description="Auto-generated rotating incident",
        ai_generated=True,
    )
    print(f"Added incident: {new_incident.title}")


def start_scheduler():
    scheduler = BackgroundScheduler()
    # Runs every 1 minute, plus a random delay up to 60 seconds (total 1 to 2 minutes)
    scheduler.add_job(rotate_incidents, "interval", minutes=1, jitter=60)
    scheduler.start()
