import re
import time
from datetime import datetime
from django.db import transaction, IntegrityError
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters, sensitive_variables
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Booking, Payment, Invoice, SystemNotification
from pnr.models import PNR, Ticket

def confirm_booking(booking, payment):
    booking.status = 'CONFIRMED'
    booking.payment_id = payment.transaction_id
    booking.save(update_fields=['status', 'payment_id'])
    
    payment.success_for_booking = booking.id
    payment.save(update_fields=['success_for_booking'])
    
    pnr = PNR.objects.create(booking=booking, status='CONFIRMED')
    Ticket.objects.create(booking=booking, ticket_number=f"TKT-{pnr.pnr_number}")
    Invoice.objects.create(
        booking=booking,
        total_amount=booking.total_fare,
        payment_status='PAID',
        transaction_id=payment.transaction_id
    )
    
    SystemNotification.objects.create(
        user=booking.user,
        notification_type='BOOKING_CONFIRM',
        message=f"Payment of ₹{booking.total_fare} successful. PNR: {pnr.pnr_number}."
    )
    return pnr

def luhn_check(card_no):
    digits = [int(x) for x in str(card_no) if x.isdigit()]
    if not digits: return False
    checksum = 0
    is_second = False
    for i in range(len(digits) - 1, -1, -1):
        d = digits[i]
        if is_second:
            d = d * 2
            if d > 9:
                d -= 9
        checksum += d
        is_second = not is_second
    return checksum % 10 == 0

