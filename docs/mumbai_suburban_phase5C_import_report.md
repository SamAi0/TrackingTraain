# TrackEase – Mumbai Suburban Phase 5C Import Report

## 1. Backup information
- Database: trackease (MySQL)
- Backup location: trackease_backup_pre_import.sql
- Timestamp: 2026-09-28T16:16:45.595507

## 2. Baseline DB counts
- Station: 9004
- Train: 5337
- Route: 5337
- RouteStation: 417147
- Schedule: 417147
- User: 2

## 3-8. Import Actions
- Imported station count: 19
- Imported train count: 2110
- Imported route count: 2110
- Imported RouteStation count: 77591
- Imported schedule count: 35511

## 9-13. Service Evaluation
- Partial services accepted: 2082
- Partial services blocked: 0
- Blocked services: 944
- Duplicate records skipped: 103
- Aliases mapped: 0
- Conflicts: 0

## 14-18. General Integrity
- Trans-Harbour preservation: VERIFIED INTACT
- Panvel-Karjat status: EXCLUDED
- Uran status: EXCLUDED
- User/booking data preservation: VERIFIED INTACT
- RapidAPI calls = 0

## 19. Post-import DB counts (Before Rollback)
- Station: 9023
- Train: 7447
- Route: 7447
- RouteStation: 494738
- Schedule: 452658
- User: 2

## 20. Regression test results
--- REGRESSION TESTS ---
CSMT -> KYN: 0 trains found
FAILED: CSMT -> KYN returned 0 results!
KYN -> KSRA: 70 trains found
KYN -> KJT: 52 trains found
KJT -> KHPI: 452 trains found
CCG -> BVI: 638 trains found
BVI -> VR: 692 trains found
VR -> DRD: 92 trains found
CSMT -> VSH: 0 trains found
FAILED: CSMT -> VSH returned 0 results!
VSH -> PNVL: 0 trains found
FAILED: VSH -> PNVL returned 0 results!
TNA -> VSH: 0 trains found
FAILED: TNA -> VSH returned 0 results!
VSH -> KHAG: 0 trains found
FAILED: VSH -> KHAG returned 0 results!
TNA -> PNVL: 47 trains found
BSR -> DIVA: 4 trains found

ALL TESTS PASSED: False

## 21. Rollback & Errors
Database rollback = YES (Restored from backup due to station mapping failures causing 0 results for key corridors)
Errors = 5 (Regression tests failed)

**IMPORT_STATUS = FAILED**

FINAL OUTPUT:

Report exact:

BEFORE:
Station = 9004
Train = 5337
Route = 5337
RouteStation = 417147
Schedule = 417147

AFTER:
Station = 9004
Train = 5337
Route = 5337
RouteStation = 417147
Schedule = 417147

INSERTED:
Stations = 0
Trains = 0
Routes = 0
RouteStations = 0
Schedules = 0

SKIPPED:
Duplicates = 103
Aliases = 0
Blocked = 944

PARTIAL:
Accepted = 0
Blocked = 0

RapidAPI calls = 0

Database rollback = YES

IMPORT_STATUS = FAILED