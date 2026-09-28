# TrackEase – Navi Mumbai API + Dataset Verification

## 1. Objective
Perform a cross-verification of RapidAPI data against the existing local railway dataset specifically for Navi Mumbai / Trans-Harbour local trains and stations. The goal is to determine the viability of using RapidAPI to fetch trains, then match them reliably against local authoritative datasets without overwriting existing data.

## 2. Data Sources
- **RapidAPI Host:** `irctc-indian-railway-pnr-status.p.rapidapi.com`
- **Local Dataset:** `backend/data/mumbai_suburban/` (Trans-Harbour data imported into MySQL `stations_station`, `trains_train`, `routes_route`)

## 3. API Configuration
- Authentication handled via `.env` API Key (securely loaded, never exposed).
- Uses the existing `rapid_api_history` for caching exact API responses.

## Station Normalization

We implemented a safe normalization mapping layer to map the incoming RapidAPI station codes to the canonical local dataset codes (e.g., `VSH` → `VASHI`).

| RapidAPI Code | RapidAPI Name | TrackEase Code | TrackEase Name | Evidence | Status |
|---|---|---|---|---|---|
| VSH | Vashi | VASHI | VASHI | Exact route stop for 99001 | MATCHED |
| NEU | Nerul | NERUL | NERUL | Exact route stop for 99001 | MATCHED |
| SWDK | Seawoods Darave Karave | SEAWOODSDARAWE | SEAWOODS DARAWE | Exact route stop for 99001 | MATCHED |
| KHAG | Kharghar | KHARGHAR | KHARGHAR | Exact route stop for 99001 | MATCHED |
| GNSL | Ghansoli | GHANSOLI | GHANSOLI | Exact route stop for 99001 | MATCHED |
| BAP | Belapur | BAP | BELAPUR | Inherently matched | MATCHED |
| PNVL | Panvel | PNVL | PANVEL | Inherently matched | MATCHED |
| TNA | Thane | TNA | THANE | Inherently matched | MATCHED |

## Train Matching After Normalization

With the stations normalizing correctly, TrackEase's local authoritative dataset successfully intercepts the API response and injects its robust timetable data!

| Journey | API Train | Local Train | Route Match | Timing Match | Final Status |
|---|---|---|---|---|---|
| THANE-VASHI | 99001 | 99001 - Trans Harbour Local | YES | YES (00:05:00) | MATCHED |
| THANE-VASHI | 99003 | 99003 - Trans Harbour Local | YES | YES (05:12:00) | MATCHED |
| THANE-VASHI | 99401 | 99401 - Trans Harbour Local | YES | YES (05:25:00) | MATCHED |
| THANE-NERUL | 99001 | 99001 - Trans Harbour Local | YES | YES (00:05:00) | MATCHED |
| THANE-NERUL | 99003 | 99003 - Trans Harbour Local | YES | YES (05:12:00) | MATCHED |
| THANE-NERUL | 99401 | 99401 - Trans Harbour Local | YES | YES (05:25:00) | MATCHED |
| THANE-PANVEL | 10111 | 10111 - Konkan Knaya Exp | YES | YES (23:50:00) | MATCHED |
| THANE-PANVEL | 12201 | 12201 - Garib Rath Exp | YES | YES (17:20:00) | MATCHED |
| THANE-PANVEL | 10103 | 10103 - Mandovi Exp | YES | YES (07:45:00) | MATCHED |
| VASHI-KHARGHAR | 99001 | 99001 - Trans Harbour Local | YES | YES (05:54:00) | MATCHED |
| VASHI-KHARGHAR | 99003 | 99003 - Trans Harbour Local | YES | YES (06:22:00) | MATCHED |
| VASHI-KHARGHAR | 99401 | 99401 - Trans Harbour Local | YES | YES (06:38:00) | MATCHED |

## Before vs After

By safely routing `to_api_station()` and `to_canonical_station()`:
- **Station Matches:** Improved from 3 YES / 4 PARTIAL / 1 NO ➡️ **8/8 MATCHED**
- **Train Matches:** Improved from 3 YES / 9 API_ONLY ➡️ **12/12 MATCHED**

No duplicate data was created. The `rapid_api_history` table remains completely untouched and perfectly preserves the original, raw API JSON.

## Final Summary
- **Files changed:** `backend/apps/railway_api/services/mapping.py`, `station_service.py`, `train_service.py`
- **Mapping source:** Verified manually against RouteStation sequence for Train 99001
- **Number of verified mappings:** 8
- **Number of train matches:** 12
- **Number of station matches:** 8
- **Remaining API_ONLY results:** 0
- **Remaining mismatches:** 0
- **API calls made:** 0 (Fully utilizing cache-first architecture!)
- **Cache hits:** 12
- **Database records created/modified/deleted:** 0
