from rest_framework import serializers
from .models import Booking, Passenger, Invoice, FareRule
from pnr.serializers import PNRSerializer
from pnr.models import PNR, Ticket
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

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['ticket_number', 'generated_at', 'ticket_class', 'valid_from', 'valid_until', 'is_valid', 'validity_status']

class BookingSerializer(serializers.ModelSerializer):
    passengers = PassengerSerializer(many=True)
    pnr_record = PNRSerializer(read_only=True)
    invoice = InvoiceSerializer(read_only=True)
    ticket = TicketSerializer(read_only=True)
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
    journey_type = serializers.CharField(write_only=True, required=False, default='SINGLE')
    ticket_type = serializers.CharField(write_only=True, required=False, default='NORMAL')
    ticket_duration = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Booking
        fields = ['id', 'user', 'pnr_record', 'invoice', 'ticket', 'booking_date', 'total_fare', 
                  'base_fare', 'gst_amount', 'fee_amount',
                  'status', 'train_number', 'train_type', 'source_code', 'destination_code', 
                  'date_of_journey', 'ticket_class', 'passengers', 'train_details', 'source_station', 'destination_station', 'expires_at', 'journey_type', 'ticket_type', 'ticket_duration']
        read_only_fields = ['user', 'booking_date', 'total_fare', 'base_fare', 'gst_amount', 'fee_amount', 'status', 'pnr_record', 'invoice', 'ticket', 'train_type', 'train_details', 'source_station', 'destination_station', 'expires_at']

    def get_train_type(self, obj):
        return obj.train.normalized_type if obj.train else 'UNKNOWN'

    def validate(self, attrs):
        train = None
        if 'train_number' in attrs:
            try:
                train = Train.objects.get(number=attrs['train_number'])
            except Train.DoesNotExist:
                pass
                
        passengers = attrs.get('passengers', [])
        if len(passengers) == 0:
            if train and train.normalized_type != 'LOCAL':
                raise serializers.ValidationError("At least one passenger is required for Express trains.")
            elif not train:
                raise serializers.ValidationError("At least one passenger is required.")
        return attrs

    def create(self, validated_data):
        train_num = validated_data.pop('train_number')
        try:
            train = Train.objects.get(number=train_num)
        except Train.DoesNotExist:
            raise serializers.ValidationError({"train_number": f"Invalid train number: {train_num}"})
            
        src_code = validated_data.pop('source_code')
        try:
            source = Station.objects.get(code=src_code)
        except Station.DoesNotExist:
            source = Station.objects.filter(name__iexact=src_code).first()
            if not source:
                raise serializers.ValidationError({"source_code": f"Invalid source station: {src_code}"})
                
        dst_code = validated_data.pop('destination_code')
        try:
            destination = Station.objects.get(code=dst_code)
        except Station.DoesNotExist:
            destination = Station.objects.filter(name__iexact=dst_code).first()
            if not destination:
                raise serializers.ValidationError({"destination_code": f"Invalid destination station: {dst_code}"})
                
        passengers_data = validated_data.pop('passengers', [])
        ticket_class = validated_data.pop('ticket_class', None)
        journey_type = validated_data.pop('journey_type', 'SINGLE')
        ticket_type = validated_data.pop('ticket_type', 'NORMAL')
        ticket_duration = validated_data.pop('ticket_duration', None)
        
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
            num_pass = max(1, len(passengers_data))
            fare_details = calculate_total_fare(train, source, destination, num_pass, ticket_class, journey_type, ticket_type)
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
            journey_type=journey_type,
            ticket_type=ticket_type,
            ticket_duration=ticket_duration,
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
