from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (CriminalViewSet, PoliceViewSet, SystemBreachView,
                    IncidentViewSet, AIIncidentGeneratorView,
                    IncidentMapDataView, IncidentGraphDataView,WarrantViewSet)

router = DefaultRouter()
router.register(r'criminals', CriminalViewSet, basename='criminal')
router.register(r'police', PoliceViewSet, basename='police')
router.register(r'incidents', IncidentViewSet, basename='incident')
router.register(r'warrants', WarrantViewSet, basename='warrant')

urlpatterns = [
    # Custom paths FIRST before router.urls
    path('breach/', SystemBreachView.as_view(), name='system-breach'),
    path('incidents/generate/', AIIncidentGeneratorView.as_view(), name='ai-generate'),
    path('incidents/map/', IncidentMapDataView.as_view(), name='incident-map'),
    path('incidents/graph/', IncidentGraphDataView.as_view(), name='incident-graph'),

    # Router LAST
    path('', include(router.urls)),
]