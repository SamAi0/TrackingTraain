import logging
from .base_service import BaseRailwayService
from .response_normalizer import ResponseNormalizer
from ..exceptions import RailwayAPIException

logger = logging.getLogger(__name__)

class FareService(BaseRailwayService):
    @classmethod
    def get_fare(cls, train_number, from_stn, to_stn, quota="GN"):
        if not all([train_number, from_stn, to_stn]):
            return ResponseNormalizer.error("train_number, from_stn, to_stn are required", error_code="INVALID_REQUEST")
            
        params = {
            "trainNo": train_number,
            "fromStationCode": from_stn,
            "toStationCode": to_stn,
            "quota": quota
        }
        
        try:
            raw_data = cls.request("getFare", params=params)
            
            # Note: User mentioned 'GetFare' is deprecated, but maybe 'getFare' v3 is used?
            # Let's normalize assuming a common format or just fallback if it fails.
            data_dict = raw_data.get("data", {}) if isinstance(raw_data, dict) else {}
            
            fare_data = {
                "train_number": train_number,
                "source": from_stn,
                "destination": to_stn,
                "fares": []
            }
            
            fare_list = data_dict.get("fare", []) if isinstance(data_dict, dict) else []
            if not fare_list and isinstance(raw_data.get("data"), list):
                fare_list = raw_data.get("data")
                
            for fare in fare_list:
                fare_data["fares"].append({
                    "class_code": fare.get("journeyClass", ""),
                    "fare": fare.get("totalFare", 0)
                })
                
            if not fare_data["fares"]:
                raise RailwayAPIException("No fare data returned", "DATA_UNAVAILABLE", 404)
                
            return ResponseNormalizer.normalize(fare_data, source="external_api")
            
        except RailwayAPIException as e:
            logger.warning(f"External API getFare failed: {e.message}. Falling back to TrackEase FareRule.")
            return cls._fallback_fare(train_number, from_stn, to_stn)
        except Exception as e:
            logger.error(f"Unexpected error in getFare: {str(e)}")
            return cls._fallback_fare(train_number, from_stn, to_stn)

    @classmethod
    def _fallback_fare(cls, train_number, from_stn, to_stn):
        from routes.models import RouteStation
        from bookings.models import FareRule
        
        try:
            r1 = RouteStation.objects.get(route__train__number=train_number, station__code=from_stn)
            r2 = RouteStation.objects.get(route__train__number=train_number, station__code=to_stn)
            
            distance = abs((r2.distance_from_source or 0) - (r1.distance_from_source or 0))
            if distance == 0:
                distance = 100 # Fallback estimate if distance is 0
                
            # Get all active fare rules
            rules = FareRule.objects.all()
            
            fares = []
            for rule in rules:
                base_fare = rule.base_fare + (rule.per_km_rate * distance)
                fares.append({
                    "class_code": rule.travel_class,
                    "fare": round(base_fare)
                })
                
            fare_data = {
                "train_number": train_number,
                "source": from_stn,
                "destination": to_stn,
                "distance": distance,
                "fares": fares
            }
            return ResponseNormalizer.normalize(fare_data, source="local_database", simulated=True)
            
        except RouteStation.DoesNotExist:
            return ResponseNormalizer.error("Segment not found for fare calculation", source="local_database", error_code="NOT_FOUND")
