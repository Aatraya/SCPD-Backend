from rest_framework import serializers
from .models import Criminal, Police, Incidents

class PoliceOfficerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Police
        fields = '__all__' 


class CriminalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Criminal
        # Define all fields available in the model
        fields = [
            'criminal_id', 'incidents', 'last_seen', 
            'loyalty_name', 'loyalty_level', 'unmonitored_lanes','casinos'
        ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        request = self.context.get('request')

        # Check if the user is NOT in the Mafia group
        is_mafia = request.user.groups.filter(name='Mafia').exists() if request else False

        if not is_mafia:
            # REMOVE secret fields for Police/Public users
            ret.pop('loyalty_name', None)
            ret.pop('loyalty_level', None)
            ret.pop('unmonitored_lanes', None)
            
        return ret


class IncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incidents
        fields = ['Inc_id', 'title', 'Location', 'Time', 'latitude', 'longitude', 'clandestine']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        request = self.context.get('request')
        
        # Check for Mafia status
        is_mafia = request.user.groups.filter(name='Mafia').exists() if request else False

        if not is_mafia:
            if instance.clandestine:
                return None 
            ret.pop('clandestine', None)
            
        return ret
