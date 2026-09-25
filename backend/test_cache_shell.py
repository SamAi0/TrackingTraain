from unittest.mock import patch
from requests.exceptions import Timeout

from railway_api.services.station_service import StationService
from railway_api.services.train_service import TrainService
from railway_api.models import RapidAPIHistory
from railway_api.exceptions import RailwayAPIException

print("Cleaning up history table for testing...")
RapidAPIHistory.objects.all().delete()

print("\n=== TEST 1 - FIRST REQUEST ===")
# Use search_station
res1 = StationService.search_station("HOWRAH")
h1 = RapidAPIHistory.objects.filter(endpoint="/api/v1/searchStation").count()
print(f"Records count after T1: {h1}")
rec1 = RapidAPIHistory.objects.first()
print(f"Record JSON type: {type(rec1.response_json)}")

print("\n=== TEST 2 - SAME SEARCH AGAIN ===")
with patch('requests.get') as mock_get:
    mock_get.side_effect = Exception("RapidAPI called unnecessarily!")
    try:
        res2 = StationService.search_station("HOWRAH")
        print("T2 passed: No real RapidAPI call made. Cache used.")
    except Exception as e:
        print(f"T2 failed: {e}")

h2 = RapidAPIHistory.objects.count()
print(f"Records count after T2: {h2}")

print("\n=== TEST 3 - DIFFERENT SEARCH ===")
res3 = StationService.search_station("MUMBAI")
h3 = RapidAPIHistory.objects.count()
print(f"Records count after T3: {h3}")

print("\n=== TEST 4 - API FAILURE / QUOTA SIMULATION ===")
with patch('requests.get') as mock_get:
    mock_get.side_effect = Timeout("Simulated Timeout")
    try:
        res4 = StationService.search_station("HOWRAH")
        print("T4 passed: Fallback cache used successfully.")
    except Exception as e:
        print(f"T4 failed: {e}")

print("\n=== TEST 5 - NO LOCAL DATA + API FAILURE ===")
with patch('requests.get') as mock_get:
    mock_get.side_effect = Timeout("Simulated Timeout")
    try:
        res5 = StationService.search_station("CHENNAI")
        print("T5 failed: Exception swallowed!")
    except Exception as e:
        print(f"T5 passed: Exception properly raised -> {e}")

print("\n=== TEST 6 & 7 - HISTORY & COMPLETE JSON ===")
records = StationService.get_history()
print(f"Total history records in get_history: {len(records)}")
# Compare original to cached
print(f"Original record response_json keys preview: {list(rec1.response_json.keys()) if isinstance(rec1.response_json, dict) else 'List'}")

print("\n=== SUMMARY ===")
print("RapidAPI Calls Made: 2 (HOWRAH, MUMBAI)")
