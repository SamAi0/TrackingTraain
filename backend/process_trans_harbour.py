import json
import re
import os
import sys

def process():
    input_file = "C:/Users/Asus/Desktop/Personal/rgc lcg/trans_harbour_line_2024_timetable.json"
    output_dir = "C:/Users/Asus/Desktop/Personal/rgc lcg/backend/data/mumbai_suburban"
    output_file = os.path.join(output_dir, "trans_harbour_line_2024_structured.json")
    report_file = "C:/Users/Asus/.gemini/antigravity-ide/brain/8584ac8c-7413-4635-b3b4-726ecc23a9fb/trackease_trans_harbour_2024_data_audit.md"
    
    os.makedirs(output_dir, exist_ok=True)
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    pages = data.get('timetable_pages', [])
    
    services_map = {}
    
    # Audit stats
    total_services = 0
    total_stations = set()
    total_timetable_rows = 0
    valid_timings = 0
    invalid_timings = []
    missing_values = 0
    duplicate_services = []
    station_names = set()
    
    for page in pages:
        lines = page.get('text', '').split('\n')
        
        train_nos = []
        train_codes = []
        
        station_times = {} # name -> list of times
        
        current_times = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line: continue
            
            if line.startswith("Train No."):
                parts = line.split()
                train_nos = parts[2:]
                continue
            
            if line.startswith("Train Code"):
                continue # Sometimes train code is before or after
                
            # If the line looks like train codes (e.g., TPL 1 TPL 3)
            if any(code in line for code in ['TPL', 'TV', 'TNU', 'TBR']) and not any(c.isdigit() for c in line if c == ':'):
                # Simple extraction, just ignore if hard to align for now, we'll map by index
                continue
                
            # If line is times
            if ':' in line and any(c.isdigit() for c in line):
                parts = line.split()
                # Check if this line is pure times
                if all(':' in p or p.isdigit() or p=='X' for p in parts):
                    current_times = parts
                    continue
                else:
                    # Mixed line (times then station or station then times)
                    pass
                    
            # If line is station name
            if not any(c.isdigit() for c in line) and len(line) > 2 and line != "Train Code" and line != "X X":
                station_name = line
                if current_times:
                    if station_name not in station_times:
                        station_times[station_name] = []
                    station_times[station_name].extend(current_times)
                    current_times = []
                    total_stations.add(station_name)
                    station_names.add(station_name)
                    
        # Now map to services
        for idx, t_no in enumerate(train_nos):
            if t_no in services_map:
                duplicate_services.append(t_no)
                
            service = {
                "service_number": t_no,
                "train_code": None,
                "service_name": None,
                "origin": None,
                "destination": None,
                "running_days": None,
                "stations": []
            }
            
            seq = 1
            for st_name, times in station_times.items():
                if idx < len(times):
                    time_val = times[idx]
                    
                    is_valid = False
                    reason = ""
                    
                    if time_val == "" or time_val == "-" or time_val == "X":
                        missing_values += 1
                        parsed_time = None
                    elif re.match(r'^([01]\d|2[0-3]):([0-5]\d)$', time_val):
                        valid_timings += 1
                        parsed_time = time_val
                        is_valid = True
                    else:
                        parsed_time = time_val
                        reason = "Malformed time pattern"
                        invalid_timings.append({
                            "service": t_no,
                            "station": st_name,
                            "raw": time_val,
                            "reason": reason
                        })
                        
                    if parsed_time is not None:
                        service["stations"].append({
                            "sequence": seq,
                            "station_name": st_name,
                            "station_code": None,
                            "arrival_time": parsed_time,
                            "departure_time": parsed_time
                        })
                        seq += 1
                        total_timetable_rows += 1
                        
            if len(service["stations"]) > 0:
                service["origin"] = service["stations"][0]["station_name"]
                service["destination"] = service["stations"][-1]["station_name"]
                
            services_map[t_no] = service
            total_services += 1
            
    # Compile JSON
    structured_data = {
        "source": "trans_harbour_line_2024_timetable.json",
        "line": "trans_harbour",
        "timetable_year": 2024,
        "services": list(services_map.values())
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(structured_data, f, indent=2)
        
    # Validation Report
    report = f"""# Trans Harbour 2024 Data Audit

## Statistics
- Total services detected: {total_services}
- Total stations detected: {len(total_stations)}
- Total timetable rows: {total_timetable_rows}
- Valid timing values: {valid_timings}
- Invalid/malformed timing values: {len(invalid_timings)}
- Missing arrival/departure values: {missing_values}

## Issues
- Duplicate services: {len(duplicate_services)} (Sample: {duplicate_services[:5]})
- Station name inconsistencies: OCR generated duplicated letters (e.g. GGHHAANNSSOOLLII). All unique stations found: {', '.join(sorted(station_names))}

### Malformed Timings (Sample 10)
"""
    for inv in invalid_timings[:10]:
        report += f"- Service {inv['service']} at {inv['station']}: `{inv['raw']}` ({inv['reason']})\n"
        
    if len(invalid_timings) > 10:
        report += f"... and {len(invalid_timings) - 10} more.\n"

    report += """
## Compatibility Check (TrackEase)
1. **service -> Train**: Each `service_number` maps to a `Train` record. The `train_type` would be `LOCAL`.
2. **station -> Station**: OCR station names (e.g. `DIGHA GAON`, `THANE`, `GGHHAANNSSOOLLII`) need mapping to standard `Station` codes.
3. **service route -> Route**: A `Route` record links the `Train`.
4. **station sequence -> RouteStation**: `RouteStation` defines the order of stops and distances (which are missing in this source, requiring fallback logic or manual updates).
5. **arrival/departure -> Schedule**: `Schedule` records time at each station. Malformed OCR times (e.g. `0000::1199`) MUST be cleaned before mapping to SQL `TimeField`.

**IMPORT STATUS:** NOT IMPORTED
No MySQL data was modified.
"""
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
        
    print("Done. Output written to", output_file)
    print("Report written to", report_file)
    
if __name__ == "__main__":
    process()
