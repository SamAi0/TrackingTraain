import datetime
from trains.models import Train

class RailwayTrackingService:
    @staticmethod
    def get_live_status(train_number):
        """
        DATABASE-DRIVEN MOCK TRACKING PROVIDER.
        Fetches the real route from MySQL and simulates the train position.
        """
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        
        try:
            train = Train.objects.get(number=train_number)
            if not hasattr(train, 'route'):
                raise ValueError("Route not found for this train.")
            
            stations = list(train.route.stations.all().select_related('station').order_by('sequence_number'))
            if not stations:
                raise ValueError("No stations found in route.")
                
            # Simulate "Current" station as the middle of the route for demo purposes
            current_index = len(stations) // 2
            
            route_timeline = []
            for idx, rs in enumerate(stations):
                if idx < current_index:
                    state = 'COMPLETED'
                elif idx == current_index:
                    state = 'CURRENT'
                else:
                    state = 'UPCOMING'
                    
                route_timeline.append({
                    'station_code': rs.station.code,
                    'station_name': rs.station.name,
                    'status': state,
                    'distance': rs.distance_from_source,
                    'lat': rs.station.latitude or 0,
                    'lng': rs.station.longitude or 0
                })
                
            current_rs = stations[current_index]
            next_rs = stations[current_index + 1] if current_index + 1 < len(stations) else current_rs
            prev_rs = stations[current_index - 1] if current_index > 0 else current_rs

            return {
                "train_number": train.number,
                "train_name": train.name,
                "running_status": "ON_TIME",
                "current_station": f"{current_rs.station.name} ({current_rs.station.code})",
                "next_station": f"{next_rs.station.name} ({next_rs.station.code})",
                "delay_minutes": 0,
                "expected_arrival": "06:45 PM",
                "coordinates": {
                    "lat": current_rs.station.latitude or 21.2049,
                    "lng": current_rs.station.longitude or 72.8407
                },
                "last_updated": current_time,
                "route_timeline": route_timeline
            }
            
        except (Train.DoesNotExist, ValueError) as e:
            # Fallback if train not in DB or missing route
            return {
                "error": str(e) if isinstance(e, ValueError) else "Train not found in mock database.",
                "train_number": train_number,
                "train_name": f"Unknown {train_number}",
                "running_status": "N/A",
                "current_station": "N/A",
                "next_station": "N/A",
                "coordinates": {"lat": 23.2599, "lng": 77.4126},
                "route_timeline": []
            }
