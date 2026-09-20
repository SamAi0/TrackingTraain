import os, sys, django
sys.path.append('c:/Users/Asus/Desktop/Personal/rgc lcg/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from trains.api_views import TrainSearchAPIView
from bookings.api_views import BookingViewSet
import json

User = get_user_model()
user = User.objects.get(username='testuser')
factory = RequestFactory()

def get_train_search(source, dest, date=None):
    url = f'/api/trains/search/?source={source}&destination={dest}'
    if date:
        url += f'&date={date}'
    request = factory.get(url, HTTP_HOST='localhost')
    request.user = user
    view = TrainSearchAPIView.as_view()
    response = view(request)
    return response.data if hasattr(response, 'data') else json.loads(response.content)

print("\n## C. Running-Day Evidence")
res_mon = get_train_search('CSMT', 'PNVL', '2026-09-21')
found_mon = any(t['number'] == '98045' for t in res_mon)

res_sun = get_train_search('CSMT', 'PNVL', '2026-09-20')
found_sun = any(t['number'] == '98045' for t in res_sun)
print(f"Case A (MON-SAT): Train 98045. Monday: Found={found_mon}. Sunday: Found={found_sun}")

res_d = get_train_search('CSMT', 'PNVL', '2026-09-20')
found_d = any(t['number'] == '98011' for t in res_d)
print(f"Case D (NOT_SPECIFIED): Train 98011. Sunday: Found={found_d}")

print("\n## D. Direction & Segment Evidence")
res_fwd = get_train_search('CSMT', 'PNVL')
print(f"Search CSMT -> PNVL returned {len(res_fwd)} trains. Numbers: {[t['number'] for t in res_fwd[:5]]}")

res_rev = get_train_search('PNVL', 'CSMT')
print(f"Search PNVL -> CSMT returned {len(res_rev)} trains. Numbers: {[t['number'] for t in res_rev]}")

res_seg = get_train_search('CSMT', 'VDLR')
if len(res_seg) > 0:
    t = res_seg[0]
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
request = factory.post('/api/bookings/', payload, content_type='application/json', HTTP_HOST='localhost')
request.user = user
# Using BookingViewSet directly
view = BookingViewSet.as_view({'post': 'create'})
response = view(request)
try:
    print(f"Booking missing distance: Status={response.status_code}, Response={response.data}")
except Exception as e:
    print(f"Booking missing distance: Status={response.status_code}, Response={response.content}")

print("\n## G. Booking Evidence")
res_express = get_train_search('CSMT', 'KOP')
if len(res_express) > 0:
    exp_t = res_express[0]
    book_payload = {
        'train_number': exp_t['number'],
        'source_code': 'CSMT',
        'destination_code': 'KOP',
        'date_of_journey': '2026-09-25',
        'ticket_class': 'SL',
        'passengers': [{'name': 'John Doe', 'age': 30, 'berth_preference': 'LB', 'gender': 'M'}]
    }
    b_request = factory.post('/api/bookings/', book_payload, content_type='application/json', HTTP_HOST='localhost')
    b_request.user = user
    b_response = view(b_request)
    if b_response.status_code == 201:
        b = b_response.data
        print(f"Booking created: From {b['source_station']['code']} To {b['destination_station']['code']}")
