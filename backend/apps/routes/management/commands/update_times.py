import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from stations.models import Station
from trains.models import Train
from routes.models import Route, RouteStation
from datetime import datetime

class Command(BaseCommand):
    help = 'Update time fields for existing railway routes in Maharashtra'

    def handle(self, *args, **kwargs):
        BASE_DIR = settings.BASE_DIR.parent
        STATIONS_FILE = os.path.join(BASE_DIR, "stations.json")
        TRAINS_FILE = os.path.join(BASE_DIR, "trains.json")

        self.stdout.write("Loading datasets...")
        with open(STATIONS_FILE, "r", encoding="utf-8") as f:
            stations_data = json.load(f)
        with open(TRAINS_FILE, "r", encoding="utf-8") as f:
            trains_data = json.load(f)

        maharashtra_codes = set()
        for s in stations_data:
            if s.get("state", "").lower() == "maharashtra":
                maharashtra_codes.add(s.get("code"))

        self.stdout.write("Finding relevant trains...")
        
        valid_trains = []
        for t in trains_data:
            route = t.get("completeOrderedRoute", [])
            if any(stop.get("stationCode") in maharashtra_codes for stop in route):
                valid_trains.append(t)
                
        self.stdout.write(f"Found {len(valid_trains)} trains touching Maharashtra.")

        def parse_time(t_str):
            if not t_str or t_str == "--:--":
                return None
            try:
                return datetime.strptime(t_str.strip(), "%H:%M").time()
            except:
                return None

        # Process trains
        trains_to_update = []
        route_stations_to_update = []
        
        routes = {r.train_id: r.id for r in Route.objects.all()}
        
        # Load route stations into memory for fast lookup
        self.stdout.write("Loading existing route stations...")
        route_stations_dict = {(rs.route_id, rs.station_id): rs for rs in RouteStation.objects.all()}
        train_objects = {t.number: t for t in Train.objects.all()}
        
        self.stdout.write("Updating objects in memory...")
        for t in valid_trains:
            t_num = t.get("trainNumber")
            train_obj = train_objects.get(t_num)
            if train_obj:
                train_obj.running_days = t.get("runningDays", {})
                trains_to_update.append(train_obj)
            
            route_id = routes.get(t_num)
            if not route_id:
                continue
                
            for stop in t.get("completeOrderedRoute", []):
                stn_code = stop.get("stationCode")
                rs = route_stations_dict.get((route_id, stn_code))
                if rs:
                    rs.arrival_time = parse_time(stop.get("arrivalTime"))
                    rs.departure_time = parse_time(stop.get("departureTime"))
                    rs.journey_day = int(stop.get("journeyDay", 1))
                    route_stations_to_update.append(rs)

        self.stdout.write(f"Updating DB ({len(trains_to_update)} trains, {len(route_stations_to_update)} route stations)...")
        if trains_to_update:
            Train.objects.bulk_update(trains_to_update, ['running_days'], batch_size=1000)
            
        if route_stations_to_update:
            RouteStation.objects.bulk_update(route_stations_to_update, ['arrival_time', 'departure_time', 'journey_day'], batch_size=5000)

        self.stdout.write("Done!")
