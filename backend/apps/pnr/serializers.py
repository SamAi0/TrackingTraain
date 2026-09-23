from rest_framework import serializers
from .models import PNR
from bookings.models import Passenger
from trains.serializers import TrainSerializer
from stations.serializers import StationSerializer

class PassengerMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passenger
        fields = ['name', 'age', 'gender', 'berth_preference', 'seat_number']

class PNRSerializer(serializers.ModelSerializer):
    train = TrainSerializer(source='booking.train', read_only=True)
    source = StationSerializer(source='booking.source', read_only=True)
    destination = StationSerializer(source='booking.destination', read_only=True)
    date_of_journey = serializers.DateField(source='booking.date_of_journey', read_only=True)
    ticket_class = serializers.CharField(source='booking.ticket_class', read_only=True)
    passengers = PassengerMinimalSerializer(source='booking.passengers', many=True, read_only=True)
    train_number = serializers.CharField(source='booking.train.number', read_only=True)

    class Meta:
        model = PNR
        fields = ['pnr_number', 'status', 'created_at', 'booking', 'train_number', 'train', 'source', 'destination', 'date_of_journey', 'ticket_class', 'passengers']
