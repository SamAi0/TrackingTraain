import os
import sys
import django
from django.test import Client
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_mysql')
django.setup()

client = Client()

print("--- Testing Train Tracking API (12951) ---")
response = client.get('/api/trains/12951/track/?demo_delay=15', HTTP_HOST='127.0.0.1')
print(f"Status Code: {response.status_code}")
data = response.json()

print(f"Train: {data.get('train_name')}")
print(f"Status: {data.get('status')}")
print(f"Delay Minutes: {data.get('delay_minutes')}")
print(f"Previous Station: {data.get('previous_station')}")
print(f"Current Station: {data.get('current_station')}")
print(f"Next Station: {data.get('next_station')}")
print(f"Expected Arrival: {data.get('expected_arrival')}")
print(f"Expected Departure: {data.get('expected_departure')}")
print(f"Progress Percentage: {data.get('progress_percentage')}%")

route = data.get('route', [])
print(f"Total Route Stations: {len(route)}")
if route:
    completed = [r for r in route if r['status'] == 'COMPLETED']
    current = [r for r in route if r['status'] == 'CURRENT']
    upcoming = [r for r in route if r['status'] == 'UPCOMING']
    
    print(f"Completed Stations: {len(completed)}")
    print(f"Current Station Count: {len(current)}")
    print(f"Upcoming Stations: {len(upcoming)}")
    
    if current:
        print(f"Current Marker: {current[0]['station_name']} Seq: {current[0]['sequence_number']}")
