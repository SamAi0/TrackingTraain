import os
import sys
import json
import django
from collections import Counter

sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_mysql')
django.setup()

from trains.models import Train
from stations.models import Station
from routes.models import Route, RouteStation
from schedules.models import Schedule

results = []

def assert_val(name, expected, actual):
    if str(expected) == str(actual):
        results.append(f"PASS: {name} | Expected: {expected}, Actual: {actual}")
    else:
        results.append(f"FAIL: {name} | Expected: {expected}, Actual: {actual}")

# Total Counts
assert_val("Station count", 9004, Station.objects.count())
assert_val("Train count", 5337, Train.objects.count())
assert_val("Route count", 5337, Route.objects.count())
assert_val("RouteStation count", 417147, RouteStation.objects.count())
assert_val("Schedule count", 417147, Schedule.objects.count())

# Load Clean JSON
data_file = 'data/mumbai_suburban/trans_harbour_line_2024_clean.json'
with open(data_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

services = data.get('services', [])
service_numbers = [s['service_number'] for s in services]

# 1, 2. Train and Route existence
db_trains = list(Train.objects.filter(number__in=service_numbers))
assert_val("Imported Trains", 131, len(db_trains))

routes = list(Route.objects.filter(train__number__in=service_numbers))
assert_val("Imported Routes", 131, len(routes))

# 3. Stations
unique_stations_names = set(st['station_name'] for s in services for st in s['stations'])
db_st_count = 0
for n in unique_stations_names:
    if Station.objects.filter(name__iexact=n).exists():
        db_st_count += 1
assert_val("Imported Stations", 17, db_st_count)

# 4, 10. Timetable records & Distance
db_route_stations = RouteStation.objects.filter(route__train__number__in=service_numbers)
assert_val("Imported RouteStations", 1401, db_route_stations.count())
db_schedules = Schedule.objects.filter(train__number__in=service_numbers)
assert_val("Imported Schedules", 1401, db_schedules.count())

distances = db_route_stations.values_list('distance_from_source', flat=True)
all_null = all(d is None for d in distances)
assert_val("Distances remain NULL", True, all_null)

# 11, 12. Existing trains untouched
train_12951_rs = RouteStation.objects.filter(route__train__number='12951').count()
assert_val("Train 12951 RouteStations", 202, train_12951_rs)

train_01101_rs = RouteStation.objects.filter(route__train__number='01101').count()
assert_val("Train 01101 RouteStations", 152, train_01101_rs)

for r in results:
    print(r)
