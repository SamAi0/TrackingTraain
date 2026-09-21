import logging
from .base_service import BaseRailwayService
from .response_normalizer import ResponseNormalizer
from ..exceptions import RailwayAPIException

logger = logging.getLogger(__name__)

class AvailabilityService(BaseRailwayService):
    @classmethod
    def check(cls, train_number, from_stn, to_stn, date, class_code, quota="GN", is_v2=True):
        if not all([train_number, from_stn, to_stn, date, class_code]):
            return ResponseNormalizer.error("Missing required parameters", error_code="INVALID_REQUEST")
            
        endpoint = "checkSeatAvailabilityV2" if is_v2 else "checkSeatAvailability"
        params = {
            "trainNo": train_number,
            "fromStationCode": from_stn,
            "toStationCode": to_stn,
            "dateOfJourney": date,
            "journeyClass": class_code,
            "quota": quota
        }
        
        try:
            raw_data = cls.request(endpoint, params=params)
            data_dict = raw_data.get("data", {}) if isinstance(raw_data, dict) else {}
            
            avail_data = {
                "train_number": train_number,
                "class_code": class_code,
                "availability": []
            }
            
            # RapidAPI returns list of availability objects
            avail_list = data_dict.get("availability", []) if is_v2 else (raw_data.get("data") if isinstance(raw_data.get("data"), list) else [])
            
            # Normalizing common structure
            if avail_list:
                for item in avail_list:
                    avail_data["availability"].append({
                        "date": item.get("date", ""),
                        "status": item.get("currentStatus", item.get("status", "")),
                        "fare": item.get("fare", 0),
                        "confirm_probability": item.get("confirmProbability", "")
                    })
            else:
                # Some API variants return direct object
                avail_data["availability"].append({
                    "date": date,
                    "status": data_dict.get("currentStatus", "NOT AVAILABLE"),
                    "fare": data_dict.get("totalFare", 0),
                    "confirm_probability": data_dict.get("confirmProbability", "")
                })
                
            return ResponseNormalizer.normalize(avail_data, source="external_api")
            
        except RailwayAPIException as e:
            logger.warning(f"External API {endpoint} failed: {e.message}. Falling back to demo.")
            return cls._fallback_availability(train_number, date, class_code)
        except Exception as e:
            logger.error(f"Unexpected error in {endpoint}: {str(e)}")
            return cls._fallback_availability(train_number, date, class_code)

    @classmethod
    def _fallback_availability(cls, train_number, date, class_code):
        # Local mock availability
        import random
        statuses = ["AVAILABLE", "RAC", "WL", "NOT AVAILABLE"]
        
        avail_data = {
            "train_number": train_number,
            "class_code": class_code,
            "availability": [{
                "date": date,
                "status": random.choice(statuses) + ("" if statuses[0] == "NOT AVAILABLE" else f" {random.randint(1, 50)}"),
                "fare": 0,  # Handled by FareService fallback
                "confirm_probability": "High"
            }]
        }
        return ResponseNormalizer.normalize(
            avail_data, 
            source="local_mock",
            simulated=True
        )
