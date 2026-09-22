import os
import sys
import json
import django
from collections import defaultdict
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_mysql')
django.setup()

from django.db import transaction
from django.apps import apps

Station = apps.get_model('stations.Station')
Train = apps.get_model('trains.Train')
Route = apps.get_model('routes.Route')
RouteStation = apps.get_model('routes.RouteStation')
Schedule = apps.get_model('schedules.Schedule')

def parse_time(t_str):
    if not t_str or t_str == 'None' or t_str.lower() == 'null':
        return None
    try:
        return datetime.strptime(t_str.strip(), '%H:%M:%S').time()
    except ValueError:
        return None

@transaction.atomic
def import_data():
    print("Importing stations...")
    with open(r'backend\data\raildrishti\stations.json', 'r', encoding='utf-8') as f:
        stations_data = json.load(f)
        
    station_objs = []
    for feature in stations_data.get('features', []):
        props = feature.get('properties') or {}
        geom = feature.get('geometry') or {}
        coords = geom.get('coordinates', [None, None])
        
        station_objs.append(Station(
            code=(props.get('code') or '').strip(),
            name=(props.get('name') or '')[:100],
            city=(props.get('state') or '')[:100],
            state=(props.get('state') or '')[:100],
            zone=(props.get('zone') or '')[:10],
            longitude=coords[0],
            latitude=coords[1]
        ))
    
    Station.objects.bulk_create(station_objs, batch_size=2000, ignore_conflicts=True)
    print(f"Imported {len(station_objs)} stations.")
    
    print("Loading schedules...")
    with open(r'backend\data\raildrishti\schedules.json', 'r', encoding='utf-8') as f:
        schedules_data = json.load(f)
        
    trains_dict = defaultdict(list)
    for row in schedules_data:
        trains_dict[row['train_number']].append(row)
        
    print(f"Grouped {len(schedules_data)} schedules into {len(trains_dict)} unique trains.")
    
    train_objs = []
    route_objs = []
    
    trains_list = []
    # Pre-fetch stations to ensure FK constraints
    valid_station_codes = set(Station.objects.values_list('code', flat=True))
    
    print("Building Trains and Routes...")
    for t_num, records in trains_dict.items():
        records.sort(key=lambda x: x.get('id', 0))
        
        # Filter out records with missing stations
        records = [r for r in records if r.get('station_code') in valid_station_codes]
        if not records:
            continue
            
        first_record = records[0]
        last_record = records[-1]
        
        train = Train(
            number=(t_num or "")[:20],
            name=(first_record.get('train_name') or f'Train {t_num}')[:100],
            train_type='EXPRESS',
            source_id=first_record['station_code'],
            destination_id=last_record['station_code'],
            running_days='NOT_SPECIFIED_IN_SOURCE'
        )
        train_objs.append(train)
        
        route = Route(
            train_id=(t_num or "")[:20],
            name=f"{first_record['station_code']} to {last_record['station_code']}"[:100]
        )
        route_objs.append(route)
        trains_list.append(records)
        
    print(f"Prepared {len(train_objs)} trains.")
    # Batch create Trains
    for i in range(0, len(train_objs), 2000):
        Train.objects.bulk_create(train_objs[i:i+2000], ignore_conflicts=True)
        
    # Batch create Routes
    for i in range(0, len(route_objs), 2000):
        Route.objects.bulk_create(route_objs[i:i+2000], ignore_conflicts=True)
        
    print("Building RouteStations and Schedules...")
    # Fetch route IDs
    route_map = dict(Route.objects.values_list('train_id', 'id'))
    
    routestation_objs = []
    schedule_objs = []
    
    for records in trains_list:
        t_num = (records[0].get('train_number') or "")[:20]
        route_id = route_map.get(t_num)
        if not route_id:
            continue
            
        for idx, row in enumerate(records):
            arr = parse_time(row.get('arrival'))
            dep = parse_time(row.get('departure'))
            st_code = row['station_code']
            day = row.get('day', 1)
            
            routestation_objs.append(RouteStation(
                route_id=route_id,
                station_id=st_code,
                sequence_number=idx + 1,
                arrival_time=arr,
                departure_time=dep,
                journey_day=day
            ))
            
            schedule_objs.append(Schedule(
                train_id=t_num,
                station_id=st_code,
                arrival_time=arr,
                departure_time=dep,
                day_count=day
            ))
            
    print(f"Prepared {len(routestation_objs)} RouteStations and Schedules.")
    
    # We must insert them in batches because of memory limits and MySQL packet size
    batch_size = 5000
    
    print("Inserting RouteStations...")
    for i in range(0, len(routestation_objs), batch_size):
        RouteStation.objects.bulk_create(routestation_objs[i:i+batch_size], ignore_conflicts=True)
        
    print("Inserting Schedules...")
    for i in range(0, len(schedule_objs), batch_size):
        Schedule.objects.bulk_create(schedule_objs[i:i+batch_size], ignore_conflicts=True)
        
    print("Import Complete!")

if __name__ == '__main__':
    import_data()
