from django.test import TestCase, TransactionTestCase, override_settings
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from bookings.models import Booking, Payment, FareRule
from trains.models import Train
from stations.models import Station
from pnr.models import PNR
import datetime
from django.utils import timezone
from decimal import Decimal
from django.db import IntegrityError, connection
from threading import Thread
import json

User = get_user_model()

class PaymentFlowTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.other_user = User.objects.create_user(username='otheruser', password='password123')
        
        self.station1 = Station.objects.create(code='NDLS', name='New Delhi')
        self.station2 = Station.objects.create(code='MMCT', name='Mumbai Central')
        self.train = Train.objects.create(number='12951', name='Rajdhani Express', source=self.station1, destination=self.station2, train_type='EXPRESS')
        
        FareRule.objects.create(train_type='EXPRESS', ticket_class='SL', base_fare=100.00, per_km_rate=1.50)
        
        self.client.force_authenticate(user=self.user)

    def create_pending_booking(self, user=None):
        if user:
            self.client.force_authenticate(user=user)
        payload = {
            'train_number': '12951',
            'source_code': 'NDLS',
            'destination_code': 'MMCT',
            'ticket_class': 'SL',
            'passengers': [{'name': 'Jane', 'age': 25, 'gender': 'F', 'berth_preference': 'L'}],
            'date_of_journey': str(datetime.date.today() + datetime.timedelta(days=1))
        }
        response = self.client.post('/api/bookings/', payload, format='json')
        return response.data['id']

    def print_scenario(self, title, response, booking_id):
        print(f"\n--- {title} ---")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.data)}")
        
        b = Booking.objects.get(id=booking_id)
        print(f"Booking Status: {b.status}")
        
        payments = Payment.objects.filter(booking=b)
        for p in payments:
            print(f"Payment row: Status={p.status}, Amount={p.amount}, Reason={p.failure_reason}, Masked={p.masked_details}, Idempotency={p.idempotency_key}")

    def test_upi_success(self):
        booking_id = self.create_pending_booking()
        payload = {'booking_id': booking_id, 'method': 'upi', 'idempotency_key': 'key_upi_1', 'payment_details': {'upi_id': 'user@okicici'}}
        resp = self.client.post('/api/bookings/process-payment/', payload, format='json')
        self.print_scenario("UPI Success", resp, booking_id)

    def test_fail_at_test(self):
        booking_id = self.create_pending_booking()
        payload = {'booking_id': booking_id, 'method': 'upi', 'idempotency_key': 'key_fail_1', 'payment_details': {'upi_id': 'fail@test'}}
        resp = self.client.post('/api/bookings/process-payment/', payload, format='json')
        self.print_scenario("fail@test", resp, booking_id)

    def test_card_success(self):
        booking_id = self.create_pending_booking()
        payload = {'booking_id': booking_id, 'method': 'card', 'idempotency_key': 'key_card_1', 'payment_details': {'card_number': '4111 1111 1111 1111', 'exp_month': '12', 'exp_year': '30', 'cvv': '123', 'name': 'John'}}
        resp = self.client.post('/api/bookings/process-payment/', payload, format='json')
        self.print_scenario("Card Success (4111)", resp, booking_id)

    def test_card_decline(self):
        booking_id = self.create_pending_booking()
        payload = {'booking_id': booking_id, 'method': 'card', 'idempotency_key': 'key_card_2', 'payment_details': {'card_number': '4000 0000 0000 0002', 'exp_month': '12', 'exp_year': '30', 'cvv': '123'}}
        resp = self.client.post('/api/bookings/process-payment/', payload, format='json')
        self.print_scenario("Card Decline (4000...0002)", resp, booking_id)

    def test_luhn_invalid(self):
        booking_id = self.create_pending_booking()
        payload = {'booking_id': booking_id, 'method': 'card', 'idempotency_key': 'key_card_3', 'payment_details': {'card_number': '4111 1111 1111 1112', 'exp_month': '12', 'exp_year': '30', 'cvv': '123'}}
        resp = self.client.post('/api/bookings/process-payment/', payload, format='json')
        self.print_scenario("Luhn Invalid", resp, booking_id)

    def test_double_submit(self):
        booking_id = self.create_pending_booking()
        payload = {'booking_id': booking_id, 'method': 'upi', 'idempotency_key': 'key_double_1', 'payment_details': {'upi_id': 'user@okicici'}}
        resp1 = self.client.post('/api/bookings/process-payment/', payload, format='json')
        resp2 = self.client.post('/api/bookings/process-payment/', payload, format='json')
        
        # PNR should match
        pnr1 = resp1.data.get('pnr_number')
        pnr2 = resp2.data.get('pnr_number')
        print(f"\\n--- Double Submit (resp1 vs resp2) ---")
        print(f"Resp1 PNR: {pnr1}, Resp2 PNR: {pnr2} (Match: {pnr1 == pnr2})")
        payment_count = Payment.objects.filter(booking_id=booking_id).count()
        pnr_count = PNR.objects.filter(booking_id=booking_id).count()
        print(f"Payment rows: {payment_count}, PNR rows: {pnr_count}")

    def test_pending_wallet(self):
        booking_id = self.create_pending_booking()
        payload = {'booking_id': booking_id, 'method': 'wallet', 'idempotency_key': 'key_pend_1', 'payment_details': {'provider': 'Paytm_Pending'}}
        resp = self.client.post('/api/bookings/process-payment/', payload, format='json')
        self.print_scenario("Pending Wallet", resp, booking_id)
        
        # Now resolve it by calling status API after 6 seconds mock
        payment_id = resp.data['payment_id']
        Payment.objects.filter(id=payment_id).update(created_at=timezone.now() - datetime.timedelta(seconds=10))
        
        # Poll 1
        resp2 = self.client.get(f'/api/bookings/payment-status/{payment_id}/')
        print(f"Status check after 10s: {resp2.data}")
        
        # Poll 2 (Idempotency check)
        resp3 = self.client.get(f'/api/bookings/payment-status/{payment_id}/')
        print(f"Status check #2 (Idempotent): {resp3.data}")

    def test_pending_booking_expires(self):
        booking_id = self.create_pending_booking()
        payload = {'booking_id': booking_id, 'method': 'wallet', 'idempotency_key': 'key_pend_exp', 'payment_details': {'provider': 'Paytm_Pending'}}
        resp = self.client.post('/api/bookings/process-payment/', payload, format='json')
        payment_id = resp.data['payment_id']
        
        # Simulate booking expiry by backdating expires_at
        Booking.objects.filter(id=booking_id).update(expires_at=timezone.now() - datetime.timedelta(minutes=1))
        
        # Poll status
        resp2 = self.client.get(f'/api/bookings/payment-status/{payment_id}/')
        print(f"\\n--- Pending Booking Expires ---")
        print(f"Status check after expiry: {resp2.data}")
        b = Booking.objects.get(id=booking_id)
        p = Payment.objects.get(id=payment_id)
        print(f"Booking Status: {b.status}, Payment Status: {p.status}")

    def test_pending_superseded(self):
        booking_id = self.create_pending_booking()
        # Create pending
        payload1 = {'booking_id': booking_id, 'method': 'wallet', 'idempotency_key': 'key_pend_sup', 'payment_details': {'provider': 'Paytm_Pending'}}
        resp1 = self.client.post('/api/bookings/process-payment/', payload1, format='json')
        payment_id_pending = resp1.data['payment_id']
        
        # Pay by another method
        payload2 = {'booking_id': booking_id, 'method': 'upi', 'idempotency_key': 'key_upi_sup', 'payment_details': {'upi_id': 'user@okicici'}}
        resp2 = self.client.post('/api/bookings/process-payment/', payload2, format='json')
        
        print(f"\\n--- Pending Superseded ---")
        print(f"Second payment PNR: {resp2.data.get('pnr_number')}")
        p_pending = Payment.objects.get(id=payment_id_pending)
        print(f"Old Pending Payment Status: {p_pending.status} (Reason: {p_pending.failure_reason})")


    def test_netbanking_success(self):
        booking_id = self.create_pending_booking()
        payload = {'booking_id': booking_id, 'method': 'netbanking', 'idempotency_key': 'key_nb_1', 'payment_details': {'provider': 'SBI'}}
        resp = self.client.post('/api/bookings/process-payment/', payload, format='json')
        self.print_scenario("NetBanking Success", resp, booking_id)

    def test_qr_success(self):
        booking_id = self.create_pending_booking()
        payload = {'booking_id': booking_id, 'method': 'qr', 'idempotency_key': 'key_qr_1', 'payment_details': {'provider': 'Scan_Success'}}
        resp = self.client.post('/api/bookings/process-payment/', payload, format='json')
        self.print_scenario("QR Success", resp, booking_id)
        
    def test_card_expiry_past(self):
        booking_id = self.create_pending_booking()
        payload = {'booking_id': booking_id, 'method': 'card', 'idempotency_key': 'key_card_exp', 'payment_details': {'card_number': '4111 1111 1111 1111', 'exp_month': '01', 'exp_year': '10', 'cvv': '123'}}
        resp = self.client.post('/api/bookings/process-payment/', payload, format='json')
        self.print_scenario("Card Expiry Past", resp, booking_id)

    def test_card_bad_cvv(self):
        booking_id = self.create_pending_booking()
        payload = {'booking_id': booking_id, 'method': 'card', 'idempotency_key': 'key_card_cvv', 'payment_details': {'card_number': '4111 1111 1111 1111', 'exp_month': '12', 'exp_year': '30', 'cvv': '12'}}
        resp = self.client.post('/api/bookings/process-payment/', payload, format='json')
        self.print_scenario("Card Bad CVV", resp, booking_id)

    def test_retry_after_failure(self):
        booking_id = self.create_pending_booking()
        payload1 = {'booking_id': booking_id, 'method': 'upi', 'idempotency_key': 'key_retry_1', 'payment_details': {'upi_id': 'fail@test'}}
        resp1 = self.client.post('/api/bookings/process-payment/', payload1, format='json')
        
        payload2 = {'booking_id': booking_id, 'method': 'upi', 'idempotency_key': 'key_retry_2', 'payment_details': {'upi_id': 'success@okicici'}}
        resp2 = self.client.post('/api/bookings/process-payment/', payload2, format='json')
        self.print_scenario("Retry After Failure (resp2)", resp2, booking_id)

    def test_other_user_paying(self):
        booking_id = self.create_pending_booking(user=self.other_user)
        self.client.force_authenticate(user=self.user) # Login as testuser to pay otheruser's booking
        payload = {'booking_id': booking_id, 'method': 'upi', 'idempotency_key': 'otheruser_key', 'payment_details': {'upi_id': 'user@ok'}}
        resp = self.client.post('/api/bookings/process-payment/', payload, format='json')
        print(f"\n--- Other user paying my booking ---")
        print(f"Status: {resp.status_code}, Response: {resp.data}")

    def test_tampered_amount(self):
        booking_id = self.create_pending_booking()
        payload = {'booking_id': booking_id, 'method': 'upi', 'idempotency_key': 'tamper_key', 'amount': '1.00', 'payment_details': {'upi_id': 'user@ok'}}
        resp = self.client.post('/api/bookings/process-payment/', payload, format='json')
        self.print_scenario("Tampered Amount (ignored)", resp, booking_id)

    @override_settings(BOOKING_EXPIRY_SECONDS=1)
    def test_natural_expiry(self):
        booking_id = self.create_pending_booking()
        import time
        time.sleep(1.5)
        # Fetching it should lazily expire it
        resp = self.client.get(f'/api/bookings/{booking_id}/')
        print(f"\\n--- Natural Expiry ---")
        print(f"Status after 1.5s: {resp.data.get('status')}")

    @override_settings(BOOKING_EXPIRY_SECONDS=-10) # Expire immediately
    def test_paying_expired_booking(self):
        booking_id = self.create_pending_booking()
        payload = {'booking_id': booking_id, 'method': 'upi', 'idempotency_key': 'exp_key_1', 'payment_details': {'upi_id': 'user@ok'}}
        resp = self.client.post('/api/bookings/process-payment/', payload, format='json')
        self.print_scenario("Paying Expired Booking", resp, booking_id)

    def test_paying_confirmed_booking(self):
        booking_id = self.create_pending_booking()
        payload = {'booking_id': booking_id, 'method': 'upi', 'idempotency_key': 'conf_key_1', 'payment_details': {'upi_id': 'user@ok'}}
        self.client.post('/api/bookings/process-payment/', payload, format='json') # First pay
        
        payload2 = {'booking_id': booking_id, 'method': 'upi', 'idempotency_key': 'conf_key_2', 'payment_details': {'upi_id': 'user@ok'}}
        resp = self.client.post('/api/bookings/process-payment/', payload2, format='json') # Second pay new key
        self.print_scenario("Paying Already Confirmed Booking", resp, booking_id)

    def test_expire_confirmed_booking(self):
        booking_id = self.create_pending_booking()
        payload = {'booking_id': booking_id, 'method': 'upi', 'idempotency_key': 'conf_key_1', 'payment_details': {'upi_id': 'user@ok'}}
        self.client.post('/api/bookings/process-payment/', payload, format='json') # First pay
        
        resp = self.client.post(f'/api/bookings/{booking_id}/expire/')
        print(f"\n--- Expire endpoint on CONFIRMED booking ---")
        print(f"Status: {resp.status_code}, Response: {resp.data}")


