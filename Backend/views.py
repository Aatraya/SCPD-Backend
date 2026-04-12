from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Criminal, Police , Incidents, Warrants
from .serializers import CriminalSerializer, PoliceOfficerSerializer,IncidentSerializer,WarrantSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import Group
from django.db.models import Count
from datetime import timedelta
import random
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated


class PoliceViewSet(viewsets.ModelViewSet):
    queryset = Police.objects.all()
    serializer_class = PoliceOfficerSerializer

    def get_permissions(self):
        if self.action in ['list','retrieve']: # read all permission
            return [permissions.IsAuthenticated()]

        return [permissions.IsAdminUser()] # deletion only by mafia


class CriminalViewSet(viewsets.ModelViewSet):
    serializer_class = CriminalSerializer

    def get_queryset(self):
        user = self.request.user
        
        # Safely check for authentication BEFORE checking groups to prevent AnonymousUser crash
        if user.is_authenticated and user.groups.filter(name='Mafia').exists():
            return Criminal.syndicate.all()
        
        # Police and everyone else get the restricted database access
        return Criminal.objects.all()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        
        return [permissions.IsAdminUser()]


class IncidentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IncidentSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.groups.filter(name='Mafia').exists():
            return Incidents.objects.all()
        # Non-mafia users only see non-clandestine incidents
        return Incidents.objects.filter(clandestine=False)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]


class SystemBreachView(APIView):
    def post(self, request):
        secret_code = request.data.get("code")
        
        # Hardcoded secret or complex logic
        if secret_code == "CORLEONE_2026":
            # Add user to Mafia group for this session
            mafia_group, _ = Group.objects.get_or_create(name='Mafia')
            request.user.groups.add(mafia_group)
            
            return Response({
                "status": "infiltrated",
                "message": "LVPD Firewall Bypassed. Welcome, Capo."
            })
        
        return Response({"error": "Access Denied"}, status=403)

class SystemBreachView(APIView):
    """
    Endpoint to escalate privileges via a secret bypass code.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        secret_code = request.data.get("code")
        
        # The bypass credential for the SCPD Firewall
        if secret_code == "CORLEONE_2026":
            mafia_group, created = Group.objects.get_or_create(name='Mafia')
            
            # Check if user is already a member to prevent duplicate effort
            if not request.user.groups.filter(name='Mafia').exists():
                request.user.groups.add(mafia_group)
            
            return Response({
                "status": "infiltrated",
                "message": "LVPD Firewall Bypassed. Welcome, Capo.",
                "access_level": "Elevated"
            }, status=status.HTTP_200_OK)
        
        return Response({
            "error": "Access Denied",
            "message": "Invalid credentials. Attempt logged."
        }, status=status.HTTP_403_FORBIDDEN)


LV_LAT_MIN, LV_LAT_MAX = 35.95, 36.40
LV_LNG_MIN, LV_LNG_MAX = -115.40, -114.96

LV_LOCATIONS = [
    # The Strip
    ("Las Vegas Strip North", 36.1716, -115.1391),
    ("Las Vegas Strip South", 36.1147, -115.1728),
    ("MGM Grand Area", 36.1029, -115.1702),
    ("Bellagio Area", 36.1126, -115.1767),
    ("Caesars Palace Area", 36.1162, -115.1745),

    # Downtown
    ("Fremont Street", 36.1699, -115.1420),
    ("Downtown Container Park", 36.1670, -115.1350),

    # Suburbs
    ("Summerlin", 36.1520, -115.3280),
    ("Henderson", 36.0397, -114.9819),
    ("North Las Vegas", 36.2332, -115.1179),
    ("Paradise Road", 36.1250, -115.1450),
    ("East Las Vegas", 36.1500, -115.0800),
    ("Spring Valley", 36.1064, -115.2377),
    ("Chinatown", 36.1350, -115.1980),
    ("Arts District", 36.1600, -115.1550),
]

INCIDENT_TYPES = ["robbery", "assault", "fraud", "murder", "smuggling"]


class AIIncidentGeneratorView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        count = request.data.get("count", 5)
        created = []

        for _ in range(count):
            loc = random.choice(LV_LOCATIONS)

            lat = loc[1] + random.uniform(-0.008, 0.008)
            lng = loc[2] + random.uniform(-0.008, 0.008)

            # Clamp to Las Vegas boundary
            lat = max(LV_LAT_MIN, min(LV_LAT_MAX, lat))
            lng = max(LV_LNG_MIN, min(LV_LNG_MAX, lng))

            incident_type = random.choice(INCIDENT_TYPES)

            incident = Incidents.objects.create(
                title=f"{incident_type.title()} at {loc[0]}",
                Location=loc[0],
                Time=timezone.now(),
                latitude=lat,
                longitude=lng,
                severity=random.randint(1, 10),
                incident_type=incident_type,
                clandestine=random.choice([True, False]),
                description="Auto-generated incident",
                ai_generated=True
            )
            created.append(incident.id)

        return Response({
            "generated": len(created),
            "incident_ids": created
        }, status=status.HTTP_201_CREATED)


class IncidentMapDataView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        is_mafia = user.groups.filter(name='Mafia').exists()

        if is_mafia:
            incidents = Incidents.objects.all()
        else:
            incidents = Incidents.objects.filter(clandestine=False)

        map_data = []
        for inc in incidents:
            map_data.append({
                "id": inc.id,
                "title": inc.title,
                "location": inc.Location,
                "latitude": float(inc.latitude),
                "longitude": float(inc.longitude),
                "severity": inc.severity,
                "incident_type": inc.incident_type,
                "time": inc.Time,
                "clandestine": inc.clandestine,
                "ai_generated": inc.ai_generated,
            })

        return Response(map_data)


class IncidentGraphDataView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # By type
        by_type = list(
            Incidents.objects.values('incident_type')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        # By severity
        by_severity = list(
            Incidents.objects.values('severity')
            .annotate(count=Count('id'))
            .order_by('severity')
        )

        # By day — last 7 days
        last_week = timezone.now() - timedelta(days=7)
        by_day = list(
            Incidents.objects.filter(Time__gte=last_week)
            .extra({'day': 'date("Time")'})
            .values('day')
            .annotate(count=Count('id'))
            .order_by('day')
        )

        return Response({
            "by_type": by_type,
            "by_severity": by_severity,
            "by_day": by_day,
            "total": Incidents.objects.count(),
            "ai_generated": Incidents.objects.filter(ai_generated=True).count(),
        })
    
class WarrantViewSet(viewsets.ModelViewSet):
    serializer_class = WarrantSerializer
    permission_classes = [permissions.IsAuthenticated] 

    def get_queryset(self):
        user = self.request.user
        # If the user is Mafia, ONLY return Burn Orders
        if user.is_authenticated and user.groups.filter(name='Mafia').exists():
            return Warrants.objects.all().order_by('-timestamp')
        
        # If the user is Police, ONLY return standard Warrants
        return Warrants.objects.filter(type_warrant='WARRANT').order_by('-timestamp')