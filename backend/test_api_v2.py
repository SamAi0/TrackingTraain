import urllib.request
import json
import sys

def check_url(url, expected_code=200):
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            status = response.status
            body = response.read().decode('utf-8')
            print(f"[SUCCESS] {url} -> {status}")
            return json.loads(body)
    except urllib.error.HTTPError as e:
        print(f"[ERROR] {url} -> {e.code}")
        body = e.read().decode('utf-8')
        print(f"Error Body: {body[:300]}")
        return None
    except Exception as e:
        print(f"[EXCEPTION] {url} -> {str(e)}")
        return None

print("Running API Tests...")
check_url("http://localhost:8000/api/stations/list/?page=1")
check_url("http://localhost:8000/api/stations/list/?page=1&q=vashi")
check_url("http://localhost:8000/api/stations/list/?page=1&q=csmt")
check_url("http://localhost:8000/api/stations/geo/")

# Test autocomplete for popular trains
auto_res = check_url("http://localhost:8000/api/stations/autocomplete/?q=MMCT")
if auto_res and auto_res.get('popular_trains'):
    print(f"Popular trains for MMCT: {[t['number'] + ' - ' + t['name'] for t in auto_res['popular_trains']]}")
else:
    print("No popular trains returned in autocomplete.")