class ConcurrentPaymentTestCase(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='concurrent_user', password='password123')
        self.booking = Booking.objects.create(
            user=self.user,
            status='PENDING',
            total_fare=Decimal('300.00'),
            base_fare=Decimal('300.00'),
            gst_amount=Decimal('0.00'),
            fee_amount=Decimal('0.00')
        )
        self.url = '/api/bookings/process-payment/'

    def test_orm_integrity_error(self):
        # Insert first success
        p1 = Payment.objects.create(booking=self.booking, status='SUCCESS', amount=300, success_for_booking=self.booking.id)
        # Attempt second success
        with self.assertRaises(IntegrityError):
            Payment.objects.create(booking=self.booking, status='SUCCESS', amount=300, success_for_booking=self.booking.id)

    def test_concurrent_double_submit(self):
        results = []
        def make_request(idx):
            try:
                client = APIClient()
                client.force_authenticate(user=self.user)
                payload = {
                    'booking_id': self.booking.id,
                    'method': 'upi',
                    'idempotency_key': f'concurrent_key', # same key or different? User said 'two parallel requests must both return a clean response' - wait, if different idempotency_key, only one succeeds and other gets error? 
                    # If same key, idempotency handles it. If DIFFERENT key, they race for select_for_update.
                    'payment_details': {'upi_id': 'user@okicici'}
                }
                if idx == 2:
                    payload['idempotency_key'] = 'concurrent_key_2'
                
                resp = client.post(self.url, payload, format='json')
                results.append((idx, resp.status_code, resp.data))
            finally:
                connection.close()
                
        t1 = Thread(target=make_request, args=(1,))
        t2 = Thread(target=make_request, args=(2,))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        print('\n--- Concurrent Thread Test ---')
        print(f'Thread 1: {results[0]}')
        print(f'Thread 2: {results[1]}')
        
        # Verify EXACTLY 1 SUCCESS payment and 1 PNR
        success_payments = Payment.objects.filter(booking=self.booking, status='SUCCESS').count()
        pnr_count = PNR.objects.filter(booking=self.booking).count()
        print(f'SUCCESS Payments: {success_payments}, PNRs: {pnr_count}')
        
        self.assertEqual(success_payments, 1)
        self.assertEqual(pnr_count, 1)
        self.assertFalse(any(status == 500 for idx, status, data in results))
