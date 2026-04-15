from rest_framework import serializers
from .models import Criminal, Police, Incidents, Warrants


class PoliceOfficerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Police
        fields = "__all__"


class CriminalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Criminal
        fields = [
            "id",
            "police_name",
            "mafia_name",
            "police_status",
            "mafia_status",
            "police_threat",
            "mafia_threat",
            "police_notes",
            "mafia_notes",
        ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        request = self.context.get("request")
        is_mafia = (
            request.user.groups.filter(name="Mafia").exists() if request else False
        )

        if not is_mafia:
            ret.pop("mafia_name", None)
            ret.pop("mafia_status", None)
            ret.pop("mafia_threat", None)
            ret.pop("mafia_notes", None)

        return ret


class IncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incidents
        fields = [
            "id",
            "title",
            "Location",
            "Time",
            "latitude",
            "longitude",
            "clandestine",
            "severity",
            "incident_type",
            "ai_generated",
            "description",
        ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        request = self.context.get("request")

        # Check for Mafia status
        is_mafia = (
            request.user.groups.filter(name="Mafia").exists() if request else False
        )

        if not is_mafia:
            if instance.clandestine:
                return None
            ret.pop("clandestine", None)

        return ret


class WarrantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warrants
        fields = [
            "id",
            "target_id",
            "urgency",
            "justification",
            "type_warrant",
            "timestamp",
        ]
