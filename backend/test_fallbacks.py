import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from railway_api.services.station_service import StationService
from railway_api.services.train_service import TrainService
from railway_api.services.schedule_service import ScheduleService
from railway_api.services.tracking_service import TrackingService
from railway_api.services.pnr_service import PNRService
from railway_api.services.availability_service import AvailabilityService
from railway_api.services.fare_service import FareService

def test_api_fallback():
    print("--- Testing Railway API Fallbacks (No External Key) ---")
    
    # 1. SearchStation
    res = StationService.search_station("CSTM")
    print(f"1. SearchStation: {res['success']} | Source: {res.get('meta', {}).get('source')} | Data len: {len(res.get('data', []))}")
    
    # 2. SearchTrain
    res = TrainService.search_train("12951")
    print(f"2. SearchTrain: {res['success']} | Source: {res.get('meta', {}).get('source')} | Data len: {len(res.get('data', []))}")
    
    # 3. TrainsBetweenStations V3
    res = TrainService.trains_between("NDLS", "MMCT")
    print(f"3. TrainsBetweenStations: {res['success']} | Source: {res.get('meta', {}).get('source')} | Data len: {len(res.get('data', []))}")
    
    # 4. Schedule V2
    res = ScheduleService.get_schedule("12951", is_v2=True)
    print(f"4. Schedule V2: {res['success']} | Source: {res.get('meta', {}).get('source')}")
    
    # 5. Schedule
    res = ScheduleService.get_schedule("12951", is_v2=False)
    print(f"5. Schedule V1: {res['success']} | Source: {res.get('meta', {}).get('source')}")
    
    # 6. Live Status
    res = TrackingService.get_live_status("12951")
    print(f"6. Live Status: {res['success']} | Source: {res.get('meta', {}).get('source')} | Simulated: {res.get('meta', {}).get('simulated')}")
    
    # 7. PNR Status V3
    res = PNRService.get_pnr("1234567890")
    print(f"7. PNR Status V3: {res['success']} | Source: {res.get('source') or res.get('meta', {}).get('source')}")
    
    # 8. Train Classes
    res = TrainService.get_classes("12951")
    print(f"8. Train Classes: {res['success']} | Source: {res.get('meta', {}).get('source')}")
    
    # 9. Seat Availability
    res = AvailabilityService.check("12951", "NDLS", "MMCT", "2026-10-10", "3A", is_v2=False)
    print(f"9. Seat Availability: {res['success']} | Source: {res.get('meta', {}).get('source')}")
    
    # 10. Seat Availability V2
    res = AvailabilityService.check("12951", "NDLS", "MMCT", "2026-10-10", "3A", is_v2=True)
    print(f"10. Seat Availability V2: {res['success']} | Source: {res.get('meta', {}).get('source')}")
    
    # 11. Fare
    res = FareService.get_fare("12951", "NDLS", "MMCT")
    print(f"11. Fare: {res['success']} | Source: {res.get('meta', {}).get('source')}")
    
    # 12. Trains By Station
    res = StationService.get_trains("NDLS")
    print(f"12. Trains By Station: {res['success']} | Source: {res.get('meta', {}).get('source')} | Data len: {len(res.get('data', []))}")
    
    # 13. Live Station
    res = StationService.get_live("NDLS")
    print(f"13. Live Station: {res['success']} | Source: {res.get('meta', {}).get('source')}")

if __name__ == "__main__":
    test_api_fallback()
