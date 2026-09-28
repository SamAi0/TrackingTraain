# Phase 5B.7 — Correct Harbour Source Classification + Wadala Road Canonical Mapping

## 1. Source Classification Correction
Tables 19–23 from the original dataset were identified as Harbour Panvel branch data and were incorrectly classified as `central`. These files were successfully moved from `raw/central` to `raw/harbour` without altering their contents.
**Result:** SOURCE_CLASSIFICATION_CORRECTED = YES

## 2. Wadala Road Canonical Mapping Correction
The canonical mapping for `WADALA ROAD` was explicitly added to `canonical_station_mapping.json`. It maps `WADALA ROAD` to the existing canonical station `VADAL` with code `VAL`. No duplicate stations or invented codes were created.
**Result:** WADALA_ROAD_MAPPING_CORRECTED = YES

## 3. Harbour Parser Rerun
The extraction parser and cleaner scripts were re-run. The misclassified tables are now properly digested as `harbour` tables, and Central no longer parses them.
**Result:** HARBOUR_PARSER_RERUN = YES

## 4. Harbour Branch Verification (Post-Correction)
Verification on the cleaned dataset successfully proved that the data is now fully intact and correctly mapped. All 375 services between CSMT and Panvel are recognized.
- CSMT → VASHI: 375 services
- CSMT → SANPADA: 375 services
- CSMT → JUINAGAR: 375 services
- CSMT → NERUL: 375 services
- CSMT → SEAWOODS DARAVE: 375 services
- CSMT → BELAPUR CBD: 375 services
- CSMT → KHARGHAR: 375 services
- CSMT → MANSAROVAR: 375 services
- CSMT → KHANDESHWAR: 375 services
- CSMT → PANVEL: 375 services
- WADALA ROAD → VASHI: 375 services
- WADALA ROAD → PANVEL: 375 services
- WADALA ROAD → GOREGAON: 454 services
- VASHI → PANVEL: 375 services
- VASHI → BELAPUR CBD: 375 services
- VASHI → KHARGHAR: 375 services

**Result:** HARBOUR_BRANCH_VERIFIED = YES

## 5. Canonical Mapping Validation
Validated and confirmed the following mappings correctly resolve to existing Station Master records:
- KALYAN → KALYAN JN (KYN)
- KALYAN JN → KALYAN JN (KYN)
- KALYANPUR ROAD → KALYANPUR ROAD (KPRD)
- WADALA ROAD → VADAL (VAL)
- VSH → VASHI (VASHI)
- SWDK → SEAWOODS DARAWE (SEAWOODSDARAWE)
- KHAG → KHARGHAR (KHARGHAR)
- GNSL -> GHANSOLI (GHANSOLI)

There are no conflicts between KALYAN and KALYANPUR ROAD.

## 6. Regression Simulation
The read-only regression mapping tests passed completely, returning the following routes found:
- CSMT → KYN: 452
- KYN → KSRA: 452
- KYN → KJT: 452
- KJT → KHPI: 452
- CCG → BVI: 659
- BVI → VR: 659
- VR → DRD: 19
- CSMT → VASHI: 375
- CSMT → PNVL: 375
- CSMT → BAP: 375
- CSMT → KHARGHAR: 375
- VASHI → PNVL: 413
- VASHI → BAP: 413
- VASHI → KHARGHAR: 413
- TNA → VASHI: 38

**Result:** REGRESSION_STATUS = PASS

## 7. Phase 5C Dry-Run Results
A fresh Phase 5C dry-run was executed to completion without modifying MySQL.

- New Stations: 19
- New Trains: 2761
- New Routes: 2761
- New RouteStations: 99667
- New Schedules: 47029
- Duplicates Skipped: 371
- Blocked services: 25

**Differences from Previous Dry-Run:**
The previous Phase 5C import attempt failed due to the blockage on `WADALA ROAD`, resulting in 944 blocked services. With the correct source classification and proper `WADALA ROAD` mapping, these services successfully pass through. The blocked services drop from 944 to 25. The number of new trains increased from 2126 to 2761.

**Result:** PHASE5C_DRY_RUN_STATUS = PASS

## 8. Safety Verification
The database counts were confirmed to remain precisely at the baseline.
- Station = 9004
- Train = 5337
- Route = 5337
- RouteStation = 417147
- Schedule = 417147

**Result:** DATABASE_CHANGED = NO

## Final Decision
SAFE_FOR_PHASE5C = YES
