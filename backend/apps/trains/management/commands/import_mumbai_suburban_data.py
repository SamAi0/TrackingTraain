import json
import datetime
from django.core.management.base import BaseCommand
from django.db import transaction
from stations.models import Station
from trains.models import Train
from routes.models import Route, RouteStation

class Command(BaseCommand):
    help = 'Imports Mumbai suburban timetable from JSON safely.'

    def handle(self, *args, **options):
        import os
        from django.conf import settings
        json_path = os.path.join(settings.BASE_DIR.parent, 'mumbai_suburban_timetable_trackease.json')
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            self.stderr.write(f"Failed to load JSON: {e}")
            return
            
        station_master = data.get('station_master', {})
        service_samples = data.get('service_samples', [])
        
        # 1. Import Stations
        self.stdout.write("Importing Stations...")
        stations_created = 0
        stations_updated = 0
        
        station_cache = {}
        with transaction.atomic():
            for line_name, stations_list in station_master.items():
                for code, name in stations_list:
                    stn, created = Station.objects.update_or_create(
                        code=code.upper(),
                        defaults={'name': name}
                    )
                    station_cache[code.upper()] = stn
                    if created:
                        stations_created += 1
                    else:
                        stations_updated += 1
                        
        # 2. Import Services
        self.stdout.write("Importing Services...")
        services_created = 0
        services_updated = 0
        routes_created = 0
        route_stations_created = 0
        skipped = 0
        invalid = 0
        
        def parse_time(time_str):
            if not time_str or time_str == "NOT_SPECIFIED_IN_SOURCE":
                return None
            try:
                # Expecting HH:MM
                return datetime.datetime.strptime(time_str.strip(), '%H:%M').time()
            except ValueError:
                return None

        with transaction.atomic():
            for s in service_samples:
                num = s.get('service_number')
                name = s.get('service_name')
                ttype = s.get('service_type')
                origin = s.get('origin')
                dest = s.get('destination')
                dep = parse_time(s.get('origin_departure'))
                arr = parse_time(s.get('destination_arrival'))
                r_days = s.get('running_days')
                
                if not num or not origin or not dest:
                    invalid += 1
                    continue
                    
                if origin not in station_cache or dest not in station_cache:
                    self.stderr.write(f"Skipping service {num}: Origin or Dest station missing.")
                    skipped += 1
                    continue
                
                # Check for completeness
                stops = s.get('stops') or s.get('route') or []
                
                # A timetable is complete ONLY if there are intermediate stops AND
                # every stop has at least a departure_time or arrival_time.
                is_complete = False
                if len(stops) > 2:
                    is_complete = True
                    for stop in stops:
                        if not stop.get('arrival_time') and not stop.get('departure_time'):
                            is_complete = False
                            break
                
                # Train
                train, t_created = Train.objects.update_or_create(
                    number=num,
                    defaults={
                        'name': name or f"Train {num}",
                        'train_type': ttype or 'LOCAL',
                        'source': station_cache[origin],
                        'destination': station_cache[dest],
                        'running_days': {'raw': r_days, 'timetable_complete': is_complete} 
                    }
                )
                if t_created:
                    services_created += 1
                else:
                    services_updated += 1
                    
                # Route
                route, r_created = Route.objects.get_or_create(
                    train=train,
                    defaults={'name': f"{origin} to {dest}"}
                )
                if r_created:
                    routes_created += 1
                    
                # RouteStations
                RouteStation.objects.filter(route=route).delete()
                
                if is_complete:
                    seq = 1
                    rs_list = []
                    for stop in stops:
                        stn_code = stop.get('station_code')
                        if stn_code not in station_cache:
                            continue
                        
                        arr_t = parse_time(stop.get('arrival_time'))
                        dep_t = parse_time(stop.get('departure_time'))
                        dist = stop.get('distance_from_source') 
                        
                        rs_list.append(RouteStation(
                            route=route,
                            station=station_cache[stn_code],
                            sequence_number=seq,
                            distance_from_source=dist, # Will be None if not provided
                            arrival_time=arr_t,
                            departure_time=dep_t
                        ))
                        seq += 1
                    RouteStation.objects.bulk_create(rs_list)
                    route_stations_created += len(rs_list)
                else:
                    # Incomplete: Only origin and destination are known
                    RouteStation.objects.create(
                        route=route,
                        station=station_cache[origin],
                        sequence_number=1,
                        distance_from_source=None,
                        arrival_time=None,
                        departure_time=dep
                    )
                    RouteStation.objects.create(
                        route=route,
                        station=station_cache[dest],
                        sequence_number=2,
                        distance_from_source=None,
                        arrival_time=arr,
                        departure_time=None
                    )
                    route_stations_created += 2

        self.stdout.write("\n=== IMPORT SUMMARY ===")
        self.stdout.write(f"Stations created: {stations_created}")
        self.stdout.write(f"Stations updated: {stations_updated}")
        self.stdout.write(f"Services created: {services_created}")
        self.stdout.write(f"Services updated: {services_updated}")
        self.stdout.write(f"Routes created: {routes_created}")
        self.stdout.write(f"RouteStations created: {route_stations_created}")
        self.stdout.write(f"Schedules created: {services_created}")
        self.stdout.write(f"Skipped records: {skipped}")
        self.stdout.write(f"Invalid records: {invalid}")
