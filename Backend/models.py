from django.db import models
from django.contrib.auth.models import User
from django.db.models import JSONField


class Criminal(models.Model):
    objects = models.Manager()    # Standard manager
    syndicate = models.Manager()  # The "Hacked" manager

    criminal_id = models.CharField(max_length=255)
    incidents = models.TextField()
    last_seen = models.DateTimeField()
    loyalty_name = models.CharField(max_length=255)
    loyalty_level = models.IntegerField()
    unmonitored_lanes = models.JSONField()
    casinos = models.TextField()


class Police(models.Model):
    police_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    dob = models.DateField()
    salary = models.DecimalField(max_digits=12, decimal_places=2)


class Incidents(models.Model):
    # Removed Inc_id — Django auto-generates a proper primary key
    title = models.CharField(max_length=500)
    Location = models.TextField()
    Time = models.DateTimeField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    clandestine = models.BooleanField(default=False)

    # New fields
    severity = models.IntegerField(default=1)                    # 1-10 scale for graph
    incident_type = models.CharField(max_length=100, default='unknown')  # robbery, murder etc
    ai_generated = models.BooleanField(default=False)            # track AI vs manually added
    description = models.TextField(blank=True, default='')       # incident description