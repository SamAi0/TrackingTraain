import logging
from .base_service import BaseRailwayService
from .response_normalizer import ResponseNormalizer
from ..exceptions import RailwayAPIException
from routes.models import Route

logger = logging.getLogger(__name__)

class ScheduleService(BaseRailwayService):
    @classmethod
    def get_schedule(cls, train_number, is_v2=True):
        if not train_number:
            return ResponseNormalizer.error("train_number is required", error_code="INVALID_REQUEST")
            
        endpoint = "/api/v1/getTrainSchedule"
        
        try:
            raw_data = cls.request(endpoint, params={"trainNo": train_number})
            
            # Normalize response to a common format
            schedule_data = {
                "train_number": train_number,
                "train_name": "",
                "source": "",
                "destination": "",
                "stations": []
            }
            
            data_dict = raw_data.get("data", {}) if isinstance(raw_data, dict) else {}
            
            if "trainName" in data_dict:
                schedule_data["train_name"] = data_dict["trainName"]
                
            stations_list = data_dict.get("route", [])
            
            for st in stations_list:
                schedule_data["stations"].append({
                    "station_code": st.get("stationCode", ""),
                    "station_name": st.get("stationName", ""),
                    "arrival_time": st.get("arrivalTime", ""),
                    "departure_time": st.get("departureTime", ""),
                    "halt_time": st.get("haltTime", ""),
                    "distance": st.get("distance", 0),
                    "day_count": st.get("dayCount", 1),
                    "sequence_number": st.get("stnSerialNumber", 0)
                })
                
            return ResponseNormalizer.normalize(schedule_data, source="external_api")
            
        except RailwayAPIException as e:
            logger.warning(f"External API {endpoint} failed: {e.message}. Falling back to DB.")
            return cls._fallback_schedule(train_number)
        except Exception as e:
            logger.error(f"Unexpected error in {endpoint}: {str(e)}")
            return cls._fallback_schedule(train_number)

    @classmethod
    def _fallback_schedule(cls, train_number):
        try:
            route = Route.objects.get(train__number=train_number)
            
            schedule_data = {
                "train_number": route.train.number,
                "train_name": route.train.name,
                "source": route.train.source.code,
                "destination": route.train.destination.code,
                "stations": []
            }
            
            for rs in route.stations.all().select_related('station').order_by('sequence_number'):
                schedule_data["stations"].append({
                    "station_code": rs.station.code,
                    "station_name": rs.station.name,
                    "arrival_time": rs.arrival_time.strftime("%H:%M") if rs.arrival_time else "00:00",
                    "departure_time": rs.departure_time.strftime("%H:%M") if rs.departure_time else "00:00",
                    "halt_time": "-",
                    "distance": rs.distance_from_source or 0,
                    "day_count": rs.journey_day,
                    "sequence_number": rs.sequence_number
                })
                
            return ResponseNormalizer.normalize(schedule_data, source="local_database")
            
        except Route.DoesNotExist:
            return ResponseNormalizer.error("Schedule not found in local database", source="local_database")
