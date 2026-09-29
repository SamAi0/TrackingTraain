import logging
import datetime
from .base_service import BaseRailwayService
from .response_normalizer import ResponseNormalizer
from ..exceptions import RailwayAPIException
from trains.models import Train

logger = logging.getLogger(__name__)

class TrackingService(BaseRailwayService):
    @classmethod
    def get_live_status(cls, train_number, date=None, demo_delay=0):
        if not train_number:
            return ResponseNormalizer.error("train_number is required", error_code="INVALID_REQUEST")
            
        params = {"trainNo": train_number}
        if date:
            params["startDay"] = date
            
        try:
            raw_data = cls.request("/api/v1/liveTrainStatus", params=params)
            
            data_dict = raw_data.get("data", {}) if isinstance(raw_data, dict) else {}
            
            # If API indicates train doesn't run today or error
            if not data_dict or data_dict.get("success") is False:
                raise RailwayAPIException("Train live status unavailable", "DATA_UNAVAILABLE", 404)
            
            status_data = {
                "train_number": data_dict.get("trainNumber", train_number),
                "train_name": data_dict.get("trainName", ""),
                "running_status": "DELAYED" if data_dict.get("delay", 0) > 0 else "ON_TIME",
                "current_station": data_dict.get("currentStationName", ""),
                "next_station": data_dict.get("nextStationName", ""),
                "delay_minutes": data_dict.get("delay", 0),
                "expected_arrival": data_dict.get("eta", ""),
                "expected_departure": data_dict.get("etd", ""),
                "coordinates": {
                    "lat": 0,  # Live coordinates might not be provided
                    "lng": 0
                },
                "last_updated": data_dict.get("updateTime", datetime.datetime.now().strftime("%I:%M %p")),
                "route_timeline": []
            }
            
            for st in data_dict.get("upcomingStations", []):
                status_data["route_timeline"].append({
                    "station_code": st.get("stationCode", ""),
                    "station_name": st.get("stationName", ""),
                    "status": "UPCOMING",
                    "distance": st.get("distance", 0)
                })
                
            return ResponseNormalizer.normalize(status_data, source="external_api", is_live=True)
            
        except RailwayAPIException as e:
            logger.warning(f"External API live status failed: {e.message}. Falling back to mock.")
            return cls._fallback_live_status(train_number, demo_delay)
        except Exception as e:
            logger.error(f"Unexpected error in live status: {str(e)}")
            return cls._fallback_live_status(train_number, demo_delay)

    @classmethod
    def _fallback_live_status(cls, train_number, demo_delay=0):
        # Local TrackEase DB fallback (simulation)
        from trains.models import Train
        try:
            train = Train.objects.get(number=train_number)
            if not hasattr(train, 'route'):
                return ResponseNormalizer.error('Route not found for this train.', source="local_mock")
                
            stations = list(train.route.stations.select_related('station').order_by('sequence_number'))
            if not stations:
                return ResponseNormalizer.error('No stations on this route.', source="local_mock")
                
            now = datetime.datetime.now()
            today = datetime.date.today()
            source_station = stations[0]
            
            if source_station.departure_time:
                base_start_time = source_station.departure_time
            elif source_station.arrival_time:
                base_start_time = source_station.arrival_time
            else:
                base_start_time = datetime.time(0, 0)
                
            base_start_dt = datetime.datetime.combine(today, base_start_time)
            delay_td = datetime.timedelta(minutes=demo_delay)
            
            route_details = []
            for idx, rs in enumerate(stations):
                day_offset = (rs.journey_day or 1) - (source_station.journey_day or 1)
                if rs.arrival_time:
                    arr_dt = datetime.datetime.combine(today, rs.arrival_time) + datetime.timedelta(days=day_offset)
                    if idx > 0 and arr_dt < route_details[idx-1]['sim_dep_dt']:
                        arr_dt += datetime.timedelta(days=1)
                else:
                    arr_dt = route_details[idx-1]['sim_dep_dt'] if idx > 0 else base_start_dt
                
                if rs.departure_time:
                    dep_dt = datetime.datetime.combine(arr_dt.date(), rs.departure_time)
                    if dep_dt < arr_dt:
                        dep_dt += datetime.timedelta(days=1)
                else:
                    dep_dt = arr_dt
                    
                route_details.append({
                    'rs': rs,
                    'sim_arr_dt': arr_dt,
                    'sim_dep_dt': dep_dt,
                    'exp_arr_dt': arr_dt + delay_td,
                    'exp_dep_dt': dep_dt + delay_td,
                    'is_first': idx == 0,
                    'is_last': idx == len(stations) - 1,
                    'index': idx
                })
            
            current_state = 'NOT_STARTED'
            current_idx = 0
            actual_end_time = route_details[-1]['exp_arr_dt']
            
            if now < route_details[0]['exp_dep_dt']:
                pass
            elif now > actual_end_time:
                current_state = 'COMPLETED'
                current_idx = len(stations) - 1
            else:
                for i in range(len(route_details)):
                    r = route_details[i]
                    if r['exp_arr_dt'] <= now <= r['exp_dep_dt']:
                        current_state = 'AT_STATION'
                        current_idx = i
                        break
                    if i < len(route_details) - 1:
                        if r['exp_dep_dt'] < now < route_details[i+1]['exp_arr_dt']:
                            current_state = 'IN_TRANSIT'
                            current_idx = i + 1
                            break
                            
            if current_state == 'NOT_STARTED':
                prev_stn = None
                curr_stn = stations[0]
                next_stn = stations[1] if len(stations) > 1 else None
                progress_pct = 0.0
                status_msg = 'DELAYED' if demo_delay > 0 else 'ON_TIME'
            elif current_state == 'COMPLETED':
                prev_stn = stations[-2] if len(stations) > 1 else None
                curr_stn = stations[-1]
                next_stn = None
                progress_pct = 100.0
                status_msg = 'COMPLETED'
            else:
                curr_stn = stations[current_idx]
                prev_stn = stations[current_idx - 1] if current_idx > 0 else None
                next_stn = stations[current_idx + 1] if current_idx < len(stations) - 1 else None
                progress_pct = round((current_idx / (len(stations) - 1)) * 100, 1) if len(stations) > 1 else 0
                if current_state == 'AT_STATION':
                    status_msg = 'HALTED' if demo_delay > 0 else 'ON_TIME'
                else:
                    status_msg = 'DELAYED' if demo_delay > 0 else 'ON_TIME'
            
            formatted_route = []
            for i, r in enumerate(route_details):
                if i < current_idx:
                    route_status = 'COMPLETED'
                elif i == current_idx:
                    route_status = 'CURRENT'
                else:
                    route_status = 'UPCOMING'
                    
                formatted_route.append({
                    'station_name': r['rs'].station.name,
                    'station_code': r['rs'].station.code,
                    'sequence_number': r['rs'].sequence_number,
                    'status': route_status,
                    'arrival_time': r['rs'].arrival_time.strftime('%H:%M') if r['rs'].arrival_time else None,
                    'departure_time': r['rs'].departure_time.strftime('%H:%M') if r['rs'].departure_time else None,
                    'expected_arrival': r['exp_arr_dt'].strftime('%H:%M'),
                    'expected_departure': r['exp_dep_dt'].strftime('%H:%M'),
                    'latitude': r['rs'].station.latitude,
                    'longitude': r['rs'].station.longitude,
                    'day': r['rs'].journey_day
                })
                
            curr_r = route_details[current_idx]
            
            response_data = {
                'train_number': train.number,
                'train_name': train.name,
                'train_type': train.train_type,
                'running_status': status_msg,
                'delay_minutes': demo_delay,
                'previous_station': prev_stn.station.name if prev_stn else None,
                'current_station': curr_stn.station.name if curr_stn else None,
                'next_station': next_stn.station.name if next_stn else None,
                'expected_arrival': curr_r['exp_arr_dt'].strftime('%H:%M') if curr_r else None,
                'expected_departure': curr_r['exp_dep_dt'].strftime('%H:%M') if curr_r else None,
                'progress_percentage': progress_pct,
                'last_updated': now.isoformat(),
                'route_timeline': formatted_route,
                'coordinates': {'lat': curr_stn.station.latitude, 'lng': curr_stn.station.longitude} if curr_stn and curr_stn.station.latitude else {'lat': 0, 'lng': 0},
                'simulated': True,
                'is_live': False
            }
            return ResponseNormalizer.normalize(response_data, source="local_mock", is_live=False, simulated=True)
            
        except Train.DoesNotExist:
            return ResponseNormalizer.error('Train not found locally.', source="local_mock")
