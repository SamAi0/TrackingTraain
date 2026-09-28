# TrackEase — Mumbai Suburban Application QA Report

**Date**: 2026-09-28 | **Time**: 21:45 IST  
**Scope**: Read-Only API & Application QA — Post Phase 5C Import

---

## QA OVERVIEW

All tests conducted against the live Django application on `http://127.0.0.1:8001` using `config.settings_mysql`.  
**Zero database writes were made. Zero RapidAPI calls were made.**

---

## 1. TRAIN SEARCH API — `/api/trains/search/?source=X&destination=Y`

All return HTTP 200. Results capped at 50 per page (by design).

| Route | HTTP | Count | Sample | Status |
|-------|------|-------|--------|--------|
| CSMT → KYN | 200 | 50 | Train 95725 | ✅ PASS |
| KYN → KSRA | 200 | 50 | Train 97307 | ✅ PASS |
| KYN → KJT | 200 | 50 | Train 97315 | ✅ PASS |
| KJT → KHPI | 200 | 50 | Train 95313 | ✅ PASS |
| CCG → BVI | 200 | 50 | Train 90001 | ✅ PASS |
| BVI → VR | 200 | 50 | Train 90157 | ✅ PASS |
| VR → DRD | 200 | 50 | Train 12227 | ✅ PASS |
| CSMT → VASHI | 200 | 50 | Train 98147 | ✅ PASS |
| CSMT → PNVL | 200 | 50 | Train 98147 | ✅ PASS |
| VASHI → PNVL | 200 | 50 | Train 91393 | ✅ PASS |
| VASHI → KHARGHAR | 200 | 50 | Train 91393 | ✅ PASS |
| TNA → VASHI | 200 | 50 | Train 99001 | ✅ PASS |
| BCT → NDLS | 200 | 2 | Train 19023 | ✅ PASS |

---

## 2. MIDDLE-STATION SEARCH

Source and destination from the middle of routes:

| Route | HTTP | Count | Sample Source→Dest | Status |
|-------|------|-------|-------------------|--------|
| SANPADA → PNVL | 200 | 50 | 91393 SANPADA→PANVEL | ✅ PASS |
| NERUL → PNVL | 200 | 50 | 91393 NERUL→PANVEL | ✅ PASS |
| DDR (Dadar) → BVI | 200 | 50 | 90867 DADAR→BORIVALI | ✅ PASS |
| ADH (Andheri) → VR | 200 | 50 | 92039 ANDHERI→VIRAR | ✅ PASS |
| KCE (King's Circle) → CSMT | 200 | 50 | 98076 KING'S CIRCLE→CSMT | ✅ PASS |

**Middle-station search correctly enforces `source_sequence < destination_sequence`.**

---

## 3. TRAIN DETAIL / ROUTE API — `/api/trains/<number>/route/`

| Train | Type | HTTP | Stops | Status |
|-------|------|------|-------|--------|
| 96002 | Central (Kasara→CSMT) | 200 | 48 | ✅ PASS |
| 98301 | Harbour (CSMT→Panvel via VDLR) | 200 | 34 | ✅ PASS |
| 99001 | Trans-Harbour (TNA→VASHI) | 200 | 17 | ✅ PASS |
| 12951 | Long-distance | 200 | Accessible | ✅ PASS |

**Train 98301 verified** — VDLR (WADALA ROAD) at sequence 8:
```
1-CSMT → 2-MSD → 3-SNRD → 4-DKRD → 5-RRD → 6-CTGN → 7-SVE → 
8-VDLR(WADALA ROAD) → 9-KCE → ... → 25-VASHI → ... → 34-PNVL
```

---

## 4. STATION AUTOCOMPLETE API — `/api/stations/autocomplete/?q=X`

| Query | HTTP | Result Codes | Status |
|-------|------|-------------|--------|
| CSMT | 200 | [CSMT] | ✅ PASS |
| VASHI | 200 | [VASHI] | ✅ PASS |
| PANVEL | 200 | [PNVL] | ✅ PASS |
| KALYAN | 200 | [KYN, KYI, KYNT] | ✅ PASS |
| BORIVALI | 200 | [BVI] | ✅ PASS |
| ANDHERI | 200 | [ADH] | ✅ PASS |
| THANE | 200 | [NGTN, TNA, TNDE] | ✅ PASS |
| KHARGHAR | 200 | [KHARGHAR] | ✅ PASS |
| **WADALA** | 200 | **[VDLR=WADALA ROAD]** | ✅ PASS |
| **VDLR** | 200 | **[VDLR=WADALA ROAD]** | ✅ PASS |

---

## 5. CANONICAL MAPPING VERIFICATION

| Source → Canonical | Code | Status |
|-------------------|------|--------|
| WADALA ROAD → VDLR | VDLR | ✅ PASS |
| VASHI → VASHI | VASHI | ✅ PASS |
| KALYAN → KALYAN JN | KYN | ✅ PASS |
| KALYANPUR ROAD → KALYANPUR ROAD | KPRD | ✅ PASS |
| VAL remains VADAL, Gujarat | VAL | ✅ PASS (not linked to any Mumbai route) |

---

## 6. RAPIDAPI

- **No RapidAPI calls made** ✅
- 27 history records intact with `response_json` populated
- Latest record: endpoint `/autocomplete/train/121`, HTTP 200, success=True

---

## 7. FRONTEND

- **GET http://127.0.0.1:8001/ → HTTP 200** ✅
- HTML page loads correctly (DOCTYPE, meta viewport confirmed)
- `/api/trains/stats/ → HTTP 200` with zone-wise station breakdown

---

## 8. REGRESSION CHECK

```
$ python manage.py check
System check identified no issues (0 silenced).
```
✅ PASS

---

## FINAL STATUS

**APPLICATION_QA = PASS**
