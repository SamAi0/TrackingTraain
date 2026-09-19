import os
import django
import json
import urllib.request
import urllib.error
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from stations.models import Station
from trains.models import Train
from routes.models import Route, RouteStation
from routes.services import clear_graph_cache, get_graph

print("--- DB COVERAGE ---")
mh_stations_in_db = Station.objects.filter(state__icontains='maharashtra').count()
print(f"Maharashtra stations in DB: {mh_stations_in_db}")

print("\n--- API ROUTES TESTING ---")
def test_api(url):
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            return response.getcode(), json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode('utf-8'))
    except Exception as e:
        return 500, str(e)

# Test normal route
code, res = test_api("http://127.0.0.1:8000/api/routes/search/?from=TNA&to=CSTM")
print(f"TNA -> CSTM -> {code}")
if code == 200:
    print(f"  Stations: {res.get('station_count')}, Distance: {res.get('total_distance_km')}")

code, res = test_api("http://127.0.0.1:8000/api/routes/search/?from=NKS&to=MMR")
print(f"NKS -> MMR -> {code}")

print("\n--- GRAPH MULTI-TRAIN ROUTING TESTING ---")
# Need to find a disjoint route. Solapur to Nashik?
t0 = time.time()
code, res = test_api("http://127.0.0.1:8000/api/routes/search/?from=PUNE&to=SUR")
t1 = time.time()
print(f"PUNE -> SUR -> {code}, time: {t1-t0:.2f}s")
if code == 200:
    print(f"  Route Type: {res.get('route_type')}")
    if res.get('route_type') == 'multi_train':
        print(f"  Transfers: {res.get('transfers')}")
        print(f"  Total Mins: {res.get('total_duration_min')}")

# Test performance caching
t2 = time.time()
code, res = test_api("http://127.0.0.1:8000/api/routes/search/?from=TNA&to=SUR")
t3 = time.time()
print(f"TNA -> SUR -> {code}, time: {t3-t2:.2f}s")

print("\n--- API ERROR TESTING ---")
code, res = test_api("http://127.0.0.1:8000/api/routes/search/?from=INVALID&to=CSTM")
print(f"INVALID source -> {code}, {res}")

code, res = test_api("http://127.0.0.1:8000/api/routes/search/?from=TNA&to=TNA")
print(f"Same station -> {code}, {res}")

code, res = test_api("http://127.0.0.1:8000/api/routes/search/")
print(f"Missing params -> {code}, {res}")

print("\n--- AUTOCOMPLETE TESTING ---")
code, res = test_api("http://127.0.0.1:8000/api/stations/autocomplete/?q=pun")
print(f"Autocomplete 'pun' -> {code}")
if code == 200:
    print([r['code'] for r in res[:5]])
