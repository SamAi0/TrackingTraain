from rest_framework import serializers
from .models import PNR
from trains.serializers import TrainSerializer
from stations.serializers import StationSerializer

class PNRSerializer(serializers.ModelSerializer):
    train = TrainSerializer(read_only=True)
    source = StationSerializer(read_only=True)
    destination = StationSerializer(read_only=True)
    passenger_name = serializers.SerializerMethodField()
    passenger_age = serializers.SerializerMethodField()

    class Meta:
        model = PNR
        fields = '__all__'
        
    def get_passenger_name(self, obj):
        # We don't have multiple passengers per PNR yet in this model, but we will return generic names.
        return "Passenger 1"
        
    def get_passenger_age(self, obj):
        return "XX"
