import os
import sys
import django
import json
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_mysql')
django.setup()

from django.test.client import Client
from stations.models import Station
from trains.models import Train
from routes.models import RouteStation

client = Client()

results = []

def run_test(feature, name, expected_behavior, endpoint, test_fn):
    status = 'PASS'
    notes = ''
    try:
        response = None
        if endpoint:
            response = client.get(endpoint, SERVER_NAME='localhost')
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.content[:200]}")
            data = response.json()
        else:
            data = None
        
        test_fn(data)
    except Exception as e:
        status = 'FAIL'
        notes = str(e)
        
    results.append({
        'feature': feature,
        'test': name,
        'expected': expected_behavior,
        'status': status,
        'notes': notes
    })

# Phase 1: Autocomplete
def test_pmj_bct(data):
    stations = data.get('data', [])
    assert len(stations) > 0, "No matching stations"
    codes = [s['code'] for s in stations]
    assert 'BCT' in codes, f"BCT not found in {codes}"
    popular = data.get('popular_trains', [])
    assert len(popular) > 0, "No popular trains returned"
    for t in popular:
        assert 'number' in t and 'name' in t, "Missing number/name in popular train"
        
run_test("Plan My Journey", "Source/Destination Autocomplete (BCT)", "Returns matching station & popular trains", "/api/stations/autocomplete/?q=BCT", test_pmj_bct)

def test_pmj_ndls(data):
    stations = data.get('data', [])
    assert len(stations) > 0, "No matching stations"
    codes = [s['code'] for s in stations]
    assert 'NDLS' in codes, f"NDLS not found in {codes}"
    popular = data.get('popular_trains', [])
    assert len(popular) > 0, "No popular trains returned"

run_test("Plan My Journey", "Source/Destination Autocomplete (NDLS)", "Returns matching station & popular trains", "/api/stations/autocomplete/?q=NDLS", test_pmj_ndls)

# Phase 2: Station Explorer
def test_st_exp_surat(data):
    res = data.get('results', [])
    assert len(res) > 0, "No results for Surat"
    assert res[0]['name'].lower() == 'surat' or res[0]['code'] == 'ST', "Wrong station returned"
    
run_test("Station Explorer", "Search by name (Surat)", "Returns Surat station", "/api/stations/list/?page=1&q=Surat", test_st_exp_surat)

def test_st_exp_cstm(data):
    res = data.get('results', [])
    assert len(res) > 0, "No results for CSTM"
    assert res[0]['code'] == 'CSTM', "Wrong station returned"
    assert 'latitude' in res[0] and 'longitude' in res[0], "Coordinates missing from response"
    
run_test("Station Explorer", "Search by code (CSTM)", "Returns CSTM station details", "/api/stations/list/?page=1&q=CSTM", test_st_exp_cstm)

# Phase 3: Map
def test_st_geo(data):
    res = data.get('data', [])
    assert len(res) > 0, "Map data empty"
    assert isinstance(res, list), "Map data is not a list"

run_test("Map", "Load Map Coordinates", "Loads without crashing, handles nulls", "/api/stations/geo/", test_st_geo)

# Phase 4: Train Search
def test_train_search_12951(data):
    res = data if isinstance(data, list) else data.get('data', [])
    assert len(res) > 0, "No train found"
    t = [x for x in res if x['number'] == '12951'][0]
    assert t['name'], "Train name missing"
    
run_test("Train Search", "Search Train (12951)", "Returns train 12951 details", "/api/trains/autocomplete/?q=12951", test_train_search_12951)

def test_trains_between(data):
    res = data.get('data', [])
    assert len(res) > 0, "No train found"
    t = [x for x in res if x['number'] == '12951']
    assert len(t) > 0, "12951 not found between BCT and NDLS"

run_test("Train Search", "Trains Between (BCT to NDLS)", "Returns trains between BCT and NDLS", "/api/railway/trains/between/?from=BCT&to=NDLS", test_trains_between)

# Phase 5: Train Details (Schedule/Route)
def test_train_details_12951(data):
    assert data.get('success'), "Failed to get schedule"
    stations = data['data']['stations']
    assert len(stations) == 202, f"Expected 202 stops, got {len(stations)}"
    assert stations[0]['station_code'] == 'BCT', "First stop not BCT"

run_test("Train Details", "Route for 12951", "Returns exactly 202 route stops", "/api/railway/trains/12951/schedule-v2/", test_train_details_12951)

def test_train_details_01101(data):
    assert data.get('success'), "Failed to get schedule"
    stations = data['data']['stations']
    assert len(stations) == 152, f"Expected 152 stops, got {len(stations)}"

run_test("Train Details", "Route for 01101", "Returns exactly 152 route stops", "/api/railway/trains/01101/schedule-v2/", test_train_details_01101)

# Phase 6: Train Tracking
def test_train_tracking(data):
    assert data.get('success'), "Failed to get live tracking"
    d = data['data']
    assert 'current_station' in d, "Missing current_station"
    assert 'running_status' in d, "Missing running_status"
    assert 'DEMO' in str(data).upper() or 'SIMULATED' in str(data).upper(), "Not labelled as DEMO/SIMULATED"

run_test("Train Tracking", "Live Status 12951", "Returns tracking info labelled as DEMO", "/api/railway/trains/12951/live/", test_train_tracking)

print(json.dumps(results, indent=2))
