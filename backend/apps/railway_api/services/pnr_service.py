import logging
from .base_service import BaseRailwayService
from .response_normalizer import ResponseNormalizer
from ..exceptions import RailwayAPIException

logger = logging.getLogger(__name__)

class PNRService(BaseRailwayService):
    @classmethod
    def get_pnr(cls, pnr_number):
        if not pnr_number or len(pnr_number) != 10:
            return ResponseNormalizer.error("Valid 10-digit PNR is required", error_code="INVALID_REQUEST")
            
        try:
            raw_data = cls.request(f"/getPNRStatus/{pnr_number}")
            data_dict = raw_data.get("data", {}) if isinstance(raw_data, dict) else {}
            
            if not data_dict:
                raise RailwayAPIException("PNR not found or flushed", "NOT_FOUND", 404)
                
            pnr_data = {
                "pnr": pnr_number,
                "train_number": data_dict.get("trainNumber", ""),
                "train_name": data_dict.get("trainName", ""),
                "journey_date": data_dict.get("dateOfJourney", ""),
                "source": data_dict.get("sourceStation", ""),
                "destination": data_dict.get("destinationStation", ""),
                "class_code": data_dict.get("journeyClass", ""),
                "chart_status": data_dict.get("chartStatus", "CHART NOT PREPARED"),
                "passengers": []
            }
            
            for pax in data_dict.get("passengerList", []):
                pnr_data["passengers"].append({
                    "passenger_number": pax.get("passengerSerialNumber", 1),
                    "booking_status": pax.get("bookingStatus", ""),
                    "booking_coach": pax.get("bookingCoachId", ""),
                    "booking_berth": pax.get("bookingBerthNo", ""),
                    "current_status": pax.get("currentStatus", ""),
                    "current_coach": pax.get("currentCoachId", ""),
                    "current_berth": pax.get("currentBerthNo", "")
                })
                
            return ResponseNormalizer.normalize(pnr_data, source="external_api")
            
        except RailwayAPIException as e:
            logger.warning(f"External API PNR failed: {e.message}. Falling back to DB.")
            return cls._fallback_pnr(pnr_number)
        except Exception as e:
            logger.error(f"Unexpected error in PNR status: {str(e)}")
            return cls._fallback_pnr(pnr_number)

    @classmethod
    def _fallback_pnr(cls, pnr_number):
        # Local TrackEase DB fallback
        from pnr.models import PNR
        try:
            pnr = PNR.objects.get(pnr_number=pnr_number)
            pnr_data = {
                "pnr": pnr.pnr_number,
                "train_number": pnr.booking.train.number,
                "train_name": pnr.booking.train.name,
                "journey_date": str(pnr.booking.journey_date),
                "source": pnr.booking.source.code,
                "destination": pnr.booking.destination.code,
                "class_code": pnr.booking.travel_class,
                "chart_status": pnr.chart_status,
                "passengers": []
            }
            
            for pax in pnr.passengers.all():
                pnr_data["passengers"].append({
                    "passenger_number": 1, # Mock
                    "booking_status": "CNF",
                    "booking_coach": pax.coach,
                    "booking_berth": pax.berth,
                    "current_status": "CNF",
                    "current_coach": pax.coach,
                    "current_berth": pax.berth
                })
                
            return ResponseNormalizer.normalize(pnr_data, source="local_database")
        except PNR.DoesNotExist:
            return ResponseNormalizer.error("PNR not found locally or externally", source="local_database", error_code="NOT_FOUND")
