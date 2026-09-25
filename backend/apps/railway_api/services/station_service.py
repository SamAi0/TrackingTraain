import logging
from django.db.models import Q
from .base_service import BaseRailwayService
from .response_normalizer import ResponseNormalizer
from ..exceptions import RailwayAPIException
from stations.models import Station

logger = logging.getLogger(__name__)

class StationService(BaseRailwayService):
    @classmethod
    def search_station(cls, query):
        if not query:
            return ResponseNormalizer.error("Query parameter is required", error_code="INVALID_REQUEST")
            
        try:
            # Try External API First
            raw_data = cls.request(f"/autocomplete/station/{query}")
            
            # Normalize RapidAPI response
            stations = []
            if isinstance(raw_data, dict) and "data" in raw_data:
                results = raw_data.get("data", [])
                for st in results:
                    stations.append({
                        "code": st.get("stationCode", ""),
                        "name": st.get("stationName", ""),
                        "city": st.get("city", ""),
                        "state": st.get("state", ""),
                    })
            elif isinstance(raw_data, list):
                for st in raw_data:
                    stations.append({
                        "code": st.get("stationCode", st.get("code", "")),
                        "name": st.get("stationName", st.get("name", "")),
                        "city": st.get("city", ""),
                        "state": st.get("state", ""),
                    })
            
            return ResponseNormalizer.normalize(stations, source="external_api")
            
        except RailwayAPIException as e:
            logger.warning(f"External API searchStation failed: {e.message}. Falling back to DB.")
            return cls._fallback_search_station(query)
        except Exception as e:
            logger.error(f"Unexpected error in searchStation: {str(e)}")
            return cls._fallback_search_station(query)
            
    @classmethod
    def _fallback_search_station(cls, query):
        """Fallback to existing local Station database"""
        stations = Station.objects.filter(
            Q(code__icontains=query) | 
            Q(name__icontains=query) | 
            Q(city__icontains=query)
        )[:10]
        
        results = []
        for st in stations:
            results.append({
                "code": st.code,
                "name": st.name,
                "city": st.city,
                "state": st.state,
                "lat": st.latitude,
                "lng": st.longitude
            })
            
        return ResponseNormalizer.normalize(
            results, 
            source="local_database", 
            simulated=False
        )

    @classmethod
    def get_trains(cls, station_code):
        if not station_code:
            return ResponseNormalizer.error("station_code is required", error_code="INVALID_REQUEST")
            
        try:
            raw_data = cls.request("/api/v3/getTrainsByStation", params={"stationCode": station_code})
            
            data_dict = raw_data.get("data", {}) if isinstance(raw_data, dict) else {}
            trains_list = data_dict.get("trains", []) if isinstance(data_dict, dict) else []
            if not trains_list and isinstance(raw_data.get("data"), list):
                trains_list = raw_data.get("data")
                
            trains = []
            for tr in trains_list:
                trains.append({
                    "number": tr.get("trainNumber", ""),
                    "name": tr.get("trainName", ""),
                    "source": tr.get("sourceStation", ""),
                    "destination": tr.get("destinationStation", ""),
                    "departure_time": tr.get("departureTime", ""),
                    "arrival_time": tr.get("arrivalTime", ""),
                    "type": tr.get("trainType", "EXPRESS")
                })
                
            return ResponseNormalizer.normalize(trains, source="external_api")
        except RailwayAPIException as e:
            logger.warning(f"External API getTrainsByStation failed: {e.message}. Falling back to DB.")
            return cls._fallback_trains_by_station(station_code)
        except Exception as e:
            logger.error(f"Unexpected error in getTrainsByStation: {str(e)}")
            return cls._fallback_trains_by_station(station_code)

    @classmethod
    def _fallback_trains_by_station(cls, station_code):
        from routes.models import RouteStation
        
        try:
            route_stations = RouteStation.objects.filter(station__code=station_code).select_related('route__train')[:20]
            trains = []
            for rs in route_stations:
                train = rs.route.train
                trains.append({
                    "number": train.number,
                    "name": train.name,
                    "source": train.source.code,
                    "destination": train.destination.code,
                    "departure_time": rs.departure_time.strftime("%H:%M") if rs.departure_time else "",
                    "arrival_time": rs.arrival_time.strftime("%H:%M") if rs.arrival_time else "",
                    "type": train.train_type
                })
            return ResponseNormalizer.normalize(trains, source="local_database")
        except Exception as e:
            logger.error(f"Fallback getTrainsByStation error: {str(e)}")
            return ResponseNormalizer.error("Failed to fetch trains locally", source="local_database")

    @classmethod
    def get_live(cls, station_code):
        if not station_code:
            return ResponseNormalizer.error("station_code is required", error_code="INVALID_REQUEST")
            
        try:
            raw_data = cls.request("/api/v3/getLiveStation", params={"stationCode": station_code, "hours": 2})
            
            data_dict = raw_data.get("data", {}) if isinstance(raw_data, dict) else {}
            trains_list = data_dict.get("trains", []) if isinstance(data_dict, dict) else []
            if not trains_list and isinstance(raw_data.get("data"), list):
                trains_list = raw_data.get("data")
                
            trains = []
            for tr in trains_list:
                trains.append({
                    "number": tr.get("trainNumber", ""),
                    "name": tr.get("trainName", ""),
                    "expected_arrival": tr.get("eta", ""),
                    "expected_departure": tr.get("etd", ""),
                    "delay": tr.get("delay", 0),
                    "platform": tr.get("platform", "")
                })
                
            return ResponseNormalizer.normalize(trains, source="external_api", is_live=True)
        except RailwayAPIException as e:
            logger.warning(f"External API getLiveStation failed: {e.message}. Falling back to mock.")
            return cls._fallback_live_station(station_code)
        except Exception as e:
            logger.error(f"Unexpected error in getLiveStation: {str(e)}")
            return cls._fallback_live_station(station_code)

    @classmethod
    def _fallback_live_station(cls, station_code):
        return ResponseNormalizer.normalize([], source="local_mock", is_live=False, simulated=True)
