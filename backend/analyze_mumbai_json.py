import json

file_path = "mumbai_suburban_timetable_trackease.json"

with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

sm = data.get('station_master', {})
stations = set()
all_stations = []
duplicate_stations = set()

for k, line_data in sm.items():
    for st in line_data:
        code = st[0]
        if code in all_stations:
            duplicate_stations.add(code)
        all_stations.append(code)
        stations.add(code)

print(f"Total stations (unique codes): {len(stations)}")
print(f"Total stations listed across all lines (including overlaps): {len(all_stations)}")
print(f"Duplicate/overlapping stations: {len(duplicate_stations)} -> {duplicate_stations}")

print("\nCounts per line:")
for k, line_data in sm.items():
    print(f"  {k}: {len(line_data)}")

services = data.get('service_samples', [])
print(f"\nTotal services (trains): {len(services)}")

missing_timings = 0
unspecified_running_days = 0

for s in services:
    if not s.get('origin_departure') or not s.get('destination_arrival'):
        missing_timings += 1
    if s.get('running_days') == "NOT_SPECIFIED_IN_SOURCE":
        unspecified_running_days += 1

print(f"Missing timings (origin/dest): {missing_timings}")
print(f"Unspecified running days: {unspecified_running_days}")
