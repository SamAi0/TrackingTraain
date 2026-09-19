import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from stations.models import Station
from trains.models import Train
from routes.models import Route, RouteStation
from datetime import datetime

class Command(BaseCommand):
    help = 'Load railway stations and trains into the database'

    def handle(self, *args, **kwargs):
        BASE_DIR = settings.BASE_DIR.parent
        STATIONS_FILE = os.path.join(BASE_DIR, "stations.json")
        TRAINS_FILE = os.path.join(BASE_DIR, "trains.json")

        self.stdout.write("Loading datasets...")
        with open(STATIONS_FILE, "r", encoding="utf-8") as f:
            stations_data = json.load(f)
        
        with open(TRAINS_FILE, "r", encoding="utf-8") as f:
            trains_data = json.load(f)

        self.stdout.write("Processing stations...")
        
        # We will load ALL stations to avoid broken ForeignKeys for trains that start/end outside Maharashtra
        station_objects = []
        maharashtra_codes = set()
        
        existing_stations = set(Station.objects.values_list('code', flat=True))
        
        for s in stations_data:
            code = s.get("code")
            if not code or code in existing_stations:
                if s.get("state", "").lower() == "maharashtra":
                    maharashtra_codes.add(code)
                continue
                
            state = s.get("state", "")
            if state.lower() == "maharashtra":
                maharashtra_codes.add(code)
                
            coords = s.get("coordinates", {})
            lat = coords.get("latitude")
            lon = coords.get("longitude")
            
            station_objects.append(Station(
                code=code,
                name=s.get("name", "")[:100],
                city=s.get("address", "")[:100],
                state=state[:100],
                latitude=lat if isinstance(lat, (float, int)) else None,
                longitude=lon if isinstance(lon, (float, int)) else None,
            ))
            
        Station.objects.bulk_create(station_objects, batch_size=1000, ignore_conflicts=True)
        self.stdout.write(f"Created {len(station_objects)} stations. Maharashtra stations: {len(maharashtra_codes)}")

        # Reload existing stations for fast lookup
        all_station_codes = set(Station.objects.values_list('code', flat=True))

        self.stdout.write("Processing trains (Filtering for Maharashtra)...")
        train_objects = []
        train_codes = set()
        
        existing_trains = set(Train.objects.values_list('number', flat=True))
        
        valid_train_data = []
        
        for t in trains_data:
            t_num = t.get("trainNumber")
            if not t_num or t_num in existing_trains or t_num in train_codes:
                continue
                
            # Check if train touches Maharashtra
            route = t.get("completeOrderedRoute", [])
            touches_mh = any(stop.get("stationCode") in maharashtra_codes for stop in route)
            
            if not touches_mh:
                continue
                
            src_code = t.get("source", {}).get("code")
            dst_code = t.get("destination", {}).get("code")
            
            if src_code not in all_station_codes or dst_code not in all_station_codes:
                continue
                
            # Create Train
            train_objects.append(Train(
                number=t_num,
                name=t.get("trainName", "")[:100],
                train_type=t.get("type", "EXPRESS")[:20],
                source_id=src_code,
                destination_id=dst_code,
                running_days=t.get("runningDays", {})
            ))
            train_codes.add(t_num)
            valid_train_data.append(t)
            
        Train.objects.bulk_create(train_objects, batch_size=1000, ignore_conflicts=True)
        self.stdout.write(f"Created {len(train_objects)} trains.")

        self.stdout.write("Processing routes and route stations...")
        route_objects = []
        for t_num in train_codes:
            route_objects.append(Route(train_id=t_num))
            
        Route.objects.bulk_create(route_objects, batch_size=1000, ignore_conflicts=True)
        
        # Create route stations
        route_station_objects = []
        routes_map = {r.train_id: r.id for r in Route.objects.filter(train_id__in=train_codes)}
        
        def parse_time(t_str):
            if not t_str or t_str == "--:--":
                return None
            try:
                # Assuming format is HH:MM
                return datetime.strptime(t_str.strip(), "%H:%M").time()
            except:
                return None
        
        for t in valid_train_data:
            t_num = t.get("trainNumber")
            route_id = routes_map.get(t_num)
            if not route_id:
                continue
                
            stops = t.get("completeOrderedRoute", [])
            for stop in stops:
                stn_code = stop.get("stationCode")
                if stn_code not in all_station_codes:
                    continue
                    
                seq = stop.get("sequence")
                if seq is None:
                    continue
                    
                dist = stop.get("distance", 0)
                try:
                    dist = int(float(dist))
                except:
                    dist = 0
                    
                route_station_objects.append(RouteStation(
                    route_id=route_id,
                    station_id=stn_code,
                    sequence_number=int(seq),
                    distance_from_source=dist,
                    arrival_time=parse_time(stop.get("arrivalTime")),
                    departure_time=parse_time(stop.get("departureTime")),
                    journey_day=int(stop.get("journeyDay", 1))
                ))
                
        self.stdout.write(f"Creating {len(route_station_objects)} route stations...")
        RouteStation.objects.bulk_create(route_station_objects, batch_size=5000, ignore_conflicts=True)
        self.stdout.write("Done!")
