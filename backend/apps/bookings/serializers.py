from rest_framework import serializers
from .models import Booking, Passenger, Invoice, FareRule
from pnr.serializers import PNRSerializer
from pnr.models import PNR
from trains.models import Train
from stations.models import Station
from routes.models import RouteStation
from .fare_calculator import calculate_total_fare, FareCalculationError
from trains.serializers import TrainSerializer
from stations.serializers import StationSerializer

class PassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passenger
        fields = ['id', 'name', 'age', 'gender', 'berth_preference', 'seat_number']
        read_only_fields = ['seat_number']

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    passengers = PassengerSerializer(many=True)
    pnr_record = PNRSerializer(read_only=True)
    invoice = InvoiceSerializer(read_only=True)
    train_type = serializers.SerializerMethodField()
    train_details = TrainSerializer(source='train', read_only=True)
    source_station = StationSerializer(source='source', read_only=True)
    destination_station = StationSerializer(source='destination', read_only=True)
    
    # Write only fields for creation
    train_number = serializers.CharField(write_only=True)
    source_code = serializers.CharField(write_only=True)
    destination_code = serializers.CharField(write_only=True)
    date_of_journey = serializers.DateField()
    ticket_class = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Booking
        fields = ['id', 'user', 'pnr_record', 'invoice', 'booking_date', 'total_fare', 
                  'status', 'train_number', 'train_type', 'source_code', 'destination_code', 
                  'date_of_journey', 'ticket_class', 'passengers', 'train_details', 'source_station', 'destination_station']
        read_only_fields = ['user', 'booking_date', 'total_fare', 'status', 'pnr_record', 'invoice', 'train_type', 'train_details', 'source_station', 'destination_station']

    def get_train_type(self, obj):
        return obj.train.normalized_type if obj.train else 'UNKNOWN'

    def validate(self, attrs):
        if len(attrs.get('passengers', [])) == 0:
            raise serializers.ValidationError("At least one passenger is required.")
        return attrs

    def create(self, validated_data):
        train = Train.objects.get(number=validated_data.pop('train_number'))
        source = Station.objects.get(code=validated_data.pop('source_code'))
        destination = Station.objects.get(code=validated_data.pop('destination_code'))
        passengers_data = validated_data.pop('passengers')
        ticket_class = validated_data.pop('ticket_class', None)
        
        # Train type specific validation
        if train.normalized_type == 'LOCAL':
            ticket_class = ticket_class or 'GN'  # Default for Local
            for p in passengers_data:
                p['berth_preference'] = ''  # Strip berth prefs for Local
        else:
            if not ticket_class:
                raise serializers.ValidationError({"ticket_class": "Class is required for Express/Superfast trains."})

        # Calculate fare
        try:
            fare_details = calculate_total_fare(train, source, destination, len(passengers_data), ticket_class)
        except FareCalculationError as e:
            raise serializers.ValidationError({"error": str(e)})
            
        from django.conf import settings
        from django.utils import timezone
        from datetime import timedelta
        
        expires_at = timezone.now() + timedelta(seconds=getattr(settings, 'BOOKING_EXPIRY_SECONDS', 600))
        
        # Create Booking as PENDING
        booking = Booking.objects.create(
            user=self.context['request'].user,
            train=train,
            source=source,
            destination=destination,
            date_of_journey=validated_data['date_of_journey'],
            ticket_class=ticket_class,
            base_fare=fare_details['base_fare'],
            gst_amount=fare_details['gst_amount'],
            fee_amount=fare_details['fee_amount'],
            total_fare=fare_details['total_fare'],
            status='PENDING',
            expires_at=expires_at
        )
        
        for p_data in passengers_data:
            Passenger.objects.create(booking=booking, **p_data)
            
        return booking
