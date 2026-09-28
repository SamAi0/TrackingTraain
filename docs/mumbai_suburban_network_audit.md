# TrackEase – Mumbai Suburban Network Audit

## 1. Objective
Perform a read-only audit of the existing TrackEase railway dataset to determine the current coverage of the Mumbai Suburban Railway network, identify missing stations/corridors, and outline the necessary steps to support full network routing including intermediate station search and train changes.

## 2. Existing Data Coverage
Based on an inspection of the MySQL database (`stations_station`, `trains_train`, `routes_route`, `schedules_schedule`) and the local JSON repository (`backend/data/mumbai_suburban/`):

### 2.1 Corridors
- **Trans-Harbour Line**: **PARTIALLY PRESENT** (Imported via `trans_harbour_line_2024_structured.json`).
- **Harbour Line**: **MISSING**
- **Central Line**: **MISSING**
- **Western Line**: **MISSING**
- **Nerul/Belapur–Uran Corridor**: **MISSING**
- **Vasai Road–Diva Connection**: **MISSING**
- **Panvel–Karjat Corridor**: **MISSING**

### 2.2 Stations
The following table summarizes the availability of major stations requested for verification:

| Network | Status | Existing Examples | Missing Examples |
|---|---|---|---|
| **Trans-Harbour** | **Mostly Present** (14/17) | THANE, VASHI, NERUL, PANVEL | (Present as Aliases) AIROLI is `AIRAVALI`, RABALE is `RABADA`, KOPAR KHAIRANE is `KOPAR KHAIRNA` |
| **Harbour Line** | **Missing** (7/19 found) | VASHI, NERUL, PANVEL | CSMT, WADALA ROAD, KURLA, CHEMBUR, MANKHURD, BANDRA, ANDHERI |
| **Central Line** | **Missing** (8/10 found) | THANE, KALYAN, KASARA, KARJAT | CSMT, DADAR, KURLA, KHOPOLI |
| **Western Line** | **Missing** (8/9 found) | BANDRA, ANDHERI, BORIVALI, VIRAR | CHURCHGATE, DADAR, MUMBAI CENTRAL |
| **Uran Line** | **Missing** (2/7 found) | NERUL, BELAPUR | BAMANDONGRI, KHARKOPAR, URAN |

*(Note: Stations marked "found" in missing corridors exist because they are part of the broader national railway dataset or Trans-Harbour overlap, but their local suburban routes/schedules are entirely absent).*

### 2.3 Trains & Timetables
- **Local Trains in DB:** 131
- **Routes for Local Trains:** 131
- All existing 131 local trains are strictly Trans-Harbour services.

## 3. Database & System Impact
To fulfill the requirement of full Mumbai Suburban support (including intermediate searches and train changes):

### 3.1 Missing Data (Requires Import)
We are completely missing the timetable, route, and station data for Central, Western, Harbour, Uran, and Vasai-Diva lines. 
- **Action Required:** We need robust JSON datasets for these lines (similar to `trans_harbour_line_2024_structured.json`) to import into the database. Without this data, TrackEase cannot route trains locally for these corridors.

### 3.2 Station Normalization
Several Trans-Harbour stations were imported with non-standard names:
- `AIRAVALI` must be mapped/updated to `AIROLI`
- `RABADA` must be mapped/updated to `RABALE`
- `KOPAR KHAIRNA` must be mapped/updated to `KOPAR KHAIRANE`
- **Action Required:** Extend `mapping.py` or apply a Django migration to safely correct these canonical names so RapidAPI and user searches can resolve them natively.

### 3.3 Search Logic (Code Changes Required)
Currently, `train_service.py` is capable of finding trains between stations, but requires improvements to strictly honor intermediate stations (`source_sequence < destination_sequence`) in a multi-corridor environment.
- **Train Change Support:** The system currently does not natively route `Source → Interchange → Destination` (e.g., `THANE → DADAR → ANDHERI`). 
- **Action Required:** Implement a connection-routing algorithm (max 1 or 2 changes) inside `train_service.py` that identifies common interchange stations (Dadar, Kurla, Thane, Wadala Road) and calculates waiting times between arriving and departing trains.

## 4. Next Steps & Implementation Strategy

1. **Acquire/Generate Dataset:** We cannot proceed with Phase 3 (Database Changes) until we have the schedule data for Central, Western, and Harbour lines. *(Please provide or authorize the generation/scraping of these JSON datasets).*
2. **Normalize Existing Stations:** Fix the `AIRAVALI` / `RABADA` names in the database via a safe data migration or mapping update.
3. **Upgrade Search Algorithm:** Modify the `TrainService._fallback_trains_between` to support `sequence_A < sequence_B` natively for intermediate station lookups.
4. **Build Connection Engine:** Implement the 1-change journey planner for Cross-Line routing (e.g., Central to Western via Dadar).
5. **Update Frontend UI:** Ensure the autocomplete allows any station and the UI can render `Leg 1` and `Leg 2` connection blocks.

**Conclusion:** The read-only audit is complete. The existing TrackEase database is safe and untouched, but it currently only contains Trans-Harbour data. We must import the remaining corridors before the system can support network-wide Mumbai local train routing.
