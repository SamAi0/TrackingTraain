# TrackEase RailDrishti Preparation Report

## 1. Prepared 12951 dataset

- Train: 12951 — Mumbai Central-New Delhi Rajdhani Express
- Route records: 202
- Source station: BCT
- Destination station: NDLS
- Intermediate stations: Yes
- Sequence: generated from source record order
- Coordinates: joined from `stations.json`
- Running days: not available
- Historical/current status: historical/reference; not verified as current

Files:
- `trackease_12951_ready.json`
- `trackease_12951_ready.csv`

## 2. Mumbai/Navi Mumbai relevant subset

Selection is based on station codes verified against the uploaded RailDrishti data. It is intentionally a subset, not the complete 417,080-record dataset.

- Schedule records: 4857
- Unique trains: 469
- Unique stations: 46

Files:
- `trackease_mumbai_navi_relevant_subset.json`
- `trackease_mumbai_navi_stations.csv`
- `trackease_mumbai_navi_schedules.csv`

## 3. Database plan

Recommended separation:

- MySQL: railway master/route/schedule data (including the large RailDrishti-derived dataset if approved)
- Supabase: user/account/application-user data only

Do not import these prepared files automatically. Review/dry-run first.

## 4. Important limitations

- This RailDrishti dataset is historical/reference data.
- Running days are not provided in `schedules.json`.
- The Mumbai/Navi subset is not a complete suburban-local timetable.
- Missing data is not invented or interpolated.
- Existing MySQL data must be backed up/preserved before any replacement or merge.
