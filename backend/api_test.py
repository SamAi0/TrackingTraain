import os
import sys
import json
import django
from django.test.client import Client

sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_mysql')
django.setup()

client = Client()

stations_to_test = ['VASHI', 'NERUL', 'KHARGHAR', 'BELAPUR', 'PANVEL', 'GHANSOLI', 'THANE']
api_results = []

def test(endpoint, params):
    res = client.get(endpoint, data=params, SERVER_NAME='localhost')
    return res

for st in stations_to_test:
    res = test('/api/stations/autocomplete/', {'q': st})
    found = False
    if res.status_code == 200:
        data = res.json()
        if any(st.lower() in s['name'].lower() for s in data.get('data', [])):
            found = True
    api_results.append(f"Station Search '{st}': {'PASS' if found else 'FAIL'}")

train_num = '99001'
res_train_search = test('/api/trains/autocomplete/', {'q': train_num})
found_train = False
if res_train_search.status_code == 200:
    data = res_train_search.json()
    res_list = data if isinstance(data, list) else data.get('data', [])
    if any(t['number'] == train_num for t in res_list):
        found_train = True
api_results.append(f"Train Search '{train_num}': {'PASS' if found_train else 'FAIL'}")

res_train_route = test(f'/api/railway/trains/{train_num}/schedule-v2/', {})
if res_train_route.status_code == 200:
    data = res_train_route.json()
    if len(data.get('data', {}).get('stations', [])) > 0:
        api_results.append(f"Train Route '{train_num}': PASS (Stops: {len(data['data']['stations'])})")
    else:
        api_results.append(f"Train Route '{train_num}': FAIL (Empty route)")
else:
    api_results.append(f"Train Route '{train_num}': FAIL")

res_journey = test('/api/railway/trains/between/', {'from': 'TNA', 'to': 'VASHI'})
if res_journey.status_code == 200:
    api_results.append(f"Plan My Journey 'THANE to VASHI': PASS")
else:
    api_results.append(f"Plan My Journey 'THANE to VASHI': FAIL")

for r in api_results:
    print(r)
