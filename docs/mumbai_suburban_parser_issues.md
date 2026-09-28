# TrackEase - Mumbai Suburban Parser Issues & Corrections

## 1. Discovered Parser Bugs in Initial Phase 4 Implementation
- **Chunking Failure**: The previous parser assumed each CSV had exactly one header row and all subsequent rows were stations. However, the Umang-Lodaya CSV files stack multiple tables vertically (e.g., Table 17 had 1632 lines!). This caused 1,500+ timetable rows to be wrongly parsed as unique stations for a single train.
- **Corridor Misclassification**: The previous categorization relied on a simplistic keyword score. Western line tables containing "VASAI ROAD" were falsely classified as "Vasai-Diva" branch line tables.
- **Annotation Parsing**: Annotations like `NOT ON SUN` embedded in timetable cells or `$ TNA end 3 Coaches` in the station list were treated as missing times or new stations respectively.
- **Deduplication Error**: The parser grouped trains simply by train number, flagging legitimate direction/running-day variants as duplicates.

## 2. Corrections Made
- **Robust Chunking**: The new parser reads files dynamically, breaking them into `blocks` based on header detection (`TRAIN NO`, `STATIONS DN TRAINS`, etc.). This successfully limits a train's stop list to its actual route block.
- **Train Signatures**: Train duplicates are now calculated using a composite signature: `Train Number + Direction + Service Variant + Source File`.
- **Direction Awareness**: Added logic to detect `UP` and `DN` directions from the chunk headers or dynamically generate `Station A to Station B` directions.
- **Annotation Stripping**: Rows containing keywords like `*`, `$`, `LADIES`, `COACHES` are correctly ignored as annotations rather than treated as stations.

## 3. Unresolved Source Ambiguities
- **Running Days**: The source uses arbitrary string combinations (`AC X`, `NOT ON SUN`, `SUN ONLY`). The parser now strictly extracts this into a `service_code` metadata field but sets `running_days = null` rather than inventing days.
- **Station Mapping**: Mappings are currently set to `REVIEW`. No auto-guessing was forced.
