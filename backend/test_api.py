import urllib.request
import json

urls = [
    "http://localhost:8000/api/stations/list/?page=1",
    "http://localhost:8000/api/stations/geo/"
]

for url in urls:
    print(f"\nGET {url}")
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            print("Status:", response.status)
            body = response.read().decode('utf-8')
            print("Body (first 200 chars):", body[:200])
    except urllib.error.HTTPError as e:
        print("HTTP Error:", e.code)
        body = e.read().decode('utf-8')
        print("Error Body:", body[:500])
    except Exception as e:
        print("Error:", str(e))
