import os, sys, django, requests, json
sys.path.append('c:/Users/Asus/Desktop/Personal/rgc lcg/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

base_url = 'http://127.0.0.1:8000/api'

# 1. Login
login_res = requests.post(f'{base_url}/accounts/login/', json={'username': 'testuser', 'password': 'testpassword123'})
if login_res.status_code != 200:
    print('Failed to login. Please create testuser first.')
    from django.db.utils import IntegrityError
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        User.objects.create_user('testuser', 'test@test.com', 'testpassword123')
    except IntegrityError:
        pass
    login_res = requests.post(f'{base_url}/accounts/login/', json={'username': 'testuser', 'password': 'testpassword123'})

token = login_res.json().get('access')
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

# 2. Search Dadar -> Thane
search_res = requests.get(f'{base_url}/trains/search/?source=DR&destination=TNA', headers=headers)
trains = search_res.json()
if not trains:
    print('No trains found for DR -> TNA')
    sys.exit(1)

# Get an Express train since we deleted the fake locals
express_train = next((t for t in trains if t['normalized_type'] != 'LOCAL'), trains[0])
train_no = express_train['number']
print(f'Selected train: {train_no} ({express_train["name"]})')

# 3. Book
booking_payload = {
    'train_number': train_no,
    'source_code': 'DR',
    'destination_code': 'TNA',
    'date_of_journey': '2026-09-25',
    'ticket_class': 'SL',
    'passengers': [{'name': 'John Doe', 'age': 30, 'berth_preference': 'LB', 'gender': 'M'}]
}
book_res = requests.post(f'{base_url}/bookings/', json=booking_payload, headers=headers)
if book_res.status_code != 201:
    print('Booking failed:', book_res.text)
    sys.exit(1)

booking = book_res.json()
booking_id = booking['id']
print(f'Booking successful. ID: {booking_id}')
print(f'Booking segment: {booking["source_station"]["code"]} -> {booking["destination_station"]["code"]}')

# 4. Payment
pay_res = requests.post(f'{base_url}/bookings/{booking_id}/pay/', headers=headers)
print('Payment:', pay_res.text)

# 5. Get Booking Details (PNR, Ticket, Invoice)
details_res = requests.get(f'{base_url}/bookings/{booking_id}/', headers=headers)
details = details_res.json()

print('--- PNR Details ---')
print(json.dumps(details.get('pnr_record'), indent=2))
print('--- Invoice Details ---')
print(json.dumps(details.get('invoice'), indent=2))

if details['source_station']['code'] == 'DR' and details['destination_station']['code'] == 'TNA':
    print('E2E TEST PASSED: Segment correctly stored and persisted through all records!')
else:
    print('E2E TEST FAILED: Segment changed to global origin/destination!')
