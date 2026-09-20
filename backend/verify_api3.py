import os, sys, django
sys.path.append('c:/Users/Asus/Desktop/Personal/rgc lcg/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
import json

User = get_user_model()
user = User.objects.get(username='testuser')
client = APIClient()
client.force_authenticate(user=user)

print("\n## C. Running-Day Evidence")
res_mon = client.get('/api/trains/search/?source=CSMT&destination=PNVL&date=2026-09-21')
found_mon = any(t['number'] == '98045' for t in res_mon.json())

res_sun = client.get('/api/trains/search/?source=CSMT&destination=PNVL&date=2026-09-20')
found_sun = any(t['number'] == '98045' for t in res_sun.json())
print(f"Case A (MON-SAT): Train 98045. Monday: Found={found_mon}. Sunday: Found={found_sun}")

res_d = client.get('/api/trains/search/?source=CSMT&destination=PNVL&date=2026-09-20')
found_d = any(t['number'] == '98011' for t in res_d.json())
print(f"Case D (NOT_SPECIFIED): Train 98011. Sunday: Found={found_d}")

print("\n## D. Direction & Segment Evidence")
res_fwd = client.get('/api/trains/search/?source=CSMT&destination=PNVL')
print(f"Search CSMT -> PNVL returned {len(res_fwd.json())} trains. Numbers: {[t['number'] for t in res_fwd.json()[:5]]}")

res_rev = client.get('/api/trains/search/?source=PNVL&destination=CSMT')
print(f"Search PNVL -> CSMT returned {len(res_rev.json())} trains. Numbers: {[t['number'] for t in res_rev.json()]}")

res_seg = client.get('/api/trains/search/?source=CSMT&destination=VDLR')
if res_seg.status_code == 200 and len(res_seg.json()) > 0:
    t = res_seg.json()[0]
    print(f"Search CSMT -> VDLR Segment extracted:")
    print(f"  Train: {t['number']}")
    print(f"  Source: {t['source']['code']}")
    print(f"  Destination: {t['destination']['code']}")

print("\n## F. Fare Evidence")
payload = {
    'train_number': '98011',
    'source_code': 'CSMT',
    'destination_code': 'PNVL',
    'date_of_journey': '2026-09-25',
    'ticket_class': 'GN',
    'passengers': [{'name': 'John', 'age': 30, 'berth_preference': '', 'gender': 'M'}]
}
res_fare = client.post('/api/bookings/', payload, format='json')
print(f"Booking missing distance: Status={res_fare.status_code}, Response={res_fare.json()}")

print("\n## G. Booking Evidence")
res_express = client.get('/api/trains/search/?source=CSMT&destination=KOP')
if res_express.status_code == 200 and len(res_express.json()) > 0:
    exp_t = res_express.json()[0]
    book_payload = {
        'train_number': exp_t['number'],
        'source_code': 'CSMT',
        'destination_code': 'KOP',
        'date_of_journey': '2026-09-25',
        'ticket_class': 'SL',
        'passengers': [{'name': 'John Doe', 'age': 30, 'berth_preference': 'LB', 'gender': 'M'}]
    }
    b_res = client.post('/api/bookings/', book_payload, format='json')
    if b_res.status_code == 201:
        b = b_res.json()
        print(f"Booking created: From {b['source_station']['code']} To {b['destination_station']['code']}")
