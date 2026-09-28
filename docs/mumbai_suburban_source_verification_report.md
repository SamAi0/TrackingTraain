# TrackEase – Mumbai Suburban Source Verification Report

## 1. Executive Summary
The proposed sources for Mumbai Suburban Railway timetable data have been independently audited. **It is confirmed that the official NTES API (`railpull`) does not track Mumbai Local Trains (9xxxx series).** Therefore, official live API extraction is not possible for suburban routes. The Kaggle URL provided in Phase 2 was invalid/hallucinatory. 

The primary viable source identified is the **Mumbai-Local-TimeTable-Extractor** by Umang Lodaya, which extracts tabular data from `TrainHelp.in` (which in turn aggregates official railway press releases/timetables). 

## 2. Sources Verified & Rejected

### A. Rejected Sources
| Source | Reason for Rejection |
|---|---|
| **Kaggle (anirudh...unsplash)** | URL is invalid. The dataset does not exist. |
| **`railpull` (NTES extractor)** | NTES API explicitly returns `Invalid Train No./Name` for Mumbai Local trains. It only supports long-distance/Mail/Express/MEMU trains. |

### B. Verified Sources
| Source | Corridors Covered | Category | Currentness | License |
|---|---|---|---|---|
| **Umang-Lodaya/Extractor** | Central, Western, Harbour, Trans-Harbour | D (Community Extracted) | 2023-2024 | MIT |
| **Official CR Press/PDF** | Uran Line (Nerul-Uran) | A (Official) | 2024 | Gov Open |

## 3. Sample Validation (`Umang-Lodaya` CSVs)
A sample audit of `Table - 1.csv` (Trans-Harbour) and `Table - 17.csv` (Central) confirmed:
- **Actual data fields:** Train Number, Train Name/Code (e.g., `C 2 X`, `S 2`), Station Sequence (Top to bottom), Timings (e.g., `03:56`, `04:04`).
- **Route sequence:** Preserved strictly in the row order of the CSV.
- **Running days:** Partially available encoded within the Train Code string (e.g., `X` indicates does not run on Sundays/holidays, `AC` indicates air-conditioned).
- **Format:** The data is pivoted (Rows = Stations, Columns = Trains). It requires custom transposition to convert into the flat JSON structure TrackEase expects.

## 4. Missing Information & Risks
- **No Geo-Coordinates:** None of the sources provide coordinates. This must be mapped manually or left out for now.
- **Running days parsing:** The string `(Will not run on Sunday / Holiday)` or `X` must be programmatically parsed and standardized before import.
- **Data Risk:** As the source is scraped from a third-party, any anomalies (like missing cells or typos) will propagate unless explicitly validated in the parsing layer.

## 5. Recommended Source Per Corridor
1. **Central Line**: Umang-Lodaya Extractor (`Table - 17.csv` to `Table - 30.csv`)
2. **Western Line**: Umang-Lodaya Extractor
3. **Harbour Line**: Umang-Lodaya Extractor
4. **Trans-Harbour**: Umang-Lodaya Extractor / Existing TrackEase JSON
5. **Vasai-Diva / Panvel-Karjat**: Umang-Lodaya Extractor
6. **Nerul-Uran**: Manual extraction from official CR PDF

## 6. Import Readiness
**NOT READY FOR DIRECT IMPORT.**
The raw CSV files from the GitHub repository are pivoted. To proceed, we must:
1. Parse the CSV files into a flattened `<line>_raw.json` structure.
2. Normalize station names against TrackEase canonical names.
3. Validate sequence and timings.
4. Output `<line>_structured.json`.

**Only after these steps should the data be imported into MySQL.**

---
**Status:** Verification complete. Awaiting approval to begin the JSON parser/converter development (Phase 4).
