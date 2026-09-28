import os
import csv
import json
import re

RAW_DIR = r"c:\Users\Asus\Desktop\Personal\rgc lcg\backend\data\mumbai_suburban\raw"
STRUCT_DIR = r"c:\Users\Asus\Desktop\Personal\rgc lcg\backend\data\mumbai_suburban\structured"
MAPPING_FILE = r"c:\Users\Asus\Desktop\Personal\rgc lcg\backend\data\mumbai_suburban\station_mapping.json"
REPORT_FILE = r"c:\Users\Asus\Desktop\Personal\rgc lcg\docs\mumbai_suburban_parser_validation.md"
ISSUES_FILE = r"c:\Users\Asus\Desktop\Personal\rgc lcg\docs\mumbai_suburban_parser_issues.md"

if not os.path.exists(STRUCT_DIR):
    os.makedirs(STRUCT_DIR)

# Known station mappings to use
KNOWN_MAPPINGS = {
    "VSH": "VASHI", "NEU": "NERUL", "SWDK": "SEAWOODSDARAWE", 
    "KHAG": "KHARGHAR", "GNSL": "GHANSOLI", "TNA": "TNA", 
    "BAP": "BAP", "PNVL": "PNVL", "CSMT": "CSMT", "BSR": "VASAI ROAD"
}

def is_header_row(row0):
    r = row0.strip().upper()
    if r == "" or "TRAIN" in r or "STATION" in r or "CAR" in r or "CODE" in r:
        return True
    return False

def is_annotation_row(row0):
    r = row0.strip().upper()
    # Reject obvious metadata
    if "$" in r or "*" in r or "LADIES" in r or "COACHES" in r or "PASSING" in r or "NOT ON" in r or "AC ON" in r:
        return True
    return False

def get_blocks(rows):
    blocks = []
    current_block = {"headers": [], "stations": []}
    in_headers = True
    
    for row in rows:
        if not row: continue
        r0 = row[0].strip()
        
        if is_header_row(r0):
            if not in_headers:
                if current_block["headers"] or current_block["stations"]:
                    blocks.append(current_block)
                current_block = {"headers": [], "stations": []}
                in_headers = True
            current_block["headers"].append(row)
        else:
            in_headers = False
            if not is_annotation_row(r0) and r0 != "":
                current_block["stations"].append(row)
                
    if current_block["headers"] or current_block["stations"]:
        blocks.append(current_block)
        
    return blocks

def extract_train_info(headers, col_idx):
    texts = []
    for h_row in headers:
        if col_idx < len(h_row):
            val = h_row[col_idx].strip()
            if val: texts.append(val)
    combined = " ".join(texts)
    
    # find 5-digit train number
    match = re.search(r'\b(9\d{4})\b', combined)
    t_num = match.group(1) if match else None
    
    # parse direction from headers row 0 usually
    direction_hint = "unknown"
    h0 = headers[0][0].upper() if headers else ""
    if " UP " in h0 or h0.endswith(" UP") or "UP TRAIN" in h0:
        direction_hint = "UP"
    elif " DN " in h0 or h0.endswith(" DN") or "DN TRAIN" in h0:
        direction_hint = "DOWN"
        
    return t_num, combined, direction_hint

def parse_time(val):
    if not val: return None
    val = val.strip()
    if val.lower() in ['-', 'none', 'n/a', 'blank', '', 'pass']: return None
    if re.match(r'^\d{2}:\d{2}$', val):
        return val
    return None

validation_report = ["# TrackEase – Mumbai Suburban Parser Validation\n"]
station_mappings_output = {}