@method_decorator(sensitive_post_parameters('payment_details'), name='dispatch')
class ProcessPaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @sensitive_variables('details', 'card_no', 'cvv', 'exp_mm', 'exp_yy')
    def post(self, request):
        booking_id = request.data.get('booking_id')
        method = request.data.get('method')
        details = request.data.get('payment_details', {})
        idempotency_key = request.data.get('idempotency_key')
        
        if not booking_id or not method or not idempotency_key:
            return Response({'error': 'Missing required fields.'}, status=400)
            
        allowed_methods = ['upi', 'card', 'netbanking', 'wallet', 'qr']
        if method not in allowed_methods:
            return Response({'error': 'Invalid payment method.'}, status=400)

        # 1. Validation
        failure_reason = None
        masked = {}
        
        if method == 'upi':
            upi_id = details.get('upi_id', '')
            if not re.match(r'^[\w.-]+@[\w.-]+$', upi_id):
                return Response({'error': 'Invalid UPI VPA format.'}, status=400)
            masked = {'upi_id': upi_id[:2] + '***' + upi_id[upi_id.find('@'):]}
            if upi_id == 'fail@test':
                failure_reason = 'Simulated UPI Failure'
                
        elif method == 'card':
            card_no = details.get('card_number', '').replace(' ', '')
            exp_mm = details.get('exp_month')
            exp_yy = details.get('exp_year')
            cvv = details.get('cvv')
            
            if not card_no or not exp_mm or not exp_yy or not cvv:
                return Response({'error': 'Missing card details.'}, status=400)
            if len(str(cvv)) not in [3, 4]:
                return Response({'error': 'Invalid CVV.'}, status=400)
            if not luhn_check(card_no):
                return Response({'error': 'Invalid card number (Luhn check failed).'}, status=400)
                
            try:
                exp_date = datetime.strptime(f"{exp_mm}/20{exp_yy}", "%m/%Y")
                # Last day of month
                if exp_date < datetime.now().replace(day=1, hour=0, minute=0, second=0):
                    return Response({'error': 'Card has expired.'}, status=400)
            except ValueError:
                return Response({'error': 'Invalid expiry date format.'}, status=400)
                
            brand = "Unknown"
            if card_no.startswith('4'): brand = 'Visa'
            elif card_no.startswith(('51','52','53','54','55')): brand = 'Mastercard'
            elif card_no.startswith(('60','65','81','82')): brand = 'RuPay'
            elif card_no.startswith(('34','37')): brand = 'Amex'
            
            masked = {'card_brand': brand, 'last4': card_no[-4:]}
            if card_no == '4000000000000002':
                failure_reason = 'Card Declined by Bank'

        elif method in ['netbanking', 'wallet', 'qr']:
            provider = details.get('provider', 'Unknown')
            masked = {'provider': provider}
            # Simulate status based on provider string
            if 'fail' in provider.lower():
                failure_reason = f'Simulated {method.title()} Failure'
            elif 'pending' in provider.lower():
                # We will handle pending down below
                pass

        # 2. Process Atomic
        try:
            with transaction.atomic():
                booking = Booking.objects.select_for_update().get(id=booking_id, user=request.user)
                
                # Idempotency check MUST happen first
                existing_payment = Payment.objects.filter(booking=booking, idempotency_key=idempotency_key).first()
                if existing_payment:
                    if existing_payment.status == 'SUCCESS':
                        return Response({'success': True, 'pnr_number': booking.pnr_record.pnr_number})
                    elif existing_payment.status == 'FAILED':
                        return Response({'success': False, 'error': existing_payment.failure_reason}, status=400)
                    elif existing_payment.status == 'PENDING':
                        return Response({'success': True, 'status': 'PENDING', 'payment_id': existing_payment.id})
                
                if booking.status == 'CONFIRMED':
                    return Response({'error': 'Booking is already confirmed.'}, status=400)
                    
                if booking.expires_at and booking.expires_at < timezone.now():
                    booking.status = 'EXPIRED'
                    booking.save(update_fields=['status'])
                    
                if booking.status in ['CANCELLED', 'FAILED', 'EXPIRED']:
                    return Response({'error': f'Booking is {booking.status.lower()} and cannot be paid.'}, status=400)

                # Determine success or failure
                payment_status = 'SUCCESS'
                if failure_reason:
                    payment_status = 'FAILED'
                elif method in ['netbanking', 'wallet', 'qr'] and 'pending' in provider.lower():
                    payment_status = 'PENDING'
                
                # Transaction ID mock
                txn_id = f"txn_{int(time.time())}_{booking.id}"
                
                payment = Payment.objects.create(
                    booking=booking,
                    method=method,
                    status=payment_status,
                    amount=booking.total_fare,
                    currency='INR',
                    transaction_id=txn_id,
                    idempotency_key=idempotency_key,
                    failure_reason=failure_reason,
                    masked_details=masked
                )

                if payment_status == 'FAILED':
                    # Do not confirm booking, just return failure
                    return Response({'success': False, 'error': failure_reason}, status=400)
                    
                if payment_status == 'PENDING':
                    return Response({'success': True, 'status': 'PENDING', 'payment_id': payment.id})
                
                # SUCCESS
                # Cancel any old PENDING payments
                Payment.objects.filter(booking=booking, status='PENDING').update(
                    status='FAILED', 
                    failure_reason='Superseded by another successful payment'
                )
                
                pnr = confirm_booking(booking, payment)
                return Response({'success': True, 'pnr_number': pnr.pnr_number})
                
        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found.'}, status=404)
        except IntegrityError:
            # Re-fetch payment if concurrent success occurred
            success_payment = Payment.objects.filter(booking_id=booking_id, status='SUCCESS').first()
            if success_payment and success_payment.idempotency_key == idempotency_key:
                return Response({'success': True, 'pnr_number': success_payment.booking.pnr_record.pnr_number})
            elif success_payment:
                # Same booking, different payment attempt (or parallel exact attempt where idempotency failed to lock first)
                return Response({'success': True, 'pnr_number': success_payment.booking.pnr_record.pnr_number})
            return Response({'error': 'A database integrity error occurred.'}, status=500)
        except Exception as e:
            return Response({'error': 'An internal error occurred during payment processing.'}, status=500)

class CheckPaymentStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, payment_id):
        payment = get_object_or_404(Payment, id=payment_id, booking__user=request.user)
        
        # Auto-resolve logic for simulation
        if payment.status == 'PENDING':
            with transaction.atomic():
                booking = Booking.objects.select_for_update().get(id=payment.booking.id)
                payment = Payment.objects.get(id=payment_id) # refetch inside lock
                
                if payment.status == 'PENDING':
                    # Check expiry
                    if booking.expires_at and booking.expires_at < timezone.now():
                        payment.status = 'FAILED'
                        payment.failure_reason = 'Booking expired before payment resolution'
                        payment.save(update_fields=['status', 'failure_reason'])
                        
                        if booking.status == 'PENDING':
                            booking.status = 'EXPIRED'
                            booking.save(update_fields=['status'])
                    else:
                        time_diff = (timezone.now() - payment.created_at).total_seconds()
                        if time_diff > 5:  # Auto resolve to SUCCESS after 5 seconds
                            payment.status = 'SUCCESS'
                            payment.save(update_fields=['status'])
                            
                            # Ensure booking is still pending before confirming
                            if booking.status == 'PENDING':
                                confirm_booking(booking, payment)
        
        if payment.status == 'SUCCESS':
            return Response({'status': 'SUCCESS', 'pnr_number': getattr(payment.booking, 'pnr_record', None) and payment.booking.pnr_record.pnr_number})
        return Response({'status': payment.status})
