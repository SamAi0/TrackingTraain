import os
import sys
import django
import json
from datetime import date, timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_mysql')
django.setup()

from django.test.client import Client
from django.contrib.auth import get_user_model
from bookings.models import Booking, Payment, Invoice, FareRule
from pnr.models import PNR

User = get_user_model()

# Setup test user and secondary user
test_user, _ = User.objects.get_or_create(username='qa_test_user', defaults={'email': 'qa@example.com'})
test_user.set_password('testpass123')
test_user.save()

other_user, _ = User.objects.get_or_create(username='qa_other_user', defaults={'email': 'other@example.com'})
other_user.set_password('testpass123')
other_user.save()

# Get tokens
try:
    from rest_framework_simplejwt.tokens import RefreshToken
    token1 = str(RefreshToken.for_user(test_user).access_token)
    token2 = str(RefreshToken.for_user(other_user).access_token)
    headers1 = {'HTTP_AUTHORIZATION': f'Bearer {token1}'}
    headers2 = {'HTTP_AUTHORIZATION': f'Bearer {token2}'}
except ImportError:
    headers1 = {}
    headers2 = {}

client = Client()
client.force_login(test_user)

results = []

def log_result(feature, name, expected, actual, status, notes=""):
    results.append({
        'Feature': feature,
        'Test Case': name,
        'Expected': expected,
        'Actual': actual,
        'Status': status,
        'Notes': notes
    })

try:
    # --- 1. SETUP DUMMY BOOKING ---
    payload = {
        "train_number": "12951",
        "source_code": "BCT",
        "destination_code": "NDLS",
        "date_of_journey": (date.today() + timedelta(days=5)).isoformat(),
        "ticket_class": "SL",
        "passengers": [{"name": "QA Tester", "age": 30, "gender": "M", "berth_preference": "L"}]
    }
    
    res = client.post('/api/bookings/', data=json.dumps(payload), content_type='application/json', SERVER_NAME='localhost', **headers1)
    if res.status_code == 201:
        booking_id = res.json()['id']
    else:
        raise Exception("Failed to create test booking")

    pay_succ_payload = {
        "booking_id": booking_id,
        "method": "card",
        "payment_details": {"card_number": "4111111111111111", "exp_month": "12", "exp_year": "30", "cvv": "123"},
        "idempotency_key": "idemp_succ_cancel_1"
    }
    res_succ = client.post('/api/bookings/process-payment/', data=json.dumps(pay_succ_payload), content_type='application/json', SERVER_NAME='localhost', **headers1)
    if res_succ.status_code == 200:
        pnr_number = res_succ.json().get('pnr_number')
    else:
        raise Exception("Failed to process payment")
        
    b = Booking.objects.get(id=booking_id)
    if b.status == 'CONFIRMED':
        log_result("Setup", "Create & Confirm Booking", "Booking is CONFIRMED", "CONFIRMED", "PASS")
    else:
        log_result("Setup", "Create & Confirm Booking", "Booking is CONFIRMED", b.status, "FAIL")

    # --- 2. CANCELLATION TESTING ---
    
    # 2.1 Unauthenticated Cancellation
    client.logout()
    res_unauth = client.post(f'/api/bookings/{booking_id}/cancel/', SERVER_NAME='localhost')
    if res_unauth.status_code in [401, 403]:
        log_result("Cancellation", "Unauthenticated Request", "Returns 401/403", str(res_unauth.status_code), "PASS")
    else:
        log_result("Cancellation", "Unauthenticated Request", "Returns 401/403", str(res_unauth.status_code), "FAIL")

    # 2.2 Cross-User Cancellation
    client.force_login(other_user)
    res_other = client.post(f'/api/bookings/{booking_id}/cancel/', SERVER_NAME='localhost', **headers2)
    if res_other.status_code == 404:
        log_result("Cancellation", "Another User's Booking", "Returns 404", str(res_other.status_code), "PASS")
    else:
        log_result("Cancellation", "Another User's Booking", "Returns 404", str(res_other.status_code), "FAIL")

    # 2.3 Invalid Booking ID
    client.force_login(test_user)
    res_inv = client.post('/api/bookings/9999999/cancel/', SERVER_NAME='localhost', **headers1)
    if res_inv.status_code == 404:
        log_result("Cancellation", "Invalid Booking ID", "Returns 404", str(res_inv.status_code), "PASS")
    else:
        log_result("Cancellation", "Invalid Booking ID", "Returns 404", str(res_inv.status_code), "FAIL")
        
    # 2.4 Valid Cancellation
    res_cancel = client.post(f'/api/bookings/{booking_id}/cancel/', SERVER_NAME='localhost', **headers1)
    if res_cancel.status_code == 200:
        log_result("Cancellation", "Valid Cancellation", "Returns 200", str(res_cancel.status_code), "PASS")
    else:
        log_result("Cancellation", "Valid Cancellation", "Returns 200", str(res_cancel.status_code), "FAIL", res_cancel.content.decode())

    # 2.5 Verify Booking Status
    b.refresh_from_db()
    if b.status == 'CANCELLED':
        log_result("Cancellation", "Booking Status Updated", "CANCELLED", b.status, "PASS")
    else:
        log_result("Cancellation", "Booking Status Updated", "CANCELLED", b.status, "FAIL")
        
    # 2.6 Verify PNR Status
    pnr = PNR.objects.get(pnr_number=pnr_number)
    if pnr.status == 'CANCELLED':
        log_result("Cancellation", "PNR Status Updated", "CANCELLED", pnr.status, "PASS")
    else:
        log_result("Cancellation", "PNR Status Updated", "CANCELLED", pnr.status, "FAIL")

    # 2.7 Verify Payment Status (SUCCESS expected as no refund model)
    pay = Payment.objects.filter(booking_id=booking_id, status='SUCCESS').first()
    if pay and pay.status == 'SUCCESS':
        log_result("Cancellation", "Payment Remains SUCCESS", "SUCCESS", pay.status, "PASS")
    else:
        log_result("Cancellation", "Payment Remains SUCCESS", "SUCCESS", str(pay.status) if pay else "None", "FAIL")

    # 2.8 Attempt Cancellation Again
    res_again = client.post(f'/api/bookings/{booking_id}/cancel/', SERVER_NAME='localhost', **headers1)
    if res_again.status_code == 400:
        log_result("Cancellation", "Already Cancelled Booking", "Returns 400", str(res_again.status_code), "PASS")
    else:
        log_result("Cancellation", "Already Cancelled Booking", "Returns 400", str(res_again.status_code), "FAIL")

    print(json.dumps({
        "results": results,
        "test_booking_id": booking_id,
        "test_pnr": pnr_number
    }, indent=2))

except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"CRITICAL SCRIPT ERROR: {e}")
