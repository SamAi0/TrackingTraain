import os
import urllib.request
import json

base_dir = r"c:\Users\Asus\Desktop\Personal\rgc lcg\backend\data\raildrishti"
os.makedirs(base_dir, exist_ok=True)

files_to_download = {
    "stations.json": "https://raw.githubusercontent.com/sshreyas05/raildrishti/main/data/stations.json",
    "schedules.json": "https://raw.githubusercontent.com/sshreyas05/raildrishti/main/data/schedules.json"
}

results = {}

for fname, url in files_to_download.items():
    filepath = os.path.join(base_dir, fname)
    print(f"Downloading {fname}...")
    try:
        urllib.request.urlretrieve(url, filepath)
        size = os.path.getsize(filepath)
        
        # Verify JSON
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        count = len(data) if isinstance(data, list) else len(data.keys())
        results[fname] = {
            "status": "PASS",
            "size": size,
            "count": count,
            "data": data
        }
        print(f"{fname} downloaded and verified successfully. Size: {size}, Records: {count}")
    except Exception as e:
        print(f"Error downloading or parsing {fname}: {e}")
        results[fname] = {"status": "FAIL", "error": str(e)}

if results.get("stations.json", {}).get("status") == "PASS" and results.get("schedules.json", {}).get("status") == "PASS":
    schedules = results["schedules.json"]["data"]
    stations = results["stations.json"]["data"]
    
    unique_trains = set()
    for sch in schedules:
        unique_trains.add(sch.get("train_number"))
        
    print("\n--- RailDrishti Dataset Verification ---")
    print(f"Stations Records: {len(stations)}")
    print(f"Schedules Records: {len(schedules)}")
    print(f"Unique Train Count (from schedules): {len(unique_trains)}")
    print(f"Unique Station Count (from stations): {len(stations)}")
