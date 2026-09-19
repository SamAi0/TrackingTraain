import json
import os
import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction

# Import models
from stations.models import Station
from trains.models import Train
from routes.models import Route, RouteStation
from schedules.models import Schedule
from bookings.models import Booking
from pnr.models import PNR

class Command(BaseCommand):
    help = 'Imports DataMeet Indian Railways datasets (stations, trains, schedules) into TrackEase database.'

    def handle(self, *args, **kwargs):
        project_root = settings.BASE_DIR.parent
        stations_path = os.path.join(project_root, 'stations.json')
        trains_path = os.path.join(project_root, 'trains.json')
        schedules_path = os.path.join(project_root, 'schedules.json')

        if not all(map(os.path.exists, [stations_path, trains_path, schedules_path])):
            self.stdout.write(self.style.ERROR('Dataset files not found in project root!'))
            return

        with transaction.atomic():
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            Booking.objects.all().delete()
            PNR.objects.all().delete()
            Schedule.objects.all().delete()
            RouteStation.objects.all().delete()
            Route.objects.all().delete()
            Train.objects.all().delete()
            Station.objects.all().delete()

            # 1. Import Stations
            self.stdout.write(self.style.SUCCESS('Importing Stations...'))
            with open(stations_path, 'r', encoding='utf-8') as f:
                stations_data = json.load(f)
            
            station_objs = []
            station_codes = set()
            for feat in stations_data.get('features', []):
                props = feat.get('properties', {})
                geom = feat.get('geometry')
                
                code = props.get('code')
                name = props.get('name')
                
                if not code or not name:
                    continue
                    
                code = str(code)[:10]
                if code in station_codes:
                    continue
                
                lat, lng = None, None
                if geom and geom.get('coordinates'):
                    # GeoJSON is [longitude, latitude]
                    lng, lat = geom['coordinates']
                
                station_objs.append(Station(
                    code=code,
                    name=name[:100],
                    state=(props.get('state', 'Unknown') or 'Unknown')[:100],
                    city=(props.get('address', 'Unknown') or 'Unknown')[:100],
                    latitude=lat,
                    longitude=lng
                ))
                station_codes.add(code)
            
            Station.objects.bulk_create(station_objs, batch_size=1000)
            self.stdout.write(f"Imported {len(station_objs)} stations.")
            
            # 2. Import Trains
            self.stdout.write(self.style.SUCCESS('Importing Trains...'))
            with open(trains_path, 'r', encoding='utf-8') as f:
                trains_data = json.load(f)
                
            train_objs = []
            train_numbers = set()
            for feat in trains_data.get('features', []):
                props = feat.get('properties', {})
                
                number = props.get('number')
                name = props.get('name')
                
                if not number or not name:
                    continue
                    
                number = str(number)[:10]
                if number in train_numbers:
                    continue
                    
                source_code = str(props.get('from_station_code', ''))[:10]
                dest_code = str(props.get('to_station_code', ''))[:10]
                
                if source_code not in station_codes or dest_code not in station_codes:
                    continue
                
                train_objs.append(Train(
                    number=number,
                    name=name[:100],
                    train_type=(props.get('type', 'EXPRESS') or 'EXPRESS')[:20],
                    source_id=source_code,
                    destination_id=dest_code
                ))
                train_numbers.add(number)
                
            Train.objects.bulk_create(train_objs, batch_size=1000)
            self.stdout.write(f"Imported {len(train_objs)} trains.")
            
            # 3. Import Routes & Schedules
            self.stdout.write(self.style.SUCCESS('Importing Routes & Schedules... (This may take a minute)'))
            with open(schedules_path, 'r', encoding='utf-8') as f:
                schedules_data = json.load(f)
                
            # Group by train number
            from collections import defaultdict
            train_schedules = defaultdict(list)
            for row in schedules_data:
                t_num = str(row.get('train_number'))
                s_code = row.get('station_code')
                if t_num in train_numbers and s_code in station_codes:
                    train_schedules[t_num].append(row)
            
            route_objs = []
            route_station_objs = []
            schedule_objs = []
            
            def parse_time(time_str):
                if not time_str or time_str == 'None':
                    return None
                try:
                    return datetime.datetime.strptime(time_str, '%H:%M:%S').time()
                except ValueError:
                    return None

            for t_num, stops in train_schedules.items():
                route = Route.objects.create(train_id=t_num)
                
                seen_stations = set()
                seq_idx = 1
                for stop in stops:
                    s_code = stop['station_code']
                    if s_code in seen_stations:
                        continue
                    seen_stations.add(s_code)
                    
                    route_station_objs.append(RouteStation(
                        route=route,
                        station_id=s_code,
                        sequence_number=seq_idx,
                        distance_from_source=0 # No distance provided in schedule.json per stop
                    ))
                    
                    schedule_objs.append(Schedule(
                        train_id=t_num,
                        station_id=s_code,
                        arrival_time=parse_time(stop.get('arrival')),
                        departure_time=parse_time(stop.get('departure')),
                        day_count=stop.get('day') if str(stop.get('day')).isdigit() else 1
                    ))
                    seq_idx += 1
            
            RouteStation.objects.bulk_create(route_station_objs, batch_size=5000)
            Schedule.objects.bulk_create(schedule_objs, batch_size=5000)
            
            self.stdout.write(f"Imported routes for {len(train_schedules)} trains.")
            self.stdout.write(f"Imported {len(route_station_objs)} route stations.")
            self.stdout.write(f"Imported {len(schedule_objs)} schedules.")
            
        self.stdout.write(self.style.SUCCESS('DataMeet Import Complete! 🎉'))
