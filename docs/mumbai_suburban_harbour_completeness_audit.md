# Phase 5B.6 — Harbour Line Source Completeness Audit

## A. Raw Harbour Files Inspected
The original raw files placed under `backend/data/mumbai_suburban/raw/harbour` were `Table - 51.csv` and `Table - 52.csv`. These tables only contain the Harbour Line Goregaon branch (CSMT–Goregaon). 
Upon performing a repository-wide text search for "VASHI" and "PANVEL", I discovered that the CSMT–Panvel branch data *is* present in the original dataset, but it was incorrectly placed in the `central` directory during Phase 4:
- `backend/data/mumbai_suburban/raw/central/Table - 19.csv`
- `backend/data/mumbai_suburban/raw/central/Table - 20.csv`
- `backend/data/mumbai_suburban/raw/central/Table - 21.csv`
- `backend/data/mumbai_suburban/raw/central/Table - 22.csv`
- `backend/data/mumbai_suburban/raw/central/Table - 23.csv`

## B. Raw Service Count
The raw files contain data for hundreds of Harbour line services on the Panvel branch.

## C. Cleaned Service Count
The parser correctly processed these misclassified tables, resulting in 722 trains stopping at both CSMT and Vashi. However, they were output into `central_cleaned.json` instead of `harbour_cleaned.json` because the parser inherits the directory name as the `corridor_name`.

## D. Branches Actually Present
- CSMT → Panvel (Present, but misclassified as `central`)
- CSMT → Vashi (Present, but misclassified as `central`)
- CSMT → Belapur (Present, but misclassified as `central`)
- CSMT → Kharghar (Present, but misclassified as `central`)
- CSMT → Goregaon (Present in `harbour_cleaned.json`)

## E. Branches Absent
- Wadala Road → Panvel (No dedicated services originating here)
- Wadala Road → Vashi (No dedicated services originating here)
- Wadala Road → Goregaon (No dedicated services originating here)
- Wadala Road → Bandra (No dedicated services originating here)

## F. VASHI Occurrence Analysis
`VASHI` appears frequently throughout the raw CSV files for Harbour line (located in `central/Table - 19.csv` to `Table - 23.csv`), as well as Trans Harbour tables (`unknown/Table - 3.csv` to `14.csv`).

## G. Parser-Loss Analysis
The parser did *not* lose the CSMT-VASHI/Panvel data. It successfully extracted the 722 services and placed them into `central_cleaned.json`.
However, the parser introduced two critical artifacts in the data it extracted:
1. It extracted the table title `"HARBOUR (MUMBAI CSMT-GOREGAON-PANVEL)"` as a legitimate station name.
2. It extracted `Wadala Road` as `"WADALA ROAD"`, which wasn't fully resolved in the `canonical_station_mapping.json` (as the existing `station_mapping.json` only knew about `"Vadala Road"` from Central, and mapping fixes were applied to specific names). 

## H. Cleaning-Loss Analysis
During the Phase 5B.5 simulated regression test (`regression_sim.py`), the test reported `0 routes found` for `CSMT -> VASHI`. The reason was **not** because the data was missing.
The root cause was that every train on this branch contained `"WADALA ROAD"` as a stop. Because `"WADALA ROAD"` was evaluated as an `UNRESOLVED` mapping, the `is_blocked = True` logic triggered, preventing all 722 trains from being imported during the simulation. Thus, 0 routes were produced.

## I. Source Completeness Conclusion
The source data for the Harbour line is **COMPLETE**. The Panvel branch data exists in the repository and was successfully parsed. The issue lies purely in misclassification of the raw CSV files and an unresolved station name string (`WADALA ROAD`) blocking the simulated import.

## J. Whether Another Source is Required
**NO.** Another source is not required. The dataset is comprehensive.

## Final Decision
**HARBOUR_SOURCE_COMPLETE = YES**
