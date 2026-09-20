import sys
import datetime
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from stations.models import Station
from trains.models import Train
from routes.models import Route, RouteStation

class Command(BaseCommand):
    help = 'Imports a train schedule from RapidAPI and populates local database.'

    def add_arguments(self, parser):
        parser.add_argument('train_number', type=str)

    def handle(self, *args, **options):
        train_number = options['train_number']
        
        headers = {
            'x-rapidapi-key': settings.RAPIDAPI_KEY,
            'x-rapidapi-host': settings.RAPIDAPI_HOST
        }
        
        self.stdout.write(f"Fetching data for train {train_number} from RapidAPI...")
        
        try:
            res = requests.get(f"https://{settings.RAPIDAPI_HOST}/api/v1/getTrainSchedule", headers=headers, params={'trainNo': train_number})
            res.raise_for_status()
            response_json = res.json()
        except Exception as e:
            self.stderr.write(f"Error fetching from RapidAPI: {e}")
            return
            
        if not response_json.get('status') or 'data' not in response_json:
            self.stderr.write(f"Invalid or failed response from RapidAPI: {response_json}")
            return
            
        data = response_json['data']
        route_data = data.get('route', [])
        
        if not route_data:
            self.stderr.write("No route data found for this train.")
            return
            
        # 1. Create or update Train
        train_name = data.get('trainName', f'Train {train_number}')
        train_type = data.get('trainType', 'UNKNOWN')
        
        source_code = route_data[0].get('station_code')
        dest_code = route_data[-1].get('station_code')
        
        # Helper to convert sta_min / std_min to time
        def minutes_to_time(minutes):
            if minutes is None:
                return None
            try:
                m = int(minutes)
                # handle if minutes > 1440 (next day)
                m = m % 1440
                hours = m // 60
                mins = m % 60
                return datetime.time(hours, mins)
            except:
                return None
        
        # 2. Process all stations first
        self.stdout.write("Processing stations...")
        for stop in route_data:
            code = stop.get('station_code')
            name = stop.get('station_name')
            if code and name:
                # Get or create the station based on code. Do not create duplicates.
                Station.objects.get_or_create(code=code, defaults={'name': name})
                
        # Get source and dest station objects
        try:
            source_stn = Station.objects.get(code=source_code)
            dest_stn = Station.objects.get(code=dest_code)
        except Station.DoesNotExist:
            self.stderr.write("Source or destination station failed to create.")
            return

        # 3. Create or update Train
        run_days = data.get('runDays', {})
        
        train, created = Train.objects.get_or_create(
            number=train_number,
            defaults={
                'name': train_name,
                'train_type': train_type,
                'source': source_stn,
                'destination': dest_stn,
                'running_days': run_days
            }
        )
        if not created:
            train.name = train_name
            train.train_type = train_type
            train.source = source_stn
            train.destination = dest_stn
            train.running_days = run_days
            train.save()
            self.stdout.write(f"Updated train {train_number}")
        else:
            self.stdout.write(f"Created train {train_number}")
            
        # 5. Route
        route, created = Route.objects.get_or_create(
            train=train,
            defaults={'name': f"{source_code} to {dest_code}"}
        )
        
        # 6. RouteStation
        self.stdout.write("Populating RouteStation sequence...")
        
        # We delete existing route stations for this route to avoid stale data
        RouteStation.objects.filter(route=route).delete()
        
        rs_list = []
        for idx, stop in enumerate(route_data, start=1):
            code = stop.get('station_code')
            dist = stop.get('distance_from_source', 0)
            sta_min = stop.get('sta_min')
            std_min = stop.get('std_min')
            
            # Arrival time
            arr_time = minutes_to_time(sta_min)
            # Departure time
            dep_time = minutes_to_time(std_min)
            
            try:
                stn = Station.objects.get(code=code)
                rs_list.append(RouteStation(
                    route=route,
                    station=stn,
                    sequence_number=idx,
                    distance_from_source=dist,
                    arrival_time=arr_time,
                    departure_time=dep_time,
                    journey_day=(1 + (int(sta_min) // 1440) if sta_min is not None else 1)
                ))
            except Station.DoesNotExist:
                continue
                
        RouteStation.objects.bulk_create(rs_list)
        
        self.stdout.write(self.style.SUCCESS(f"Successfully imported {len(rs_list)} RouteStation records for Train {train_number}."))
