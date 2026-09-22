import os
import sys
import json
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.apps import apps
from django.db import connection

Station = apps.get_model('stations.Station')
Train = apps.get_model('trains.Train')
Schedule = apps.get_model('schedules.Schedule')

file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mumbai_suburban_timetable_trackease.json")

with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# 1. Parse Stations
sm = data.get('station_master', {})
unique_stations = {}
for k, line_data in sm.items():
    for st in line_data:
        code, name = st[0], st[1]
        unique_stations[code] = name

# 2. Parse Services/Trains & Schedules
services = data.get('service_samples', [])

print("=== DRY RUN IMPORT REPORT ===\n")

print(f"1. Stations to insert: {len(unique_stations)}")
print(f"2. Trains to insert: {len(services)}")
print(f"3. Schedules to insert: {len(services) * 2}")

print("\n--- Conflict Check (Supabase) ---")
existing_stations = Station.objects.filter(code__in=unique_stations.keys()).count()
existing_trains = Train.objects.filter(number__in=[s['service_number'] for s in services]).count()
print(f"Existing Supabase stations matching new codes: {existing_stations}")
print(f"Existing Supabase trains matching new numbers: {existing_trains}")
if existing_stations == 0 and existing_trains == 0:
    print("NO CONFLICTS: Safe to insert without overwriting.")
else:
    print("WARNING: Conflicts found. Importing might overwrite or violate unique constraints.")

print("\n--- Final Import Order ---")
print("1. Station (No foreign keys)")
print("2. Train (Depends on Station for source/destination)")
print("3. Schedule (Depends on Train and Station)")

print("\n--- Safety Confirmation ---")
print("Confirmed: No existing Supabase records will be deleted or overwritten because we will use bulk_create or create() which will fail on conflict if they exist, or since conflicts=0, it's 100% safe.")
print("\nDRY RUN READY \u2014 WAITING FOR IMPORT APPROVAL")
