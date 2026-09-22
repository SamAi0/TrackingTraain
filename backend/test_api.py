import os
import sys
import django
from django.test import Client

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_mysql')
django.setup()

client = Client()

print("--- Testing Station Autocomplete API ---")
response = client.get('/api/stations/autocomplete/?q=mumbai', HTTP_HOST='127.0.0.1')
print(f"Status Code: {response.status_code}")
data = response.json()
print(f"Results Count: {len(data)}")
if data:
    print(f"First Result: {data[0]['name']} ({data[0]['code']})")

print("\n--- Testing Train Autocomplete API ---")
response = client.get('/api/trains/autocomplete/?q=rajdhani', HTTP_HOST='127.0.0.1')
print(f"Status Code: {response.status_code}")
data = response.json()
print(f"Results Count: {len(data)}")
if data:
    print(f"First Result: {data[0]['name']} ({data[0]['number']})")

print("\n--- Testing Train Search API (BCT to NDLS) ---")
response = client.get('/api/trains/search/?source=BCT&destination=NDLS', HTTP_HOST='127.0.0.1')
print(f"Status Code: {response.status_code}")
data = response.json()
print(f"Results Count: {len(data)}")
found_12951 = False
for tr in data:
    if tr['number'] == '12951':
        found_12951 = True
        print(f"Train 12951 Found! Duration: {tr['duration']}, Dep: {tr['departure_time']}, Arr: {tr['arrival_time']}")
print(f"Is 12951 in results? {found_12951}")

print("\n--- Testing Full Route API (12951) ---")
response = client.get('/api/trains/12951/route/', HTTP_HOST='127.0.0.1')
print(f"Status Code: {response.status_code}")
data = response.json()
print(f"Train: {data.get('train_name')}")
route = data.get('route', [])
print(f"Route Stations Count: {len(route)}")
if route:
    print(f"First Station: {route[0]['station_name']}")
    print(f"Last Station: {route[-1]['station_name']}")
    
print("\n--- Testing Full Route API with filtering (12951 from BRC to KOTA) ---")
response = client.get('/api/trains/12951/route/?source=BRC&destination=KOTA', HTTP_HOST='127.0.0.1')
print(f"Status Code: {response.status_code}")
data = response.json()
route = data.get('route', [])
print(f"Filtered Route Stations Count: {len(route)}")
if route:
    print(f"First Station: {route[0]['station_name']}")
    print(f"Last Station: {route[-1]['station_name']}")
