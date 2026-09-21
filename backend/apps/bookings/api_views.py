from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Booking, Invoice
from .serializers import BookingSerializer
from pnr.models import PNR, Ticket

class BookingListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).order_by('-booking_date')

    def perform_create(self, serializer):
        booking = serializer.save(user=self.request.user)
        from utils.supabase_logger import SupabaseLogger
        SupabaseLogger.log_activity(
            user_id=self.request.user.id,
            activity_type='Booking Started',
            train_number=booking.train.number,
            from_station=booking.source.code,
            to_station=booking.destination.code,
            booking_id=booking.id,
            journey_date=str(booking.date_of_journey)
        )

class BookingDetailAPIView(generics.RetrieveAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)
        
    def get_object(self):
        obj = super().get_object()
        from django.utils import timezone
        if obj.status == 'PENDING' and obj.expires_at and obj.expires_at < timezone.now():
            obj.status = 'EXPIRED'
            obj.save(update_fields=['status'])
            # We don't have actual seats held in DB to release, but status update is enough
        return obj

class VerifyPaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        with transaction.atomic():
            booking = get_object_or_404(Booking.objects.select_for_update(), id=pk, user=request.user)
            
            if booking.status != 'PENDING':
                return Response({'error': 'Booking is not pending payment.'}, status=status.HTTP_400_BAD_REQUEST)
                
            payment_id = request.data.get('payment_id')
            if not payment_id:
                return Response({'error': 'Payment ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
                
            # Simulate payment verification
            booking.status = 'CONFIRMED'
            booking.payment_id = payment_id
            booking.save()
        
        # Generate PNR
        pnr = PNR.objects.create(booking=booking, status='CONFIRMED')
        
        # Generate Ticket
        import time
        ticket_number = f"TKT{int(time.time())}"
        Ticket.objects.create(booking=booking, ticket_number=ticket_number)
        
        # Generate Invoice
        Invoice.objects.create(
            booking=booking,
            total_amount=booking.total_fare,
            payment_status='PAID',
            transaction_id=payment_id
        )
        
        # Trigger Notification
        from .models import SystemNotification
        SystemNotification.objects.create(
            user=request.user,
            notification_type='BOOKING_CONFIRM',
            message=f"Your booking for train {booking.train.number} from {booking.source.code} to {booking.destination.code} is confirmed. PNR: {pnr.pnr_number}."
        )
        
        from utils.supabase_logger import SupabaseLogger
        SupabaseLogger.log_activity(
            user_id=request.user.id,
            activity_type='Payment Success',
            booking_id=booking.id,
            pnr=pnr.pnr_number
        )
        SupabaseLogger.log_activity(
            user_id=request.user.id,
            activity_type='Booking Confirmed',
            booking_id=booking.id,
            pnr=pnr.pnr_number,
            train_number=booking.train.number,
            from_station=booking.source.code,
            to_station=booking.destination.code,
            journey_date=str(booking.date_of_journey)
        )
        
        return Response({'success': True, 'pnr_number': pnr.pnr_number})

class ExpireBookingAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        with transaction.atomic():
            booking = get_object_or_404(Booking.objects.select_for_update(), id=pk, user=request.user)
            
            if booking.status != 'PENDING':
                return Response({'error': 'Only pending bookings can be expired.'}, status=status.HTTP_400_BAD_REQUEST)
                
            booking.status = 'EXPIRED'
            booking.save(update_fields=['status'])
        
        from utils.supabase_logger import SupabaseLogger
        SupabaseLogger.log_activity(
            user_id=request.user.id,
            activity_type='Booking Cancellation',
            booking_id=booking.id,
            train_number=booking.train.number
        )
        
        return Response({'success': True, 'message': 'Booking expired and seats released.'})
