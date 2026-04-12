from django.db import models
from django.contrib.auth.models import User
from django.db.models import JSONField


class Criminal(models.Model):
    objects = models.Manager()
    syndicate = models.Manager()

    police_name = models.CharField(max_length=255, default='Unknown')
    mafia_name = models.CharField(max_length=255, default='Unknown')
    police_status = models.CharField(max_length=50, default='ACTIVE')
    mafia_status = models.CharField(max_length=50, default='ONLINE')
    police_threat = models.CharField(max_length=50, default='LOW')
    mafia_threat = models.CharField(max_length=50, default='LOW')
    police_notes = models.TextField(blank=True, default='')
    mafia_notes = models.TextField(blank=True, default='')


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

class Warrants(models.Model):
    TYPE_CHOICES = (('WARRANT', 'Warrant'), ('BURN','Burn Order'),) 
    target_id = models.CharField(max_length=300)
    urgency = models.IntegerField(default = 50)
    justification = models.TextField(blank = True , null = True)
    type_warrant = models.CharField(max_length=20, choices=TYPE_CHOICES,default='WARRANT')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type_warrant} - Target : {self.target_id} (Urgency: {self.urgency})"