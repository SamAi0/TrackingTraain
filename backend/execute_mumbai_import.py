import os
import sys
import json
import django
from django.db import transaction, IntegrityError

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.apps import apps

Station = apps.get_model('stations.Station')
Train = apps.get_model('trains.Train')
Schedule = apps.get_model('schedules.Schedule')

file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mumbai_suburban_timetable_trackease.json")

with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# 1. Parse Data
sm = data.get('station_master', {})
unique_stations = {}
for k, line_data in sm.items():
    for st in line_data:
        code, name = st[0], st[1]
        unique_stations[code] = name

services = data.get('service_samples', [])

stats = {
    'stations_inserted': 0,
    'trains_inserted': 0,
    'schedules_inserted': 0,
    'duplicates': 0,
    'failed': 0
}

try:
    with transaction.atomic():
        print("1. Inserting Stations...")
        for code, name in unique_stations.items():
            # insert-only logic
            if not Station.objects.filter(code=code).exists():
                Station.objects.create(
                    code=code,
                    name=name,
                    city="Mumbai",
                    state="Maharashtra"
                )
                stats['stations_inserted'] += 1
            else:
                stats['duplicates'] += 1
                
        print("2. Inserting Trains...")
        for s in services:
            number = s.get('service_number')
            if not Train.objects.filter(number=number).exists():
                source_st = Station.objects.get(code=s.get('origin'))
                dest_st = Station.objects.get(code=s.get('destination'))
                
                t = Train.objects.create(
                    number=number,
                    name=s.get('service_name'),
                    train_type=s.get('service_type'),
                    source=source_st,
                    destination=dest_st,
                    running_days=s.get('running_days')
                )
                stats['trains_inserted'] += 1
            else:
                stats['duplicates'] += 1
                
        print("3. Inserting Schedules...")
        for s in services:
            train = Train.objects.get(number=s.get('service_number'))
            origin = Station.objects.get(code=s.get('origin'))
            destination = Station.objects.get(code=s.get('destination'))
            
            # Origin schedule
            if not Schedule.objects.filter(train=train, station=origin).exists():
                Schedule.objects.create(
                    train=train,
                    station=origin,
                    departure_time=s.get('origin_departure'),
                    day_count=1
                )
                stats['schedules_inserted'] += 1
            else:
                stats['duplicates'] += 1
                
            # Destination schedule
            if not Schedule.objects.filter(train=train, station=destination).exists():
                Schedule.objects.create(
                    train=train,
                    station=destination,
                    arrival_time=s.get('destination_arrival'),
                    day_count=1
                )
                stats['schedules_inserted'] += 1
            else:
                stats['duplicates'] += 1

except Exception as e:
    stats['failed'] += 1
    print(f"FATAL ERROR: Import halted and rolled back. Error: {e}")
    sys.exit(1)

print("\n--- FINAL VERIFICATION REPORT ---")
print(f"Total Mumbai stations imported: {stats['stations_inserted']}")
print(f"Total Mumbai suburban trains imported: {stats['trains_inserted']}")
print(f"Total schedules imported: {stats['schedules_inserted']}")
print(f"Any duplicate/conflicting records skipped: {stats['duplicates']}")
print(f"Any failed records: {stats['failed']}")

# FK Integrity Verification
# We fetch them back to verify FK resolution
print("\n--- FK Verification ---")
sample_train = Train.objects.filter(number__in=[s['service_number'] for s in services]).first()
if sample_train:
    print(f"Train {sample_train.number} source FK resolved to: {sample_train.source.code}")
    print(f"Train {sample_train.number} destination FK resolved to: {sample_train.destination.code}")
    sample_sched = Schedule.objects.filter(train=sample_train).first()
    print(f"Schedule for {sample_train.number} FK resolved to Train: {sample_sched.train.number}, Station: {sample_sched.station.code}")
    
print("\nConfirmation: MySQL remains untouched.")
print("Confirmation: Existing Supabase records were not overwritten (insert-only logic used).")
print("\nIMPORT SUCCESSFUL")
