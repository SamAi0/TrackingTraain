from rest_framework import serializers
from .models import Train
from stations.serializers import StationSerializer

class TrainSerializer(serializers.ModelSerializer):
    source = StationSerializer(read_only=True)
    destination = StationSerializer(read_only=True)
    normalized_type = serializers.CharField(read_only=True)

    class Meta:
        model = Train
        fields = ['number', 'name', 'train_type', 'normalized_type', 'source', 'destination']
