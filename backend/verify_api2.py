import requests, json

headers = {'Content-Type': 'application/json'}
res = requests.post('http://127.0.0.1:8000/api/accounts/login/', json={'username': 'testuser', 'password': 'testpassword123'})
token = res.json().get('access')
headers['Authorization'] = f'Bearer {token}'

print('\n## C. Running-Day Evidence')
res_mon = requests.get('http://127.0.0.1:8000/api/trains/search/?source=CSMT&destination=PNVL&date=2026-09-21', headers=headers)
found_mon = any(t['number'] == '98045' for t in res_mon.json())

res_sun = requests.get('http://127.0.0.1:8000/api/trains/search/?source=CSMT&destination=PNVL&date=2026-09-20', headers=headers)
found_sun = any(t['number'] == '98045' for t in res_sun.json())
print(f'Case A (MON-SAT): Train 98045. Monday: Found={found_mon}. Sunday: Found={found_sun}')

res_d = requests.get('http://127.0.0.1:8000/api/trains/search/?source=CSMT&destination=PNVL&date=2026-09-20', headers=headers)
found_d = any(t['number'] == '98011' for t in res_d.json())
print(f'Case D (NOT_SPECIFIED): Train 98011. Sunday: Found={found_d}')

print('\n## D. Direction & Segment Evidence')
res_fwd = requests.get('http://127.0.0.1:8000/api/trains/search/?source=CSMT&destination=PNVL', headers=headers)
print(f"Search CSMT -> PNVL returned {len(res_fwd.json())} trains. Numbers: {[t['number'] for t in res_fwd.json()[:5]]}")

res_rev = requests.get('http://127.0.0.1:8000/api/trains/search/?source=PNVL&destination=CSMT', headers=headers)
print(f"Search PNVL -> CSMT returned {len(res_rev.json())} trains. Numbers: {[t['number'] for t in res_rev.json()]}")

res_seg = requests.get('http://127.0.0.1:8000/api/trains/search/?source=CSMT&destination=VDLR', headers=headers)
if res_seg.status_code == 200 and len(res_seg.json()) > 0:
    t = res_seg.json()[0]
    print(f"Search CSMT -> VDLR Segment extracted:")
    print(f"  Train: {t['number']}")
    print(f"  Source: {t['source']['code']}")
    print(f"  Destination: {t['destination']['code']}")

print('\n## F. Fare Evidence')
payload = {
    'train_number': '98011',
    'source_code': 'CSMT',
    'destination_code': 'PNVL',
    'date_of_journey': '2026-09-25',
    'ticket_class': 'GN',
    'passengers': [{'name': 'John', 'age': 30, 'berth_preference': '', 'gender': 'M'}]
}
res_fare = requests.post('http://127.0.0.1:8000/api/bookings/', json=payload, headers=headers)
print(f"Booking missing distance: Status={res_fare.status_code}, Response={res_fare.json()}")

print('\n## G. Booking Evidence')
res_express = requests.get('http://127.0.0.1:8000/api/trains/search/?source=CSMT&destination=KOP', headers=headers)
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
    b_res = requests.post('http://127.0.0.1:8000/api/bookings/', json=book_payload, headers=headers)
    if b_res.status_code == 201:
        b = b_res.json()
        print(f"Booking created: From {b['source_station']['code']} To {b['destination_station']['code']}")