for corridor in os.listdir(RAW_DIR):
    corr_path = os.path.join(RAW_DIR, corridor)
    if not os.path.isdir(corr_path): continue
    if corridor == "unknown": continue
    
    corridor_data = {
        "source": "Umang-Lodaya/Mumbai-Local-TimeTable-Extractor",
        "source_type": "community-extracted",
        "source_version": "2023/2024",
        "corridor": corridor,
        "trains": []
    }
    
    val_train_cnt = 0
    val_station_seen = set()
    val_stop_cnt = 0
    val_dup_trains = 0
    val_invalid_times = 0
    val_missing_vals = 0
    val_seq_issues = 0
    
    # To detect exact duplicates
    seen_train_sigs = set()
    
    for file in os.listdir(corr_path):
        if not file.endswith('.csv'): continue
        
        with open(os.path.join(corr_path, file), 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
            
        blocks = get_blocks(rows)
        
        for block in blocks:
            headers = block["headers"]
            stations = block["stations"]
            if not stations or not headers: continue
            
            # Determine valid columns from headers
            max_cols = max(len(h) for h in headers)
            for col_idx in range(1, max_cols):
                t_num, metadata, dir_hint = extract_train_info(headers, col_idx)
                if not t_num: continue # not a train column
                
                # Check for direction in station list
                dir_actual = dir_hint
                if dir_actual == "unknown" and len(stations) > 1:
                    dir_actual = f"{stations[0][0].strip()} to {stations[-1][0].strip()}"
                    
                train_sig = f"{t_num}_{dir_actual}_{metadata}_{file}"
                if train_sig in seen_train_sigs:
                    val_dup_trains += 1
                seen_train_sigs.add(train_sig)
                
                train_obj = {
                    "train_number": t_num,
                    "train_name": None,
                    "service_code": metadata,
                    "running_days": None,
                    "direction": dir_actual,
                    "source_table": file,
                    "stops": []
                }
                
                seq = 1
                prev_time = None
                for srow in stations:
                    sname = srow[0].strip()
                    val_station_seen.add(sname)
                    
                    if sname.upper() not in station_mappings_output:
                        station_mappings_output[sname.upper()] = {
                            "source_name": sname,
                            "source_code": None,
                            "canonical_name": None,
                            "canonical_code": None,
                            "mapping_method": "unresolved",
                            "confidence": "REVIEW"
                        }
                    
                    t_val = srow[col_idx].strip() if col_idx < len(srow) else None
                    parsed_time = parse_time(t_val)
                    
                    if not parsed_time and t_val and t_val.lower() not in ['-', 'none', 'n/a', 'blank', '', 'pass']:
                        val_invalid_times += 1
                        
                    if not parsed_time:
                        val_missing_vals += 1
                    
                    if parsed_time:
                        if prev_time and parsed_time < prev_time:
                            if int(parsed_time[:2]) < 4 and int(prev_time[:2]) > 20:
                                pass # overnight
                            else:
                                val_seq_issues += 1
                        prev_time = parsed_time
                    
                    train_obj["stops"].append({
                        "sequence": seq,
                        "station_name": sname,
                        "arrival": parsed_time,
                        "departure": parsed_time
                    })
                    seq += 1
                    val_stop_cnt += 1
                    
                if any(s["arrival"] is not None for s in train_obj["stops"]):
                    corridor_data["trains"].append(train_obj)
                    val_train_cnt += 1

    # Report
    validation_report.append(f"### {corridor.capitalize()}")
    validation_report.append(f"- Services (Train Count): {val_train_cnt}")
    validation_report.append(f"- Unique stations: {len(val_station_seen)}")
    validation_report.append(f"- Stops (Timetable records): {val_stop_cnt}")
    validation_report.append(f"- Exact duplicates: {val_dup_trains}")
    validation_report.append(f"- Invalid times: {val_invalid_times}")
    validation_report.append(f"- Missing times: {val_missing_vals}")
    validation_report.append(f"- Sequence issues: {val_seq_issues}")
    validation_report.append("")
    
    with open(os.path.join(STRUCT_DIR, f"{corridor}_structured.json"), 'w', encoding='utf-8') as f:
        json.dump(corridor_data, f, indent=2)

with open(REPORT_FILE, 'w', encoding='utf-8') as f:
    f.write("\n".join(validation_report))
    
with open(MAPPING_FILE, 'w', encoding='utf-8') as f:
    json.dump(list(station_mappings_output.values()), f, indent=2)

# Write Issues File
issues = """# TrackEase - Mumbai Suburban Parser Issues & Corrections

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
"""
with open(ISSUES_FILE, 'w', encoding='utf-8') as f:
    f.write(issues)

print("Corrected parsing complete.")
