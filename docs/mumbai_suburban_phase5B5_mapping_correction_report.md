# TrackEase - Phase 5B.5: Canonical Station Mapping Correction Report

## 1. Previous Mapping Defect
In the failed Phase 5C import, critical station aliases were incorrectly resolved. The string matcher over-aggressively mapped Central Line stations to incorrect physical stations (e.g., KALYAN to Kalyanpur Road). Additionally, the regression tests were mistakenly testing RapidAPI normalization codes (like `VSH`) instead of TrackEase local canonical codes (like `VASHI`).

## 2. KALYAN Correction
- KALYAN and KALYAN JN have been strictly hardcoded to map to **KYN** (Kalyan Junction).
- KALYANPUR ROAD has been verified and strictly mapped to **KPRD** (Kalyanpur Road).
- Any failsafe logic checks ensure KALYAN doesn't default to KPRD.

## 3. VASHI/API Correction
The API-to-TrackEase normalizations have been explicitly preserved as `API_NORMALIZATION` types:
- `VSH` → `VASHI`
- `NEU` → `NERUL`
- `SWDK` → `SEAWOODSDARAWE`
- `KHAG` → `KHARGHAR`
- `GNSL` → `GHANSOLI`
- `BAP` → `BAP`
- `PNVL` → `PNVL`
- `TNA` → `TNA`

## 4. All Canonical Mappings
167 canonical mappings have been successfully generated into `backend/data/mumbai_suburban/canonical_station_mapping.json`.
- `EXISTING_DB_EXACT`: 58
- `EXISTING_DB_ALIAS`: 77
- `NEW_VERIFIED_STATION`: 22
- `API_NORMALIZATION`: 8
- `UNRESOLVED`: 2

## 5. Ambiguous Station Audit
A comprehensive audit of the `Station` master revealed:
- `VASHI` correctly resolves to `VASHI` (VASHI).
- `SEAWOODS` aliases correctly resolve to `SEAWOODSDARAWE` (SEAWOODS DARAWE).
- `TURBHE` correctly resolves to `TURBHE` (TURBHE).
- `AIROLI` (from CSV) has been mapped to `AIRAVALI` (the existing TrackEase code for Airoli).
- `RABALE` (from CSV) has been mapped to `RABADA` (the existing TrackEase code for Rabale).
- `KOPAR KHAIRANE` (from CSV) has been mapped to `KOPARKHAIRNA` (the existing TrackEase code for Kopar Khairane).
- `DIGHA GAON` (from CSV) has been mapped to `DIGHAGAON` (the existing TrackEase code for Digha Gaon).

## 6. RouteStation Validation
Before any simulated import, the existing `RouteStation` sequences confirm:
- `KYN` belongs to Kalyan Junction.
- `KPRD` belongs to Kalyanpur Road.
- `VASHI` belongs to Vashi.
- `PNVL` belongs to Panvel.
- `TNA` belongs to Thane.
- `KHARGHAR` belongs to Kharghar.

## 7. Dry-run Results
Using the corrected mappings, the simulated dry-run (Phase 5B.5) produced:
- **Importable:** 29
- **Partially_Resolved:** 2184
- **Blocked:** 944
- **New_Stations:** 19
- **New_Trains:** 2110
- **New_Routes:** 2110
- **New_RouteStations:** 77591
- **New_Schedules:** 35511
- **Duplicates:** 103
- **Conflicts:** 0

## 8. Regression Mapping Simulation
The simulation checked if the incoming data + existing DB data can satisfy the specified routes:
- CSMT → KYN: 452 routes found
- KYN → KSRA: 452 routes found
- KYN → KJT: 452 routes found
- KJT → KHPI: 452 routes found
- **CSMT → VASHI: 0 routes found (FAIL)**
- VASHI → PNVL: 37 DB routes found instead
- TNA → VASHI: 60 DB routes found instead
- VASHI → KHARGHAR: 37 DB routes found instead
- CCG → BVI: 659 routes found
- BVI → VR: 659 routes found
- VR → DRD: 19 routes found
- BSR → DIVA: 4 DB routes found instead

## 9. Database Counts
MySQL counts remain strictly unchanged from the rollback:
- Station = 9004
- Train = 5337
- Route = 5337
- RouteStation = 417147
- Schedule = 417147

## 10. RapidAPI Calls
RapidAPI calls = 0 (No external calls were made).

## 11. Remaining Blockers
While the mapping correction correctly routed 2110 trains (including Central Line CSMT -> KYN), the simulated regression test for **CSMT -> VASHI** failed.
The root cause is that the underlying `harbour_cleaned.json` data currently *does not contain any services connecting CSMT to VASHI or Panvel*. The parser output for Harbour line only successfully extracted the Goregaon branch (CSMT to Goregaon), leaving the primary Panvel branch missing from the JSON dataset itself.

Because the underlying CSV extraction data is missing this critical corridor, the regression mapping simulation fails.

**SAFE_FOR_PHASE5C = NO**

STOP.
DO NOT IMPORT.
