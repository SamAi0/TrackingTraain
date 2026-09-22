# 🚆 Indian Railway Data (Open Dataset)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Dataset](https://img.shields.io/badge/Data%20Format-JSON-blue.svg)](https://www.json.org/)
[![Stations](https://img.shields.io/badge/Stations-8%2C990%2B-orange.svg)](#-stationsjson)
[![Trains](https://img.shields.io/badge/Trains-5%2C208%2B-green.svg)](#-trainsjson)

A structured, comprehensive, and developer-friendly open dataset of the **Indian Railways network**. This repository contains clean JSON datasets covering **8,990+ railway stations** (with geocoded coordinates, state, zone, and address) and **5,208+ trains** (with full route schedules, halt timings, journey days, and running days).

---

## 📌 Dataset Summary

| File | Description | Records | File Size | Key Features |
| :--- | :--- | :--- | :--- | :--- |
| [`stations.json`](./stations.json) | Railway station directory | **8,990** | ~1.9 MB | Station codes, names, states, railway zones, addresses, latitude & longitude |
| [`trains.json`](./trains.json) | Train master directory & schedules | **5,208** | ~96.6 MB | Train number, name, type, source, destination, weekly running days, distance, ordered route with arrival/departure times |

---

## 📂 Data Schemas & Structure

### 1. `stations.json`

An array of JSON objects representing Indian Railway stations.

```json
[
  {
    "code": "BDHL",
    "name": "Badhal",
    "state": "Rajasthan",
    "zone": "NWR",
    "address": "Kishangarh Renwal, Rajasthan",
    "coordinates": {
      "longitude": 75.4516454,
      "latitude": 27.2520587
    }
  }
]
```

#### Field Specifications:

| Field | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `code` | `string` | Unique IRCTC / Indian Railways station code | `"NDLS"`, `"BDHL"` |
| `name` | `string` | Official name of the station | `"New Delhi"`, `"Badhal"` |
| `state` | `string` | State / Union Territory where the station is located | `"Rajasthan"`, `"Delhi"` |
| `zone` | `string` | Railway Zone code (e.g., NR, NWR, SR, CR, WR, ER, ECR) | `"NWR"` |
| `address` | `string` | Locality / city and state address | `"Kishangarh Renwal, Rajasthan"` |
| `coordinates.latitude` | `number` | Latitude coordinate (WGS84 decimal degrees) | `27.2520587` |
| `coordinates.longitude` | `number` | Longitude coordinate (WGS84 decimal degrees) | `75.4516454` |

---

### 2. `trains.json`

An array of JSON objects representing trains operating across India with complete route details and intermediate stops.

```json
[
  {
    "trainNumber": "12951",
    "trainName": "MUMBAI TEJAS RAJDHANI",
    "type": "Raj",
    "source": {
      "code": "MMCT",
      "name": "MUMBAI CENTRAL"
    },
    "destination": {
      "code": "NDLS",
      "name": "NEW DELHI"
    },
    "runningDays": {
      "SUN": true,
      "MON": true,
      "TUE": true,
      "WED": true,
      "THU": true,
      "FRI": true,
      "SAT": true
    },
    "overallDistanceKm": 1386,
    "completeOrderedRoute": [
      {
        "sequence": 1,
        "stationCode": "MMCT",
        "stationName": "MUMBAI CENTRAL",
        "arrivalTime": null,
        "departureTime": "17:00:00",
        "journeyDay": 1,
        "distance": 0
      },
      {
        "sequence": 2,
        "stationCode": "BVI",
        "stationName": "BORIVALI",
        "arrivalTime": "17:22:00",
        "departureTime": "17:24:00",
        "journeyDay": 1,
        "distance": 30
      },
      {
        "sequence": 8,
        "stationCode": "NDLS",
        "stationName": "NEW DELHI",
        "arrivalTime": "08:32:00",
        "departureTime": null,
        "journeyDay": 2,
        "distance": 1386
      }
    ]
  }
]
```

#### Field Specifications:

| Field | Type | Description |
| :--- | :--- | :--- |
| `trainNumber` | `string` | 5-digit Indian Railways train number (e.g. `"12951"`, `"04601"`) |
| `trainName` | `string` | Official name of the train |
| `type` | `string` | Category (e.g., `Raj` (Rajdhani), `SF` (Superfast), `Exp` (Express), `Pass` (Passenger), `MEMU`, `DEMU`, `Drnt` (Duronto), `GR` (Garib Rath)) |
| `source` | `object` | Origin station containing `code` and `name` |
| `destination` | `object` | Terminating station containing `code` and `name` |
| `runningDays` | `object` | Days of the week (`SUN`-`SAT`) with boolean flags indicating active schedule |
| `overallDistanceKm` | `number` | Total journey distance in kilometers |
| `completeOrderedRoute` | `array` | Sequential list of all stopping stations and halts |
| ↳ `sequence` | `number` | Stop order index (starts at 1) |
| ↳ `stationCode` | `string` | Station code for this stop |
| ↳ `stationName` | `string` | Station name for this stop |
| ↳ `arrivalTime` | `string` \| `null` | Arrival time in `HH:MM:SS` (or `null` at origin) |
| ↳ `departureTime` | `string` \| `null` | Departure time in `HH:MM:SS` (or `null` at destination) |
| ↳ `journeyDay` | `number` | Day count of the journey (1 for day 1, 2 for day 2, etc.) |
| ↳ `distance` | `number` | Cumulative distance in km from source |

---

## 🚀 Quickstart & Usage Examples

### 🐍 Python

#### 1. Load Data and Search for a Station
```python
import json

# Load stations
with open("stations.json", "r", encoding="utf-8") as f:
    stations = json.load(f)

# Find station by code
station_code = "NDLS"
station = next((s for s in stations if s["code"] == station_code), None)
print(f"Station: {station['name']}, State: {station['state']}, Zone: {station['zone']}")
print(f"Coordinates: {station['coordinates']['latitude']}, {station['coordinates']['longitude']}")
```

#### 2. Search for Trains and View Timetable
```python
import json

# Load trains
with open("trains.json", "r", encoding="utf-8") as f:
    trains = json.load(f)

# Find train by number
train_num = "12951"
train = next((t for t in trains if t["trainNumber"] == train_num), None)

if train:
    print(f"🚆 {train['trainNumber']} - {train['trainName']} ({train['type']})")
    print(f"Route: {train['source']['name']} ➔ {train['destination']['name']} ({train['overallDistanceKm']} km)")
    print("\n--- Stops ---")
    for stop in train["completeOrderedRoute"]:
        arr = stop["arrivalTime"] or "Origin"
        dep = stop["departureTime"] or "Destination"
        print(f"[{stop['sequence']:02d}] {stop['stationCode']:<5} {stop['stationName']:<25} Arr: {arr:<10} Dep: {dep:<10} Day {stop['journeyDay']}")
```

#### 3. Find Direct Trains Between Two Stations
```python
import json

def find_direct_trains(src_code, dest_code, trains):
    matches = []
    for train in trains:
        station_codes = [s["stationCode"] for s in train["completeOrderedRoute"]]
        if src_code in station_codes and dest_code in station_codes:
            src_idx = station_codes.index(src_code)
            dest_idx = station_codes.index(dest_code)
            if src_idx < dest_idx:  # verify direction
                matches.append(train)
    return matches

with open("trains.json", "r", encoding="utf-8") as f:
    trains = json.load(f)

results = find_direct_trains("BVI", "NDLS", trains)
print(f"Found {len(results)} direct trains from BVI to NDLS:")
for t in results:
    print(f"- {t['trainNumber']}: {t['trainName']}")
```

---

### 🌐 JavaScript / Node.js

```javascript
const fs = require('fs');

// Load stations
const stations = JSON.parse(fs.readFileSync('stations.json', 'utf8'));

// Filter stations by Zone
const nwrStations = stations.filter(s => s.zone === 'NWR');
console.log(`Found ${nwrStations.length} stations in North Western Railway (NWR) zone.`);

// Load trains
const trains = JSON.parse(fs.readFileSync('trains.json', 'utf8'));

// Find Rajdhani trains
const rajdhaniTrains = trains.filter(t => t.type === 'Raj');
console.log(`Found ${rajdhaniTrains.length} Rajdhani Express trains.`);
```

---

### 🐼 Python Pandas

```python
import pandas as pd

# Load stations into DataFrame
df_stations = pd.read_json("stations.json")
print("Top 5 States by station count:")
print(df_stations["state"].value_counts().head(5))

# Load trains into DataFrame
df_trains = pd.read_json("trains.json")
print("\nTrain count by type:")
print(df_trains["type"].value_counts())
```

## ⚙️ Local Project Setup (TrackEase Application)

If you want to run the full TrackEase Django application locally:

### 1. Clone the repository
```bash
git clone https://github.com/your-repo/trackease.git
cd trackease
```

### 2. Set up Virtual Environment
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:
```env
SECRET_KEY=your_django_secret_key
DEBUG=True
DATABASE_HOST=your_supabase_postgresql_url
RAPIDAPI_KEY=your_rapidapi_key
RAPIDAPI_HOST=irctc1.p.rapidapi.com
```

### 5. Run Migrations & Start Server
```bash
python manage.py migrate
python manage.py runserver
```
The frontend will be available at `http://127.0.0.1:8000/`.

---

## 💡 Potential Use Cases

- 🗺️ **GIS & Railway Map Visualizations**: Plot railway stations and interconnecting routes on interactive maps (Leaflet, Mapbox, Deck.gl, QGIS).
- 🔍 **Trip & Route Planning Applications**: Build custom graph-based routing algorithms, Dijkstra transit paths, or transfer finders.
- 📊 **Indian Railways Analytics**: Study network connectivity, distance distributions, station densities per state, and zone coverage.
- 🤖 **AI / LLM Retrieval-Augmented Generation (RAG)**: Use as a ground-truth dataset for train chatbots, IRCTC assistant apps, and semantic search.
- 📱 **Mobile & Web Apps**: Integrate offline train timetable lookups and station auto-complete widgets.

---

## 🛠️ Ready-to-Run Scripts

Check out the [`examples/`](./examples) directory for complete executable scripts:
- [`examples/quickstart.py`](./examples/quickstart.py): Interactive CLI tool to lookup stations, inspect train routes, and search direct trains.

Run it with:
```bash
python examples/quickstart.py
```

---

## 🤝 Contributing

Contributions, corrections, and data updates are warmly welcome!
If you find missing stations, updated coordinates, or altered train routes:

1. Fork the repository
2. Create your feature branch (`git checkout -b update/station-data`)
3. Commit your changes (`git commit -m 'Add new station details'`)
4. Push to the branch (`git push origin update/station-data`)
5. Open a **Pull Request**

Please read [`CONTRIBUTING.md`](./CONTRIBUTING.md) for details.

---

## 📄 License

This dataset and all associated code examples are released under the [MIT License](./LICENSE). You are free to use, modify, and distribute this data in personal, academic, and commercial projects.

---

⭐ **If you find this dataset helpful, please consider giving this repository a star on GitHub!**
