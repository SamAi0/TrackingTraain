from rest_framework import serializers
from .models import TrainStatus
from trains.serializers import TrainSerializer
from stations.serializers import StationSerializer

class TrainStatusSerializer(serializers.ModelSerializer):
    train = TrainSerializer(read_only=True)
    current_station = StationSerializer(read_only=True)
    next_station = StationSerializer(read_only=True)

    class Meta:
        model = TrainStatus
        fields = '__all__'
