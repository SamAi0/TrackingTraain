import os
import sys
import json
import argparse
import django
from django.db import transaction

# Setup Django
sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_mysql')
django.setup()

from trains.models import Train
from stations.models import Station
from routes.models import Route, RouteStation
from schedules.models import Schedule

def run_import(dry_run=True):
    data_file = 'data/mumbai_suburban/trans_harbour_line_2024_clean.json'
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    services = data.get('services', [])
    
    # Tracking counts
    stats = {
        'stations_to_create': 0,
        'stations_existing': 0,
        'trains_to_create': 0,
        'trains_existing': 0,
        'routes_to_create_or_update': 0,
        'route_stations_to_create_or_update': 0,
        'schedules_to_create_or_update': 0,
        'skipped_records': 0,
        'conflicts_errors': 0,
        'errors_details': []
    }
    
    station_cache = {}
    
    # 1. Map Stations
    unique_stations = set()
    for s in services:
        for st in s['stations']:
            unique_stations.add(st['station_name'])
            
    for name in unique_stations:
        db_stations = list(Station.objects.filter(name__iexact=name))
        if len(db_stations) == 1:
            station_cache[name] = db_stations[0]
            stats['stations_existing'] += 1
        elif len(db_stations) > 1:
            stats['conflicts_errors'] += 1
            stats['errors_details'].append(f"Ambiguous station name: {name} matches {len(db_stations)} records.")
        else:
            # Generate a code since it's required
            code = name.upper().replace(' ', '')[:20]
            if Station.objects.filter(code=code).exists():
                stats['conflicts_errors'] += 1
                stats['errors_details'].append(f"Derived code {code} for station {name} already exists.")
            else:
                new_st = Station(
                    code=code,
                    name=name,
                    city="Navi Mumbai", # Best guess for Trans-Harbour, but we leave it simple
                    state="Maharashtra",
                    zone="CR"
                )
                station_cache[name] = new_st
                stats['stations_to_create'] += 1
                
    if stats['conflicts_errors'] > 0:
        print("Stopping due to station mapping conflicts.")
        for err in stats['errors_details']:
            print("ERROR:", err)
        return stats
        
    # Begin simulated or real transaction
    try:
        with transaction.atomic():
            if not dry_run:
                # Save new stations first
                for st_name, st_obj in station_cache.items():
                    if not st_obj.pk or not Station.objects.filter(pk=st_obj.pk).exists():
                        st_obj.save()
                        
            # 2. Map Trains and Schedules
            for s in services:
                if not s['timetable_complete']:
                    stats['skipped_records'] += 1
                    continue
                    
                train_num = s['service_number']
                train_name = s['service_name'] or f"Trans Harbour Local {train_num}"
                
                origin_name = s['origin']
                dest_name = s['destination']
                if not origin_name or not dest_name:
                    stats['skipped_records'] += 1
                    continue
                    
                origin_st = station_cache[origin_name]
                dest_st = station_cache[dest_name]
                
                # Check Train
                train = Train.objects.filter(number=train_num).first()
                if train:
                    stats['trains_existing'] += 1
                else:
                    train = Train(
                        number=train_num,
                        name=train_name,
                        train_type='LOCAL',
                        source=origin_st,
                        destination=dest_st,
                        running_days=s.get('running_days')
                    )
                    stats['trains_to_create'] += 1
                    if not dry_run:
                        train.save()
                        
                # Route
                route = Route.objects.filter(train=train).first()
                if not route:
                    route = Route(train=train, name=f"{origin_st.code} to {dest_st.code}")
                    stats['routes_to_create_or_update'] += 1
                    if not dry_run:
                        route.save()
                else:
                    stats['routes_to_create_or_update'] += 1 # consider it touched
                    
                # RouteStation & Schedule
                for st in s['stations']:
                    st_obj = station_cache[st['station_name']]
                    seq = st['sequence']
                    
                    if not dry_run:
                        # RouteStation
                        rs, created = RouteStation.objects.update_or_create(
                            route=route,
                            station=st_obj,
                            defaults={
                                'sequence_number': seq,
                                'arrival_time': st['arrival_time'],
                                'departure_time': st['departure_time'],
                                # Keep distance NULL
                            }
                        )
                        # Schedule
                        sch, created = Schedule.objects.update_or_create(
                            train=train,
                            station=st_obj,
                            defaults={
                                'arrival_time': st['arrival_time'],
                                'departure_time': st['departure_time']
                            }
                        )
                    stats['route_stations_to_create_or_update'] += 1
                    stats['schedules_to_create_or_update'] += 1
                    
            if dry_run:
                # Force rollback to ensure absolutely no DB changes in dry-run
                raise Exception("DRY RUN ABORT")
                
    except Exception as e:
        if str(e) == "DRY RUN ABORT":
            pass # Expected
        else:
            stats['conflicts_errors'] += 1
            stats['errors_details'].append(str(e))
            
    print("--- DRY RUN REPORT ---" if dry_run else "--- IMPORT REPORT ---")
    print(f"Stations to create: {stats['stations_to_create']}")
    print(f"Stations existing: {stats['stations_existing']}")
    print(f"Trains to create: {stats['trains_to_create']}")
    print(f"Trains existing: {stats['trains_existing']}")
    print(f"Routes to create/update: {stats['routes_to_create_or_update']}")
    print(f"RouteStations to create/update: {stats['route_stations_to_create_or_update']}")
    print(f"Schedules to create/update: {stats['schedules_to_create_or_update']}")
    print(f"Skipped records: {stats['skipped_records']}")
    print(f"Conflicts/Errors: {stats['conflicts_errors']}")
    
    if stats['errors_details']:
        print("Error Details:")
        for e in stats['errors_details']:
            print(f"- {e}")
            
    return stats

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    
    run_import(dry_run=args.dry_run)
