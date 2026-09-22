import os
import json
import csv

files_to_check = [
    "trackease_12951_ready.json",
    "trackease_12951_ready.csv",
    "trackease_mumbai_navi_relevant_subset.json",
    "trackease_mumbai_navi_stations.csv",
    "trackease_mumbai_navi_schedules.csv"
]

base_dir = r"c:\Users\Asus\Desktop\Personal\rgc lcg"

for fname in files_to_check:
    path = os.path.join(base_dir, fname)
    if os.path.exists(path):
        size = os.path.getsize(path)
        records = 0
        if fname.endswith(".json"):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        records = len(data)
                    elif isinstance(data, dict):
                        # count keys or something
                        records = len(data)
            except Exception as e:
                records = f"Error: {e}"
        elif fname.endswith(".csv"):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    records = sum(1 for _ in reader) - 1 # exclude header
            except Exception as e:
                records = f"Error: {e}"
        
        print(f"File: {fname}")
        print(f"Path: {path}")
        print(f"Size: {size / 1024:.2f} KB")
        print(f"Records: {records}")
        print("-" * 40)
    else:
        print(f"File: {fname} NOT FOUND")
        print("-" * 40)

print("\nChecking for stations.json and schedules.json...")
s1 = os.path.join(base_dir, "stations.json")
s2 = os.path.join(base_dir, "schedules.json")
if os.path.exists(s1):
    print(f"stations.json FOUND: {os.path.getsize(s1)} bytes")
else:
    print("stations.json NOT FOUND")

if os.path.exists(s2):
    print(f"schedules.json FOUND: {os.path.getsize(s2)} bytes")
else:
    print("schedules.json NOT FOUND")
