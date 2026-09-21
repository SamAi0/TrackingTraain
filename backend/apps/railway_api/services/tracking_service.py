import logging
import datetime
from .base_service import BaseRailwayService
from .response_normalizer import ResponseNormalizer
from ..exceptions import RailwayAPIException
from trains.models import Train

logger = logging.getLogger(__name__)

class TrackingService(BaseRailwayService):
    @classmethod
    def get_live_status(cls, train_number, date=None):
        if not train_number:
            return ResponseNormalizer.error("train_number is required", error_code="INVALID_REQUEST")
            
        params = {"trainNo": train_number}
        if date:
            params["startDay"] = date
            
        try:
            raw_data = cls.request("getTrainLiveStatus", params=params)
            
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
            return cls._fallback_live_status(train_number)
        except Exception as e:
            logger.error(f"Unexpected error in live status: {str(e)}")
            return cls._fallback_live_status(train_number)

    @classmethod
    def _fallback_live_status(cls, train_number):
        # We reuse the original DB-driven mock logic here
        from services.railway_api import RailwayTrackingService as OldService
        old_data = OldService.get_live_status(train_number)
        
        if "error" in old_data:
            return ResponseNormalizer.error(old_data["error"], source="local_mock")
            
        return ResponseNormalizer.normalize(
            old_data, 
            source="local_mock", 
            is_live=False, 
            simulated=True
        )
