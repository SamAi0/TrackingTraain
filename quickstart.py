#!/usr/bin/env python3
"""
Indian Railway Data - Quickstart Helper Script
Demonstrates querying stations.json and trains.json.
"""

import json
import os
import sys

# Ensure UTF-8 output on Windows consoles if supported
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIONS_FILE = os.path.join(BASE_DIR, "stations.json")
TRAINS_FILE = os.path.join(BASE_DIR, "trains.json")


def load_dataset():
    print("[*] Loading datasets...")
    with open(STATIONS_FILE, "r", encoding="utf-8") as f:
        stations = json.load(f)
    with open(TRAINS_FILE, "r", encoding="utf-8") as f:
        trains = json.load(f)
    print(f"[+] Loaded {len(stations):,} stations and {len(trains):,} trains.\n")
    return stations, trains


def search_station(query, stations):
    query_upper = query.strip().upper()
    matches = [
        s for s in stations
        if query_upper in s.get("code", "").upper()
        or query_upper in s.get("name", "").upper()
        or query_upper in s.get("state", "").upper()
    ]
    return matches


def search_train(query, trains):
    query_upper = query.strip().upper()
    matches = [
        t for t in trains
        if query_upper in t.get("trainNumber", "").upper()
        or query_upper in t.get("trainName", "").upper()
    ]
    return matches


def print_train_schedule(train):
    print("=" * 70)
    print(f"Train: {train['trainNumber']} - {train['trainName']} [{train.get('type', 'N/A')}]")
    print(f"Route: {train['source']['name']} ({train['source']['code']}) -> {train['destination']['name']} ({train['destination']['code']})")
    print(f"Total Distance: {train.get('overallDistanceKm', 'N/A')} km")
    
    running_days = [day for day, active in train.get("runningDays", {}).items() if active]
    print(f"Runs On: {', '.join(running_days) if running_days else 'All Days'}")
    print("=" * 70)
    print(f"{'#':<3} {'Code':<6} {'Station Name':<28} {'Arrival':<10} {'Departure':<10} {'Day':<4} {'Distance'}")
    print("-" * 70)
    
    for stop in train.get("completeOrderedRoute", []):
        seq = stop.get("sequence", "-")
        code = stop.get("stationCode", "-")
        name = stop.get("stationName", "-")
        arr = stop.get("arrivalTime") or "--:--"
        dep = stop.get("departureTime") or "--:--"
        day = stop.get("journeyDay", 1)
        dist = f"{stop.get('distance', 0)} km"
        print(f"{seq:<3} {code:<6} {name[:27]:<28} {arr:<10} {dep:<10} {day:<4} {dist}")
    print("=" * 70)


def find_direct_trains(src_code, dest_code, trains):
    src_upper = src_code.strip().upper()
    dest_upper = dest_code.strip().upper()
    
    results = []
    for train in trains:
        station_codes = [s.get("stationCode", "").upper() for s in train.get("completeOrderedRoute", [])]
        if src_upper in station_codes and dest_upper in station_codes:
            src_idx = station_codes.index(src_upper)
            dest_idx = station_codes.index(dest_upper)
            if src_idx < dest_idx:
                results.append(train)
    return results


def main():
    stations, trains = load_dataset()

    print("--- DEMO 1: Station Lookup (e.g. 'NDLS') ---")
    stn_matches = search_station("NDLS", stations)
    for s in stn_matches:
        print(f"[{s['code']}] {s['name']} - State: {s['state']}, Zone: {s['zone']}")
        coords = s.get("coordinates", {})
        print(f"Coordinates: Lat {coords.get('latitude')}, Long {coords.get('longitude')}")

    print("\n--- DEMO 2: Train Lookup & Timetable (e.g. '12951') ---")
    train_matches = search_train("12951", trains)
    if train_matches:
        print_train_schedule(train_matches[0])

    print("\n--- DEMO 3: Find Direct Trains (e.g. BVI to NDLS) ---")
    direct_trains = find_direct_trains("BVI", "NDLS", trains)
    print(f"Found {len(direct_trains)} direct trains from BVI (Borivali) to NDLS (New Delhi):")
    for t in direct_trains[:5]:
        print(f"  * {t['trainNumber']} - {t['trainName']} ({t['type']})")
    if len(direct_trains) > 5:
        print(f"  ... and {len(direct_trains) - 5} more.")


if __name__ == "__main__":
    main()
