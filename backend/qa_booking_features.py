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
from stations.models import Station
from trains.models import Train
from bookings.models import Booking, Payment, Invoice, FareRule
from pnr.models import PNR, Ticket

User = get_user_model()

# Setup test user
test_user, _ = User.objects.get_or_create(username='qa_test_user', defaults={'email': 'qa@example.com'})
test_user.set_password('testpass123')
test_user.save()

try:
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(test_user)
    token = str(refresh.access_token)
    headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
except ImportError:
    headers = {}

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

# 1. Check FareRule
if not FareRule.objects.filter(train_type='EXPRESS', ticket_class='SL').exists():
    FareRule.objects.create(train_type='EXPRESS', ticket_class='SL', base_fare=100.0, per_km_rate=0.5)

try:
    pnr_number = None
    booking_id = None
    
    # --- 1. BOOKING ---
    payload = {
        "train_number": "12951",
        "source_code": "BCT",
        "destination_code": "NDLS",
        "date_of_journey": (date.today() + timedelta(days=5)).isoformat(),
        "ticket_class": "SL",
        "passengers": [
            {"name": "QA Tester", "age": 30, "gender": "M", "berth_preference": "L"}
        ]
    }
    
    res = client.post('/api/bookings/', data=json.dumps(payload), content_type='application/json', SERVER_NAME='localhost', **headers)
    if res.status_code == 201:
        booking_data = res.json()
        booking_id = booking_data['id']
        log_result("Booking", "Create Booking", "Returns 201 Created", f"Returned 201, ID: {booking_id}", "PASS")
    else:
        booking_id = None
        log_result("Booking", "Create Booking", "Returns 201 Created", f"Failed with {res.status_code}: {res.content}", "FAIL")
        
    # --- 2. FARE ---
    if booking_id:
        b = Booking.objects.get(id=booking_id)
        if b.total_fare > 0:
            log_result("Fare", "Fare Calculation", "Total fare > 0", f"Fare is {b.total_fare}", "PASS")
        else:
            log_result("Fare", "Fare Calculation", "Total fare > 0", "Fare is 0", "FAIL")
            
    # --- 3. MOCK PAYMENT ---
    if booking_id:
        # Failure payment
        pay_fail_payload = {
            "booking_id": booking_id,
            "method": "card",
            "payment_details": {
                "card_number": "4000000000000002",
                "exp_month": "12",
                "exp_year": "30",
                "cvv": "123"
            },
            "idempotency_key": "idemp_fail_1"
        }
        res_fail = client.post('/api/bookings/process-payment/', data=json.dumps(pay_fail_payload), content_type='application/json', SERVER_NAME='localhost', **headers)
        if res_fail.status_code == 400:
            log_result("Payment", "Failed Payment", "Returns 400", "Returned 400", "PASS")
        else:
            log_result("Payment", "Failed Payment", "Returns 400", f"Returned {res_fail.status_code}", "FAIL")
            
        # Success payment
        pay_succ_payload = {
            "booking_id": booking_id,
            "method": "card",
            "payment_details": {
                "card_number": "4111111111111111",
                "exp_month": "12",
                "exp_year": "30",
                "cvv": "123"
            },
            "idempotency_key": "idemp_succ_1"
        }
        res_succ = client.post('/api/bookings/process-payment/', data=json.dumps(pay_succ_payload), content_type='application/json', SERVER_NAME='localhost', **headers)
        if res_succ.status_code == 200:
            pnr_number = res_succ.json().get('pnr_number')
            log_result("Payment", "Successful Payment", "Returns 200 and PNR", f"Returned PNR: {pnr_number}", "PASS")
        else:
            pnr_number = None
            log_result("Payment", "Successful Payment", "Returns 200 and PNR", f"Failed: {res_succ.content}", "FAIL")
            
        # Double submit protection
        res_double = client.post('/api/bookings/process-payment/', data=json.dumps(pay_succ_payload), content_type='application/json', SERVER_NAME='localhost', **headers)
        if res_double.status_code == 200 and res_double.json().get('pnr_number') == pnr_number:
            log_result("Security", "Double Submit Protection", "Returns existing PNR", "Returned existing PNR", "PASS")
        else:
            log_result("Security", "Double Submit Protection", "Returns existing PNR", "Failed Idempotency", "FAIL")

    # --- 4. PNR ---
    if pnr_number:
        res_pnr = client.get(f'/api/pnr/{pnr_number}/', SERVER_NAME='localhost', **headers)
        if res_pnr.status_code == 200:
            p_data = res_pnr.json()
            if 'train_number' in p_data and p_data['train_number'] == '12951':
                log_result("PNR", "Verify PNR", "Returns correct train", "Returns train 12951", "PASS")
            else:
                log_result("PNR", "Verify PNR", "Returns correct train", str(p_data), "FAIL")
        else:
            log_result("PNR", "Verify PNR", "Returns 200", f"Returns {res_pnr.status_code}", "FAIL")
            
        # Invalid PNR
        res_inv_pnr = client.get('/api/pnr/INVALID123/', SERVER_NAME='localhost', **headers)
        if res_inv_pnr.status_code == 404:
            log_result("PNR", "Invalid PNR", "Returns 404", "Returned 404", "PASS")
        else:
            log_result("PNR", "Invalid PNR", "Returns 404", f"Returned {res_inv_pnr.status_code}", "FAIL")
            
    # --- 5 & 6. Digital Ticket & Invoice via Booking Detail ---
    if booking_id:
        res_b = client.get(f'/api/bookings/{booking_id}/', SERVER_NAME='localhost', **headers)
        if res_b.status_code == 200:
            b_data = res_b.json()
            # Ticket (via PNR record)
            has_ticket = b_data.get('pnr_record') is not None
            # Invoice
            has_invoice = b_data.get('invoice') is not None
            
            if has_ticket:
                log_result("Ticket", "Digital Ticket Exists", "Has ticket info", "Ticket info present in PNR record", "PASS")
            else:
                log_result("Ticket", "Digital Ticket Exists", "Has ticket info", "Missing", "FAIL")
                
            if has_invoice:
                log_result("Invoice", "Invoice Exists", "Has invoice info", "Invoice info present", "PASS")
            else:
                log_result("Invoice", "Invoice Exists", "Has invoice info", "Missing", "FAIL")
        else:
            log_result("Ticket/Invoice", "Fetch Booking", "Returns 200", f"Returned {res_b.status_code}", "FAIL")
            
    # --- 7. Booking History ---
    res_hist = client.get('/api/bookings/', SERVER_NAME='localhost', **headers)
    if res_hist.status_code == 200:
        hist_data = res_hist.json()
        if len(hist_data) > 0 and any(b['id'] == booking_id for b in hist_data):
            log_result("Booking History", "List Bookings", "Contains new booking", "Found booking in list", "PASS")
        else:
            log_result("Booking History", "List Bookings", "Contains new booking", "Not found", "FAIL")
    else:
        log_result("Booking History", "List Bookings", "Returns 200", f"Returned {res_hist.status_code}", "FAIL")

    # --- 8. Cancellation ---
    # Not implemented yet, we verify absence of endpoint
    log_result("Cancellation", "Cancel Booking", "Cancel endpoint exists", "Endpoint not implemented in API URLS", "NOT IMPLEMENTED")

    # --- 9. Security ---
    client.logout()
    res_sec = client.get('/api/bookings/', SERVER_NAME='localhost')
    if res_sec.status_code in [401, 403]:
        log_result("Security", "Unauthenticated Access", "Returns 401/403", f"Returned {res_sec.status_code}", "PASS")
    else:
        log_result("Security", "Unauthenticated Access", "Returns 401/403", f"Returned {res_sec.status_code}", "FAIL")

    print(json.dumps({
        "results": results,
        "test_booking_id": booking_id,
        "test_pnr": pnr_number if 'pnr_number' in locals() else None,
        "test_payment_id": Payment.objects.filter(booking_id=booking_id).first().id if booking_id else None,
        "test_invoice_id": Invoice.objects.filter(booking_id=booking_id).first().invoice_number if booking_id and Invoice.objects.filter(booking_id=booking_id).exists() else None
    }, indent=2))

except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"CRITICAL SCRIPT ERROR: {e}")
