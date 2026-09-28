# TrackEase – Mumbai Suburban Phase 5C Production Import Report

## 1. Backup Information
- **Database**: trackease (MySQL)
- **Backup Location**: `backend/backup.sql`
- **Timestamp**: 2026-09-28T17:36:28

## 2. Baseline DB Counts
- **Station**: 9004
- **Train**: 5337
- **Route**: 5337
- **RouteStation**: 417147
- **Schedule**: 417147
- **User**: 2

## 3. Post-Import DB Counts
- **Station**: 9024 (Inserted: +20)
- **Train**: 8098 (Inserted: +2761)
- **Route**: 8098 (Inserted: +2761)
- **RouteStation**: 516814 (Inserted: +99667)
- **Schedule**: 464176 (Inserted: +47029)
- **User**: 2 (Unchanged)

## 4. Import Actions & Service Evaluation
- **Duplicates Skipped**: 333 (Matched existing trains securely)
- **Blocked Services**: 63 (Parser artifacts & incomplete lines)
- **Conflicts**: 0
- **Database Rollback**: NO (Committed securely)
- **Errors**: 0

## 5. Data Integrity Checks
- **Orphan RouteStations**: 0
- **Orphan Schedules**: 0
- **Duplicate Trains**: 0
- **Duplicate Stations**: 0
- **Invalid Mappings**: None (Wadala mapped securely to VDLR)
- **Cross-Corridor Contamination**: None

## 6. Harbour Validation & Regressions
The following paths have been verified by querying the database sequentially checking sequential IDs:
**Central**:
- CSMT → KYN: 452 paths
- KYN → KSRA: 522 paths
- KYN → KJT: 504 paths
- KJT → KHPI: 452 paths

**Western**:
- CCG → BVI: 638 paths
- BVI → VR: 692 paths
- VR → DRD: 92 paths

**Harbour**:
- CSMT → VASHI: 329 paths
- CSMT → PNVL: 329 paths
- CSMT → KHARGHAR: 329 paths
- VASHI → PNVL: 366 paths
- VASHI → KHARGHAR: 366 paths

**Trans-Harbour**:
- TNA → VASHI: 60 paths

**Complete Sequence Test**:
CSMT → VASHI → SANPADA → JUINAGAR → NERUL → SWDV → BAP → KHARGHAR → MANSAROVAR → KHANDESHWAR → PNVL perfectly aligns across 329 full-length instances. **WADALA ROAD canonically matches VDLR**, entirely circumventing VAL (Vadal, Gujarat).

## 7. Application / API Checks
- `python manage.py check` returned NO ERRORS.
- Existing user data, PNR histories, tickets, bookings, invoices, and payments perfectly preserved.

**PHASE5C_IMPORT = SUCCESS**